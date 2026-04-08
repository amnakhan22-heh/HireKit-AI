QUERY_EXPANSION_PROMPT = """
You are a talent acquisition expert. Given a job role description and context, extract a
concise list of the most relevant keywords and themes for finding interview questions.

Include: key technical skills, soft skills, seniority signals, domain knowledge areas,
and likely interview themes (e.g. system design, stakeholder management, debugging).

Role Level: {role_level}
Industry: {industry}
Role Description: {role_description}

Respond with a single plain-text paragraph of comma-separated keywords and short phrases.
No bullet points, no headers, no explanation — just the keywords.
"""

FULL_KIT_PROMPT = """
You are an expert talent acquisition specialist and HR professional. A hiring manager has described
a role they want to fill. Your task is to generate a complete, professional interview kit.

Use inclusive, bias-free language throughout. Avoid gendered pronouns. Focus on skills and
outcomes, not personal characteristics.

Role Description provided by the hiring manager:
{role_description}

Additional context to tailor the kit:
- Role Level: {role_level}
- Industry: {industry}
- Company Size: {company_size}
- Remote Policy: {remote_policy}

Use all of the above context to make the job description, scorecard, interview questions, and
skills rubric highly specific and relevant. For example:
- Adjust seniority expectations and compensation language to match the role level.
- Use industry-appropriate terminology and domain knowledge in questions and rubrics.
- Reflect the company size culture (e.g. Startup: generalist scope, bias for action;
  Enterprise: process, stakeholder management).
- Include remote/hybrid/on-site expectations in responsibilities and what_we_offer sections.

Reference questions from our curated knowledge base (use as inspiration and starting points,
but generate a complete, fully tailored kit — do not copy these verbatim):
{reference_questions}

IMPORTANT: The interview_questions section must contain a minimum of 3 behavioral questions
and a minimum of 3 technical questions. Do not generate fewer than this.

Return a single JSON object with exactly this structure (no markdown, no extra text):
{{
  "job_description": {{
    "role_title": "<standardized title aligned with industry norms>",
    "role_level": "<e.g. Junior, Mid-level, Senior, Staff, Principal>",
    "summary": "<2-3 sentence overview of the role and its impact>",
    "responsibilities": ["<responsibility 1>", "<responsibility 2>", "..."],
    "required_qualifications": ["<qualification 1>", "<qualification 2>", "..."],
    "preferred_qualifications": ["<qualification 1>", "<qualification 2>", "..."],
    "what_we_offer": ["<benefit or value proposition 1>", "..."]
  }},
  "scorecard": {{
    "dimensions": [
      {{
        "name": "<dimension name, e.g. Technical Skills>",
        "weight": "<percentage, e.g. 30%>",
        "criteria": ["<criterion 1>", "<criterion 2>"]
      }}
    ]
  }},
  "interview_questions": {{
    "behavioral": [
      {{
        "question": "<behavioral question using STAR format cue>",
        "what_to_listen_for": "<evaluation guidance for the interviewer>"
      }}
    ],
    "technical": [
      {{
        "question": "<technical question>",
        "what_to_listen_for": "<evaluation guidance for the interviewer>"
      }}
    ]
  }},
  "skills_assessment_rubric": {{
    "skills": [
      {{
        "skill": "<skill name>",
        "levels": {{
          "below_expectations": "<description>",
          "meets_expectations": "<description>",
          "exceeds_expectations": "<description>"
        }}
      }}
    ]
  }}
}}
"""

SECTION_REGENERATION_PROMPT = """
You are an expert talent acquisition specialist and HR professional. Regenerate only the
"{section_name}" section of an interview kit for the following role.

Use inclusive, bias-free language throughout. Avoid gendered pronouns.

Role Description:
{role_description}

Context:
- Role Level: {role_level}
- Industry: {industry}
- Company Size: {company_size}
- Remote Policy: {remote_policy}

Return a single JSON object containing only the "{section_name}" key with fresh, high-quality
content. Use the same schema as below (no markdown, no extra text):

{section_schema}
"""

JOB_DESCRIPTION_SCHEMA = """{
  "job_description": {
    "role_title": "<standardized title>",
    "role_level": "<Junior/Mid-level/Senior/Lead>",
    "summary": "<2-3 sentence overview>",
    "responsibilities": ["<responsibility>", "..."],
    "required_qualifications": ["<qualification>", "..."],
    "preferred_qualifications": ["<qualification>", "..."],
    "what_we_offer": ["<benefit>", "..."]
  }
}"""

