# Ide/AI (formerly ideaFORGE) — Context Handoff Document

> Use this file to get caught up on the current state of the project.
> Last updated: 2026-03-18

---

## What is Ide/AI?

Ide/AI takes a rough idea and turns it into a structured, export-ready design kit before the user opens a builder tool. The core problem: people waste credits, time, and money figuring out what to build inside metered platforms (Bubble, Cursor, Claude Code, Bolt, etc.) when that planning should happen beforehand.

The full process: describe an idea → configure options → AI-guided discovery conversation → walk away with a prioritized feature breakdown, tech stack recommendation, platform-specific prompts, and exportable docs.

**Live deployment:** Railway (backend + frontend as separate public services)

---

## Tech Stack

| Layer | Stack |
|-------|-------|
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic, PostgreSQL, Anthropic Claude API (claude-sonnet-4-6) |
| **Frontend** | React 18, TypeScript, Vite 7, Tailwind CSS v4, Framer Motion, Zustand |
| **Auth** | **Clerk** (Google/Microsoft/GitHub OAuth + email/password) — migrated from custom JWT |
| **Billing** | Stripe (checkout sessions, billing portal, webhook sync) |
| **Email** | Resend API — verification codes, password resets, inbound email webhooks for Idea Inbox |
| **Deployment** | Railway (2 services), Docker, Caddy (frontend static) |
| **AI Streaming** | Server-Sent Events (SSE) for discovery chat + market analysis |
| **Export** | fpdf2 (PDF), python-docx (DOCX), Jinja2 templates, ZIP bundling |

---

## Major Architecture Changes (since Mar 11)

### 1. Auth: Custom JWT → Clerk (migration 021)
- Ripped out custom JWT token flow, replaced with Clerk SDKs
- Backend: `clerk_webhook.py` syncs Clerk users to local DB via webhooks
- Backend: `core/clerk.py` verifies Clerk session tokens
- Frontend: `@clerk/clerk-react` wraps app, `SignInPage.tsx` / `SignUpPage.tsx` use Clerk components
- `ProtectedRoute.tsx` now uses Clerk's `useAuth()` instead of custom JWT checks
- `apiClient.ts` attaches Clerk session token via `getToken()`
- `authStore.ts` simplified — fetches user from `/auth/me` after Clerk auth
- Old `Login.tsx` / `Register.tsx` / `VerifyEmail.tsx` / `OAuthCallback.tsx` are legacy (may need cleanup)

### 2. Stripe Billing (migration 019)
- `stripe_customer_id` column on users table
- `backend/app/routers/billing.py` — checkout session creation, billing portal, webhook
- `frontend/src/pages/CheckoutRedirect.tsx` — redirect flow for Stripe checkout
- `Profile.tsx` has "Manage Billing" button linking to Stripe portal
- Landing page has pricing section with "Upgrade" buttons

### 3. Rebrand: ideaFORGE → Ide/AI
- Landing page completely redesigned with new logo (`logo-landing.png`)
- Email templates updated to use "Ide/AI" branding
- New `Landing.tsx` with hero section, keyword highlights, pricing

### 4. Forgot/Reset Password (migration 020)
- `ForgotPassword.tsx` + `ResetPassword.tsx` pages
- Backend: password reset tokens via `password_reset` model
- Email: Resend-powered reset link delivery

### 5. Home Page Cleanup (most recent work)
- Removed old pathway picker dropdown
- Removed preset cards (Quick Start)
- Removed pill dropdowns from project creation form
- Skip AI categorization when project already has a category
- Cleaned up unused imports (useRef, useCallback, setSelectedPreset)

---

## Database Migrations (linear chain: 001–023)

| # | Description |
|---|-------------|
| 001–010 | Original schema through AI partner styles |
| 011 | Modular pathway system (categories, module_pathways, module_responses) |
| 012 | Email verification |
| 013 | User profile fields (account_type, bio) |
| 014 | Idea inbox |
| 015 | Sharing feedback + templates |
| 016 | Concept branches + external integrations |
| 017 | Seed project templates |
| 018 | Seed category templates |
| 019 | **Add stripe_customer_id to users** |
| 020 | **Add password_resets table** |
| 021 | **Add clerk_user_id to users** |
| 022 | **Widen avatar_url column to TEXT** |
| 023 | **Deduplicate user rows** (cleanup from webhook issues) |

---

## Backend Routers

