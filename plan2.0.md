# Two-Sided Platform Extension Plan

## Context

The job-kit-generator is being extended from a single-user AI tool into a two-sided platform. Currently it is an unauthenticated app where anyone can generate, view, and delete interview kits. The new direction splits usage into:

- **Manager side** (authenticated): create roles, generate AI kits, publish/unpublish roles
- **Applicant side** (fully public): browse published roles, upload a CV, get AI-powered compatibility match

This plan extends the existing codebase without replacing it — the core OpenAI generation pipeline, prompt system, and component library are all reused.

**Key existing assets to reuse:**
- `generator/services.py` — add `match_cv_to_role()` alongside existing `generate_full_kit()`
- `generator/prompts.py` — add `CV_MATCH_PROMPT`
- `frontend/src/api/kitApi.js` — extend with auth and CV match calls
- `frontend/src/components/RoleForm.jsx`, `KitDisplay.jsx`, `KitSection.jsx` — reused as-is on manager side
- `rest_framework.authtoken` already in `INSTALLED_APPS`, `TokenAuthentication` already in `REST_FRAMEWORK` settings — just needs endpoints and enforcement

---

## Phase 1: Backend — Model Changes and Auth

**Goal:** Extend the data model, enforce authentication on write endpoints, and expose login/logout endpoints.

### 1.1 Extend the InterviewKit model
**File:** `backend/generator/models.py`
- Add `status` field: `CharField(max_length=20, choices=[('draft','Draft'),('published','Published')], default='draft')`
- Add `created_by` field: `ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='kits')`
- Import `settings` from `django.conf`
- The four optional fields (role_level, industry, company_size, remote_policy) already exist — no change needed

### 1.2 Create and run migration
**File:** `backend/generator/migrations/` (new migration file auto-generated)
- Run `python manage.py makemigrations` — Django generates migration for new fields
- Because `created_by` is a non-nullable FK, migration must provide a default. Two options: set `null=True` initially and backfill, or set `default=1` if a superuser exists
- Recommended: add `null=True, blank=True` initially, run migration, then tighten later — keeps dev flow smooth
- Dependency: 1.1 must be done first

### 1.3 Update serializers
**File:** `backend/generator/serializers.py`
- `InterviewKitSerializer`: add `status` and `created_by` (read-only) to fields; expose `created_by` as username string using `SerializerMethodField`
- `InterviewKitCreateSerializer`: no change needed (create logic sets `created_by` from `request.user` in the view)
- Add new `PublishToggleSerializer` with a single `status` field (ChoiceField: draft/published) for the publish/unpublish endpoint

### 1.4 Add login/logout endpoints
**File:** `backend/generator/views.py` (or new `backend/generator/auth_views.py` for separation)
- `LoginView` (POST): accepts `username` + `password`, calls `authenticate()`, returns `Token.objects.get_or_create(user=user)` key; returns 400 on bad credentials
- `LogoutView` (POST): requires `IsAuthenticated`, deletes the user's token; returns 204

### 1.5 Update existing views with authentication
**File:** `backend/generator/views.py`
- `GenerateFullKitView`: add `permission_classes = [IsAuthenticated]`; set `created_by=request.user` when creating the InterviewKit
- `InterviewKitDetailView` (DELETE): add `IsAuthenticated`; add `get_queryset()` to restrict to `request.user`'s kits
- `RegenerateSectionView`: add `IsAuthenticated`; restrict to owner's kits
- `InterviewKitListView` (GET /api/kits/): keep `AllowAny` — public browsing; filter to only `status='published'` for unauthenticated users; return all kits for authenticated manager
- `InterviewKitDetailView` (GET): keep `AllowAny` — but only return kit if published OR if requester is the owner

### 1.6 Add publish/unpublish endpoint
**File:** `backend/generator/views.py`
- `PublishToggleView` (PATCH `/api/kits/<uuid>/publish/`): `IsAuthenticated`, restrict to owner's kits, accepts `{"status": "published"}` or `{"status": "draft"}`, updates and saves

### 1.7 Add edit endpoint
**File:** `backend/generator/views.py`
- `InterviewKitUpdateView` (PATCH `/api/kits/<uuid>/`): `IsAuthenticated`, restrict to owner, accepts `role_title` and/or `role_description` updates
- After update, optionally trigger `generate_full_kit()` if `regenerate=true` is passed in request body

