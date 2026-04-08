# HireKit AI — Build Log

A running log of issues hit, decisions made, and lessons learned throughout development.

---

## Phase 1 — Initial Setup

Scaffolded the monorepo with Django REST Framework on the backend and React + Vite + Tailwind on the frontend. Set up DRF Token Authentication from the start to avoid retrofitting auth later.

**Decisions made:**
- All OpenAI calls isolated to `generator/services.py` — no inline API calls anywhere else
- All prompt strings live in `generator/prompts.py` — version-controlled and swappable
- PostgreSQL over SQLite from the start since the app was always going to be deployed

---

## Phase 2 — React Frontend

Built the initial single-page React app. At this point everything lived on one scrollable home page — hero, how it works, and get started CTA all stacked vertically.

---

## Phase 3 — Custom Agents + Skills

### Claude Code Skills (`.claude/skills/`)
Added reusable slash-command skills for common one-off tasks invoked directly in the Claude Code prompt:
- `add-endpoint` — scaffolds a new DRF endpoint
- `add-component` — scaffolds a React component
- `debug-backend` — diagnoses Django errors

**Problem:** Initial skill prompts were too generic and produced boilerplate that didn't match project conventions. Had to iterate on the prompts to include project-specific context.

### Custom Agents (`.claude/agents/`)
Added persistent sub-agents for heavier, multi-step workflows that run autonomously:
- `code-reviewer` — audits recently changed files against CLAUDE.md standards, produces a `CODE_REVIEW.md` report without touching source files
- `docs-writer` — regenerates README.md, API.md, and adds missing docstrings to backend functions and classes
- `prompt-engineer` — audits all prompt templates in `generator/prompts.py` for consistency, structured output instructions, and bias-free language
- `qa` — writes and runs tests for any new or modified code, detects the stack automatically
- `security-auditor` — scans for vulnerabilities, exposed secrets, and misconfigurations, produces a `SECURITY_REPORT.md`
- `solution-architect-reviewer` — reviews codebase structure against architectural principles, produces an `ARCHITECTURE_REVIEW.md`

---

## Phase 4 — Platform Redesign + CV Matching + RAG

Major feature addition — introduced candidate-facing CV matching. A candidate can browse published roles, upload their CV as a PDF, and receive an AI-generated match score.

**Stack added:**
- `pdfplumber` for PDF text extraction
- RAG pipeline (`generator/rag.py`) for context retrieval
- LangGraph two-stage pipeline (`generator/cv_pipeline.py`): extract candidate profile → score against role

**Problems hit:**

**1. PDF extraction was fragile**
Scanned PDFs (image-based) returned empty text. Fix: added a `ValueError` if extracted text was below a minimum length threshold, with a clear error message to the user.

**2. OpenAI responses not always valid JSON**
The CV match pipeline occasionally returned markdown-wrapped JSON (` ```json ... ``` `). Fix: added a strip/parse utility in `services.py` that removes code fences before `json.loads()`.

**3. RAG retrieval adding noise**
Early version of the RAG pipeline was retrieving loosely related chunks that confused the scoring prompt. Fix: tightened the similarity threshold and reduced `top_k` from 5 to 3.

---

## Phase 5 — LangGraph Pipeline

Replaced the single-shot CV scoring call with a proper LangGraph state machine. Two nodes: `extract_profile` and `score_candidate`. This made the pipeline easier to debug since each stage's output could be inspected independently.

**Problem:** LangGraph's async execution conflicted with Django's synchronous view layer. Fix: wrapped the graph invocation in `asyncio.run()` inside the service function.

---

## Phase 6 — Bug Fixes + Frontend Overhaul

This phase was mostly fixing a series of frontend bugs discovered during real use as a manager.

---

### Bug: Kits not loading for managers — "Kit not found or could not be loaded"

**Symptom:** Logging in as a manager and clicking View on any kit returned a 404 error from the backend. All kits appeared to be missing.

**Root cause:** `getKit()` in `kitApi.js` was making an unauthenticated request — no `Authorization` header. The backend `InterviewKitDetailView` correctly returns 404 for draft kits when the requester is not the owner. Since draft is the default status, every kit was 404ing.

**Also fixed:** `KitDetailPage` and `CreateEditRolePage` were calling `getKit(id)` without passing the token, so updated both call sites.

---

### Bug: "View Kits" button taking managers to the public apply page

**Symptom:** After logging in, clicking "View Kits" in the hero section landed on `/kits` — the public "Browse Open Roles" page with "View & Apply" buttons — instead of the manager's own kits.

**Root cause:** `HeroSection` had a hardcoded `href="/kits"` with no awareness of auth state.

**Fix:** Added a `viewKitsTo` prop to `HeroSection`, defaulting to `/kits`. `HomePage` passes `/manager` when the user is authenticated.

---

### Bug: "Back to Kit History" link sending managers to public page

**Symptom:** After viewing a kit from the dashboard, the back link on `KitDetailPage` sent managers to `/kits` (public) instead of `/manager` (their dashboard).

**Fix:** Made the back link context-aware — checks for `token` and renders "Back to My Roles → /manager" for authenticated users, "Back to Open Roles → /kits" for everyone else.

---

### Bug: "Get Started" button doing nothing

**Symptom:** Clicking "Get Started" on the home page had no effect.

**Root cause:** The button called `scrollToForm()` which looked for `document.getElementById('form')`. That element no longer existed after the page was refactored — the form had been moved to its own route.

**Fix:** Replaced the button with a `<Link>` using a `getStartedTo` prop. Managers get sent to `/manager/roles/new`, unauthenticated users to `/login`.

---

### Bug: Edit role page showing blank form

**Symptom:** Clicking "Edit" on a kit card opened the role form completely empty — no prefilled data.

**Root cause 1:** `RoleForm` accepted a `prefillData` prop but never destructured it — the prop was completely ignored. State was always initialized to empty strings.

**Root cause 2:** `CreateEditRolePage` was building the prefill object without `role_title`, so even after fixing the form the title field would have been blank.

**Root cause 3:** The `useEffect` that fetches the kit had `[id, isEditMode]` as dependencies but not `token`, so it wouldn't re-run if the token wasn't ready on first render.

**Fix:**
- Added `useEffect` in `RoleForm` that populates all fields when `prefillData` arrives
- Added `roleTitle: existingKit.role_title` to the prefill object
- Added `token` to the `useEffect` dependency array

---

## Phase 7 — Multi-page Split + UI Cleanup

**Problem:** The entire app lived on one scrollable home page. No navigation structure, no clear separation between the manager and candidate experiences.

**Changes made:**

- Split into proper pages: `/`, `/how-it-works`, `/kits`, `/roles/:id`, `/kits/:id`, `/manager`
- `HowItWorksSection` (manager flow) moved to `/how-it-works` with its heading updated to "For Hiring Managers"
- New `CVHowItWorksSection` component added to `/how-it-works` covering the candidate flow (browse → upload CV → get match score), styled in violet to visually separate it from the manager flow
- Navbar updated to show all pages and adapts based on auth state:
  - Unauthenticated: How It Works | Browse Roles | Login
  - Authenticated: How It Works | My Roles | Logout
- Removed the redundant "Get Started" section that duplicated the hero CTA buttons
- Removed all GPT/model mentions from the frontend — replaced with generic "AI"
- Renamed app from "Interview Kit Generator" to **HireKit AI** across navbar, login page, and browser tab title. Logo initials changed from "IK" to "HK"
- Removed the separate "Edit" button on dashboard kit cards — "View" renamed to "View / Edit" since `KitDisplay` already has per-section regenerate and edit capabilities

---
