# ChatGPT Mobile Setup Guide

Configure ChatGPT on your iPhone to trigger local development tasks.

## Prerequisites

- ChatGPT mobile app (iOS)
- ChatGPT Plus subscription (required for custom instructions)
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

## Step 2: Add Custom Instructions

1. Open ChatGPT app on iPhone
2. Tap your profile icon (bottom right)
3. Tap **Settings**
4. Tap **Personalization**
5. Tap **Custom instructions**
6. Enable **Custom instructions**

### What would you like ChatGPT to know about you?

```
I'm a developer who uses a local webhook system to execute tasks on my development machine remotely.

When I ask you to execute local tasks (like checking git status, running commands, or reviewing code), send a webhook to:

Endpoint: https://web-production-3d53a.up.railway.app/webhook
Method: POST
Headers:
  Content-Type: application/json
  X-API-Key: YOUR_API_KEY_HERE

The webhook format is:
{
  "type": "task_command",
  "data": {
    "task_id": "unique_id",
    "action_type": "git|shell|claude_code",
    "params": { ... }
  }
}

My default working directory: /Users/tim/gameplan.ai/ai-webhook
```

**Important**: Replace `YOUR_API_KEY_HERE` with your actual API key.

### How would you like ChatGPT to respond?

```
When I ask you to execute local development tasks, immediately send the appropriate webhook and confirm what you sent.

Be concise. Don't explain unless I ask.

For task results, remind me to check: http://localhost:5001
```

---

## Step 3: Test It

Say to ChatGPT:

> "Check git status on my ai-webhook repo"

ChatGPT should respond with something like:

> "I've sent a webhook to check git status. You can view results at http://localhost:5001"

Then ChatGPT will attempt to send:

```json
{
  "type": "task_command",
  "data": {
    "task_id": "git_status_001",
    "action_type": "git",
    "params": {
      "command": ["git", "status"],
      "working_dir": "/Users/tim/gameplan.ai/ai-webhook"
    }
  }
}
```

---

## Example Prompts

### Check Repository Status
> "What's the git status?"

### View Recent Commits
> "Show me the last 5 commits"

### Run a Command
> "Run 'echo hello' on my local machine"

### Check Disk Space
> "How much disk space do I have?"

---

## Troubleshooting

### ChatGPT Says "I can't send webhooks"

ChatGPT's ability to send webhooks may be limited or unavailable. Try:

1. Use ChatGPT with Actions (requires ChatGPT Team/Enterprise)
2. Use Claude instead (see [CLAUDE_SETUP.md](./CLAUDE_SETUP.md))
3. Send webhooks manually via curl (see examples below)

### Manual Webhook Testing

Test the webhook directly:

```bash
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "type": "task_command",
    "data": {
      "task_id": "test_001",
      "action_type": "git",
      "params": {
        "command": ["git", "status"],
        "working_dir": "/Users/tim/gameplan.ai/ai-webhook"
      }
    }
  }'
```

---

## Limitations

**Current ChatGPT Limitations:**
- Free tier: No custom instructions
- Custom instructions: May not support webhook sending in all cases
- Actions: Require Team/Enterprise subscription

**Alternative**: Use Claude or Shortcuts app for more reliable webhook sending.

---

## Next Steps

- **View Results**: http://localhost:5001
- **Action Reference**: [LLM_ACTIONS.md](./LLM_ACTIONS.md)
- **Examples**: [../examples/](../examples/)

---

**Last Updated**: 2025-01-17
