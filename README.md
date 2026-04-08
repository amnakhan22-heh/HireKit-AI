# Job Kit Generator

> An AI-powered tool for hiring managers who describe a role in plain language and receive a complete, printable interview kit in return.

## Features

- Generate a complete interview kit from a plain-language role description
- Produces an inclusive, bias-free job description aligned with industry-standard role levels
- Generates a structured interview scorecard with weighted evaluation dimensions
- Creates behavioral and technical interview questions with per-question evaluation guidance
- Produces a skills assessment rubric with below/meets/exceeds levels per skill
- RAG (Retrieval-Augmented Generation) pipeline enriches prompts with semantically similar questions from a curated knowledge base stored in ChromaDB
- Two-stage LangGraph pipeline for CV matching: extract candidate profile, then score against role requirements
- Per-section regeneration — refresh any one section of a kit without regenerating the whole kit
- Publish/draft status control for sharing kits publicly
- Token-based authentication for hiring manager accounts
- PDF export of the generated kit from the browser

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Django REST Framework, SQLite (dev) / PostgreSQL (prod) |
| Frontend | React 19 + Vite + Tailwind CSS 4 |
| AI — kit generation | OpenAI API (gpt-4o) |
| AI — CV extraction | OpenAI API (gpt-4o-mini via LangChain) |
| AI — CV scoring | OpenAI API (gpt-4o via LangChain) |
| RAG retrieval | ChromaDB + OpenAI text-embedding-3-small |
| CV pipeline | LangGraph (2-node state graph) |
| Auth | DRF Token Authentication |

## Prerequisites

- Python 3.10+
- Node.js 18+
- An OpenAI API key

> The project ships with SQLite for development. For production, install PostgreSQL and set `DATABASE_URL` accordingly (requires `psycopg2-binary`, which is already in `requirements.txt`).

## Installation

### 1. Clone the Repository

```bash
git clone <repo-url>
cd job-kit-generator
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file inside `backend/`:

```env
OPENAI_API_KEY=sk-...
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

Run database migrations:

```bash
python manage.py migrate
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

## Running Locally

### Backend

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`.

> The frontend API client is hardcoded to `http://127.0.0.1:8001/api`. If you run the backend on port 8000 (the default), update `BASE_URL` in `frontend/src/api/kitApi.js` to match.

### Running Tests

```bash
cd backend
pytest
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | `sk-...` |
| `SECRET_KEY` | Django secret key | `your-secret-key` |
| `DEBUG` | Enable Django debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `localhost,127.0.0.1` |
| `CORS_ALLOWED_ORIGINS` | Comma-separated list of allowed CORS origins | `http://localhost:5173` |

Create a `.env` file in the `backend/` directory:

```env
OPENAI_API_KEY=
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

> `DATABASE_URL` is listed in `CLAUDE.md` as a future variable. The current settings file uses SQLite by default and does not read `DATABASE_URL`. Configure `DATABASES` in `backend/core/settings.py` directly for PostgreSQL.

## Project Structure

```
job-kit-generator/
├── backend/
│   ├── core/               Django project settings and root URL conf
│   └── generator/          Main application
│       ├── services.py     All OpenAI API calls — sole entry point for AI
│       ├── prompts.py      All prompt templates and JSON schemas
│       ├── rag.py          ChromaDB knowledge base and RAG retrieval
│       ├── cv_pipeline.py  LangGraph 2-node CV matching graph
│       ├── utils.py        PDF text extraction helper
│       ├── models.py       InterviewKit model
│       ├── views.py        Thin API views
│       ├── serializers.py  Input validation serializers
│       ├── urls.py         URL routing
│       └── tests/          pytest-django test suite
├── frontend/
│   └── src/
│       ├── api/            All backend fetch calls (kitApi.js)
│       ├── components/     Reusable UI components
│       ├── context/        AuthContext for token management
│       ├── pages/          Route-level page components
│       └── utils/          PDF export utility
├── CLAUDE.md
└── README.md
```

## Screenshots

> Screenshots coming soon.

<!-- Add screenshots here once UI is finalized -->
