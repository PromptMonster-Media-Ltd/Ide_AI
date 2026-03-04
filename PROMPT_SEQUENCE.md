# Ide/AI — Claude Code Prompt Sequence

Use these prompts IN ORDER in your Claude Code CLI session.
Always wait for each step to complete before running the next.
Run `claude` from the root of your project directory.

---

## PROMPT 1 — Project Scaffold
```
Read SYSTEM_PROMPT.md, PRD.md, ARCHITECTURE.md, and FEATURE_SPEC.md in full before doing anything.

Then scaffold the full Ide/AI project directory exactly as described in ARCHITECTURE.md.
Create all directories and placeholder files with correct top-of-file docstrings.
Initialize:
- frontend/ with Vite + React 18 + TypeScript template
- Install: tailwindcss, framer-motion, zustand, @tanstack/react-query, axios, @dnd-kit/core, reactflow
- backend/ with Poetry, FastAPI, SQLAlchemy 2.0 async, alembic, anthropic, pydantic-settings, python-dotenv, fpdf2, python-docx, jinja2, passlib, python-jose
- docker-compose.yml with postgres:15, backend, frontend services

Do not write any feature logic yet. Scaffold only.
```

---

## PROMPT 2 — Database & Auth
```
Using ARCHITECTURE.md schema as the source of truth:

1. Create all SQLAlchemy async ORM models in backend/app/models/
2. Write Pydantic v2 schemas for all models in backend/app/schemas/
3. Set up Alembic and generate the initial migration
4. Implement JWT auth in core/security.py and routers/auth.py
   - Endpoints: POST /api/v1/auth/register, POST /api/v1/auth/login, GET /api/v1/auth/me
5. Write backend/app/core/database.py with async session factory

All models must use UUID primary keys. Include created_at/updated_at timestamps on all tables.
```

---

## PROMPT 3 — AI Service & Discovery Engine
```
Build the core AI layer:

1. backend/app/services/ai_service.py
   - Async Claude client wrapper using anthropic SDK
   - build_system_prompt(project, stage) → str
   - stream_response(messages, system_prompt) → AsyncGenerator[str, None]

2. backend/app/services/discovery_service.py
   - State machine with 5 stages: greeting, problem, audience, features, constraints
   - next_stage(current_stage, sheet) → str
   - compute_confidence(design_sheet) → int (0–100)
   - Fields checked: problem, audience, mvp, tone, features, constraints

3. backend/app/routers/discovery.py
   - POST /api/v1/discovery/start → creates session, returns session_id
   - POST /api/v1/discovery/{session_id}/message (SSE) → StreamingResponse
     - Accepts user message, calls AI, streams tokens
     - After full response: extracts design sheet fields, saves to DB, emits sheet_update event
   - GET /api/v1/discovery/{session_id}/sheet → returns current design sheet state

Use Server-Sent Events. Stream format: data: {"type": "token"|"sheet_update"|"done", "content": ...}
```

---

## PROMPT 4 — Frontend Core + Discovery UI
```
Build the frontend foundation and the Discovery page:

1. Set up TailwindCSS with custom config:
   - Background: #0d0d12
   - Accent: #00E5FF (cyan)
   - Font: Inter (UI), JetBrains Mono (code)
   - Card radius 12px, subtle glass border

2. Create layout components:
   - Sidebar (icon + label nav, project switcher)
   - TopBar (project name, search, Flow Mode toggle)
   - FlowModeWrapper (hides sidebar + topbar, ambient gradient background)

3. Build pages/Home.tsx
   - Centered input + 4 selector chips
   - IdeaNebulaCanvas.tsx behind input (Framer Motion pulsing nodes, 8 nodes)
   - On submit: POST /api/v1/projects + navigate to /discovery/:id

4. Build pages/Discovery.tsx
   - Left: StagesStepper (5 stages, vertical, cyan active state)
   - Center: ChatThread with streamed tokens via useSSE hook
   - Right: DesignSheetPanel (live fields, confidence bar)
   - Bottom: chat input + QuickChips (populated from AI response metadata)

5. hooks/useSSE.ts — wraps EventSource, returns messages array + isStreaming bool
```

---

