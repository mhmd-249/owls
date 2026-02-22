# CrowdTest Backend

## Tech Stack
- Python 3.11+
- FastAPI + uvicorn
- anthropic SDK (async)
- sse-starlette (Server-Sent Events)
- Pydantic (data models)
- python-dotenv (env vars)

## Directory Structure
```
backend/
├── app/
│   ├── main.py          # FastAPI app entry, CORS config
│   ├── config.py        # Environment variable loading
│   ├── routers/         # API route handlers
│   │   ├── test.py      # /api/test endpoints
│   │   └── profiles.py  # /api/profiles endpoints
│   ├── services/        # Business logic
│   │   ├── agent_runner.py    # Parallel Claude agent execution
│   │   ├── aggregator.py      # Insight aggregation with Claude Opus
│   │   ├── profile_builder.py # Profile-to-persona pipeline
│   │   └── prompt_manager.py  # Prompt template loading
│   ├── models/          # Pydantic models
│   │   ├── schemas.py   # API request/response models
│   │   └── profile.py   # Customer profile model
│   └── prompts/         # Prompt template files
│       ├── agent_persona.txt
│       ├── agent_evaluation.txt
│       ├── aggregation_summary.txt
│       └── segment_analysis.txt
├── data/
│   ├── profiles/        # Raw customer profile JSONs
│   └── processed/       # Generated persona prompts
├── tests/
└── requirements.txt
```

## Environment Variables
- `ANTHROPIC_API_KEY` — Required for Claude API calls
- `AGENT_MODEL` — Model for agent calls (default: claude-sonnet-4-20250514)
- `AGGREGATION_MODEL` — Model for aggregation (default: claude-opus-4-20250514)
- `MAX_CONCURRENT_AGENTS` — Semaphore limit (default: 50)
- `MAX_AGENTS` — Total agents to run (default: 200)
- `PROFILES_DIR` — Path to profile JSONs (default: data/profiles)
- `PROCESSED_DIR` — Path to generated personas (default: data/processed)

## API Endpoints
```
POST /api/test             — Submit a product test
GET  /api/test/{id}/stream — SSE stream of agent responses
GET  /api/test/{id}/results — Final aggregated insights
GET  /api/profiles/stats   — Profile statistics
```

## Code Style
- Type hints on all functions
- async/await for IO operations
- Pydantic models for all data
- black + isort for formatting