### 1.8 Register new URLs
**File:** `backend/generator/urls.py`
- `POST /api/auth/login/` → `LoginView`
- `POST /api/auth/logout/` → `LogoutView`
- `PATCH /api/kits/<uuid>/publish/` → `PublishToggleView`
- `PATCH /api/kits/<uuid>/` → `InterviewKitUpdateView`

---

## Phase 2: Backend — CV Matching Feature

**Goal:** Accept a PDF CV upload, extract text, send to OpenAI alongside role details, return match result, discard the file.

### 2.1 Add PDF extraction dependency
**File:** `backend/requirements.txt`
- Add `pypdf` (preferred: pure-Python, no system deps) or `pdfplumber`
- Dependency: must be installed before any CV matching code runs

### 2.2 Add CV match prompt
**File:** `backend/generator/prompts.py`
- Add `CV_MATCH_PROMPT` string: instructs GPT-4o to compare CV text against role's job description, required qualifications, and preferred qualifications
- Prompt must instruct model to return JSON with keys: `compatibility_percentage` (int 0-100), `explanation` (string), `strengths_matched` (list of strings), `gaps_identified` (list of strings)
- Prompt must emphasize bias-free evaluation — assess skills, experience, qualifications only; ignore personal details

### 2.3 Add CV match service function
**File:** `backend/generator/services.py`
- Add `match_cv_to_role(cv_text, role_data)` function
- `role_data` dict contains: role_title, role_description, role_level, job_description section from generated_kit
- Formats `CV_MATCH_PROMPT`, calls OpenAI gpt-4o with `response_format: json_object`
- Validates response contains required keys; raises `ValueError` on bad response
- Returns dict with: `compatibility_percentage`, `explanation`, `strengths_matched`, `gaps_identified`
- CV text is never persisted — it lives only in function scope

### 2.4 Add PDF text extraction utility
**File:** `backend/generator/utils.py` (new file)
- Add `extract_text_from_pdf(file_object)` function
- Uses `pypdf.PdfReader` to read the in-memory file object
- Iterates pages, concatenates extracted text
- Raises `ValueError` if extraction yields empty string (unreadable PDF)
- File object is not saved to disk at any point

### 2.5 Add CV match view
**File:** `backend/generator/views.py`
- `CVMatchView` (POST `/api/kits/<uuid>/match-cv/`): `AllowAny` (public endpoint)
- Accepts multipart form data with `cv_file` field (PDF)
- Validates file is present and is a PDF (check content type)
- Calls `extract_text_from_pdf(request.FILES['cv_file'])`
- Fetches the kit (must be published — 404 if not)
- Calls `match_cv_to_role(cv_text, kit_data)`
- Returns match result JSON; does not save anything
- Returns structured errors on bad input (no file, wrong type, extraction failure)

### 2.6 Register CV match URL
**File:** `backend/generator/urls.py`
- `POST /api/kits/<uuid>/match-cv/` → `CVMatchView`

---

## Phase 3: Frontend — Manager Side

**Goal:** Add login flow, protected manager dashboard, and create/edit role pages.

### 3.1 Add auth state management
**File:** `frontend/src/context/AuthContext.jsx` (new file)
- React Context providing: `user`, `token`, `login(token, user)`, `logout()`
- Persists token to `localStorage` on login; clears on logout
- On mount, reads token from localStorage and restores auth state
- Wrap entire app in `<AuthProvider>` in `App.jsx`

### 3.2 Add auth API calls
**File:** `frontend/src/api/kitApi.js`
- Add `loginManager(username, password)` — POST `/api/auth/login/`, returns token
- Add `logoutManager()` — POST `/api/auth/logout/`, sends `Authorization: Token <token>` header
- Update all write-operation functions (generateFullKit, deleteKit, regenerateSection) to include auth header from stored token
- Add `publishKit(kitId, status)` — PATCH `/api/kits/:id/publish/`
- Add `updateKit(kitId, data)` — PATCH `/api/kits/:id/`
- Add `matchCv(kitId, file)` — POST `/api/kits/:id/match-cv/` with FormData

### 3.3 Add ProtectedRoute component
**File:** `frontend/src/components/ProtectedRoute.jsx` (new file)
- Reads `token` from AuthContext
- If no token: redirect to `/login`
- If token exists: render `<Outlet />`

### 3.4 Add Login page
**File:** `frontend/src/pages/LoginPage.jsx` (new file)
- Form with username and password fields
- On submit: calls `loginManager()`, stores token via `AuthContext.login()`, redirects to `/manager`
- Shows error message on failed login
- If already authenticated: redirect to `/manager`

