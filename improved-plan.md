# Job Kit Generator — Major Improvement Plan

## Context
The existing app is a minimal single-page tool: one form, one spinner, one results display. The goal is to transform it into a polished, portfolio-quality product with a redesigned SPA (multi-section), a kit history page, smarter AI context, client-side PDF export, per-section regeneration (persisted to DB), copy-to-clipboard, inline editing, shareable kit URLs, dark mode, and toast notifications.

User decisions confirmed:
- PDF export: **client-side** (html2canvas + jsPDF)
- Regenerate section: **persists to DB**
- Auth: **none** (AllowAny)
- Extra features: shareable kit links, delete from history, editable sections, dark mode

---

## Phase 1 — Backend Updates

### 1.1 Model — add context fields
**File:** `backend/generator/models.py`
- Add `role_level` (CharField, choices: Junior/Mid-level/Senior/Lead)
- Add `industry` (CharField, choices: Tech/Finance/Healthcare/Marketing/Operations/Other)
- Add `company_size` (CharField, choices: Startup/Mid-size/Enterprise)
- Add `remote_policy` (CharField, choices: Remote/Hybrid/On-site)
- All new fields: `max_length=50`, `blank=True` (backward-compatible)

### 1.2 Migration
**File to create:** `backend/generator/migrations/0002_interviewkit_context_fields.py`
- Auto-generated via `python manage.py makemigrations`

### 1.3 Serializers
**File:** `backend/generator/serializers.py`
- Add `role_level`, `industry`, `company_size`, `remote_policy` to `InterviewKitCreateSerializer` as optional `ChoiceField`s with the same choices as the model
- Add these four fields to `InterviewKitSerializer` output (read-only)
- Add `RegenerateSectionSerializer`: validates `section_name` against allowed values (`job_description`, `scorecard`, `interview_questions`, `skills_assessment_rubric`)

### 1.4 Prompts
**File:** `backend/generator/prompts.py`
- Update `FULL_KIT_PROMPT` to include a new context block:
  ```
  Role Level: {role_level}
  Industry: {industry}
  Company Size: {company_size}
  Remote Policy: {remote_policy}
  ```
  Instruct the model to tailor content specifically to these dimensions.
- Add `SECTION_REGENERATION_PROMPT`: takes `section_name`, `role_description`, and the same 4 context fields. Returns only the JSON for that single section (same schema as the full kit but just the one key).

### 1.5 Services
**File:** `backend/generator/services.py`
- Update `generate_full_kit(role_description, role_level, industry, company_size, remote_policy)` — pass new params into prompt format
- Add `generate_section(section_name, role_description, role_level, industry, company_size, remote_policy) -> dict` — calls OpenAI with `SECTION_REGENERATION_PROMPT`, validates the returned key matches `section_name`, returns the section dict

### 1.6 Views
**File:** `backend/generator/views.py`
- Update `GenerateFullKitView.post()` to extract and pass the 4 new fields to `generate_full_kit()`; save them to the model
- Add `RegenerateSectionView(APIView)` at `POST /api/kits/<uuid:pk>/regenerate-section/`:
  - Validates `section_name` via `RegenerateSectionSerializer`
  - Fetches kit by pk (404 if not found)
  - Calls `generate_section()`
  - Merges result into `kit.generated_kit[section_name]`
  - Saves kit to DB
  - Returns `{"section_name": ..., "data": <regenerated section>}`

### 1.7 URLs
**File:** `backend/generator/urls.py`
- Add: `path("kits/<uuid:pk>/regenerate-section/", RegenerateSectionView.as_view(), name="regenerate-section")`

### 1.8 Tests
**File:** `backend/generator/tests/test_endpoints.py`
- Update `TestGenerateFullKit` fixtures and post payloads to include the 4 new optional fields; verify they are saved and returned
- Add `TestRegenerateSection` class:
  - `test_returns_200_and_updates_section` — mock `generate_section`, verify DB updated
  - `test_returns_400_for_invalid_section_name`
  - `test_returns_404_for_nonexistent_kit`

---

## Phase 2 — Frontend Redesign

### 2.1 Dependencies
**File:** `frontend/package.json`
- Add: `react-router-dom`, `jspdf`, `html2canvas`, `react-hot-toast`
- Install via `npm install react-router-dom jspdf html2canvas react-hot-toast`