| Router | Purpose |
|--------|---------|
| `auth.py` | Register, login, /me, avatar upload, password change/reset, email verification |
| `billing.py` | **NEW** — Stripe checkout, billing portal, webhook |
| `clerk_webhook.py` | **NEW** — Clerk user sync (create/update/delete) |
| `discovery.py` | SSE chat, greeting, partner switching |
| `module_pathway.py` | Categorize, assemble, review, lock pathways |
| `modules.py` | Module start/respond/skip/summary |
| `projects.py` | Project CRUD |
| `pathways.py` | GET /pathways, POST /pathways/detect |
| `meta.py` | GET /meta/partner-styles |
| `blocks.py` | Feature blocks CRUD + generate |
| `pipeline.py` | Stack recommendation, UI skeleton |
| `exports.py` | MD/PDF/DOCX/ZIP export |
| `market.py` | Market analysis (SSE) |
| `sprints.py` | Sprint plan generation |
| `sharing.py` | Project sharing with comments + ratings |
| `inbox.py` | Idea inbox CRUD + build-to-project |
| `templates.py` | Seed templates |
| `branching.py` | Concept branching (fork/compare/merge) |
| `integrations.py` | External tool OAuth + push |
| `webhooks.py` | Inbound email webhook (Resend) |

---

## Frontend Pages

| Page | Purpose |
|------|---------|
| `Landing.tsx` | Public landing page with hero, features, pricing |
| `SignInPage.tsx` | **Clerk sign-in** |
| `SignUpPage.tsx` | **Clerk sign-up** |
| `CheckoutRedirect.tsx` | **Stripe checkout redirect** |
| `ForgotPassword.tsx` | **Password reset request** |
| `ResetPassword.tsx` | **Password reset form** |
| `Home.tsx` | Idea input, partner grid, template grid, project creation (recently cleaned up) |
| `Discovery.tsx` | SSE chat with AI partner |
| `PathwayReview.tsx` | Module pathway review/reorder |
| `PathwayExecute.tsx` | Module pathway execution |
| `ModuleSession.tsx` | Per-module AI conversation |
| `Pipeline.tsx` | Stack recommendation canvas |
| `Exports.tsx` | Export generation |
| `MarketAnalysis.tsx` | Competitive analysis |
| `SprintPlanner.tsx` | Sprint plan generation |
| `Profile.tsx` | Avatar, bio, stats, billing portal link |
| `Inbox.tsx` | Idea inbox |
| `Library.tsx` | Project library with branches |
| `Settings.tsx` | App settings, tutorial reset |
| `SharedProject.tsx` | Public shared view |
| `PitchMode.tsx` | Shareable one-page brief |
| `Login.tsx` / `Register.tsx` | **Legacy** — pre-Clerk auth pages |
| `VerifyEmail.tsx` | **Legacy** — pre-Clerk verification |
| `OAuthCallback.tsx` | **Legacy** — pre-Clerk OAuth |

---

## What Still Needs Attention (Release Readiness)

1. **Legacy auth pages** — `Login.tsx`, `Register.tsx`, `VerifyEmail.tsx`, `OAuthCallback.tsx` may need removal or redirect since Clerk handles auth now
2. **CLAUDE.md is outdated** — doesn't mention Clerk, Stripe, rebrand, or migrations 017–023
3. **Untracked file** — `client_secret_641870004801-...json` in git status (Google OAuth secret — should NOT be committed)
4. **Dead code audit** — old JWT helpers in `core/security.py`, old auth routes, unused stores
5. **Frontend build verification** — `tsc -b` and `vite build` should pass cleanly
6. **Backend startup verification** — all routers register, no import errors
7. **Environment variables** — Clerk + Stripe keys need to be documented

---

## Key Files for New Sessions

| Purpose | File |
|---------|------|
| Project instructions | `CLAUDE.md` |
| This handoff | `CONTEXT_HANDOFF.md` |
| AI partner spec | `AI_PARTNER_SELECTOR_SPEC.md` |
| Modular pathway spec | `MODULAR_PATHWAY_SPEC.md` |
| Seed data (categories) | `backend/app/data/concept_categories.seed.json` |
| Seed data (modules) | `backend/app/data/module_library.seed.json` |
| Seed data (templates) | `project_templates.seed.json` |
| Clerk auth | `backend/app/core/clerk.py`, `backend/app/routers/clerk_webhook.py` |
| Stripe billing | `backend/app/routers/billing.py` |
| Landing page | `frontend/src/pages/Landing.tsx` |

---

## Recent Commit History (newest first)

```
382a56b Remove unused useRef import from Home.tsx
14dde5c Remove pill dropdowns from project creation form
9d4c7ab Skip AI categorization when project already has a category
66d3c9f Remove leftover setSelectedPreset reference in Home
6275d2e Remove old pathway picker and preset cards from Home page
e36e082 Fix dynamic module selection by moving seed files into Docker build context
ef5f8ea Fix pathways 404 by adding route without trailing slash
59b17f3 Fix Upgrade button to use /pricing route with auto-scroll
b2d5468 Add checkout flow persistence, billing portal, and success toast
97ee7bf Fix webhook robustness and deduplicate user rows
7ad2e19 Fix webhook duplicate user crash and avatar column truncation
6b60203 Migrate authentication from custom JWT to Clerk
ddf52e5 Add forgot/reset password flow and rebrand emails to Ide/AI
c7ee6d4 Rebrand landing page from ideaFORGE to Ide/AI and add hero background logo
921d72f chore: regenerate poetry.lock for stripe dependency
```
