# Handoff — CrowdTest Session Continuity

> Update this file after each phase. The next Claude Code session should read this first.

## Completed Phases
Pre-Phase: Initial Setup
Phase 1: Data Processing & Profile-to-Prompt Pipeline

## Current Phase
Phase 2: Agent Execution Engine (Parallel Claude Calls)

## Phase Status Log

### Pre-Phase: Project Scaffolding
- **Status:** complete
- **Notes:** 
Frontend (frontend/)
  - Next.js 14 app with TypeScript, Tailwind CSS, App Router, src/ directory
  - Additional deps installed: framer-motion, recharts
  - Components — placeholder files for all 9 components:
    - lab/: ChatSidebar, Character, ThoughtBubble, CrowdScene
    - insights/: ExecutiveSummary, SentimentChart, SegmentAnalysis, ThemeExtractor, ResponseDrillDown
  - Hooks: useSSE.ts, useTestSession.ts
  - Lib: api.ts (API client), types.ts (all 6 interfaces + supporting types)
  - frontend/CLAUDE.md with frontend-specific context
  Backend (backend/)
  - FastAPI app (app/main.py) with CORS middleware for localhost:3000
  - Config (app/config.py) loading all env vars with defaults
  - Pydantic models (app/models/schemas.py) — TestRequest, AgentResponse, TestSession, InsightResults, SentimentBreakdown, SegmentData
  - Prompt templates — all 4 files in app/prompts/
  - Directory structure — routers/, services/, data/profiles/, data/processed/, tests/
  - .env.example with all env vars
  - backend/CLAUDE.md with backend-specific context
  Root
  - Makefile with dev, frontend, backend, install targets
  - .gitignore covering Node, Python, .env, IDE, OS files
  - docs/HANDOFF.md — initial handoff template
  - docs/IMPLEMENTATION_GUIDE.md moved to docs/
  Verification
  - npm run build — compiled successfully, no TypeScript errors
  - Backend FastAPI app imports and uvicorn config validated successfully
- **Issues:**

### Phase 1: Data Processing & Profile-to-Prompt Pipeline
- **Status:** complete
- **Notes:**
Task 1: CustomerProfile Model (backend/app/models/profile.py)
                                                                                                                                                                                             
  - Comprehensive Pydantic models: CustomerProfile, PurchaseItem, BrowsingBehavior, FeedbackItem, CustomerPreferences
  - Field validator to normalize style (string or list input)

Task 2: Profile Builder Service (backend/app/services/profile_builder.py)

  - load_raw_profiles() — Loads all customer_*.json files from a directory into validated CustomerProfile instances
  - generate_persona_prompt() — Transforms profiles into rich 150-300 word second-person persona descriptions including purchase history, browsing patterns, style preferences, feedback
  quotes, and segment categorization
  - build_all_personas() — Batch generates persona .txt files + manifest.json mapping customer IDs to demographics

Task 3: Prompt Templates

  - Already in place from Pre-Phase: agent_persona.txt and agent_evaluation.txt

Task 4: Sample Data + Tests

  - 10 diverse customer profiles in backend/data/profiles/ covering ages 19-62, 10 European cities, varied shopping segments
  - 13 tests passing — validates word counts (150-300), required fields, uniqueness, manifest structure

Verification

  python3.13 -m pytest tests/test_profile_builder.py -v
  → 13 passed in 0.03s

All 10 persona prompts are unique, realistic, and in range. Manifest.json maps all profiles correctly.
- **Issues:**

### Phase 2: Agent Execution Engine
- **Status:** completed
- **Notes:**
  Task 1: Agent Runner Service (backend/app/services/agent_runner.py)
                                                                                                                                                                                             
  - AgentRunner class with asyncio.Semaphore for rate limiting (default 50 concurrent)                                                                                                     
  - run_single_agent() — calls Claude API with persona as system prompt, handles errors gracefully (returns error response instead of crashing)
  - run_all_agents() — parallel execution via asyncio.gather, supports callback for SSE streaming, logs timing/failures
  - detect_sentiment() — keyword-based MVP detection with 20 positive and 20 negative keywords, returns positive/negative/neutral

  Task 2: Prompt Manager Service (backend/app/services/prompt_manager.py)

  - Loads and caches prompt templates from app/prompts/
  - format_agent_prompt() — detects if persona already has instructions to avoid double-wrapping
  - format_evaluation_prompt() — fills product description into the evaluation template

  Task 3: Pydantic Models

  - Already correct from Pre-Phase setup — no changes needed

  Task 4: Live Test Results

  - 5 agents responded in 7.6s (well under 30s limit)
  - All responses realistic and persona-specific (e.g., Alex the 61-year-old practical buyer rejected the trendy tees)
  - Callback mechanism verified (3 callbacks received correctly)
  - Sentiment detection labeling correct

  Verification

  python3.13 -m pytest tests/ -v
  → 20 passed in 13.20s
- **Issues:**

### Phase 3: SSE Streaming & Aggregation
- **Status:** Not Started
- **Notes:**
- **Issues:**

### Phase 4: Frontend — Testing Lab (Minions Scene)
- **Status:** Not Started
- **Notes:**
- **Issues:**

### Phase 5: Frontend — Insights Dashboard
- **Status:** Not Started
- **Notes:**
- **Issues:**

### Phase 6: Integration & Polish
- **Status:** Not Started
- **Notes:**
- **Issues:**

### Phase 7: Demo Preparation
- **Status:** Not Started
- **Notes:**
- **Issues:**

## Key Decisions Made
- Tech stack: Next.js 14 frontend + Python FastAPI backend
- LLM: Claude Sonnet for agents (speed), Opus for aggregation (quality)
- No database — JSON files for profiles, in-memory for test sessions
- SSE for real-time streaming of agent responses
- 30 characters visible on screen, representing 200 agents
- Simple SVG characters with thought bubbles

## Known Issues / Blockers
_None yet_

## Architecture Changes
_None yet — following original plan_

## What the Next Session Needs to Know
- Start by reading CLAUDE.md for project context
- Read the relevant phase prompt from docs/IMPLEMENTATION_GUIDE.md
- Check this file for any issues from previous phases
