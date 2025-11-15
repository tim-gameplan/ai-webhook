# Contributing to AI Webhook Relay

Welcome! This guide will help you get started as a new engineer on this project.

## Table of Contents

1. [Project Overview](#project-overview)
2. [First-Time Setup](#first-time-setup)
3. [Understanding the Task System](#understanding-the-task-system)
4. [Working on a Task](#working-on-a-task)
5. [Testing Your Changes](#testing-your-changes)
6. [Submitting Your Work](#submitting-your-work)
7. [Important Documentation](#important-documentation)
8. [Getting Help](#getting-help)

---

## Project Overview

**What is this?** A webhook relay system that lets local machines receive GitHub webhook events in real-time.

**Architecture:**
```
GitHub Event → Railway Server (FastAPI) → WebSocket → Local Client (Python)
```

**Key Components:**
- **`app.py`** - FastAPI server that receives webhooks and broadcasts via WebSocket
- **`client/client.py`** - Local client that connects to server and processes events
- **`tasks/`** - Local task management (not in git)
- **`docs/`** - Documentation, deployment guides, worklogs

**Tech Stack:**
- Python 3.9+
- FastAPI (server)
- WebSockets (real-time communication)
- Railway (deployment)
- HMAC-SHA256 (webhook security)

---

## First-Time Setup

### 1. Clone the Repository

```bash
git clone https://github.com/tim-gameplan/ai-webhook.git
cd ai-webhook
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate  # On Windows

# Install server dependencies
pip install -r requirements.txt

# Install client dependencies
cd client
pip install -r requirements.txt
cd ..
```

### 3. Verify Installation

```bash
# Run server locally
python app.py
# Should see: "Application startup complete"
# Server runs on http://localhost:8000

# In another terminal, test health endpoint
curl http://localhost:8000/
# Should return: {"status": "running", "service": "github-webhook-relay", ...}
```

### 4. Set Up Task Directory

The `tasks/` directory is local-only (not tracked in git):

```bash
# Create tasks directory
mkdir -p tasks/archive

# Copy task convention docs from someone on the team
# These define how we name and structure tasks
```

### 5. Understand Current Deployment

**Production Server:** https://web-production-3d53a.up.railway.app
- Deployed on Railway
- Connected to GitHub webhook on `tim-gameplan/ai-webhook` repo
- Environment variables: `GITHUB_WEBHOOK_SECRET`, `API_KEY`, `PORT`, `ENVIRONMENT`

**Test the production server:**
```bash
curl https://web-production-3d53a.up.railway.app/
```

---

## Understanding the Task System

### Task Naming Convention

Tasks follow this format: `<category>-<number>-<brief-description>.md`

**Categories:**
- `security` - Security enhancements
- `feature` - New features
- `bugfix` - Bug fixes
- `devops` - Infrastructure/deployment
- `docs` - Documentation
- `refactor` - Code refactoring
- `test` - Testing improvements
- `perf` - Performance optimization

**Examples:**
- `security-001-enable-github-webhook-signature.md`
- `feature-005-add-slack-integration.md`
- `bugfix-003-fix-websocket-reconnection.md`

### Task Structure

Each task file contains:
- **Category & Priority** - What type of work, how urgent
- **Estimated Time** - How long it should take
- **Description** - What needs to be done and why
- **Acceptance Criteria** - How we know it's done
- **Implementation Steps** - Specific steps to follow
- **Testing** - How to verify it works
- **Rollback Plan** - How to undo if needed
- **Related Tasks** - Dependencies

### Finding Available Tasks

Check `tasks/INDEX.md` for a quick lookup of all active tasks:
- See task status (active, blocked, completed)
- Filter by category
- View priorities and time estimates

Ask your team lead which task to pick up!

---

## Working on a Task

### Step 1: Read the Task File

```bash
# Example: You're assigned security-004-add-rate-limiting
cat tasks/security-004-add-rate-limiting.md
```

Read through:
- Description and context
- Acceptance criteria (these are your success metrics)
- Implementation steps
- Testing requirements

### Step 2: Create Feature Branch

Branch naming follows: `<category>/<number>-<brief-description>`

```bash
# For task: security-004-add-rate-limiting.md
git checkout main
git pull origin main
git checkout -b security/004-add-rate-limiting
```

### Step 3: Implement Changes

Follow the implementation steps in the task file:
- Make small, focused commits
- Write clear commit messages
- Reference the task number in commits

```bash
# Example commits
git commit -m "feat: add rate limiting middleware"
git commit -m "test: add rate limiting tests for security-004"
git commit -m "docs: update SECURITY_SETUP.md with rate limiting info"
```

### Step 4: Update Documentation

If your changes affect:
- **Setup/deployment** → Update `README.md` or `CLAUDE.md`
- **Security** → Update `SECURITY_SETUP.md`
- **API** → Update relevant docs in `docs/`
- **Future work** → Consider adding to `FUTURE_TASKS.md`

---

## Testing Your Changes

### Local Testing

**1. Test Server Changes:**
```bash
# Start server with your changes
python app.py

# In another terminal, run manual tests
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: ping" \
  -d '{"test": "data"}'
```

**2. Test Client Changes:**
```bash
# Start local server in one terminal
python app.py

# Start client in another terminal
cd client
export RELAY_SERVER_URL="ws://localhost:8000/ws"
python client.py
```

**3. Test Integration:**
```bash
# With both server and client running...

# Send test webhook
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -d '{
    "ref": "refs/heads/main",
    "repository": {"name": "test-repo"}
  }'

# Check client terminal - should receive and log the event
```

### Security Testing

If your task involves security:

**1. Test unauthorized requests:**
```bash
# Should return 401 Unauthorized
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"unauthorized": true}'
```

**2. Test with API key:**
```bash
# Should return 200 OK
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-test-key" \
  -d '{"authorized": true}'
```

**3. Test signature verification:**
```python
# Use Python to generate valid HMAC signature
import hmac
import hashlib

secret = "your-secret"
payload = b'{"test": "data"}'
signature = "sha256=" + hmac.new(
    secret.encode(),
    payload,
    hashlib.sha256
).hexdigest()

# Then use signature in curl with -H "X-Hub-Signature-256: $signature"
```

### Acceptance Criteria Checklist

Before considering your task complete, verify ALL acceptance criteria from the task file are met:

- [ ] All implementation steps completed
- [ ] All tests passing
- [ ] Documentation updated
- [ ] No security vulnerabilities introduced
- [ ] Code follows existing patterns in the codebase
- [ ] Local testing successful

---

## Submitting Your Work

### Step 1: Self-Review

```bash
# Review all your changes
git diff main

# Check for:
# - Debugging code left in (console.log, print statements)
# - Commented-out code
# - Hardcoded values that should be environment variables
# - Missing error handling
```

### Step 2: Commit and Push

```bash
# Ensure all changes committed
git status

# Push your feature branch
git push origin security/004-add-rate-limiting
```

### Step 3: Create Pull Request

1. Go to GitHub repository
2. Click "Compare & pull request"
3. Use this PR template:

```markdown
## Task: security-004-add-rate-limiting

### Summary
Added rate limiting middleware to prevent abuse of webhook endpoint.

### Changes
- Added rate limiting using slowapi library
- Configured 100 requests per hour per IP
- Added rate limit headers to responses
- Updated SECURITY_SETUP.md with rate limiting documentation

### Testing
- [x] Manual testing with >100 requests
- [x] Verified 429 status returned after limit exceeded
- [x] Verified rate limit headers present
- [x] All existing tests still pass

### Acceptance Criteria
- [x] Rate limiting enabled on /webhook endpoint
- [x] Configurable via environment variables
- [x] Returns 429 with appropriate headers
- [x] Documentation updated

### Rollback Plan
If issues arise:
1. Revert commit [commit-hash]
2. Or disable via RATE_LIMIT_ENABLED=false env var
```

### Step 4: Request Review

- Tag your team lead for review
- Address any feedback
- Make requested changes in additional commits

### Step 5: Merge and Cleanup

After PR approval:

```bash
# Merge via GitHub UI, then locally:
git checkout main
git pull origin main
git branch -d security/004-add-rate-limiting

# Archive the task file
mv tasks/security-004-*.md tasks/archive/

# Optional: Create completion documentation
cp tasks/archive/security-004-add-rate-limiting.md \
   tasks/archive/security-004-COMPLETED.md
# Add completion notes, challenges faced, lessons learned
```

---

## Important Documentation

**Essential Reading:**
- `README.md` - Quick start and basic usage
- `CLAUDE.md` - Architecture details, development commands, code patterns
- `tasks/TASKS_CONVENTION.md` - Complete task system guide
- `SECURITY_SETUP.md` - Security configuration and testing

**Reference Documentation:**
- `docs/deployment/railway-github-webhook-setup.md` - Deployment guide
- `docs/worklogs/` - Historical development logs
- `FUTURE_TASKS.md` - Roadmap of planned improvements

**For Claude Code Users:**
Claude Code instances working in this repo automatically read `CLAUDE.md` for context.

---

## Getting Help

### Common Issues

**1. "Module not found" errors**
```bash
# Make sure you're in virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**2. "Connection refused" when testing client**
```bash
# Make sure server is running first
python app.py
# Then start client in another terminal
```

**3. "Signature verification failed" during testing**
```bash
# Set the webhook secret as environment variable
export GITHUB_WEBHOOK_SECRET="your-secret"
python app.py
```

**4. Railway deployment fails**
- Check Railway logs: Railway Dashboard → Deployments → View Logs
- Verify environment variables are set correctly
- Ensure latest code is pushed to `main` branch

### Resources

- **GitHub Repository:** https://github.com/tim-gameplan/ai-webhook
- **Production Server:** https://web-production-3d53a.up.railway.app
- **Railway Dashboard:** https://railway.app/dashboard

### Ask Your Team

If you're stuck:
1. Check existing documentation first
2. Look for similar patterns in the codebase
3. Ask in team chat with:
   - What you're trying to do
   - What you've tried
   - Error messages or unexpected behavior
   - Relevant code snippets

---

## Development Tips

### Code Style

Follow existing patterns in the codebase:
- Use type hints: `def verify_signature(payload: bytes, signature: str) -> bool:`
- Use descriptive variable names
- Add docstrings to functions
- Use f-strings for string formatting

### Git Workflow

```bash
# Always start from latest main
git checkout main
git pull origin main

# Create feature branch
git checkout -b category/number-description

# Make small, focused commits
git add specific_file.py
git commit -m "feat: add specific feature"

# Push regularly
git push origin category/number-description
```

### Environment Variables

Never commit secrets! Use environment variables:
```python
# Good
SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")

# Bad
SECRET = "hardcoded-secret-value"  # Never do this!
```

### Debugging

Add descriptive logging:
```python
# Use emoji for visual scanning in logs
print("✅ Webhook signature verified")
print("❌ Webhook rejected: Invalid signature")
print("⚠️  WARNING: GITHUB_WEBHOOK_SECRET not set")
```

### Testing Webhooks Locally

Use ngrok to expose local server for GitHub webhooks:
```bash
# Install ngrok, then:
ngrok http 8000

# Use the https URL in GitHub webhook settings
# Webhooks will reach your local machine!
```

---

**Welcome to the team! 🚀**

*Last updated: November 14, 2025*
