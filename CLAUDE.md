# HireKit AI

## Project Overview
An amazing AI-powered tool where hiring managers describe a role in plain language and receive a complete, printable interview kit containing:
- A polished, inclusive job description aligned with industry-standard role levels
- A structured interview scorecard
- Behavioral and technical interview questions with evaluation criteria
- A skills assessment rubric

Candidates can also browse published roles and upload their CV to receive an AI-powered match score against a role.

## Tech Stack
- **Backend:** Django REST Framework, PostgreSQL
- **Frontend:** React + Vite + Tailwind CSS
- **AI:** OpenAI API (gpt-4o)
- **Auth:** DRF Token Authentication

## Project Structure
job-kit-generator/
├── backend/
│   ├── core/              # Django project settings
│   ├── generator/         # Main app: models, views, serializers
│   │   ├── services.py    # All OpenAI API calls go here, nowhere else
│   │   ├── prompts.py     # All prompt templates go here
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── tests/
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api/           # All API calls to backend go here
│   │   └── main.jsx
│   └── package.json
├── CLAUDE.md
└── README.md

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/login/ | Authenticate and receive token |
| POST | /api/auth/logout/ | Invalidate token |
| POST | /api/generate/full-kit/ | Generate complete interview kit from role description |
| GET | /api/kits/ | List kits (own kits if authenticated, published only if not) |
| GET | /api/kits/:id/ | Retrieve a specific kit |
| PATCH | /api/kits/:id/ | Update role_title or role_description |
| DELETE | /api/kits/:id/ | Delete a kit |
| PATCH | /api/kits/:id/publish/ | Toggle kit status between draft and published |
| POST | /api/kits/:id/regenerate-section/ | Regenerate a single section of a kit |
| POST | /api/kits/:id/match-cv/ | Match a candidate CV PDF against a published kit |

## Frontend Pages
| Route | Page | Access |
|-------|------|--------|
| / | Home (hero + CTA) | Public |
| /how-it-works | How It Works (manager + candidate flows) | Public |
| /kits | Browse Open Roles | Public |
| /roles/:id | Role detail + CV upload | Public |
| /kits/:id | Kit detail + edit sections | Public (draft = owner only) |
| /login | Manager login | Public |
| /manager | Manager dashboard (My Roles) | Protected |
| /manager/roles/new | Create new role | Protected |

## Coding Standards

### General
- Never hardcode secrets, API keys, or credentials — always use environment variables
- Every function must have a clear single responsibility
- Use descriptive variable and function names — no abbreviations like `tmp`, `x`, `fn`
- Keep functions under 30 lines; break up anything longer
- Always handle errors explicitly — no silent failures
- When i ask you to make agents always make them inside this project under the /agents folder 

### Backend (Django)
- Follow PEP 8 strictly for all Python code
- Use Django ORM for all database operations — never raw SQL
- All OpenAI calls must go through `generator/services.py` only
- All prompt strings must live in `generator/prompts.py` only — never inline
- Serializers must validate all input before it reaches views
- Views must be thin — business logic belongs in services, not views
- Write pytest-django tests for every endpoint before marking a feature done
- Return structured JSON always — never return raw text from the API
- Use Django's built-in pagination for list endpoints

### Frontend (React)
- Use functional components and hooks only — no class components
- All backend API calls must go through `src/api/` — never call fetch/axios directly in components
- Keep components small and focused — one responsibility per component
- Use Tailwind utility classes for styling — no custom CSS files unless absolutely necessary
- Handle loading and error states for every API call

### AI / Prompts
- All prompts must be version-controlled in `generator/prompts.py`
- Prompts must explicitly instruct the model to use inclusive, bias-free language
- Prompts must request structured JSON output — parse and validate before saving
- Never expose raw OpenAI responses directly to the frontend

### Git
- Commit after every working feature — not before
- Use clear commit messages: `feat:`, `fix:`, `test:`, `refactor:`
- Never commit `.env` files or secrets

## Environment Variables
```env
OPENAI_API_KEY=
DATABASE_URL=
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

## Running the Project

### Backend
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Tests
```bash
cd backend
pytest
```