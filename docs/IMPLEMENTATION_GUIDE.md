# Implementation Guide — Phased Prompts for Claude Code

> **How to use this file:** Copy the prompt for each phase into Claude Code as a new session.
> After each phase, run `/clear` to start fresh. Update HANDOFF.md with status.
> IMPORTANT: Start each Claude Code session by telling it to read CLAUDE.md first.

---

## Pre-Phase: Initial Setup

> Run this ONCE before starting Phase 1. This sets up the project structure.

### Prompt:
```
Read CLAUDE.md for full project context.

Set up the project scaffolding for CrowdTest — a customer digital twin simulation platform. Create the full directory structure as described in CLAUDE.md.

**Frontend setup:**
1. Create a Next.js 14 app with App Router in `frontend/` using `npx create-next-app@latest`
   - TypeScript: yes, Tailwind: yes, App Router: yes, src/ directory: yes
2. Install additional deps: `framer-motion recharts`
3. Create the component directory structure from frontend/CLAUDE.md
4. Create placeholder files for all components (just export default empty functions)
5. Set up `src/lib/types.ts` with all TypeScript interfaces we'll need:
   - AgentResponse, TestSession, InsightResults, CustomerProfile, SentimentBreakdown, SegmentData

**Backend setup:**
1. Create `backend/` with the structure from backend/CLAUDE.md
2. Create `requirements.txt` with: fastapi, uvicorn[standard], anthropic, sse-starlette, pydantic, python-dotenv, pytest, black, isort
3. Create `app/main.py` with basic FastAPI app, CORS middleware allowing localhost:3000
4. Create `app/config.py` loading env vars with defaults
5. Create `.env.example` with all env vars from backend/CLAUDE.md
6. Create empty Pydantic models in `app/models/schemas.py`
7. Create empty prompt template files in `app/prompts/`

**Root setup:**
1. Create a Makefile with `dev` target that starts both servers
2. Create `.gitignore` covering Node, Python, .env files
3. Create `docs/HANDOFF.md` with initial template

Verify: both `npm run dev` (frontend) and `uvicorn app.main:app` (backend) start without errors.
```

---

## Phase 1: Data Processing & Profile-to-Prompt Pipeline

> **Goal:** Transform raw H&M customer data into rich persona prompts that make agents realistic.
> **This is the most critical phase for demo quality.**

### Prompt:
```
Read CLAUDE.md and backend/CLAUDE.md for context.

## Phase 1: Build the Profile-to-Prompt Pipeline

We have H&M customer data in `backend/data/profiles/`. The data includes customer demographics, purchase history, preferences, browsing behavior, support interactions, and feedback.

### Task 1: Create the Profile Data Model
In `backend/app/models/profile.py`, create a comprehensive Pydantic model `CustomerProfile` that can hold:
- customer_id, name, age, gender, location
- purchase_history: list of items with category, subcategory, color, size, price, date
- browsing_behavior: categories viewed, time spent, items wishlisted
- feedback_history: any reviews, complaints, or support tickets
- preferences: inferred style preferences, price sensitivity, brand affinity
- segments: list of segment tags (e.g., "casual_weekend", "sustainable_fashion", "budget_conscious")

### Task 2: Build the Profile Builder Service
In `backend/app/services/profile_builder.py`:

1. Create a function `load_raw_profiles(data_dir: str) -> list[CustomerProfile]` that reads the H&M data files and maps them to our model.

2. Create a function `generate_persona_prompt(profile: CustomerProfile) -> str` that transforms a profile into a rich, natural-language persona description. This is THE critical function. The prompt should read like a character description, for example:

"You are Maria, a 34-year-old woman living in Gothenburg, Sweden. You primarily shop at H&M for everyday casual wear. Over the past year, you've purchased 8 items — mostly basic t-shirts and jeans in neutral tones (black, white, gray). Your average order value is €35. You tend to shop during sales and are price-sensitive. You returned one item because the fabric felt cheap. You've browsed the sustainable 'Conscious Collection' 3 times but never purchased. In your last feedback, you mentioned wanting more size-inclusive options. You prefer minimalist styles and avoid loud patterns."

The prompt should:
- Be written in second person ("You are...")
- Include specific details from purchase history (quantities, categories, colors, price points)
- Reference actual behavioral patterns (browsing, returns, support tickets)
- Capture the customer's "voice" based on their feedback history
- Include inferred preferences that a real customer would have
- Be 150-300 words per persona

3. Create a function `build_all_personas(profiles_dir: str, output_dir: str)` that:
   - Loads all profiles
   - Generates persona prompts for each
   - Saves them as individual text files in `data/processed/`
   - Also saves a `manifest.json` mapping customer_id to persona file path and key demographics

### Task 3: Create Prompt Templates
In `backend/app/prompts/`:

1. `agent_persona.txt` — A wrapper template that takes the generated persona and adds instructions:
```
{persona_description}

