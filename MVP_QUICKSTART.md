# MVP Quick Start Guide

Get the Voice LLM → Local Action system running in 5 minutes.

## What is This?

Trigger local development tasks (git, shell, Claude Code) from your phone using voice LLMs like ChatGPT or Claude.

**Example**:
> "Hey Claude, check git status on my repo"
>
> → Task executes locally → Results at http://localhost:5001

---

## Prerequisites

- Python 3.7+
- Git repository (for testing)
- WiFi (for webhook connection)

---

## 1. Setup (One-time, 2 minutes)

### Clone Repository
```bash
cd ~/projects  # or wherever you keep projects
git clone <repo-url>
cd ai-webhook
```

### Configure Environment
```bash
# Copy example config
cp .env.example .env

# Edit with your editor
nano .env
```

**Update these lines in `.env`**:
```bash
# Change from 'postgres' to 'sqlite'
STORAGE_BACKEND=sqlite

# Add SQLite path (or keep default)
SQLITE_PATH=./tasks.db
```

**Your API key is already set** - it's in the `.env.example` file. You can use that or generate a new one:
```bash
# Optional: Generate new API key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Then update API_KEY in .env
```

### Install Dependencies
```bash
pip3 install websockets python-dotenv flask
```

---

## 2. Start MVP (30 seconds)

```bash
./start_mvp.sh
```

**You should see**:
```
========================================
✅ MVP is running!
========================================

📊 Services:
   • Webhook Client: PID 12345
   • Results Viewer: http://localhost:5001

🧪 Test it:
   curl -X POST https://web-production-3d53a.up.railway.app/webhook \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-api-key" \
     -d @examples/git_status.json
```

**Leave this terminal running** - it's your webhook client.

---

## 3. Test It (1 minute)

### Option A: Manual Test (Recommended First)

Open a **new terminal** and run:

```bash
# Load your API key
source .env

# Send test webhook
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d @examples/git_status.json
```

**Expected**:
```json
{
  "status": "ok",
  "message": "Webhook received",
  "clients_notified": 1
}
```

**Check results**:
```bash
open http://localhost:5001
```

You should see your `git status` task with output!

---

### Option B: Voice LLM Test

See setup guides for your preferred LLM:
- [ChatGPT Setup](docs/CHATGPT_SETUP.md)
- [Claude Setup](docs/CLAUDE_SETUP.md) ⭐ Recommended
- [Gemini Setup](docs/GEMINI_SETUP.md)

---

## 4. Use It

### Common Commands

**Check git status**:
```bash
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d @examples/git_status.json
```

**View recent commits**:
```bash
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d @examples/git_log.json
```

**Custom command**:
```bash
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "type": "task_command",
    "data": {
      "task_id": "my_task_001",
      "action_type": "shell",
      "params": {
        "command": "echo \"Hello from mobile!\""
      }
    }
  }'
```

**View results**:
```bash
# Web UI
open http://localhost:5001

# API
curl http://localhost:5001/api/task/git_status_001
```

---

## 5. Stop It

When done:
```bash
./stop_mvp.sh
```

**Restart anytime**:
```bash
./start_mvp.sh
```

---

## Troubleshooting

### "Connection refused" when testing
- Is `./start_mvp.sh` running? Check terminal output.
- Wait 5 seconds after starting, then try again.

### Tasks not showing in results viewer
- Check client logs: `tail -f client_output.log`
- Verify webhook client is connected (look for "✅ Connected")
- Check task ID matches between webhook and viewer

### "API_KEY not set"
- Run: `cat .env | grep API_KEY`
- Should show your API key
- If empty, copy from `.env.example`

### Results viewer shows empty
- Did you send a webhook yet? Try manual test first.
- Check database exists: `ls -la tasks.db`
- Check logs: `tail -f results_server.log`

---

## File Structure

After setup, you'll have:

```
ai-webhook/
├── client/
│   ├── storage/sqlite_backend.py  # Database layer
│   ├── task_executor.py           # Executes tasks
│   ├── results_server.py          # Web viewer (:5001)
│   ├── templates/tasks.html       # Results UI
│   └── client.py                  # Webhook client
├── docs/
│   ├── LLM_ACTIONS.md             # Action reference
│   ├── CHATGPT_SETUP.md           # ChatGPT guide
│   ├── CLAUDE_SETUP.md            # Claude guide
│   └── GEMINI_SETUP.md            # Gemini guide
├── examples/
│   ├── git_status.json            # Example webhooks
│   └── ...
├── start_mvp.sh                   # Start script
├── stop_mvp.sh                    # Stop script
├── test_mvp.py                    # Test suite
├── tasks.db                       # SQLite database (created on first run)
└── .env                           # Your configuration
```

---

## Next Steps

### For Daily Use

1. **Start on boot** (optional):
   ```bash
   # Add to ~/.zshrc or ~/.bashrc
   alias start-tasks='cd ~/projects/ai-webhook && ./start_mvp.sh'
   ```

2. **Create shortcuts**:
   - Add iOS Shortcuts for common tasks
   - See [CLAUDE_SETUP.md](docs/CLAUDE_SETUP.md#shortcuts-integration)

3. **Monitor usage**:
   ```bash
   # View recent tasks
   sqlite3 tasks.db "SELECT id, command, status FROM tasks ORDER BY created_at DESC LIMIT 10;"
   ```

### Learn More

- **Action Types**: [docs/LLM_ACTIONS.md](docs/LLM_ACTIONS.md)
- **Full Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Validation Plan

**After 1 week of use**, ask yourself:

1. Did I actually use it 10+ times?
2. Was it faster than alternatives (SSH, Shortcuts, Claude Desktop)?
3. Which action types were most valuable?
4. What would make this indispensable?

**If valuable** → Build Phase 2 (real-time notifications, push results back to LLM)

**If not** → Archive and learn. MVP validated the concept wasn't worth pursuing.

---

## Support

**Issues**: Check logs first
```bash
# Client logs
tail -f client_output.log

# Results server logs
tail -f results_server.log

# Webhook logs
ls -la webhook_logs/
```

**Run tests**:
```bash
python3 test_mvp.py
```

**Documentation**:
- [LLM Actions Reference](docs/LLM_ACTIONS.md)
- [Architecture Overview](ARCHITECTURE.md)

---

**Happy hacking!** 🚀

---

**Created**: 2025-01-17
**Status**: MVP Ready for Testing
