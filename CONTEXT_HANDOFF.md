# ideaFORGE — Context Handoff Document

> Use this file to get caught up on the current state of the ideaFORGE project. It covers architecture, recent work, key files, and known issues.

---

## What is ideaFORGE?

ideaFORGE is a full-stack AI-powered product design kit generator. A user describes an idea, selects configuration options, and enters a **Discovery** chat session where an AI partner collaborates to extract structured design sheets (features, user personas, UX flows, color palettes, etc.). The extracted data feeds into downstream tools: exports, market analysis, sprint planning, and pitch mode.

**Live deployment:** Railway (backend + frontend as separate services)

---

## Tech Stack

| Layer | Stack |
|-------|-------|
| **Backend** | Python 3.12, FastAPI, SQLAlchemy (async), Alembic, PostgreSQL, Anthropic Claude API (claude-sonnet-4-6) |
| **Frontend** | React 18, TypeScript, Vite 7, Tailwind CSS v4, Framer Motion, Zustand |
| **Auth** | Google OAuth + email/password, JWT tokens |
| **Deployment** | Railway (2 services), Docker, Caddy (frontend static) |
| **AI Streaming** | Server-Sent Events (SSE) for discovery chat + market analysis |

---

## Repository Structure

```
D:\Development\Ide_AI\
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app, router registration
│   │   ├── models/                    # SQLAlchemy ORM models
│   │   │   ├── project.py             # Project model (has ai_partner_style, pathway_id)
│   │   │   ├── session.py             # DiscoverySession (has ai_partner_style, stage)
│   │   │   ├── user.py, block.py, design_sheet.py, market_analysis.py,
│   │   │   │   sprint_plan.py, pipeline_node.py, prompt_kit.py, etc.
│   │   ├── schemas/                   # Pydantic request/response schemas
│   │   │   ├── project.py             # ProjectCreate/Read/Update + PartnerUpdatePayload (in session.py)
│   │   │   ├── session.py             # SessionRead, PartnerUpdatePayload
│   │   ├── routers/                   # FastAPI route handlers
│   │   │   ├── discovery.py           # SSE chat, greeting, partner switching
│   │   │   ├── projects.py, exports.py, market.py, sprints.py, pipeline.py
│   │   │   ├── meta.py                # GET /meta/partner-styles
│   │   │   ├── pathways.py            # GET /pathways, POST /pathways/detect
│   │   │   ├── auth.py, sharing.py, library.py, blocks.py, prompts.py
│   │   ├── services/                  # Business logic layer
│   │   │   ├── ai_service.py          # build_system_prompt(), build_greeting_prompt(), stream_chat()
│   │   │   ├── partner_style_service.py  # 10 AI partner styles, metadata, prompt fragments
│   │   │   ├── discovery_service.py   # Session management, concept-sheet extraction
│   │   │   ├── sheet_service.py       # Design sheet CRUD
│   │   │   ├── pipeline_service.py, export_service.py, market_service.py, sprint_service.py, etc.
│   │   │   ├── pathway_service.py     # Concept Pathway registry
│   │   ├── alembic/versions/          # Database migrations (001–010)
│   │   ├── config.py                  # Settings from env vars
│   ├── pyproject.toml                 # Poetry dependencies
│   ├── Dockerfile, railway.toml
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.tsx               # Idea input, pathway picker, partner style grid, project creation
│   │   │   ├── Discovery.tsx          # SSE chat UI, active partner badge, mid-session switching
│   │   │   ├── Pipeline.tsx, Exports.tsx, MarketAnalysis.tsx, SprintPlanner.tsx, etc.
│   │   ├── components/
│   │   │   ├── partner/               # PartnerCard.tsx, PartnerSelector.tsx, ActivePartnerBadge.tsx
│   │   │   ├── home/PresetCard.tsx    # Glassmorphism preset card component
│   │   │   ├── discovery/             # ChatBubble, TopBar, SheetSidebar, etc.
│   │   │   ├── framework/             # DesignSheetPanel, SheetCard
│   │   │   ├── layout/Sidebar.tsx     # Navigation sidebar
│   │   │   ├── nebula/                # Animated background canvas
│   │   │   ├── ui/                    # Button, Modal, etc.
│   │   ├── stores/pathwayStore.ts     # Zustand store for pathway state
│   │   ├── types/                     # TypeScript interfaces
│   │   │   ├── project.ts             # Project, ProjectCreate, PartnerStyleMeta
│   │   │   ├── discovery.ts           # Session (has ai_partner_style)
│   │   │   ├── pathway.ts             # PathwayDefinition, CreationField, CreationPreset
│   │   ├── lib/apiClient.ts           # Axios instance with auth interceptors
│   │   ├── styles/                    # Tailwind v4 CSS
│   ├── vite.config.ts, tsconfig.json
│   ├── Dockerfile, Caddyfile, railway.toml
├── docker-compose.yml
├── AI_PARTNER_SELECTOR_SPEC.md        # Full spec for the partner feature
├── ARCHITECTURE.md, PRD.md, FEATURE_SPEC.md, SYSTEM_PROMPT.md
```