IMPORTANT INSTRUCTIONS:
- You ARE this person. Respond naturally as yourself, in first person.
- When presented with a product idea, react authentically based on your shopping habits, preferences, and lifestyle.
- Be specific: mention what you like, dislike, what would make you buy or not buy.
- Reference your past experiences with similar products when relevant.
- Keep your response to 3-5 sentences. Be conversational, not formal.
- If the product isn't relevant to you at all, say so and explain why.
```

2. `agent_evaluation.txt` — The user message template for product evaluation:
```
H&M is considering this new product/change:

{product_description}

As a customer, what's your honest reaction? Would you buy this? Why or why not? What would you change about it?
```

### Task 4: Test the Pipeline
Create a test script `backend/tests/test_profile_builder.py` that:
- Loads at least 3 sample profiles
- Generates persona prompts for each
- Prints them out for manual review
- Validates they are between 150-300 words
- Validates they contain key profile details

Run the test and verify the persona prompts look realistic and detailed.

### Verification:
- `python -m pytest backend/tests/test_profile_builder.py -v` passes
- At least 3 persona prompts printed look realistic and unique
- Manifest.json is created with all profiles mapped
```

---

## Phase 2: Agent Execution Engine (Parallel Claude Calls)

> **Goal:** Build the core engine that runs 198 agents in parallel with rate limiting.

### Prompt:
```
Read CLAUDE.md and backend/CLAUDE.md for context.
Read docs/HANDOFF.md for Phase 1 status.

## Phase 2: Build the Agent Execution Engine

### Task 1: Agent Runner Service
In `backend/app/services/agent_runner.py`, build the parallel agent execution system:

1. Create class `AgentRunner`:
   - `__init__(self, api_key: str, model: str, max_concurrent: int = 50)`
   - Store an `anthropic.AsyncAnthropic` client
   - Create an `asyncio.Semaphore(max_concurrent)` for rate limiting

2. Create method `async run_single_agent(self, profile_id: str, persona_prompt: str, product_description: str) -> AgentResponse`:
   - Acquire semaphore
   - Call Claude API with persona as system prompt, product evaluation as user message
   - Parse response and detect sentiment (simple keyword-based: positive/negative/neutral)
   - Return an AgentResponse Pydantic model with: agent_id, profile_name, age, segment, response_text, sentiment, response_time_ms
   - Handle errors gracefully — if one agent fails, return error response, don't crash the batch

3. Create method `async run_all_agents(self, product_description: str, callback: Callable = None) -> list[AgentResponse]`:
   - Load all persona prompts from `data/processed/`
   - Create tasks for all agents using `asyncio.gather(return_exceptions=True)`
   - After each agent completes, call `callback(agent_response)` if provided (this is how we'll stream to SSE)
   - Return all responses
   - Log timing: total time, avg per agent, failures count

4. Create a simple sentiment analyzer function `detect_sentiment(text: str) -> str`:
   - Use keyword matching for MVP: scan for positive words (love, great, definitely, would buy) and negative words (don't like, wouldn't, not interested, dislike)
   - Return "positive", "negative", or "neutral"
   - This doesn't need to be perfect — it's for the visualization color coding

### Task 2: Prompt Manager Service  
In `backend/app/services/prompt_manager.py`:
- Load prompt templates from `app/prompts/` directory
- Provide `format_agent_prompt(persona: str) -> str` and `format_evaluation_prompt(product_desc: str) -> str`
- Cache loaded templates

### Task 3: Update Pydantic Models
In `backend/app/models/schemas.py`:
- `TestRequest`: product_description (str), target_segments (optional list[str])
- `AgentResponse`: agent_id, profile_name, age, segment, response_text, sentiment, response_time_ms
- `TestSession`: test_id, status, product_description, responses (list), created_at
- `InsightResults`: executive_summary, sentiment_breakdown, segments, key_themes, total_agents, response_rate

### Task 4: Test with 5 Agents
Create `backend/tests/test_agent_runner.py`:
- Use 5 sample persona prompts
- Run them against a test product description: "H&M is launching a new line of oversized graphic t-shirts with vintage 90s designs, priced at €24.99"
- Print all 5 responses
- Verify all return within 30 seconds
- Verify sentiment detection works

IMPORTANT: This test requires a real ANTHROPIC_API_KEY in .env. Make sure the test file has a skip decorator if the key is not found.

### Verification:
- Test passes with 5 agents responding
- Responses are realistic and match persona profiles
- Total execution time under 30 seconds for 5 agents
- Sentiment detection labels make sense
```

