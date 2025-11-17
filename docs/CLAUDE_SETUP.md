# Claude Mobile Setup Guide

Configure Claude on your iPhone to trigger local development tasks.

---

## Quick Start

**New**: We've created comprehensive LLM instructions you can copy/paste:

1. **For Claude Projects**: Use `../LLM_SYSTEM_PROMPT.md` (complete reference)
2. **For Custom Instructions**: Use `../LLM_CUSTOM_INSTRUCTIONS.md` (shorter)
3. **Testing Guide**: See `../LLM_INTEGRATION_TEST.md` to validate setup

This guide below provides the original manual setup process. For faster setup, just copy/paste the content from the files above into your Claude Project.

---

## Prerequisites

- Claude mobile app (iOS)
- Claude Pro subscription (recommended for Projects feature)
- Local webhook client running
- API key from your `.env` file

---

## Step 1: Get Your API Key

Your API key is in `.env`:

```bash
cat .env | grep API_KEY
```

Example: `qVaBlMjz5GODXoAdpOJs_Hl_y3HolOqSvnCJf-YcZok`

---

## Step 2: Create a Project (Recommended)

Projects allow you to set persistent context that Claude will always remember.

1. Open Claude app on iPhone
2. Tap **Projects** (folder icon)
3. Tap **+ New Project**
4. Name it: "Local Dev Tasks"
5. Add project knowledge

### Project Knowledge

```markdown
# Local Development Task System

I have a webhook system that executes tasks on my local development machine.

## Webhook Endpoint
- URL: https://web-production-3d53a.up.railway.app/webhook
- Method: POST
- Auth: X-API-Key header
- API Key: YOUR_API_KEY_HERE

## My Setup
- Default working directory: /Users/tim/gameplan.ai/ai-webhook
- Results viewer: http://localhost:5001

## When I Ask You To Execute Tasks

Send a webhook using this format:

```json
{
  "type": "task_command",
  "data": {
    "task_id": "unique_id_with_timestamp",
    "action_type": "git|shell|claude_code",
    "params": {
      "command": [...],
      "working_dir": "/Users/tim/gameplan.ai/ai-webhook",
      "timeout": 30
    }
  }
}
```

## Available Actions

1. **git**: Git commands
   - Example: `["git", "status"]`
   - Must start with "git"

2. **shell**: Shell commands
   - Example: `["ls", "-la"]` or `"echo test"`

3. **claude_code**: Claude Code CLI (if installed)
   - Example: `{"prompt": "Review latest changes"}`

## Response Format

After sending webhook:
1. Confirm what you sent
2. Remind me results at: http://localhost:5001
3. Be concise unless I ask for details
```

**Important**: Replace `YOUR_API_KEY_HERE` with your actual API key.

---

## Step 3: Test It

In the "Local Dev Tasks" project, say:

> "Check git status on my ai-webhook repo"

Claude should:
1. Send the webhook
2. Confirm what was sent
3. Remind you where to check results

---

## Alternative: Use Custom Instructions (No Project)

If not using Projects, add this to each conversation:

```
I have a local webhook system. When I ask you to execute local tasks, send a POST webhook to:

https://web-production-3d53a.up.railway.app/webhook

Headers:
- Content-Type: application/json
- X-API-Key: YOUR_API_KEY

Format:
{
  "type": "task_command",
  "data": {
    "task_id": "unique_id",
    "action_type": "git|shell|claude_code",
    "params": { "command": [...], "working_dir": "/path" }
  }
}

Results at: http://localhost:5001
```

---

## Example Conversations

### Git Status
**You**: "What's the status of my repo?"

**Claude**: "I'll check the git status for you."

*Sends webhook:*
```json
{
  "type": "task_command",
  "data": {
    "task_id": "git_status_20250117_1030",
    "action_type": "git",
    "params": {
      "command": ["git", "status"],
      "working_dir": "/Users/tim/gameplan.ai/ai-webhook"
    }
  }
}
```

**Claude**: "✅ Sent. Check results at http://localhost:5001"

---

### Recent Commits
**You**: "Show last 10 commits"

**Claude**: "I'll get the last 10 commits."

*Sends webhook:*
```json
{
  "type": "task_command",
  "data": {
    "task_id": "git_log_20250117_1031",
    "action_type": "git",
    "params": {
      "command": ["git", "log", "--oneline", "-10"],
      "working_dir": "/Users/tim/gameplan.ai/ai-webhook"
    }
  }
}
```

---

### Run Shell Command
**You**: "List files in my project"

**Claude**: "I'll list the files."

*Sends webhook:*
```json
{
  "type": "task_command",
  "data": {
    "task_id": "ls_20250117_1032",
    "action_type": "shell",
    "params": {
      "command": ["ls", "-la"],
      "working_dir": "/Users/tim/gameplan.ai/ai-webhook"
    }
  }
}
```

---

## Manual Testing

Test webhooks manually to verify setup:

```bash
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "type": "task_command",
    "data": {
      "task_id": "manual_test_001",
      "action_type": "git",
      "params": {
        "command": ["git", "status"],
        "working_dir": "/Users/tim/gameplan.ai/ai-webhook"
      }
    }
  }'
```

Check results:
```bash
open http://localhost:5001
```

---

## Advanced: Shortcuts Integration

Create iOS Shortcut to send webhooks directly:

1. Open **Shortcuts** app
2. Create new shortcut: "Git Status"
3. Add action: **Get Contents of URL**
   - URL: `https://web-production-3d53a.up.railway.app/webhook`
   - Method: POST
   - Headers:
     - `Content-Type`: `application/json`
     - `X-API-Key`: `YOUR_API_KEY`
   - Request Body: JSON from examples above

4. Add to Siri: "Hey Siri, git status"

---

## Troubleshooting

### Claude doesn't send webhook

Claude may not always have access to make HTTP requests. Try:

1. Explicitly say "send a webhook to..."
2. Use Shortcuts app instead
3. Send manually via curl (see examples)

### Results not showing

1. Verify webhook client is running: `ps aux | grep client.py`
2. Check API key is correct
3. View webhook logs: `ls -la webhook_logs/`

### Wrong working directory

Update project knowledge with your actual paths:
```
Default working directory: /your/actual/path
```

---

## Best Practices

### 1. Use Descriptive Task IDs
```
✅ "git_status_myproject_20250117_1030"
❌ "task1"
```

### 2. Specify Working Directory
Always include `working_dir` in params to avoid ambiguity.

### 3. Set Appropriate Timeouts
- Git/ls commands: 30 seconds
- Tests: 120 seconds
- Complex operations: 300+ seconds

---

## Next Steps

- **View Results**: http://localhost:5001
- **Action Reference**: [LLM_ACTIONS.md](./LLM_ACTIONS.md)
- **Examples**: [../examples/](../examples/)

---

**Last Updated**: 2025-01-17
