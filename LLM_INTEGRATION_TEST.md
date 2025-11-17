# LLM Integration Test Guide

**Purpose**: Verify your LLM (ChatGPT, Claude, etc.) can successfully send webhooks to trigger local tasks.

---

## Prerequisites

1. ✅ MVP is running: `./start_mvp.sh`
2. ✅ LLM has been configured with system prompt/custom instructions
   - See: `LLM_CUSTOM_INSTRUCTIONS.md` or `LLM_SYSTEM_PROMPT.md`

---

## Test 1: Simple Git Status (2 minutes)

### What to Say to Your LLM

```
Can you check the git status on my repo?
```

### Expected LLM Behavior

The LLM should:
1. Recognize this as a git command request
2. Send a webhook to the endpoint
3. Tell you the webhook was sent
4. Remind you to check http://localhost:5001 for results

### Expected LLM Response (example)

```
I'll check the git status on your repo.

[Sends webhook]

✅ Command triggered! You can view the results at http://localhost:5001

The git status task has been sent to your local machine.
```

### Verify Success

**Check results viewer**:
```bash
open http://localhost:5001
```

**Or check via API**:
```bash
curl http://localhost:5001/api/task/git_status_001 | jq .status
# Should return: "completed"
```

**Or check database**:
```bash
sqlite3 tasks.db "SELECT id, status FROM tasks WHERE id LIKE 'git_status%' ORDER BY created_at DESC LIMIT 1;"
# Should show: git_status_001|completed
```

**✅ Test passes if**: Task appears in results viewer with status "completed"

---

## Test 2: View Recent Commits (2 minutes)

### What to Say

```
Show me my last 5 commits
```

### Expected LLM Action

Send webhook with:
- `action_type`: `"git"`
- `command`: `["git", "log", "--oneline", "-5"]`

### Verify Success

Check http://localhost:5001 - should see task with recent commit history in output.

**✅ Test passes if**: Commit history is visible in task output

---

## Test 3: List Files (2 minutes)

### What to Say

```
Can you list the Python files in my project?
```

### Expected LLM Action

Send webhook with:
- `action_type`: `"shell"`
- `command`: `"find . -name '*.py' -type f | head -10"` or similar

### Verify Success

Check http://localhost:5001 - should see list of .py files.

**✅ Test passes if**: Python files are listed in task output

---

## Test 4: Check Current Branch (2 minutes)

### What to Say

```
What git branch am I on?
```

### Expected LLM Action

Send webhook with:
- `action_type`: `"git"`
- `command`: `["git", "branch", "--show-current"]`

### Verify Success

Check http://localhost:5001 - should see current branch name (e.g., "main").

**✅ Test passes if**: Branch name is visible

---

## Test 5: Error Handling (2 minutes)

### What to Say

```
Run git status in /nonexistent/directory
```

### Expected LLM Action

Send webhook with invalid `working_dir`.

### Expected Result

Task should fail gracefully with error message in results viewer.

**✅ Test passes if**: Task shows status "failed" with error message explaining the directory doesn't exist

---

## Troubleshooting

### LLM Doesn't Send Webhook

**Symptoms**: LLM just talks about what it would do, doesn't actually send request

**Fixes**:
1. Re-paste custom instructions/system prompt
2. Explicitly say: "Actually send the webhook request, don't just describe it"
3. Try a different LLM (Claude Projects work better than ChatGPT custom instructions)

### Webhook Sent But No Results

**Symptoms**: LLM says webhook sent, but nothing in results viewer

**Check**:
```bash
# Is MVP running?
ps aux | grep -E 'client.py|results_server.py'

# Check client logs
tail -20 client_output.log

# Check database
sqlite3 tasks.db "SELECT COUNT(*) FROM tasks;"
```

**Fixes**:
1. Restart MVP: `./stop_mvp.sh && ./start_mvp.sh`
2. Check API key matches in webhook and .env
3. Check relay server is reachable: `curl https://web-production-3d53a.up.railway.app/`

### Wrong API Key

**Symptoms**: Webhook returns 401 or 403

**Fix**:
1. Check `.env` file: `cat .env | grep API_KEY`
2. Update custom instructions with correct key
3. Resend webhook

### Task Stays "Pending"

**Symptoms**: Task created but never completes

**Check**:
```bash
# Client logs
tail -30 client_output.log

# Look for errors
grep -i error client_output.log
```

**Common causes**:
- Client not connected to relay server
- Task executor crashed
- Invalid command syntax

---

## Validation Checklist

After running all 5 tests:

- [ ] Test 1: Git status ✅
- [ ] Test 2: Recent commits ✅
- [ ] Test 3: List files ✅
- [ ] Test 4: Current branch ✅
- [ ] Test 5: Error handling ✅

**If all pass**: Your LLM integration is working! 🎉

**If any fail**: See troubleshooting section above

---

## Example Conversation Transcript

Here's what a successful conversation looks like:

**You**: "Can you check the git status on my repo?"

**LLM**: "I'll check the git status on your repository.

[Sends POST to https://web-production-3d53a.up.railway.app/webhook]

✅ Git status check has been triggered on your local machine. You can view the results at http://localhost:5001.

The task ID is `git_status_001`."

**You** (after checking results): "Great! Now show me the last 5 commits"

**LLM**: "I'll retrieve your last 5 commits.

[Sends webhook for git log]

✅ Commit history retrieval triggered. Check http://localhost:5001 for the results.

Task ID: `git_log_001`"

---

## Advanced: Testing from Mobile

Once desktop testing works, test from mobile:

1. Open mobile LLM app (ChatGPT, Claude)
2. Say (via voice): "Check git status on my repo"
3. Wait 5-10 seconds
4. Open http://localhost:5001 on your Mac
5. Verify task completed

**Note**: Results viewer must be on same WiFi network or use ngrok/tunneling.

---

## Next Steps After Validation

**If all tests pass**:
- Start using it for real tasks!
- Track usage over 1 week
- Note: frequency, usefulness, common actions

**If tests fail**:
- Review troubleshooting section
- Check logs: `client_output.log`, `results_server.log`
- Verify MVP is running: `ps aux | grep client.py`

---

## Quick Debugging Commands

```bash
# Check MVP status
ps aux | grep -E 'client.py|results_server.py'

# View recent tasks
sqlite3 tasks.db "SELECT id, status, created_at FROM tasks ORDER BY created_at DESC LIMIT 5;"

# Check client logs
tail -30 client_output.log

# Check results server logs
tail -30 results_server.log

# Restart MVP
./stop_mvp.sh && ./start_mvp.sh
```

---

**Last Updated**: 2025-11-17
**Status**: Ready for Testing
