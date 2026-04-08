# HireKit AI — Architecture

## Overview

HireKit AI has two distinct user flows sharing the same backend: **hiring managers** who create and manage interview kits, and **candidates** who browse published roles and submit their CV for AI-powered matching.

---

## High-Level Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        React Frontend                           │
│                                                                 │
│  Public                      │  Manager (authenticated)        │
│  ─────────────────────────   │  ──────────────────────────     │
│  /                (Home)     │  /manager     (Dashboard)       │
│  /how-it-works               │  /manager/roles/new             │
│  /kits            (Browse)   │  /kits/:id    (View / Edit)     │
│  /roles/:id  (Apply + CV)    │                                 │
│                              │                                 │
│              src/api/kitApi.js  (all fetch calls)              │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTP + Token Auth
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│                     Django REST Framework                       │
│                                                                 │
│  urls.py  ──►  views.py  ──►  serializers.py                   │
│                   │                                             │
│                   ▼                                             │
│              services.py  (all AI calls go here)               │
│              prompts.py   (all prompt strings go here)         │
│                   │                                             │
│         ┌─────────┴──────────┐                                 │
│         │                    │                                 │
│      Kit Gen             CV Match                              │
│      Pipeline            Pipeline                              │
│         │                    │                                 │
│      rag.py             cv_pipeline.py                         │
│         │               (LangGraph)                            │
│         │                    │                                 │
│    ChromaDB              2-node graph                          │
│  (vector store)      extract → score                           │
│                                                                 │
│              models.py  ──►  PostgreSQL                        │
└─────────────────────────────────────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
   OpenAI Embeddings          OpenAI Chat
   (text-embedding-3-small)   (gpt-4o / gpt-4o-mini)
```

---

## Manager Flow — Kit Generation

```
Manager fills role form
        │
        ▼
POST /api/generate/full-kit/
        │
        ▼
GenerateFullKitView  ──►  InterviewKitCreateSerializer (validates input)
        │
        ▼
services.generate_full_kit()
        │
        ├──► rag.retrieve_relevant_questions()
        │         │
        │         ├── _expand_query()        gpt-4o-mini
        │         │   (turns role context    (query expansion)
        │         │    into search query)
        │         │
        │         └── ChromaDB cosine search
        │             (returns top-10 relevant questions
        │              from knowledge_base.json)
        │
        ├── prompts.py  (FULL_KIT_PROMPT with RAG results injected)
        │
        └── gpt-4o  ──►  JSON response
                │
                ▼
        Parsed into 4 sections:
        ┌─────────────────────────┐
        │  job_description        │
        │  scorecard              │
        │  interview_questions    │
        │  skills_assessment_rubric│
        └─────────────────────────┘
                │
                ▼
        InterviewKit.objects.create()  ──►  PostgreSQL
                │
                ▼
        InterviewKitSerializer  ──►  JSON response to frontend
```

---

## Candidate Flow — CV Matching

```
Candidate uploads CV PDF on a published role page
        │
        ▼
POST /api/kits/:id/match-cv/
        │
        ▼
CVMatchView
        │
        ├── utils.extract_text_from_pdf()  (pdfplumber)
        │
        └── services.match_cv_to_role()
                │
                ▼
        cv_pipeline.build_cv_match_graph()  (LangGraph)
                │
                ▼
        ┌───────────────────────────────┐
        │  Node 1: extract_profile      │
        │  ─────────────────────────    │
        │  Input:  raw CV text          │
        │  Model:  gpt-4o-mini          │
        │  Output: structured candidate │
        │          profile (JSON)       │
        └──────────────┬────────────────┘
                       │
                       ▼
        ┌───────────────────────────────┐
        │  Node 2: score_candidate      │
        │  ─────────────────────────    │
        │  Input:  candidate profile    │
        │          + role requirements  │
        │  Model:  gpt-4o               │
        │  Output: match score,         │
        │          strengths, gaps      │
        └──────────────┬────────────────┘
                       │
                       ▼
              JSON response to frontend
              (score, strengths, gaps — not persisted)
```

---

## Data Model

```
InterviewKit
├── id              UUID (PK)
├── role_title      CharField
├── role_description TextField
├── role_level      CharField  (Junior / Mid-level / Senior / Lead)
├── industry        CharField  (Tech / Finance / Healthcare / …)
├── company_size    CharField  (Startup / Mid-size / Enterprise)
├── remote_policy   CharField  (Remote / Hybrid / On-site)
├── generated_kit   JSONField  ← the 4 sections live here
├── status          CharField  (draft | published)
├── created_by      FK → User
└── created_at      DateTimeField
```

`generated_kit` JSON structure:
```json
{
  "job_description": {
    "role_level": "...",
    "summary": "...",
    "responsibilities": [...],
    "required_qualifications": [...],
    "preferred_qualifications": [...],
    "what_we_offer": [...]
  },
  "scorecard": {
    "dimensions": [
      { "name": "...", "weight": "...", "criteria": [...] }
    ]
  },
  "interview_questions": {
    "behavioral": [
      { "question": "...", "what_to_listen_for": "..." }
    ],
    "technical": [
      { "question": "...", "what_to_listen_for": "..." }
    ]
  },
  "skills_assessment_rubric": {
    "skills": [
      {
        "skill": "...",
        "levels": {
          "below_expectations": "...",
          "meets_expectations": "...",
          "exceeds_expectations": "..."
        }
      }
    ]
  }
}
```

---

## Authentication

- DRF Token Authentication — one token per user, stored in the database
- Frontend stores the token in `localStorage`, attaches it as `Authorization: Token <token>` on every protected request
- Draft kits are only visible to their owner; published kits are public
- CV matching requires no authentication — candidates are anonymous

---

## Key Architectural Rules

| Rule | Where enforced |
|------|---------------|
| All OpenAI calls go through `services.py` | CLAUDE.md + code review |
| All prompt strings live in `prompts.py` | CLAUDE.md + code review |
| All frontend API calls go through `src/api/kitApi.js` | CLAUDE.md + code review |
| Views are thin — business logic in services | CLAUDE.md |
| Serializers validate all input before it reaches views | CLAUDE.md |
| Never raw SQL — Django ORM only | CLAUDE.md |
