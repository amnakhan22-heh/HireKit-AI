# API Reference

Base URL: `http://localhost:8000`

All endpoints are mounted under `/api/`. Endpoints that require authentication expect a DRF token in the `Authorization` header:

```
Authorization: Token <your-token>
```

---

## Authentication

### Login

**`POST /api/auth/login/`**

Authenticates a user and returns a DRF token. No authentication header required.

#### Request Body

```json
{
  "username": "string",
  "password": "string"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | string | Yes | The user's Django username |
| `password` | string | Yes | The user's password |

#### Success Response

**Status:** `200 OK`

```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "username": "hiring_manager"
}
```

#### Error Responses

**`400 Bad Request`** — Invalid credentials

```json
{
  "detail": "Invalid credentials."
}
```

---

### Logout

**`POST /api/auth/logout/`**

Deletes the authenticated user's token, ending the session.

#### Request Body

None.

#### Success Response

**Status:** `204 No Content`

#### Error Responses

**`401 Unauthorized`** — Missing or invalid token

```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## Interview Kit Generation

### Generate Full Kit

**`POST /api/generate/full-kit/`**

Generates a complete interview kit from a plain-language role description. Uses a RAG pipeline to enrich the prompt with semantically relevant questions from the knowledge base, then calls gpt-4o to produce the full kit. The resulting kit is saved to the database and returned.

Requires authentication.

#### Request Body

```json
{
  "role_description": "string",
  "role_level": "string",
  "industry": "string",
  "company_size": "string",
  "remote_policy": "string"
}
```

| Field | Type | Required | Allowed Values | Description |
|-------|------|----------|----------------|-------------|
| `role_description` | string | Yes | 20–5000 characters | Plain-language description of the role written by the hiring manager |
| `role_level` | string | No | `Junior`, `Mid-level`, `Senior`, `Lead` | Seniority level; leave blank if unspecified |
| `industry` | string | No | `Tech`, `Finance`, `Healthcare`, `Marketing`, `Operations`, `Other` | Industry context for tailoring the kit |
| `company_size` | string | No | `Startup`, `Mid-size`, `Enterprise` | Company size context; affects tone and scope |
| `remote_policy` | string | No | `Remote`, `Hybrid`, `On-site` | Work arrangement; included in job description output |

#### Success Response

**Status:** `201 Created`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "role_title": "Senior Software Engineer",
  "role_description": "We need a senior engineer to own our backend services...",
  "role_level": "Senior",
  "industry": "Tech",
  "company_size": "Startup",
  "remote_policy": "Remote",
  "generated_kit": {
    "job_description": {
      "role_title": "Senior Software Engineer",
      "role_level": "Senior",
      "summary": "2-3 sentence overview...",
      "responsibilities": ["Design and maintain REST APIs", "..."],
      "required_qualifications": ["5+ years Python", "..."],
      "preferred_qualifications": ["Experience with Django REST Framework", "..."],
      "what_we_offer": ["Fully remote", "Competitive salary", "..."]
    },
    "scorecard": {
      "dimensions": [
        {
          "name": "Technical Skills",
          "weight": "40%",
          "criteria": ["Writes clean, maintainable code", "..."]
        }
      ]
    },
    "interview_questions": {
      "behavioral": [
        {
          "question": "Tell me about a time you led a complex project...",
          "what_to_listen_for": "Look for ownership, stakeholder communication, outcome."
        }
      ],
      "technical": [
        {
          "question": "How would you design a rate-limiting system at scale?",
          "what_to_listen_for": "Understanding of tokens, sliding windows, tradeoffs."
        }
      ]
    },
    "skills_assessment_rubric": {
      "skills": [
        {
          "skill": "Python",
          "levels": {
            "below_expectations": "Struggles with idiomatic patterns.",
            "meets_expectations": "Writes clean, working Python.",
            "exceeds_expectations": "Optimises performance, mentors others."
          }
        }
      ]
    }
  },
  "status": "draft",
  "created_by": "hiring_manager",
  "created_at": "2026-04-08T10:00:00Z"
}
```

> `interview_questions.behavioral` will contain at least 3 questions. `interview_questions.technical` will contain at least 3 questions.

#### Error Responses

**`400 Bad Request`** — Validation failure (e.g., description too short, invalid choice)

```json
{
  "role_description": ["Role description must be at least 20 characters."]
}
```

**`401 Unauthorized`** — Missing or invalid token

```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## Kit Management