### 2.2 Router setup
**File:** `frontend/src/App.jsx`
- Wrap app in `BrowserRouter`
- Route `/` → `HomePage`
- Route `/kits` → `KitsPage`
- Route `/kits/:id` → `KitDetailPage`
- Add `<Toaster />` from react-hot-toast at root level

### 2.3 HTML title
**File:** `frontend/index.html`
- Update `<title>` to "Interview Kit Generator"
- Add meta description

### 2.4 Dark mode
**File:** `frontend/src/index.css`
- Add `color-scheme` and base dark mode variables using Tailwind v4 `@variant dark` or class strategy

### 2.5 Navbar (new)
**File to create:** `frontend/src/components/Navbar.jsx`
- App name/logo on left
- Nav links: "History (/kits)" on right
- Dark mode toggle button (moon/sun icon, stores preference in `localStorage`)
- Sticky, glass-morphism style

### 2.6 HeroSection (new)
**File to create:** `frontend/src/components/HeroSection.jsx`
- App name, tagline ("Generate polished interview kits in seconds")
- "Get Started" button that smooth-scrolls to the form section (`#form`)
- Large, visually bold layout

### 2.7 HowItWorksSection (new)
**File to create:** `frontend/src/components/HowItWorksSection.jsx`
- 3 steps with numbered icons:
  1. Describe the role
  2. AI generates your kit
  3. Export, share, or refine

### 2.8 RoleForm (update)
**File:** `frontend/src/components/RoleForm.jsx`
- Add 4 new `<select>` dropdowns with helper text: Role Level, Industry, Company Size, Remote Policy
- Pass all 6 values to `onSubmit`
- Improved layout: label + helper text above each field
- Visual grouping of dropdowns in a 2×2 grid on desktop

### 2.9 LoadingSkeleton (new, replaces spinner)
**File to create:** `frontend/src/components/LoadingSkeleton.jsx`
- Animated pulse skeleton blocks mimicking the 4 kit sections
- Delete `LoadingSpinner.jsx` after replacing all usages

### 2.10 KitSection (new)
**File to create:** `frontend/src/components/KitSection.jsx`
- Wrapper for each of the 4 sections
- Action bar in the section header: **Copy**, **Regenerate**, **Edit**
- **Copy**: copies section JSON as formatted text to clipboard, shows toast
- **Regenerate**: calls `regenerateSection()` API, shows loading state inline, shows toast on success/fail, updates parent state
- **Edit**: toggles inline edit mode — replaces display with a `<textarea>` pre-filled with section content, with **Save** and **Cancel** buttons; Save updates local state (not DB, editing is UI-only)

### 2.11 KitDisplay (update)
**File:** `frontend/src/components/KitDisplay.jsx`
- Wrap each of the 4 sections in `KitSection` instead of `SectionCard`
- Pass `kitId`, `sectionName`, and `onSectionRegenerated` callback
- Add **Export PDF** button at the top — calls `exportKitAsPdf()` utility
- Add **Share** button at the top — copies current page URL to clipboard, shows toast
- Add smooth fade-in animation when kit first renders

### 2.12 PDF export utility (new)
**File to create:** `frontend/src/utils/exportPdf.js`
- `exportKitAsPdf(elementId, filename)` function
- Uses `html2canvas` to capture the DOM element with id `kit-display`
- Passes canvas to `jsPDF` and saves as `interview-kit-<role-title>.pdf`

### 2.13 API (update)
**File:** `frontend/src/api/kitApi.js`
- Update `generateFullKit()` to accept and send all 6 fields
- Add `regenerateSection(kitId, sectionName)` — POST to `/api/kits/:id/regenerate-section/`
- Ensure `listKits()` and `getKit()` handle paginated and single responses correctly
- Add `deleteKit()` (already exists)

### 2.14 HomePage (update)
**File:** `frontend/src/pages/HomePage.jsx`
- Restructure as scroll-sections: `<Navbar>`, `<HeroSection>`, `<HowItWorksSection>`, `<section id="form">`, `<section id="kit">`
- Handle state for all 6 form fields
- Pass `kitId` to `KitDisplay` so sections can regenerate