### 3.5 Add Manager Dashboard page
**File:** `frontend/src/pages/ManagerDashboard.jsx` (new file)
- Fetches all kits for the authenticated manager (GET `/api/kits/` with token — returns all owner kits)
- Renders role cards with: role title, status badge (Draft/Published), created date, role level
- Each card has buttons: View, Edit (→ `/manager/roles/:id/edit`), Delete (with confirmation), Publish/Unpublish toggle
- Empty state with "Create your first role" CTA
- Loading and error states
- Logout button in header area

### 3.6 Add Create/Edit Role page
**File:** `frontend/src/pages/CreateEditRolePage.jsx` (new file)
- Reuses existing `RoleForm` component
- If `:id` param present: fetch kit data, pre-fill form (edit mode)
- On submit in create mode: calls `generateFullKit()`, redirect to dashboard on success
- On submit in edit mode: calls `updateKit()` with form data, optionally `regenerateSection()` for full kit regeneration
- Shows `LoadingSkeleton` while generating
- After success in edit mode: shows updated `KitDisplay` inline before redirecting

### 3.7 Update App.jsx routing
**File:** `frontend/src/App.jsx`
- Add `AuthProvider` wrapper around all routes
- Add routes:
  - `/login` → `LoginPage`
  - `/manager` → `ProtectedRoute` → `ManagerDashboard`
  - `/manager/roles/new` → `ProtectedRoute` → `CreateEditRolePage`
  - `/manager/roles/:id/edit` → `ProtectedRoute` → `CreateEditRolePage`
- Keep existing routes: `/`, `/kits`, `/kits/:id` (these become the public applicant-side routes, see Phase 4)

### 3.8 Update Navbar
**File:** `frontend/src/components/Navbar.jsx`
- If authenticated: show "Dashboard" link and "Logout" button
- If not authenticated: show "Browse Roles" link
- Logout calls `AuthContext.logout()` and redirects to `/login`

---

## Phase 4: Frontend — Applicant Side

**Goal:** Public roles browsing, role detail with job description, and CV upload + match result display.

### 4.1 Update Public Roles Listing page
**File:** `frontend/src/pages/KitsPage.jsx` (modify existing)
- Currently shows all kits with delete buttons — this needs to become the public browsing page
- Remove delete button (applicants cannot delete)
- Remove any manager-only actions
- Only shows published roles (backend already filters for unauthenticated requests)
- Each card shows: role title, role level, industry, remote policy, "View & Apply" button
- Link to `/roles/:id` for role detail

### 4.2 Add Public Role Detail page
**File:** `frontend/src/pages/RoleDetailPage.jsx` (new file)
- Fetches kit by ID (GET `/api/kits/:id/`)
- Displays only the `job_description` section from `generated_kit` (not scorecard or interview questions — those are manager-only intel)
- Below the job description: CV upload section
- Upload form: file input (PDF only), "Analyze My CV" button
- On submit: calls `matchCv(kitId, file)`, shows loading state
- On result: renders `CVMatchResult` component

### 4.3 Add CVMatchResult component
**File:** `frontend/src/components/CVMatchResult.jsx` (new file)
- Displays compatibility percentage as a large circular or bar visual (pure Tailwind/CSS, no extra library)
- Color-coded: green ≥75%, yellow 50-74%, red <50%
- Shows explanation paragraph
- Shows "Strengths Matched" as a green-badged list
- Shows "Gaps Identified" as an amber-badged list
- "Try with a different CV" button resets the form

### 4.4 Add public role detail route
**File:** `frontend/src/App.jsx`
- Add route `/roles/:id` → `RoleDetailPage`
- The existing `/kits/:id` route can remain for backward compat or be redirected

### 4.5 Update HomePage
**File:** `frontend/src/pages/HomePage.jsx`
- The current homepage is the kit generation form — it should become a landing page only
- Keep `HeroSection` and `HowItWorksSection`
- Change CTAs: "Browse Open Roles" → `/kits` (public), "Manager Login" → `/login`
- Remove the `RoleForm` from the public homepage (kit generation is now a manager-only action at `/manager/roles/new`)

---

## Phase 5: Polish and Testing

**Goal:** End-to-end verification, edge case handling, and test coverage.

### 5.1 Backend tests — auth and model changes
**File:** `backend/generator/tests/test_auth.py` (new file)
- Test login with valid credentials → returns token
- Test login with invalid credentials → returns 400
- Test logout → token deleted
- Test unauthenticated access to POST /api/generate/full-kit/ → 401
- Test authenticated access → 201

