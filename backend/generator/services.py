import json
import os
from openai import OpenAI
from .prompts import FULL_KIT_PROMPT


def generate_full_kit(role_description: str) -> dict:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    prompt = FULL_KIT_PROMPT.format(role_description=role_description)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.7,
    )

    raw_content = response.choices[0].message.content
    return _parse_and_validate_kit(raw_content)


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