---

## Concept Pathways System (Phases 1–6)

The app supports multiple **Concept Pathways** — different project types that customize the entire discovery experience:

| Pathway | ID | Description |
|---------|----|-------------|
| Software Product | `software_product` | Apps, SaaS, tools — the original/default pathway |
| Marketing Campaign | `marketing_campaign` | Campaign briefs, audience targeting, channel strategy |
| Brand Identity | `brand_identity` | Logo systems, brand guidelines, visual identity |
| Creative Writing | `creative_writing` | Stories, scripts, world-building |

Each pathway defines:
- `base_persona` — system prompt personality
- `discovery_stages` — divergent/convergent thinking stages with specific questions
- `sheet_schema` — structured output fields extracted from chat
- `creation_fields` — Home page configuration options (platform, audience, etc.)
- `creation_presets` — Quick Start preset cards

Pathway configs live in `backend/app/services/pathway_service.py` and are served via `GET /api/v1/pathways`.

---

## AI Partner Selector (Latest Feature)

**Spec:** `AI_PARTNER_SELECTOR_SPEC.md`

10 collaboration styles that genuinely change AI behavior (not cosmetic):

| Partner | Icon | Behavior |
|---------|------|----------|
| Creative | 🎨 | Wild ideas, lateral thinking, "yes-and" |
| Intellectual | 📚 | Deep analysis, frameworks, first principles |
| Trailblazer | 🚀 | Speed, MVPs, bold moves |
| Strategist | ♟️ | Chess-like planning, competitive positioning (DEFAULT) |
| Architect | 🏗️ | Systems thinking, scalability, technical depth |
| Coach | 🧭 | Empowerment, guided questioning, growth |
| Skeptic | 🔍 | Stress-testing, devil's advocate, risk analysis |
| Visionary | 🔮 | 10x moonshots, paradigm shifts |
| Editor | ✂️ | Ruthless clarity, cutting bloat, polish |
| Scientist | 🧪 | Hypothesis-driven, data, experiments |

### Architecture: 3-Layer Prompt Composition

```
Layer 1: Base Persona (from pathway config)
Layer 2: Partner Style Fragment (from partner_style_service.py)
Layer 3: Session Context (user name, memories, platform, stage, sheet schema)
```

### Key Files
- `backend/app/services/partner_style_service.py` — All partner metadata, prompt fragments, validation
- `backend/app/services/ai_service.py` — `build_system_prompt()` and `build_greeting_prompt()` compose the 3 layers
- `backend/app/routers/meta.py` — `GET /api/v1/meta/partner-styles`
- `backend/app/routers/discovery.py` — `PATCH /api/v1/discovery/{session_id}/partner` for mid-session switching
- `backend/app/alembic/versions/010_add_ai_partner_style.py` — Migration adding column to projects + sessions
- `frontend/src/pages/Home.tsx` — Inline 5×2 grid of partner preset boxes (NOT a modal)
- `frontend/src/pages/Discovery.tsx` — ActivePartnerBadge in header, PartnerSelector modal for mid-session switch
- `frontend/src/components/partner/` — PartnerCard, PartnerSelector, ActivePartnerBadge

### Home Page Partner UI
The partner selector on the Home page is an **inline grid** (not a pill/modal). It shows "Choose a partner style:" label followed by 10 compact preset boxes in a 5-column grid (2 rows), matching the glassmorphism style of the Quick Start preset cards. Selected partner gets cyan border + glow.

---