## PROMPT 5 — Design Blocks + Prompt Kit
```
Build the Design Blocks board and Prompt Kit panel:

1. backend/app/services/sheet_service.py
   - generate_blocks(design_sheet) → List[Block] using Claude
   - Auto-assigns effort (S/M/L) and priority (mvp/v2) based on feature complexity

2. backend/app/routers/blocks.py
   - GET /api/v1/projects/{id}/blocks → list blocks
   - POST /api/v1/projects/{id}/blocks/generate → AI generates blocks
   - PATCH /api/v1/blocks/{id} → update priority/effort/order
   - DELETE /api/v1/blocks/{id}

3. backend/app/services/prompt_kit_service.py
   - Platform-specific Jinja2 templates in backend/templates/prompts/{platform}.j2
   - generate_prompt_kit(project, blocks, sheet) → str
   - Templates for: bubble, webflow, flutterflow, claude_code, cursor, bolt, replit

4. pages/Blocks.tsx
   - @dnd-kit drag-and-drop grid of BlockCard components
   - ScopeSlider (Lean/Balanced/Full)
   - Right panel: PromptKitPanel with copy buttons, platform dropdown, Zero Dev toggle

5. Zustand store: discoveryStore.ts tracks session, sheet state, stage, confidence
```

---

## PROMPT 6 — Pipeline Builder
```
Build the Pipeline Builder:

1. backend/app/services/pipeline_service.py
   - PIPELINE_OPTIONS dict: each layer has curated tool options with cost/complexity metadata
   - recommend_pipeline(design_sheet) → Dict[layer, tool] using rule-based logic + Claude suggestion
   - estimate_cost(pipeline) → {"min": int, "max": int, "currency": "USD/mo"}
   - check_compatibility(pipeline) → List[str] notes

2. backend/app/routers/pipeline.py
   - GET /api/v1/projects/{id}/pipeline
   - POST /api/v1/projects/{id}/pipeline/recommend
   - PATCH /api/v1/projects/{id}/pipeline/{layer}
   - POST /api/v1/projects/{id}/pipeline/ui-skeleton → returns JSON screen list

3. pages/Pipeline.tsx
   - Horizontal scrollable canvas
   - PipelineCard per layer with dropdown (options from backend)
   - Animated connector lines between cards (SVG)
   - Right panel: CostPanel + compatibility notes + "Why this stack" bullets
   - "Generate UI Skeleton" and "Export" buttons
```

---

## PROMPT 7 — Export System + Pitch Mode + Project Folders
```
Build the remaining features:

1. backend/app/services/export_service.py
   - generate_markdown(project) → str
   - generate_pdf(project) → bytes (fpdf2)
   - generate_docx(project) → bytes (python-docx)
   - generate_zip(project) → bytes (all formats)
   - Use Jinja2 templates in backend/templates/exports/

2. backend/app/routers/exports.py
   - GET /api/v1/projects/{id}/export?format=md|pdf|docx|zip

3. pages/Exports.tsx — format selector, preview pane, download

4. pages/PitchMode.tsx
   - Clean document layout
   - React Flow read-only diagram (4–6 nodes from blocks)
   - SharePanel: toggle public, copy link, expiry

5. components/projects/FolderTree.tsx
   - Collapsible tree, sections per project
   - VersionTimeline at base of each project folder
   - Restore version via POST /api/v1/projects/{id}/versions/{vid}/restore

6. backend/app/routers/versions.py + version snapshotting on every major save
```

---

## PROMPT 8 — Polish, Animations & QA
```
Final polish pass:

1. Add Framer Motion transitions to all page navigations (fade + slide)
2. Add skeleton loaders for all async data fetches
3. Add toast notifications (react-hot-toast) for: save, copy, export, error states
4. Implement Zero Dev Language Mode toggle — POST /api/v1/prompts/{id}/rewrite?mode=plain
5. Implement Flow State mode (FlowModeWrapper hides all chrome, ambient gradient bg)
6. Add Launch Readiness Score panel to Blocks page (4 circular gauge indicators)
7. Mobile responsiveness: sidebar collapses to bottom nav on <768px
8. Write .env.example with all required env vars documented
9. Write README.md with setup instructions, stack overview, and feature list
10. Final QA: check all SSE connections close cleanly, all exports download correctly,
    all DB writes are transactional, all routes return proper HTTP status codes
```
