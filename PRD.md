# Ide/AI — Product Requirements Document (PRD)

## Overview
Ide/AI is a web application that helps non-technical users transform raw product ideas into
structured, platform-specific design kits ready for use in no-code, low-code, agentic, or CLI
builder tools (e.g., Bubble, Webflow, FlutterFlow, Bolt, Claude Code, Cursor, Replit).

## Target User
Someone with zero development experience who has product ideas and needs structured output
to hand off to a builder tool or developer without wasting credits, time, or money.

## Core User Flow
1. User lands on the app → enters idea in a single input box
2. Selects platform target, audience, tone, and complexity
3. AI enters "Discovery Phase" — Socratic questions to flesh out the idea
4. In the background, a structured Design Sheet auto-populates in real time
5. After discovery, user views Design Blocks (feature cards), Pipeline Builder, and Prompt Kit
6. User exports the full "Design Kit" tailored to their chosen platform
7. All work is saved in a native Project Folder system with version history

## Key Features (P0 = must-have at launch)
### P0
- Single input onboarding with platform/audience/tone/complexity selectors
- AI Discovery Phase (SSE streamed chat, Socratic questioning engine)
- Live Design Sheet sidebar (auto-fills as discovery progresses)
- Launch Readiness Score (Clarity, Complexity, Platform Fit, Prompt Quality)
- Design Blocks board (drag-and-drop, MVP/V2 toggles, effort tags S/M/L)
- Prompt Kit Generator (platform-specific prompt output, copyable)
- Project Folder system with persistent storage per user
- Export: .txt, .md, .pdf, .docx

### P1
- Visual Pipeline Builder (frontend/backend/db/automations/ai/deploy cards)
- Exportable UI skeleton (screen list + nav flow + component inventory as JSON/HTML)
- Pitch Mode (shareable one-page brief, public link toggle)
- Version History + Pivot Tracker (snapshot per save, branchable)
- Zero Dev Language Mode (jargon-free toggle)
- Flow State minimal mode (distraction-free writing)

### P2
- Prompt Template Library (curated + user-saved)
- Quick Launch Scoring with one-click fixes
- Multi-user project sharing
- Platform-specific onboarding tutorials

## Design System
- Dark glassmorphism base (#0d0d12 background)
- Single accent color per project (default: electric cyan #00E5FF)
- Font: Inter (UI), JetBrains Mono (code/prompts)
- Framer Motion for all transitions and node animations
- Card radius: 12px, border: 1px solid rgba(255,255,255,0.08)