---

## Phase 3: SSE Streaming & Aggregation Engine

> **Goal:** Build the streaming API and the insight aggregation system.

### Prompt:
```
Read CLAUDE.md and backend/CLAUDE.md for context.
Read docs/HANDOFF.md for Phase 1-2 status.

## Phase 3: SSE Streaming + Aggregation Engine

### Task 1: Create the Test Router with SSE
In `backend/app/routers/test.py`:

1. `POST /api/test` — Start a new test:
   - Accept TestRequest body
   - Generate a unique test_id (uuid4)
   - Store TestSession in an in-memory dict
   - Kick off agent execution in background (asyncio.create_task)
   - Return { test_id, status: "running" }

2. `GET /api/test/{test_id}/stream` — SSE stream of agent responses:
   - Use sse-starlette's EventSourceResponse
   - As each agent completes, stream an "agent_response" event with the AgentResponse JSON
   - When all agents complete, stream "agents_complete" event
   - Then trigger aggregation and stream "aggregation_started" event
   - When aggregation completes, stream "insights_ready" event with the test_id
   - Use an asyncio.Queue for the callback → SSE bridge

   The pattern:
   ```python
   queue = asyncio.Queue()
   
   async def on_agent_done(response):
       await queue.put(response)
   
   # Start agent runner in background with callback
   task = asyncio.create_task(runner.run_all_agents(desc, callback=on_agent_done))
   
   async def event_generator():
       completed = 0
       while completed < total_agents:
           response = await queue.get()
           completed += 1
           yield {"event": "agent_response", "data": response.model_dump_json()}
       yield {"event": "agents_complete", "data": json.dumps({"total": completed})}
       # Trigger aggregation...
   
   return EventSourceResponse(event_generator())
   ```

3. `GET /api/test/{test_id}/results` — Get final insights (for the insights page):
   - Return the stored InsightResults for the test
   - 404 if test not found or insights not ready yet

### Task 2: Build the Aggregation Service
In `backend/app/services/aggregator.py`:

1. Create class `InsightAggregator`:
   - Uses Claude Opus for high-quality synthesis

2. Method `async generate_executive_summary(responses: list[AgentResponse], product_description: str) -> str`:
   - Compile all agent responses into a structured input
   - Send to Claude Opus with the aggregation prompt
   - The prompt should ask for: overall reception, key positive themes, key concerns, recommended actions
   - Return markdown-formatted executive summary

3. Method `compute_sentiment_breakdown(responses: list[AgentResponse]) -> SentimentBreakdown`:
   - Count positive/neutral/negative
   - Calculate percentages
   - Return structured data for charts

4. Method `async generate_segment_analysis(responses: list[AgentResponse], product_description: str) -> list[SegmentData]`:
   - Group responses by customer segment
   - For each segment, use Claude to summarize the segment's reaction
   - Return per-segment insights

5. Method `extract_key_themes(responses: list[AgentResponse]) -> list[str]`:
   - Use Claude to identify the top 5-8 recurring themes across all responses
   - Return as a list of theme strings with brief descriptions

6. Method `async aggregate_all(responses: list[AgentResponse], product_description: str) -> InsightResults`:
   - Run all above methods (some can run in parallel)
   - Return complete InsightResults

### Task 3: Create Aggregation Prompt Templates
In `backend/app/prompts/`:

1. `aggregation_summary.txt`:
```
You are an expert market research analyst. You have collected feedback from {total_agents} real customers about a proposed product/change:

PRODUCT DESCRIPTION:
{product_description}

CUSTOMER RESPONSES:
{all_responses}

Provide a comprehensive executive summary including:
1. **Overall Reception**: What percentage appears positive vs negative? What's the general mood?
2. **Key Positive Themes**: What aspects excited customers most? (3-5 bullet points)
3. **Key Concerns**: What worried or turned off customers? (3-5 bullet points)
4. **Surprising Insights**: Any unexpected patterns or minority opinions worth noting?
5. **Recommended Actions**: Based on this feedback, what should the company do? (3-5 specific recommendations)

