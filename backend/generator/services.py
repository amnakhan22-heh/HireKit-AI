import json
import logging
import os
from openai import OpenAI
from .prompts import FULL_KIT_PROMPT, SECTION_REGENERATION_PROMPT, SECTION_SCHEMAS
from .rag import retrieve_relevant_questions
from .cv_pipeline import build_cv_match_graph

logger = logging.getLogger(__name__)


def generate_full_kit(
    role_description: str,
    role_level: str = "",
    industry: str = "",
    company_size: str = "",
    remote_policy: str = "",
) -> dict:
    """
    Generate a complete interview kit for the described role using gpt-4o.

    Fetches semantically relevant reference questions via the RAG pipeline,
    formats them into the prompt, and calls the OpenAI chat completions API.
    The response is parsed, structurally validated, and returned as a dict.

    Args:
        role_description (str): Plain-language description of the role, written
            by the hiring manager. Must be between 20 and 5000 characters.
        role_level (str): Seniority level (e.g. "Senior"). Defaults to "".
        industry (str): Industry context (e.g. "Tech"). Defaults to "".
        company_size (str): Company size (e.g. "Startup"). Defaults to "".
        remote_policy (str): Work arrangement (e.g. "Remote"). Defaults to "".

    Returns:
        dict: Validated kit containing keys: ``job_description``, ``scorecard``,
            ``interview_questions``, and ``skills_assessment_rubric``.

    Raises:
        ValueError: If the OpenAI response cannot be parsed as JSON, if any of
            the four required top-level sections are missing, or if the generated
            kit contains fewer than 3 behavioral or 3 technical questions.
    """
    reference_questions = _fetch_reference_questions(
        role_description=role_description,
        role_level=role_level,
        industry=industry,
    )
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    prompt = FULL_KIT_PROMPT.format(
        role_description=role_description,
        role_level=role_level or "Not specified",
        industry=industry or "Not specified",
        company_size=company_size or "Not specified",
        remote_policy=remote_policy or "Not specified",
        reference_questions=_format_reference_questions(reference_questions),
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.7,
    )

    print("\n--- RAG PROMPT PREVIEW ---\n", prompt[:3000], "\n---\n")
    raw_content = response.choices[0].message.content
    return _parse_and_validate_kit(raw_content)


def _fetch_reference_questions(
    role_description: str,
    role_level: str,
    industry: str,
) -> list:
    """Return RAG-retrieved questions, or an empty list if retrieval fails."""
    try:
        return retrieve_relevant_questions(
            role_title="",
            role_description=role_description,
            role_level=role_level or "",
            industry=industry or "",
            n=10,
        )
    except Exception as error:
        logger.warning("RAG retrieval failed, proceeding without context: %s", error)
        return []


def _format_reference_questions(questions: list) -> str:
    """Format a list of question strings as a numbered reference list."""
    if not questions:
        return "No reference questions available."
    return "\n".join(f"{index + 1}. {question}" for index, question in enumerate(questions))


def generate_section(
    section_name: str,
    role_description: str,
    role_level: str = "",
    industry: str = "",
    company_size: str = "",
    remote_policy: str = "",
) -> dict:
    """
    Regenerate a single section of an interview kit using gpt-4o.

    Looks up the expected JSON schema for the given section name, builds a
    targeted prompt, and calls the OpenAI chat completions API. The response
    is parsed and validated to ensure the expected section key is present.

    Args:
        section_name (str): The kit section to regenerate. Must be one of:
            ``job_description``, ``scorecard``, ``interview_questions``,
            ``skills_assessment_rubric``.
        role_description (str): Original plain-language role description.
        role_level (str): Seniority level. Defaults to "".
        industry (str): Industry context. Defaults to "".
        company_size (str): Company size context. Defaults to "".
        remote_policy (str): Work arrangement. Defaults to "".

    Returns:
        dict: The regenerated section content (the value under ``section_name``,
            not a wrapper dict).

    Raises:
        KeyError: If ``section_name`` is not present in ``SECTION_SCHEMAS``.
        ValueError: If the OpenAI response cannot be parsed as JSON or if the
            expected section key is absent from the response.
    """
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    schema = SECTION_SCHEMAS[section_name]
    prompt = SECTION_REGENERATION_PROMPT.format(
        section_name=section_name,
        role_description=role_description,
        role_level=role_level or "Not specified",
        industry=industry or "Not specified",
        company_size=company_size or "Not specified",
        remote_policy=remote_policy or "Not specified",
        section_schema=schema,
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.7,
    )

    raw_content = response.choices[0].message.content
    return _parse_and_validate_section(raw_content, section_name)


def _parse_and_validate_kit(raw_content: str) -> dict:
    """
    Parse and structurally validate the raw JSON string returned by gpt-4o for a full kit.

    Args:
        raw_content (str): Raw JSON string from the OpenAI chat completion response.

    Returns:
        dict: Parsed and validated kit dictionary.

    Raises:
        ValueError: If the content is not valid JSON, if any of the four required
            top-level keys are missing, or if the interview question minimums
            are not met.
    """
    try:
        kit = json.loads(raw_content)
    except json.JSONDecodeError as error:
        raise ValueError(f"OpenAI returned invalid JSON: {error}") from error

    required_keys = [
        "job_description",
        "scorecard",
        "interview_questions",
        "skills_assessment_rubric",
    ]
    missing = [key for key in required_keys if key not in kit]
    if missing:
        raise ValueError(f"Generated kit is missing required sections: {missing}")

    _validate_interview_question_minimums(kit)
    return kit