## API Endpoints (prefix: `/api/v1`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/projects` | Create project (accepts `ai_partner_style`, `pathway_id`) |
| GET | `/projects/{id}` | Get project |
| GET | `/pathways` | List all pathway definitions |
| POST | `/pathways/detect` | AI-detect pathway from description |
| GET | `/meta/partner-styles` | List all 10 partner style metadata objects |
| POST | `/discovery/{project_id}/start` | Start discovery session (inherits partner from project) |
| POST | `/discovery/{session_id}/greeting` | Get AI greeting (SSE) |
| POST | `/discovery/{session_id}/message` | Send chat message (SSE) |
| PATCH | `/discovery/{session_id}/partner` | Switch partner mid-session |
| GET | `/discovery/{session_id}` | Get session with messages |
| GET/POST | `/exports/...` | Export design sheets |
| POST | `/market/{project_id}/analyze` | Market analysis (SSE) |
| POST | `/sprints/{project_id}/generate` | Sprint plan generation |
| GET/POST | `/pipeline/...` | Pipeline nodes |
| GET/POST | `/auth/...` | Auth (login, register, OAuth, me) |

---

## Design System

- **Theme:** Dark glassmorphism — `bg-surface/60`, `backdrop-blur`, semi-transparent borders
- **Accent:** Cyan `#00E5FF` (`text-accent`, `border-accent`, `bg-accent/10`)
- **Text:** `text-white`, `text-text-muted` for secondary
- **Cards:** `bg-white/5 border border-border rounded-xl` with hover `hover:border-white/15 hover:scale-[1.02]`
- **Selected state:** `bg-accent/5 border-accent shadow-[0_0_16px_rgba(0,229,255,0.1)]`
- **Tailwind v4** with CSS-based config (no `tailwind.config.js`)

---

## Database Migrations

Linear chain: `001` → `002` → ... → `010`

| # | Description |
|---|-------------|
| 001 | Initial schema (users, projects, sessions, design_sheets, blocks) |
| 002 | Market analyses table |
| 003 | Project snapshots |
| 004 | OAuth + profile fields |
| 005 | User memory |
| 006 | Project shares |
| 007 | Sprint plans |
| 008 | Sprint error message patch |
| 009 | Pathway infrastructure (pathway_id on projects, stages on sessions) |
| 010 | AI partner style (ai_partner_style on projects + sessions) |

---

## Recent Commit History

```
ec228e3 refactor: replace partner pill/modal with inline 5×2 preset grid on Home page
eff0454 feat: AI Partner Selector — 10 collaboration styles with namesake-aligned behaviour
3a82ea0 fix: Alembic multiple heads + DesignSheetPanel TS cast error
ecf4c4d feat: Phase 6 — Marketing Campaign, Brand Identity, Creative Writing pathways
d56c9d2 feat: Phase 5 — Divergent-convergent thinking stages in discovery
781b992 feat: Phase 4 — AI pathway detection + hybrid selection UX
7eeb1bd feat: Phase 3 — Dynamic frontend driven by pathway config
4f9a805 feat: Phase 2 — Parameterize all services by PathwayConfig
5e7ba18 feat: Phase 1 — Concept Pathway registry infrastructure
```

---

## Known Issues / Notes

1. **Node.js v24 + Vite 7 ESM:** The local preview tool can't run Vite dev server due to ESM/require() incompatibility. Builds verified via `tsc -b` and `vite build` directly.
2. **C: drive space:** Vite builds may fail if C: is full. Use `TMPDIR=D:/tmp` when building locally.
3. **Integration tests:** 4 tests in `backend/tests/test_partner_style.py` require the `anthropic` module (only on Railway). The 24 unit tests run locally with just pytest.
4. **PartnerSelector component** (`frontend/src/components/partner/PartnerSelector.tsx`) is still used in `Discovery.tsx` for mid-session switching. It was removed from `Home.tsx` in favor of the inline grid.
5. **Partner style default** is `"strategist"` everywhere (model defaults, schema defaults, frontend state init).

---

## Critical Rules

- **Each AI Partner must genuinely live up to its namesake in behavior. This must not be cosmetic.** Every partner fragment in `partner_style_service.py` contains detailed behavioral instructions with Core Behaviour, Questioning Style, and Guardrails sections.
- **Structured output schema is never altered by partner choice.** Partners change *how* the AI collaborates, not *what* gets extracted.
- **All API routes are prefixed with `/api/v1`.**
- **Railway deployment** — both services auto-deploy on push to `main`.
