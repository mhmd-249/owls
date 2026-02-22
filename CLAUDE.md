# CrowdTest — Customer Digital Twin Simulation Engine

## What This Project Is
A platform that transforms real customer data into AI-powered "digital twin" agents. Companies submit product ideas → agents respond as their real customers would → system aggregates into actionable insights. Built for H&M as demo, using 200 real customer profiles.

## Architecture
Monorepo with two apps:
- `frontend/` — Next.js 14 (App Router) + Tailwind CSS + Framer Motion
- `backend/` — Python FastAPI + async Claude API calls

## Tech Stack
- **Frontend:** Next.js 14, TypeScript, Tailwind CSS, Framer Motion, Recharts
- **Backend:** Python 3.11+, FastAPI, uvicorn, anthropic SDK, SSE (sse-starlette)
- **LLM:** Claude API — Sonnet for agents (200 parallel), Opus for aggregation
- **Data:** JSON files for customer profiles (no database needed for MVP)
- **Real-time:** Server-Sent Events from FastAPI → Next.js frontend

## Directory Structure
```
/
├── CLAUDE.md              # You are here
├── frontend/
│   ├── CLAUDE.md          # Frontend-specific context
│   ├── src/app/           # Next.js App Router pages
│   ├── src/components/    # React components
│   └── src/lib/           # Utilities, API client, types
├── backend/
│   ├── CLAUDE.md          # Backend-specific context
│   ├── app/
│   │   ├── main.py        # FastAPI app entry
│   │   ├── routers/       # API route handlers
│   │   ├── services/      # Business logic (agent runner, aggregator)
│   │   ├── models/        # Pydantic models
│   │   └── prompts/       # Prompt templates
│   └── data/
│       ├── profiles/      # Customer profile JSONs
│       └── processed/     # Generated persona prompts
├── docs/
│   ├── IMPLEMENTATION_GUIDE.md  # Phased prompts for Claude Code
│   └── HANDOFF.md               # Session continuity between phases
└── .claude/
    ├── commands/          # Slash commands
    └── skills/            # Custom skills
```

## Key Commands
```bash
# Frontend
cd frontend && npm run dev          # Start Next.js dev server (port 3000)
cd frontend && npm run build        # Build for production
cd frontend && npm run lint         # Run ESLint

# Backend
cd backend && pip install -r requirements.txt   # Install deps
cd backend && uvicorn app.main:app --reload --port 8000  # Start FastAPI (port 8000)

# Both (from root)
make dev    # Start both frontend and backend
```

## Code Style
- TypeScript: strict mode, prefer `interface` over `type`, named exports
- Python: type hints on all functions, async/await for IO, Pydantic models for data
- Use ES modules in frontend (import/export), not CommonJS
- Prefer functional components with hooks in React
- Use Tailwind utility classes; avoid custom CSS files
- Python formatting: black, isort

## API Contract (Frontend ↔ Backend)
```
POST /api/test           — Submit a product test (returns test_id)
GET  /api/test/{id}/stream — SSE stream of agent responses  
GET  /api/test/{id}/results — Final aggregated insights
GET  /api/profiles/stats   — Profile statistics for UI
```

## IMPORTANT Rules
- NEVER hardcode API keys. Use environment variables (ANTHROPIC_API_KEY).
- Use `claude-sonnet-4-20250514` for agent calls (fast, cheap for 200 parallel).
- Use `claude-opus-4-20250514` for the final aggregation/insight call (quality matters).
- SSE responses must include `event:` and `data:` fields for proper parsing.
- Every agent call must include the full customer persona in the system prompt.
- Frontend characters are SIMPLE SVGs — circles with eyes. Do not overcomplicate.
- Keep all prompts in separate template files under `backend/app/prompts/`.
- Run `npm run build` after frontend changes to verify no TypeScript errors.
- Run `python -m pytest` after backend changes to verify no regressions.
- Always use /clear between phases to keep context fresh.

## Phase Workflow
This project is built in 7 phases. After completing each phase:
1. Verify the phase works by running tests/checks specified in the phase
2. Update docs/HANDOFF.md with what was completed and any issues
3. Start a new Claude Code session with /clear for the next phase
4. Begin next phase by reading docs/IMPLEMENTATION_GUIDE.md for the phase prompt
