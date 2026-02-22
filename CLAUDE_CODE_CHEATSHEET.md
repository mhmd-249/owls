# Claude Code Hackathon Cheatsheet

## Essential Commands
| Command | What it does |
|---------|-------------|
| `/clear` | Wipe context. **Do this between every phase.** |
| `/compact` | Summarize context if getting long mid-phase |
| `Shift+Tab` (×2) | Plan Mode — Claude plans without coding. Use before each phase. |
| `/next-phase` | Custom command: loads next phase from IMPLEMENTATION_GUIDE |
| `/complete-phase` | Custom command: runs verification + updates HANDOFF.md |
| `Ctrl+C` | Stop Claude mid-response if it's going wrong |
| `claude --resume` | Resume the last session if terminal crashed |
| `claude --continue` | Continue the most recent conversation |

## The Golden Rules (from research)

### 1. Context is King
- CLAUDE.md is loaded every session — keep it concise and accurate
- `/clear` between phases to avoid context pollution
- If Claude starts making mistakes, context is probably too long → `/clear`

### 2. Plan Before Code
- Always use Plan Mode first for each phase
- Review the plan before approving implementation
- "Think of Claude as a fast junior dev who needs good direction"

### 3. Small Batches Win
- Don't paste the entire phase prompt if Claude struggles
- Break tasks into individual requests if needed
- Verify after each major component before moving on

### 4. Git is Your Safety Net
- Commit after every working milestone
- If Claude breaks something, `git stash` or `git checkout .`
- Branch per phase if you want extra safety: `git checkout -b phase-X`

### 5. Be Specific About What You Want
- ❌ "Make the UI look nice" 
- ✅ "Add Framer Motion fade-in to the thought bubble with 0.3s duration and backOut easing"
- ❌ "Fix the errors"
- ✅ "Read the error output from `npm run build` and fix the TypeScript errors in CrowdScene.tsx"

## When Things Go Wrong

### Claude is looping / repeating itself
→ `/clear`, then give it ONLY the specific file path and a focused task

### Build is broken
→ Run the build command, copy the error, paste it to Claude with "fix this error"

### Claude made a mess of a file
→ `git checkout -- path/to/file.tsx` to revert, then re-prompt with clearer instructions

### Context window is full
→ `/compact` first. If still bad, `/clear` and start the sub-task fresh.

### Claude isn't following CLAUDE.md rules
→ CLAUDE.md might be too long. Check if it exceeds ~100 lines. Trim if needed.

### API rate limits during agent testing
→ Reduce MAX_CONCURRENT_AGENTS in .env (try 20 instead of 50)

## Time Budget (2-Day Hackathon)

| Phase | Estimated Time | Priority |
|-------|---------------|----------|
| Pre-Phase: Setup | 30 min | Must |
| Phase 1: Data Pipeline | 1-2 hrs | Must |
| Phase 2: Agent Engine | 1-2 hrs | Must |
| Phase 3: SSE + Aggregation | 1-2 hrs | Must |
| Phase 4: Minions UI ⭐ | 3-4 hrs | Must (wow factor) |
| Phase 5: Insights Dashboard | 2-3 hrs | Must |
| Phase 6: Polish | 1-2 hrs | Should |
| Phase 7: Demo Prep | 1 hr | Must |

**Total: ~12-16 hours of Claude Code time**

⭐ = This is where the judges will be most impressed. Spend extra time here.

## Pro Tips for Speed

1. **Run multiple Claude Code instances** — one for frontend, one for backend (use VS Code split terminals)
2. **Pre-write your .env** file before starting so you're not hunting for keys
3. **Test with 5-10 agents** during development, only scale to 198 for the final demo
4. **Don't perfect early phases** — get them working, move on, polish in Phase 6
5. **Keep your H&M data clean** — garbage in = garbage out for persona quality