### 2.15 KitsPage (new)
**File to create:** `frontend/src/pages/KitsPage.jsx`
- Fetches all kits via `listKits()` on mount
- Shows loading skeleton while loading
- Table/card list: role title, industry, role level, created date, **View** and **Delete** buttons
- Delete calls `deleteKit()`, shows toast, removes from list
- Empty state with CTA to generate first kit
- Pagination controls if >20 kits

### 2.16 KitDetailPage (new)
**File to create:** `frontend/src/pages/KitDetailPage.jsx`
- Fetches kit by ID from URL param via `getKit(id)`
- Renders full `KitDisplay` with all actions (copy, regenerate, edit, export PDF)
- This is the shareable URL: `/kits/:id`

---

## Phase 3 — Feature Checklist

| Feature | Where implemented |
|---|---|
| PDF export | `exportPdf.js` + **Export PDF** button in `KitDisplay` |
| Copy to clipboard | `KitSection` action bar + toast |
| Regenerate section (persisted) | `KitSection` → `regenerateSection()` API → `RegenerateSectionView` |
| Kit history page | `KitsPage` at `/kits` |
| Delete from history | `KitsPage` delete button → `deleteKit()` |
| Shareable kit links | `KitDetailPage` at `/kits/:id` + **Share** button |
| Editable sections (UI-only) | `KitSection` edit mode with textarea |
| Toast notifications | `react-hot-toast` on all async actions |
| Loading skeleton | `LoadingSkeleton` replaces `LoadingSpinner` |
| Dark mode | Navbar toggle + Tailwind dark: classes throughout |
| Smooth animations | Tailwind `transition`, `animate-fade-in` on kit load |
| Responsive | Tailwind responsive breakpoints in all new components |

---

## Phase 4 — Polish

- **Navbar:** sticky with backdrop blur (`backdrop-blur-sm bg-white/80 dark:bg-slate-900/80`)
- **Hero:** large gradient headline, subtle background pattern
- **Animations:** kit sections animate in with staggered delay using CSS `animation-delay`
- **Empty states:** meaningful messaging on KitsPage with icon and CTA
- **Error boundaries:** wrap KitDisplay in try/catch with fallback UI
- **index.html:** proper title, meta description, favicon path
- **Color palette consistency:** verify indigo + slate scheme works in both light and dark modes

---

## Critical Files Summary

### Backend — modify
- `backend/generator/models.py`
- `backend/generator/serializers.py`
- `backend/generator/services.py`
- `backend/generator/prompts.py`
- `backend/generator/views.py`
- `backend/generator/urls.py`
- `backend/generator/tests/test_endpoints.py`

### Backend — create
- `backend/generator/migrations/0002_interviewkit_context_fields.py` (via makemigrations)

### Frontend — modify
- `frontend/package.json`
- `frontend/index.html`
- `frontend/src/App.jsx`
- `frontend/src/index.css`
- `frontend/src/api/kitApi.js`
- `frontend/src/components/RoleForm.jsx`
- `frontend/src/components/KitDisplay.jsx`
- `frontend/src/pages/HomePage.jsx`

### Frontend — create
- `frontend/src/components/Navbar.jsx`
- `frontend/src/components/HeroSection.jsx`
- `frontend/src/components/HowItWorksSection.jsx`
- `frontend/src/components/LoadingSkeleton.jsx`
- `frontend/src/components/KitSection.jsx`
- `frontend/src/utils/exportPdf.js`
- `frontend/src/pages/KitsPage.jsx`
- `frontend/src/pages/KitDetailPage.jsx`

### Frontend — delete
- `frontend/src/components/LoadingSpinner.jsx` (replaced by LoadingSkeleton)

---

## Verification

1. **Backend tests:** `cd backend && pytest` — all existing tests pass + new tests for regenerate-section pass
2. **Migration:** `python manage.py migrate` runs cleanly; existing kits still load (new fields are blank=True)
3. **Full kit generation:** submit form with all 6 fields → kit generated → saved with context fields → appears in `/kits`
4. **Regenerate section:** click Regenerate on any section → loading state shows → section updates in UI → refreshing `/kits/:id` shows updated section
5. **PDF export:** click Export PDF → browser downloads a formatted PDF of the kit
6. **Kit history:** navigate to `/kits` → list shows → clicking View goes to `/kits/:id` → Delete removes it with toast
7. **Dark mode:** toggle in Navbar → page switches themes → preference survives page reload
8. **Responsive:** test at 375px, 768px, 1280px breakpoints in browser DevTools