### 5.2 Backend tests — kit access control
**File:** `backend/generator/tests/test_views.py` (modify existing)
- Test GET /api/kits/ unauthenticated → only published kits returned
- Test GET /api/kits/ authenticated → all owner kits returned
- Test DELETE /api/kits/:id/ by non-owner → 403 or 404
- Test PATCH /api/kits/:id/publish/ unauthenticated → 401

### 5.3 Backend tests — CV matching
**File:** `backend/generator/tests/test_cv_match.py` (new file)
- Test POST /api/kits/:id/match-cv/ with valid PDF → returns match result JSON
- Test with non-PDF file → returns 400
- Test with unpublished kit → returns 404
- Test with empty/unreadable PDF → returns 400
- Mock OpenAI call in tests to avoid real API calls

### 5.4 Frontend — API token header validation
**File:** `frontend/src/api/kitApi.js`
- Verify all write-endpoint functions include `Authorization: Token <token>` header
- Verify 401 responses trigger logout and redirect to login (add response interceptor or per-function handling)

### 5.5 Frontend — CV upload edge cases
**File:** `frontend/src/pages/RoleDetailPage.jsx`
- Validate file type client-side before upload (accept="application/pdf")
- Show file name after selection
- Clear previous match result when new file selected
- Handle API error states (timeout, bad response)

### 5.6 Environment and dependencies check
**File:** `backend/requirements.txt`
- Confirm `pypdf` added
**File:** `backend/.env`
- No new env vars required (OPENAI_API_KEY already present)

### 5.7 Manual end-to-end verification checklist
1. Create superuser: `python manage.py createsuperuser`
2. Login via `/login` → redirected to `/manager`
3. Create a new role → kit generated → appears as Draft on dashboard
4. Publish the role → status changes to Published
5. Open an incognito window → browse `/kits` → see only published roles
6. Click role → see job description only (no scorecard)
7. Upload a PDF CV → receive match result with percentage, explanation, strengths, gaps
8. Upload a second CV → result refreshes, previous result replaced
9. Back on manager dashboard: delete the role → removed from list
10. Unauthenticated POST to /api/generate/full-kit/ → 401 Unauthorized

---

## Critical File Map

| File | Action | Phase |
|---|---|---|
| `backend/generator/models.py` | Add `status`, `created_by` fields | 1 |
| `backend/generator/migrations/` | New migration | 1 |
| `backend/generator/serializers.py` | Add `status`, `created_by`; new `PublishToggleSerializer` | 1 |
| `backend/generator/views.py` | Add LoginView, LogoutView, PublishToggleView, UpdateView, CVMatchView; add auth to existing | 1, 2 |
| `backend/generator/urls.py` | Register all new endpoints | 1, 2 |
| `backend/generator/prompts.py` | Add `CV_MATCH_PROMPT` | 2 |
| `backend/generator/services.py` | Add `match_cv_to_role()` | 2 |
| `backend/generator/utils.py` | New: `extract_text_from_pdf()` | 2 |
| `backend/requirements.txt` | Add `pypdf` | 2 |
| `frontend/src/context/AuthContext.jsx` | New: auth state management | 3 |
| `frontend/src/api/kitApi.js` | Add auth headers, new endpoint functions | 3 |
| `frontend/src/components/ProtectedRoute.jsx` | New: route guard | 3 |
| `frontend/src/pages/LoginPage.jsx` | New: login form | 3 |
| `frontend/src/pages/ManagerDashboard.jsx` | New: manager role list | 3 |
| `frontend/src/pages/CreateEditRolePage.jsx` | New: create/edit form page | 3 |
| `frontend/src/components/Navbar.jsx` | Add auth-aware links | 3 |
| `frontend/src/App.jsx` | Add AuthProvider, new routes | 3, 4 |
| `frontend/src/pages/KitsPage.jsx` | Refactor to public-only browsing | 4 |
| `frontend/src/pages/RoleDetailPage.jsx` | New: public role detail + CV upload | 4 |
| `frontend/src/components/CVMatchResult.jsx` | New: match result display | 4 |
| `frontend/src/pages/HomePage.jsx` | Refactor to landing-only (remove form) | 4 |
| `backend/generator/tests/test_auth.py` | New: auth tests | 5 |
| `backend/generator/tests/test_views.py` | Extend: access control tests | 5 |
| `backend/generator/tests/test_cv_match.py` | New: CV matching tests | 5 |
