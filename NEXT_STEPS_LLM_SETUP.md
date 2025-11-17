# Next Steps: LLM Setup

**Status**: MVP is running ✅
**Next**: Configure your LLM to use it

---

## What Just Got Created

Three new documents to seed LLMs with system knowledge:

1. **LLM_SYSTEM_PROMPT.md** - Complete reference (for Claude Projects, no char limit)
2. **LLM_CUSTOM_INSTRUCTIONS.md** - Short versions (for ChatGPT, 1500 char limit)
3. **LLM_INTEGRATION_TEST.md** - 5 tests to validate it works

---

## Quick Setup (5 minutes)

### Option A: Claude Mobile (Recommended)

1. Open Claude app on iPhone
2. Tap **Projects** → **+ New Project**
3. Name it: "Local Dev Tasks"
4. **Copy/paste** the entire content of `LLM_SYSTEM_PROMPT.md` into Project Knowledge
5. Done! Try: "Check git status on my repo"

### Option B: ChatGPT Mobile

1. Open ChatGPT app on iPhone
2. Tap profile → **Settings** → **Custom Instructions**
3. **Copy/paste** the "Full Version" from `LLM_CUSTOM_INSTRUCTIONS.md` (1,450 chars)
4. Done! Try: "Check git status on my repo"

### Option C: This Claude Code Session

You can test the system right now in this conversation:

**Try saying**: "Check the git status on my repo at /Users/tim/gameplan.ai/ai-webhook"

I should send a webhook and tell you to check http://localhost:5001 for results.

---

## Validation (10 minutes)

After setting up your LLM, run through `LLM_INTEGRATION_TEST.md`:

**5 Quick Tests**:
1. "Check git status on my repo" → Should trigger webhook
2. "Show me my last 5 commits" → Should get git log
3. "List Python files in my project" → Should run find command
4. "What git branch am I on?" → Should get current branch
5. "Run git status in /nonexistent/directory" → Should fail gracefully

**Success**: All 5 tasks appear at http://localhost:5001

---

## Files Reference

| File | Purpose | Character Count |
|------|---------|-----------------|
| `LLM_SYSTEM_PROMPT.md` | Complete reference with all details | ~8,500 chars |
| `LLM_CUSTOM_INSTRUCTIONS.md` | Short versions for char limits | 650-1,450 chars |
| `LLM_INTEGRATION_TEST.md` | Test suite to validate setup | N/A |
| `docs/CLAUDE_SETUP.md` | Claude-specific setup guide | N/A |
| `docs/CHATGPT_SETUP.md` | ChatGPT-specific setup guide | N/A |

---

## What's In the Instructions

The LLM instructions include:

✅ Webhook endpoint and API key
✅ Request format for all action types
✅ Git command examples (status, log, diff, branch)
✅ Shell command examples (ls, find, df)
✅ Claude Code integration
✅ Working directory defaults
✅ Task ID conventions
✅ Safety guidelines (no destructive commands)
✅ Error handling guidance
✅ Response expectations

---

## Quick Test (Right Now)

Want to test immediately? Try this:

**Say to me (Claude Code)**:
> "Check the git status on my repo"

I should recognize the webhook format and send a POST request to your relay server.

**Then check**:
```bash
# View results
open http://localhost:5001

# Or via API
curl http://localhost:5001/api/tasks | jq
```

---

## Common Issues

**LLM doesn't send webhook, just talks about it**:
- Re-paste the custom instructions
- Say: "Actually send the webhook, don't just describe it"
- Claude Projects work better than ChatGPT custom instructions

**Webhook sent but no results**:
- Check MVP is running: `ps aux | grep client.py`
- Check logs: `tail -f client_output.log`
- Restart: `./stop_mvp.sh && ./start_mvp.sh`

**Wrong API key error**:
- Get current key: `cat .env | grep API_KEY`
- Update custom instructions with correct key

---

## Example Mobile Flow

**You (via voice)**: "Hey Claude, check git status on my repo"

**Claude**: "I'll check the git status on your repository.

[Sends webhook]

✅ Git status check has been triggered. You can view the results at http://localhost:5001.

Task ID: git_status_001"

**You**: Opens Safari → http://localhost:5001 → Sees git status output

**Total time**: ~10 seconds

---

## Files Location

All new files are in the root directory:

```
ai-webhook/
├── LLM_SYSTEM_PROMPT.md          ← Complete reference
├── LLM_CUSTOM_INSTRUCTIONS.md    ← Short versions
├── LLM_INTEGRATION_TEST.md       ← Test suite
├── docs/
│   ├── CLAUDE_SETUP.md           ← Updated with quick start
│   └── CHATGPT_SETUP.md          ← Updated with quick start
```

---

## Recommended Path

1. **Now** (2 min): Test with me in this Claude Code session
2. **Today** (5 min): Setup Claude mobile app with LLM_SYSTEM_PROMPT.md
3. **Today** (10 min): Run LLM_INTEGRATION_TEST.md (5 tests)
4. **This week**: Use it 10+ times from mobile
5. **Next week**: Decide if Phase 2 is worth building

---

## Ready to Test?

Try saying:
- "Check the git status on my repo"
- "Show me my recent commits"
- "List the Python files in my project"

I should send webhooks and tell you to check http://localhost:5001 for results!

---

**Created**: 2025-11-17
**Status**: Ready for LLM Integration
