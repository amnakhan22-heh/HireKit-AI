import json
import logging
import os
from openai import OpenAI
from .prompts import FULL_KIT_PROMPT, SECTION_REGENERATION_PROMPT, SECTION_SCHEMAS, CV_MATCH_PROMPT
from .rag import retrieve_relevant_questions

logger = logging.getLogger(__name__)


def generate_full_kit(
    role_description: str,
    role_level: str = "",
    industry: str = "",
    company_size: str = "",
    remote_policy: str = "",
) -> dict:
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

    return kit


def _parse_and_validate_section(raw_content: str, section_name: str) -> dict:
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
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    job_desc = role_data.get('job_description', {})
    required_qualifications = '\n'.join(
        f'- {q}' for q in job_desc.get('required_qualifications', [])
    )
    preferred_qualifications = '\n'.join(
        f'- {q}' for q in job_desc.get('preferred_qualifications', [])
    )

    prompt = CV_MATCH_PROMPT.format(
        role_title=role_data.get('role_title', ''),
        role_level=role_data.get('role_level', 'Not specified'),
        job_description_summary=job_desc.get('summary', ''),
        required_qualifications=required_qualifications or 'Not specified',
        preferred_qualifications=preferred_qualifications or 'Not specified',
        cv_text=cv_text,
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.3,
    )

    raw_content = response.choices[0].message.content
    return _parse_and_validate_cv_match(raw_content)


def _parse_and_validate_cv_match(raw_content: str) -> dict:
    try:
        result = json.loads(raw_content)
    except json.JSONDecodeError as error:
        raise ValueError(f"OpenAI returned invalid JSON: {error}") from error

    required_keys = [
        'compatibility_percentage',
        'explanation',
        'strengths_matched',
        'gaps_identified',
    ]
    missing = [key for key in required_keys if key not in result]
    if missing:
        raise ValueError(f"CV match result is missing required keys: {missing}")

    if not isinstance(result['compatibility_percentage'], int):
        raise ValueError("compatibility_percentage must be an integer")

    return result