SCORECARD_SCHEMA = """{
  "scorecard": {
    "dimensions": [
      {
        "name": "<dimension name>",
        "weight": "<percentage>",
        "criteria": ["<criterion>", "..."]
      }
    ]
  }
}"""

INTERVIEW_QUESTIONS_SCHEMA = """{
  "interview_questions": {
    "behavioral": [
      {
        "question": "<behavioral question>",
        "what_to_listen_for": "<evaluation guidance>"
      }
    ],
    "technical": [
      {
        "question": "<technical question>",
        "what_to_listen_for": "<evaluation guidance>"
      }
    ]
  }
}"""

SKILLS_RUBRIC_SCHEMA = """{
  "skills_assessment_rubric": {
    "skills": [
      {
        "skill": "<skill name>",
        "levels": {
          "below_expectations": "<description>",
          "meets_expectations": "<description>",
          "exceeds_expectations": "<description>"
        }
      }
    ]
  }
}"""

SECTION_SCHEMAS = {
    "job_description": JOB_DESCRIPTION_SCHEMA,
    "scorecard": SCORECARD_SCHEMA,
    "interview_questions": INTERVIEW_QUESTIONS_SCHEMA,
    "skills_assessment_rubric": SKILLS_RUBRIC_SCHEMA,
}

CV_EXTRACT_PROMPT = """
You are a talent acquisition specialist. Extract structured information from the candidate's CV.
Ignore all personal details such as name, age, gender, ethnicity, nationality, and address.
Focus only on professional content.

CV Text:
{cv_text}

Return a single JSON object with exactly this structure (no markdown, no extra text):
{{
  "skills": ["<skill 1>", "<skill 2>", "..."],
  "years_of_experience": <integer or null if unclear>,
  "education": ["<degree and field>", "..."],
  "achievements": ["<notable achievement 1>", "..."],
  "previous_roles": ["<job title at company>", "..."]
}}
"""

CV_MATCH_PROMPT = """
You are an expert talent acquisition specialist producing a detailed candidate evaluation report.
Be specific — reference actual skills, roles, and achievements from the candidate profile.
Never be vague or generic. Every insight must be grounded in evidence from the candidate profile.
Use inclusive, bias-free language. Do not reference age, gender, ethnicity, or nationality.

Job Title: {role_title}
Role Level: {role_level}

Job Description Summary:
{job_description_summary}

Required Qualifications:
{required_qualifications}

Preferred Qualifications:
{preferred_qualifications}

Candidate Profile (pre-extracted from CV):
{candidate_profile}

Return a single JSON object with exactly this structure (no markdown, no extra text):
{{
  "compatibility_percentage": <integer between 0 and 100>,
  "score_explanation": "<one paragraph explaining exactly why this score was given — reference specific matches and gaps that drove the number>",
  "executive_summary": "<2-3 paragraphs: who this candidate is professionally, how well they fit this specific role, and what kind of employee they would likely be based on their CV>",
  "key_strengths": [
    {{
      "strength": "<specific skill or experience from their CV>",
      "relevance": "<why this is directly relevant to this role>",
      "match_level": "<Strong Match | Good Match | Partial Match>"
    }}
  ],
  "key_gaps": [
    {{
      "gap": "<what is missing or underdeveloped relative to the role requirements>",
      "criticality": "<Critical | Important | Minor>",
      "learnable_on_job": <true | false>
    }}
  ],
  "experience_analysis": "<detailed paragraph comparing the candidate's years and type of experience to what this role requires — be specific about where they align and where they fall short>",
  "cultural_and_role_fit": "<paragraph assessing whether their background suggests they would thrive in this type of role, company size, and industry — reference their previous roles and achievements as evidence>",
  "recommendation": "<Strong Fit | Good Fit | Possible Fit | Not a Fit>",
  "recommendation_detail": "<detailed paragraph explaining the recommendation and specific advice for the hiring manager on what to probe in the interview — name the actual areas to dig into>"
}}

Rules:
- key_strengths must contain a minimum of 5 items
- key_gaps must contain a minimum of 4 items
- Every field must be populated — no nulls, no empty strings, no empty arrays
- Do not copy the job description back — evaluate the candidate against it
"""
