# Ide/AI — Architecture Document

## Directory Structure
```
Ide_AI/
├── frontend/                  # React/Vite app
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   │   ├── ui/            # Base: Button, Card, Input, Badge, Drawer
│   │   │   ├── layout/        # Sidebar, TopBar, FlowModeWrapper
│   │   │   ├── nebula/        # IdeaNebulaCanvas (canvas animation)
│   │   │   ├── discovery/     # ChatThread, StagesStepper, QuickChips
│   │   │   ├── framework/     # DesignSheetPanel, ReadinessScores
│   │   │   ├── blocks/        # BlocksBoard, BlockCard, ScopeSlider
│   │   │   ├── pipeline/      # PipelineCanvas, PipelineCard, CostPanel
│   │   │   ├── promptkit/     # PromptKitPanel, PromptSnippet
│   │   │   ├── projects/      # FolderTree, ProjectCard, VersionTimeline
│   │   │   └── pitch/         # PitchDocument, SharePanel
│   │   ├── pages/             # Home, Discovery, Blocks, Pipeline, Exports, Settings
│   │   ├── stores/            # Zustand: projectStore, uiStore, discoveryStore
│   │   ├── hooks/             # useSSE, useDiscovery, useExport, useVersions
│   │   ├── lib/               # apiClient (axios), sseClient, exportUtils
│   │   ├── types/             # TypeScript interfaces/enums
│   │   └── styles/            # globals.css, tailwind config
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
│
├── backend/                   # FastAPI app
│   ├── app/
│   │   ├── main.py            # FastAPI app factory, CORS, router include
│   │   ├── core/
│   │   │   ├── config.py      # Settings via pydantic-settings
│   │   │   ├── security.py    # JWT helpers
│   │   │   └── database.py    # Async SQLAlchemy engine + session
│   │   ├── models/            # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── session.py     # Discovery session
│   │   │   ├── design_sheet.py
│   │   │   ├── block.py
│   │   │   └── version.py
│   │   ├── schemas/           # Pydantic v2 request/response schemas
│   │   ├── routers/           # One file per domain
│   │   │   ├── auth.py
│   │   │   ├── projects.py
│   │   │   ├── discovery.py   # SSE streaming endpoint lives here
│   │   │   ├── design_sheet.py
│   │   │   ├── blocks.py
│   │   │   ├── pipeline.py
│   │   │   ├── prompts.py
│   │   │   └── exports.py
│   │   ├── services/          # Business logic
│   │   │   ├── ai_service.py          # Claude API wrapper, prompt builder
│   │   │   ├── discovery_service.py   # Socratic engine, confidence scoring
│   │   │   ├── sheet_service.py       # Auto-fill design sheet logic
│   │   │   ├── prompt_kit_service.py  # Platform-specific prompt templates
│   │   │   ├── pipeline_service.py    # Stack recommendation engine
│   │   │   └── export_service.py      # .md/.pdf/.docx generators
│   │   └── alembic/           # DB migrations
│   ├── pyproject.toml         # Poetry config
│   └── .env.example
│
└── docker-compose.yml         # postgres + backend + frontend dev setup
```

## Database Schema (Key Tables)
```
users           id, email, hashed_password, created_at
projects        id, user_id, name, accent_color, platform, created_at
sessions        id, project_id, status (active|complete), messages JSONB
design_sheets   id, project_id, problem, audience, mvp, features JSONB, tone, platform
blocks          id, project_id, name, category, priority (mvp|v2), effort (S|M|L), order
pipeline_nodes  id, project_id, layer, selected_tool, config JSONB
prompt_kits     id, project_id, platform, content TEXT, version INT
versions        id, project_id, snapshot JSONB, label, created_at
```

## AI Service Design
- All Claude calls go through `ai_service.py`
- System prompt is built dynamically from: base persona + platform context + discovery state
- Discovery uses a state machine: [greeting → problem → audience → features → constraints → confirm]
- Confidence score is computed after each turn (0–100) based on fields populated in design_sheet
- SSE stream: FastAPI StreamingResponse with `text/event-stream`, frontend uses EventSource