### List Kits

**`GET /api/kits/`**

Returns a paginated list of interview kits.

- Authenticated users see all kits they created (draft and published).
- Unauthenticated users see only published kits.

Authentication is optional.

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number (default: 1). Page size is 20. |

#### Success Response

**Status:** `200 OK`

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "role_title": "Senior Software Engineer",
      "role_description": "...",
      "role_level": "Senior",
      "industry": "Tech",
      "company_size": "Startup",
      "remote_policy": "Remote",
      "generated_kit": { "...": "..." },
      "status": "published",
      "created_by": "hiring_manager",
      "created_at": "2026-04-08T10:00:00Z"
    }
  ]
}
```

---

### Retrieve Kit

**`GET /api/kits/<kit-id>/`**

Retrieves a single interview kit by its UUID.

- Published kits are accessible to everyone.
- Draft kits are only accessible to the user who created them.

Authentication is optional.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `kit-id` | UUID | The UUID of the interview kit |

#### Success Response

**Status:** `200 OK`

Returns the full kit object (same shape as the generate response above).

#### Error Responses

**`404 Not Found`** — Kit does not exist, or kit is a draft and the requesting user is not the owner

```json
{
  "detail": "Not found."
}
```

---

### Update Kit

**`PATCH /api/kits/<kit-id>/`**

Updates editable fields on a kit. Only the owner can update their own kits.

Requires authentication.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `kit-id` | UUID | The UUID of the interview kit |

#### Request Body

All fields are optional. Only the fields provided will be updated.

```json
{
  "role_title": "string",
  "role_description": "string"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `role_title` | string | No | Override the displayed role title |
| `role_description` | string | No | Update the stored role description |

#### Success Response

**Status:** `200 OK`

Returns the full updated kit object.

#### Error Responses

**`401 Unauthorized`** — Missing or invalid token

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**`404 Not Found`** — Kit does not exist or belongs to another user

```json
{
  "detail": "Not found."
}
```

---

### Delete Kit

**`DELETE /api/kits/<kit-id>/`**

Permanently deletes a kit. Only the owner can delete their own kits.

Requires authentication.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `kit-id` | UUID | The UUID of the interview kit |

#### Success Response

**Status:** `204 No Content`

#### Error Responses

**`401 Unauthorized`** — Missing or invalid token

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**`404 Not Found`** — Kit does not exist or belongs to another user

```json
{
  "detail": "Not found."
}
```

---

### Toggle Publish Status

**`PATCH /api/kits/<kit-id>/publish/`**

Sets a kit's status to `published` or `draft`. Published kits are publicly visible.

Requires authentication.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `kit-id` | UUID | The UUID of the interview kit |

#### Request Body

```json
{
  "status": "published"
}
```

| Field | Type | Required | Allowed Values | Description |
|-------|------|----------|----------------|-------------|
| `status` | string | Yes | `draft`, `published` | New status for the kit |

#### Success Response

**Status:** `200 OK`

Returns the full updated kit object with the new `status` value.

#### Error Responses

**`400 Bad Request`** — Invalid status value

```json
{
  "status": ["\"invalid\" is not a valid choice."]
}
```

**`401 Unauthorized`** — Missing or invalid token

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**`404 Not Found`** — Kit does not exist or belongs to another user

```json
{
  "detail": "Not found."
}
```

---

### Regenerate Section

**`POST /api/kits/<kit-id>/regenerate-section/`**

Regenerates a single section of an existing kit using gpt-4o. The regenerated section replaces the existing section in the database and is returned in the response. The rest of the kit is unchanged.

Requires authentication.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `kit-id` | UUID | The UUID of the interview kit |

#### Request Body

```json
{
  "section_name": "scorecard"
}
```

| Field | Type | Required | Allowed Values | Description |
|-------|------|----------|----------------|-------------|
| `section_name` | string | Yes | `job_description`, `scorecard`, `interview_questions`, `skills_assessment_rubric` | The section to regenerate |

#### Success Response

**Status:** `200 OK`

```json
{
  "section_name": "scorecard",
  "data": {
    "dimensions": [
      {
        "name": "Problem Solving",
        "weight": "30%",
        "criteria": ["Breaks down ambiguous problems", "..."]
      }
    ]
  }
}
```

The `data` field contains the raw regenerated section content (the value, not the key).

#### Error Responses

**`400 Bad Request`** — Invalid section name

```json
{
  "section_name": ["\"invalid_section\" is not a valid choice."]
}
```

**`401 Unauthorized`** — Missing or invalid token

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**`404 Not Found`** — Kit does not exist or belongs to another user

```json
{
  "detail": "Not found."
}
```

---

## CV Matching

### Match CV to Role

**`POST /api/kits/<kit-id>/match-cv/`**

Accepts a candidate's CV as a PDF file upload and scores it against the requirements of the specified kit. The kit must be in `published` status. No authentication is required — this endpoint is intended for public-facing job applicant use.

Uses a two-stage LangGraph pipeline: first extracts a structured candidate profile from the CV text (gpt-4o-mini), then scores it against the role requirements (gpt-4o).

Authentication is not required.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `kit-id` | UUID | The UUID of a **published** interview kit |

#### Request Body

`Content-Type: multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `cv_file` | file | Yes | The candidate's CV as a PDF file |

#### Success Response

**Status:** `200 OK`

```json
{
  "compatibility_percentage": 82,
  "score_explanation": "The candidate scores 82% due to strong Python and API design experience that directly matches the required qualifications...",
  "executive_summary": "This candidate is a mid-career software engineer with 6 years of backend experience...",
  "key_strengths": [
    {
      "strength": "Python and Django REST Framework",
      "relevance": "Core technology stack for this role",
      "match_level": "Strong Match"
    }
  ],
  "key_gaps": [
    {
      "gap": "No demonstrated experience with Kubernetes",
      "criticality": "Important",
      "learnable_on_job": true
    }
  ],
  "experience_analysis": "The candidate has 6 years in backend engineering, which aligns with the Senior level requirement...",
  "cultural_and_role_fit": "Previous roles at two startups suggest comfort with ambiguity and generalist scope...",
  "recommendation": "Strong Fit",
  "recommendation_detail": "Recommend proceeding to technical interview. Probe Kubernetes experience and system design depth."
}
```

| Field | Type | Description |
|-------|------|-------------|
| `compatibility_percentage` | integer | Score from 0 to 100 |
| `score_explanation` | string | One paragraph explaining the score |
| `executive_summary` | string | 2-3 paragraph candidate profile and fit assessment |
| `key_strengths` | array | At least 5 strengths with `strength`, `relevance`, and `match_level` (`Strong Match`, `Good Match`, `Partial Match`) |
| `key_gaps` | array | At least 4 gaps with `gap`, `criticality` (`Critical`, `Important`, `Minor`), and `learnable_on_job` (boolean) |
| `experience_analysis` | string | Detailed comparison of candidate experience vs. role requirements |
| `cultural_and_role_fit` | string | Assessment of fit based on background and previous roles |
| `recommendation` | string | One of: `Strong Fit`, `Good Fit`, `Possible Fit`, `Not a Fit` |
| `recommendation_detail` | string | Detailed recommendation and interview probe suggestions |

#### Error Responses

**`400 Bad Request`** — Missing file

```json
{
  "detail": "cv_file is required."
}
```

**`400 Bad Request`** — File is not a PDF

```json
{
  "detail": "File must be a PDF."
}
```

**`400 Bad Request`** — PDF is unreadable (e.g., scanned image)

```json
{
  "detail": "Could not extract text from the PDF. The file may be scanned or unreadable."
}
```

**`404 Not Found`** — Kit does not exist or is not published

```json
{
  "detail": "Not found."
}
```

---

## Kit Object Schema

All endpoints that return a kit object use this shape:

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Unique identifier |
| `role_title` | string | Role title extracted from the generated job description |
| `role_description` | string | Original plain-language description submitted by the hiring manager |
| `role_level` | string | Seniority level (`Junior`, `Mid-level`, `Senior`, `Lead`, or blank) |
| `industry` | string | Industry context (`Tech`, `Finance`, etc., or blank) |
| `company_size` | string | Company size (`Startup`, `Mid-size`, `Enterprise`, or blank) |
| `remote_policy` | string | Work arrangement (`Remote`, `Hybrid`, `On-site`, or blank) |
| `generated_kit` | object | Full JSON kit with `job_description`, `scorecard`, `interview_questions`, and `skills_assessment_rubric` |
| `status` | string | `draft` or `published` |
| `created_by` | string | Username of the hiring manager who created the kit (or `null`) |
| `created_at` | ISO 8601 datetime | Creation timestamp in UTC |