def _validate_interview_question_minimums(kit: dict) -> None:
    """
    Raise ValueError if the kit contains fewer than 3 behavioral or 3 technical questions.

    Args:
        kit (dict): Parsed kit dictionary containing an ``interview_questions`` key.

    Raises:
        ValueError: If ``behavioral`` or ``technical`` question lists have fewer
            than 3 items each.
    """
    questions = kit.get("interview_questions", {})
    behavioral_count = len(questions.get("behavioral", []))
    technical_count = len(questions.get("technical", []))
    if behavioral_count < 3:
        raise ValueError(
            f"Generated kit has only {behavioral_count} behavioral question(s); minimum is 3."
        )
    if technical_count < 3:
        raise ValueError(
            f"Generated kit has only {technical_count} technical question(s); minimum is 3."
        )


def _parse_and_validate_section(raw_content: str, section_name: str) -> dict:
    """
    Parse and validate the raw JSON string returned by gpt-4o for a single section.

    Args:
        raw_content (str): Raw JSON string from the OpenAI chat completion response.
        section_name (str): The expected top-level key that must be present in the
            parsed JSON (e.g. ``"scorecard"``).

    Returns:
        dict: The section content extracted from under ``section_name``.

    Raises:
        ValueError: If the content is not valid JSON or if ``section_name`` is
            absent from the parsed object.
    """
    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError as error:
        raise ValueError(f"OpenAI returned invalid JSON: {error}") from error

    if section_name not in data:
        raise ValueError(
            f"Regenerated section is missing expected key '{section_name}'"
        )

    return data[section_name]


def match_cv_to_role(cv_text: str, role_data: dict) -> dict:
    """
    Score a candidate's CV against a role using the LangGraph CV matching pipeline.

    Builds a formatted state dict from the role data, invokes the two-node
    LangGraph graph (extract profile, then score), and validates the final
    match result before returning it.

    Args:
        cv_text (str): Plain text extracted from the candidate's CV PDF.
        role_data (dict): Role context with keys ``role_title``, ``role_level``,
            and ``job_description`` (a dict containing ``summary``,
            ``required_qualifications``, and ``preferred_qualifications``).

    Returns:
        dict: Validated CV match result containing compatibility score,
            strengths, gaps, and hiring recommendation.

    Raises:
        ValueError: If the pipeline result is missing required keys, if
            ``compatibility_percentage`` is not an integer, or if the minimum
            strength/gap counts are not met.
    """
    job_desc = role_data.get('job_description', {})
    required_qualifications = '\n'.join(
        f'- {q}' for q in job_desc.get('required_qualifications', [])
    )
    preferred_qualifications = '\n'.join(
        f'- {q}' for q in job_desc.get('preferred_qualifications', [])
    )

    graph = build_cv_match_graph()
    final_state = graph.invoke({
        "cv_text": cv_text,
        "role_title": role_data.get('role_title', ''),
        "role_level": role_data.get('role_level', 'Not specified'),
        "job_description_summary": job_desc.get('summary', ''),
        "required_qualifications": required_qualifications or 'Not specified',
        "preferred_qualifications": preferred_qualifications or 'Not specified',
        "candidate_profile": {},
        "match_result": {},
    })

    return _parse_and_validate_cv_match(json.dumps(final_state["match_result"]))


def _parse_and_validate_cv_match(raw_content: str) -> dict:
    """
    Parse and validate the JSON result produced by the CV scoring LangGraph node.

    Args:
        raw_content (str): JSON string of the match result dict.

    Returns:
        dict: Validated CV match result.

    Raises:
        ValueError: If the content is not valid JSON, if required keys are missing,
            if ``compatibility_percentage`` is not an integer, or if ``key_strengths``
            contains fewer than 5 items or ``key_gaps`` fewer than 4 items.
    """
    try:
        result = json.loads(raw_content)
    except json.JSONDecodeError as error:
        raise ValueError(f"OpenAI returned invalid JSON: {error}") from error

    required_keys = [
        'compatibility_percentage',
        'score_explanation',
        'executive_summary',
        'key_strengths',
        'key_gaps',
        'experience_analysis',
        'cultural_and_role_fit',
        'recommendation',
        'recommendation_detail',
    ]
    missing = [key for key in required_keys if key not in result]
    if missing:
        raise ValueError(f"CV match result is missing required keys: {missing}")

    if not isinstance(result['compatibility_percentage'], int):
        raise ValueError("compatibility_percentage must be an integer")
    if len(result['key_strengths']) < 5:
        raise ValueError("CV match result must contain at least 5 key strengths")
    if len(result['key_gaps']) < 4:
        raise ValueError("CV match result must contain at least 4 key gaps")

    return result