Be specific. Quote or paraphrase actual customer responses to support your points.
Format your response in clean markdown.
```

2. `segment_analysis.txt`:
```
Analyze how this specific customer segment reacted to the product:

SEGMENT: {segment_name} ({segment_count} customers)
PRODUCT: {product_description}

RESPONSES FROM THIS SEGMENT:
{segment_responses}

Provide:
1. Segment sentiment (positive/mixed/negative)
2. What this segment cares about most
3. Key quotes that represent this segment's view
4. Specific recommendation for targeting this segment

Keep it concise — 3-4 sentences per point.
```

### Task 4: Profiles Stats Endpoint
In `backend/app/routers/profiles.py`:
- `GET /api/profiles/stats` — Return summary stats: total profiles, segment distribution, age distribution, top categories
- This feeds the frontend's sidebar info

### Verification:
- Start the backend: `uvicorn app.main:app --reload --port 8000`
- Test SSE with curl: `curl -N http://localhost:8000/api/test/stream` (after POSTing a test)
- Verify agent responses stream one by one
- Verify aggregation produces meaningful insights
- Test with 10 agents first, then scale to 50 to check rate limiting
```

---

## Phase 4: Frontend — Testing Lab Page (The Minions Scene)

> **Goal:** Build the main page with chat sidebar and animated character crowd.
> **This is the "wow factor" phase. Spend the most time here.**

### Prompt:
```
Read CLAUDE.md and frontend/CLAUDE.md for context.
Read docs/HANDOFF.md for Phase 1-3 status.

## Phase 4: Build the Testing Lab Page

### Task 1: Layout Structure
In `src/app/page.tsx`:
- Full-height layout with two sections:
  - Left sidebar (width: 380px): Chat/input panel
  - Main area (remaining width): Minions crowd scene
- Use CSS Grid or Flexbox. Dark background (slate-900) for crowd scene, light for sidebar.

### Task 2: Chat Sidebar (`src/components/lab/ChatSidebar.tsx`)
- Header with app logo/name "CrowdTest" and tagline "Test ideas with your digital customers"
- A brief stats display: "198 customer agents ready" with small segment breakdown
- A text area for product description input (6 lines tall, placeholder text)
- Optional: a few quick-select category buttons (T-shirts, Pants, Dresses, Accessories)
- A big "Run Test" button with loading state
- Below the input, show a status feed:
  - "Deploying 198 agents..." (when test starts)
  - "42/198 agents responded..." (live counter)
  - "Generating insights..." (when aggregation starts)
  - Link to "View Full Insights →" when done

### Task 3: Character Component (`src/components/lab/Character.tsx`)
Create a simple SVG character. Keep it MINIMAL and charming:
```
- Body: rounded rectangle (~30x40px), random pastel color from a palette of 8 colors
- Eyes: two white circles with smaller black pupil circles
- Optional: tiny line mouth
- Each character has a slight random rotation (-5 to 5 degrees) for organic feel
- Idle animation: subtle up/down bobbing (2-3px) using Framer Motion, each with random delay so they're not synced
```

Props: id, color, position (x, y), isThinking (boolean), thoughtContent (string | null), sentiment (string | null)

### Task 4: Thought Bubble (`src/components/lab/ThoughtBubble.tsx`)
- Classic comic thought bubble shape (rounded rectangle with 3 small circles leading to character)
- Appears with Framer Motion animation: scale from 0 → 1 with slight bounce
- Contains 1-2 lines of text (max 60 chars, truncated with "...")
- Background color based on sentiment: green-100/green-700 text, yellow-100/yellow-700 text, red-100/red-700 text
- Fades out after 5 seconds to make room for new thoughts (or stays if paused)
- Positioned above the character

### Task 5: Crowd Scene (`src/components/lab/CrowdScene.tsx`)
- Container fills the main area with dark background
- Generate 30 characters at random positions (avoid overlap)
  - Use a grid-based placement with jitter for organic feel
  - Characters should be spread across the scene, denser in the middle
- Initial state: all characters idle, bobbing
- When test starts: characters start "thinking" one by one as SSE responses arrive
  - Pick a random character that hasn't shown a thought yet
  - Display their thought bubble for 5 seconds
  - After 5 seconds, reset that character and they can be used again
- Progress overlay: "{n}/198 responses" counter in top-right corner
- When all responses in: brief celebratory moment (characters could all bounce once, or a subtle particle effect)
- Then show "Insights Ready!" banner with link to insights page

