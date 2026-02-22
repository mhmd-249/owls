# CrowdTest — Session Handoff

## Current Status
- **Last completed phase:** Phase 2 (Agent Execution Engine)
- **Date:** 2026-02-22

## Pre-Phase: Initial Setup
- [x] Next.js 14 frontend created with TypeScript, Tailwind, App Router
- [x] framer-motion and recharts installed
- [x] Component directory structure created with placeholders
- [x] TypeScript interfaces defined in src/lib/types.ts
- [x] FastAPI backend scaffolded with CORS middleware
- [x] requirements.txt created
- [x] Pydantic models defined in app/models/schemas.py
- [x] Prompt template files created in app/prompts/
- [x] Makefile, .gitignore, and docs/HANDOFF.md created
- [x] Both servers verified to start without errors

## Phase 1: Profile-to-Prompt Pipeline
- [x] CustomerProfile Pydantic model created in `app/models/profile.py`
  - Includes PurchaseItem, BrowsingBehavior, FeedbackItem, CustomerPreferences
  - Field validator normalizes `style` (accepts string or list)
- [x] 10 diverse H&M customer profiles generated in `data/profiles/`
  - Ages 19-62, mix of genders, 10 European cities
  - Varied segments: sustainable, premium, budget, streetwear, athleisure, family, etc.
  - 5-15 purchases per customer, realistic H&M prices (€9.99-€79.99)
  - Each with 2-3 feedback items (reviews, complaints, surveys)
- [x] Profile builder service (`app/services/profile_builder.py`)
  - `load_raw_profiles()` — loads and validates all JSON profiles
  - `generate_persona_prompt()` — generates 150-300 word second-person persona descriptions
  - `build_all_personas()` — batch process all profiles, saves persona .txt files + manifest.json
- [x] Persona prompts generated in `data/processed/` with manifest.json
- [x] Prompt templates already in place (`agent_persona.txt`, `agent_evaluation.txt`)
- [x] 13 tests passing in `tests/test_profile_builder.py`

## Phase 2: Agent Execution Engine
- [x] Prompt Manager service (`app/services/prompt_manager.py`)
  - Loads and caches prompt templates from `app/prompts/`
  - `format_agent_prompt()` — wraps persona with instructions (detects pre-existing instructions)
  - `format_evaluation_prompt()` — formats product description into user message
- [x] Agent Runner service (`app/services/agent_runner.py`)
  - `AgentRunner` class with `asyncio.Semaphore` rate limiting
  - `run_single_agent()` — calls Claude API with persona system prompt, handles errors gracefully
  - `run_all_agents()` — parallel execution via `asyncio.gather`, supports callback for SSE streaming
  - `detect_sentiment()` — keyword-based MVP sentiment detection (positive/negative/neutral)
- [x] Pydantic models in `schemas.py` already correct from Pre-Phase
- [x] 198 persona files in `data/processed/` with manifest.json (from earlier pipeline run)
  - Manifest uses hashed IDs, fields: persona_file, display_name, age, purchase_count, segments, club_member_status
- [x] Live test: 5 agents responded in 7.6s (well under 30s limit)
  - Responses are realistic and persona-specific
  - Callback mechanism verified for SSE streaming
  - Sentiment detection labels correct
- [x] 20 total tests passing (13 Phase 1 + 7 Phase 2)

## Known Issues
- Python 3.13 is available system-wide with pytest; python3 (3.12) lacks pytest. Use `python3.13` to run tests.
- Manifest persona_file paths are relative to project root (e.g., `backend/data/processed/persona_000_alex.txt`), agent_runner handles this with fallback resolution.

## Next Phase
Phase 3: SSE Streaming & Aggregation Engine
- See IMPLEMENTATION_GUIDE.md for the full prompt
