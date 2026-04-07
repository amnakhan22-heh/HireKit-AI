import json
import os
from openai import OpenAI
from .prompts import FULL_KIT_PROMPT, SECTION_REGENERATION_PROMPT, SECTION_SCHEMAS


def generate_full_kit(
    role_description: str,
    role_level: str = "",
    industry: str = "",
    company_size: str = "",
    remote_policy: str = "",
) -> dict:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    prompt = FULL_KIT_PROMPT.format(
        role_description=role_description,
        role_level=role_level or "Not specified",
        industry=industry or "Not specified",
        company_size=company_size or "Not specified",
        remote_policy=remote_policy or "Not specified",
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.7,
    )

    raw_content = response.choices[0].message.content
    return _parse_and_validate_kit(raw_content)


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