### Task 6: SSE Hook (`src/hooks/useSSE.ts`)
- Custom hook that connects to the backend SSE endpoint
- Returns: { responses: AgentResponse[], isRunning, isComplete, error, totalCompleted }
- Handles connection lifecycle: open, message parsing, error, close
- Accumulates all responses for later use

### Task 7: Test Session Hook (`src/hooks/useTestSession.ts`)
- Manages the full test lifecycle
- `startTest(productDescription)` → POST to backend, then open SSE
- Stores all responses
- Tracks state: idle → running → aggregating → complete
- When complete, navigates to insights page OR shows link

### Task 8: API Client (`src/lib/api.ts`)
- `submitTest(description: string): Promise<{ test_id: string }>`
- `getResults(testId: string): Promise<InsightResults>`
- `getProfileStats(): Promise<ProfileStats>`
- Base URL from env var NEXT_PUBLIC_API_URL (default http://localhost:8000)

### Verification:
- Start frontend and backend together
- Enter a product description and click "Run Test"
- Watch characters animate with thought bubbles appearing one by one
- Verify sentiment colors are correct
- Verify progress counter updates
- Check that the experience feels smooth and visually appealing
- Test with a small batch first (set MAX_AGENTS=10 in .env for testing)
```

---

## Phase 5: Frontend — Insights Dashboard

> **Goal:** Build the insights page with charts, segments, and drill-down.

### Prompt:
```
Read CLAUDE.md and frontend/CLAUDE.md for context.
Read docs/HANDOFF.md for Phase 1-4 status.

## Phase 5: Build the Insights Dashboard

### Task 1: Page Layout (`src/app/insights/[testId]/page.tsx`)
- Fetch results from `GET /api/test/{testId}/results`
- Loading state while waiting for insights
- Layout:
  - Top: Product description that was tested + test metadata (date, agent count)
  - Main grid: 2 columns on desktop
    - Left (wider): Executive Summary + Segment Analysis
    - Right (narrower): Sentiment Chart + Key Themes
  - Bottom: Response Drill-Down (expandable)

### Task 2: Executive Summary (`src/components/insights/ExecutiveSummary.tsx`)
- Render the markdown summary from the aggregation
- Use a clean card with subtle left border accent color
- Key stats at top: Total agents, Response rate, Overall sentiment (with emoji: 😊/😐/😟)
- The markdown body rendered with proper formatting

### Task 3: Sentiment Chart (`src/components/insights/SentimentChart.tsx`)
- Use Recharts to create a donut/pie chart
- Three segments: Positive (green), Neutral (yellow), Negative (red)
- Center label: dominant sentiment + percentage
- Legend below with exact counts

### Task 4: Segment Analysis (`src/components/insights/SegmentAnalysis.tsx`)
- Accordion/expandable cards, one per segment
- Each card shows: segment name, count, overall sentiment badge
- Expanded: the segment-specific analysis text
- Sort segments by size (largest first)

### Task 5: Key Themes (`src/components/insights/ThemeExtractor.tsx`)
- Visual list of top themes as "tags" or "pills"
- Each theme with a brief description (1 line)
- Maybe color-coded by sentiment association

### Task 6: Response Drill-Down (`src/components/insights/ResponseDrillDown.tsx`)
- Searchable/filterable table of all 198 individual responses
- Columns: Agent Name, Age, Segment, Sentiment, Response (truncated)
- Click to expand and see full response
- Filter by: sentiment (positive/neutral/negative), segment
- Sort by: sentiment, age, segment

### Task 7: Navigation
- Add a "← Back to Lab" button on insights page
- Add a "View Insights →" link on the lab page (appears when test complete)
- Pass test_id through URL params

### Verification:
- Complete a full test run (can use small batch)
- Navigate to insights page
- Verify all sections render with real data
- Check charts display correctly
- Test drill-down search and filters
- Verify responsive layout looks good on laptop screen
```

---

## Phase 6: Integration, Polish & Edge Cases

> **Goal:** Connect everything end-to-end, handle errors, polish the UI.

### Prompt:
```
Read CLAUDE.md for context.
Read docs/HANDOFF.md for Phase 1-5 status.

## Phase 6: Integration & Polish

### Task 1: End-to-End Flow
Test the complete flow:
1. User opens app → sees Testing Lab with idle characters
2. User types product description → clicks "Run Test"
3. Backend creates test, starts 198 agents in parallel
4. SSE streams responses → characters animate with thought bubbles
5. Progress counter updates in real-time
6. When all agents done → "Generating insights..." status
7. Aggregation completes → "Insights Ready! View →" link
8. User clicks through → full insights dashboard loads

Fix any issues in this flow.

### Task 2: Error Handling
- Backend: if an agent call fails, skip it and continue (don't break the test)
- Frontend: if SSE connection drops, show reconnecting message
- If backend is unreachable, show friendly error on frontend
- Handle case where user refreshes during a test (reconnect to SSE or show results if done)

### Task 3: Loading States
- Skeleton loaders on insights page while data loads
- Smooth transitions between states on the lab page
- "Run Test" button shows spinner + disabled state while running
- Characters scene has a subtle loading indicator before test starts

### Task 4: Visual Polish
- Add subtle gradient or glow effects to the crowd scene background
- Make thought bubbles feel more natural with varied sizes
- Add a "pulse" effect to the Run Test button when idle (inviting the user to click)
- Ensure consistent spacing and typography across both pages
- Add the app name/logo in the top-left corner
- Footer or subtle branding

### Task 5: Demo-Ready Tweaks
- Pre-fill a compelling example product description in the input placeholder
- Add a "Try Example" button that fills in a pre-written product description
- Ensure the first-time experience is clear (what to do, what to expect)
- If running with fewer than 198 agents for demo (e.g., 50), make sure the crowd still looks full

### Task 6: Environment Configuration
- Make sure `.env.example` files are complete for both frontend and backend
- Add a `README.md` at root with quick setup instructions
- Test that `make dev` starts everything correctly

### Verification:
- Run the full flow 3 times with different product descriptions
- No errors in browser console or server logs
- UI feels smooth and professional
- The "wow factor" of the Minions scene is strong
- Insights are meaningful and well-formatted
```

---

## Phase 7: Demo Preparation

> **Goal:** Final optimizations and practice run for the hackathon presentation.

### Prompt:
```
Read CLAUDE.md for context.
Read docs/HANDOFF.md for Phase 1-6 status.

## Phase 7: Demo Preparation

### Task 1: Performance Optimization
- Pre-cache persona prompts so they're loaded at startup
- Verify 198 agents complete in under 2 minutes
- If too slow, reduce to 100 or 50 agents for demo and adjust UI accordingly
- Ensure SSE stream doesn't lag — responses should appear within 1 second of completing

### Task 2: Demo Script
Create `docs/DEMO_SCRIPT.md` with a step-by-step demo script:
1. Open the app — show the Testing Lab
2. Explain: "Each character represents a real customer profile built from actual data"
3. Type a product description (prepare 2-3 compelling examples)
4. Click Run Test — narrate what's happening as characters animate
5. When insights load — walk through the dashboard
6. Show drill-down into individual responses
7. Key talking points for each section

### Task 3: Backup Plan
- Prepare pre-computed results for 2-3 test scenarios in case of API failures
- Add a "demo mode" flag that uses cached results instead of live API calls
- This ensures the demo works even with bad WiFi

### Task 4: Final Checklist
- [ ] Both servers start without errors
- [ ] Full test with 198 agents completes successfully
- [ ] All UI components render correctly
- [ ] No console errors
- [ ] Insights are accurate and well-written
- [ ] Demo script is rehearsed
- [ ] Backup pre-computed results are ready
- [ ] .env files are configured
- [ ] One compelling 30-second pitch for what this product does
```

---

## Claude Code Best Practices Cheatsheet (Refer to during all phases)

### Before Each Phase
1. Start a new session or `/clear` context
2. Tell Claude to read `CLAUDE.md` first
3. Paste the phase prompt
4. Use Plan Mode (`Shift+Tab` twice) to review the plan before coding

### During Each Phase
- If Claude suggests an approach, review it before approving
- If context gets long, `/clear` and re-provide only what's needed
- Commit after each working milestone: `git add -A && git commit -m "Phase X: description"`
- If Claude gets confused, use `/clear` and paste a shorter, more focused prompt
- Run tests after every significant change

### After Each Phase
1. Run all verification steps from the phase
2. Commit to git: `git add -A && git commit -m "Complete Phase X"`
3. Update `docs/HANDOFF.md`
4. `/clear` before starting next phase

### Emergency Patterns
- **Claude is looping/stuck:** `/clear`, give it only the specific file and task
- **Build is broken:** Ask Claude to read the error output and fix just the error
- **Context too long:** `/compact` to summarize, or `/clear` and start fresh
- **Need to modify a previous phase:** Create a focused mini-prompt for just that change
