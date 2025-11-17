# Gemini Mobile Setup Guide

Configure Google Gemini on your iPhone to trigger local development tasks.

## Prerequisites

- Google Gemini mobile app (iOS)
- Google account
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

## Step 2: Configure Gemini

Gemini doesn't have persistent custom instructions like ChatGPT or Claude's Projects, so you'll need to provide context at the start of each conversation.

### Conversation Starter Template

Copy this and send at the start of your Gemini conversation:

```
I have a local webhook system for executing development tasks. When I ask you to execute local tasks, send a POST webhook to:

Endpoint: https://web-production-3d53a.up.railway.app/webhook

Headers:
Content-Type: application/json
X-API-Key: YOUR_API_KEY_HERE

Body format:
{
  "type": "task_command",
  "data": {
    "task_id": "unique_identifier",
    "action_type": "git|shell|claude_code",
    "params": {
      "command": [...],
      "working_dir": "/Users/tim/gameplan.ai/ai-webhook",
      "timeout": 30
    }
  }
}

Available actions:
- git: Git commands (e.g., ["git", "status"])
- shell: Shell commands (e.g., ["ls", "-la"])
- claude_code: Claude Code CLI (e.g., {"prompt": "Review code"})

My default working directory: /Users/tim/gameplan.ai/ai-webhook
Results viewer: http://localhost:5001

Please confirm when you send a webhook and remind me where to check results. Be concise.
```

**Important**: Replace `YOUR_API_KEY_HERE` with your actual API key.

---

## Step 3: Test It

After providing the context, say:

> "Check git status on my ai-webhook repo"

Gemini should:
1. Send the webhook with correct format
2. Confirm what was sent
3. Remind you to check http://localhost:5001

---

## Example Conversation

**You**:
```
[Paste conversation starter template]

Now check git status on my repo.
```

**Gemini**:
"I'll send a webhook to check git status."

*Sends:*
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

**Gemini**: "✅ Webhook sent. Check results at http://localhost:5001"

---

## Common Prompts

### Git Status
> "What's the git status?"

### Recent Commits
> "Show me the last 5 commits"

### List Files
> "List all files in the project"

### Run Tests
> "Run pytest in the tests directory"

---

## Limitations

**Gemini Constraints:**
- No persistent memory between conversations
- Must provide context each time
- HTTP request capability may vary

**Workarounds:**
1. Use saved prompts in Notes app (copy/paste to start conversations)
2. Use iOS Shortcuts app for direct webhook sending
3. Use Claude instead (has Projects feature)

---

## Alternative: iOS Shortcuts

Create Siri shortcuts for common tasks:

### Shortcut: "Git Status"

1. Open **Shortcuts** app
2. Create new shortcut
3. Add **Get Contents of URL**:
   - URL: `https://web-production-3d53a.up.railway.app/webhook`
   - Method: POST
   - Headers:
     ```
     Content-Type: application/json
     X-API-Key: YOUR_API_KEY
     ```
   - Request Body:
     ```json
     {
       "type": "task_command",
       "data": {
         "task_id": "git_status_siri",
         "action_type": "git",
         "params": {
           "command": ["git", "status"],
           "working_dir": "/Users/tim/gameplan.ai/ai-webhook"
         }
       }
     }
     ```

4. Add to Siri: "Hey Siri, git status"

### Shortcut: "Recent Commits"

Same steps, but use:
```json
{
  "type": "task_command",
  "data": {
    "task_id": "git_log_siri",
    "action_type": "git",
    "params": {
      "command": ["git", "log", "--oneline", "-10"],
      "working_dir": "/Users/tim/gameplan.ai/ai-webhook"
    }
  }
}
```

---

## Manual Testing

Test webhooks directly:

```bash
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "type": "task_command",
    "data": {
      "task_id": "test_gemini_001",
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

Or via API:
```bash
curl http://localhost:5001/api/task/test_gemini_001
```

---

## Troubleshooting

### Gemini doesn't send webhook

1. Gemini may not have HTTP request capabilities in all regions/versions
2. Try being more explicit: "Send a POST request to..."
3. Use Shortcuts app as alternative
4. Use manual curl commands

### Context forgotten between conversations

Gemini doesn't have persistent memory. Solutions:
1. Save template in Notes app, copy at conversation start
2. Use Shortcuts app instead
3. Switch to Claude (has Projects feature)

### Wrong parameters sent

Double-check conversation starter template includes:
- Correct API key
- Correct working directory
- All three action types explained

---

## Recommended Setup: Use Shortcuts Instead

Since Gemini lacks persistent context, iOS Shortcuts may be more reliable:

**Advantages**:
- No context needed
- Siri integration
- Faster execution
- More reliable

**Create shortcuts for**:
- Git status
- Recent commits
- Git diff
- Custom commands you use frequently

See [Shortcuts section](#alternative-ios-shortcuts) above.

---

## Next Steps

- **View Results**: http://localhost:5001
- **Action Reference**: [LLM_ACTIONS.md](./LLM_ACTIONS.md)
- **Examples**: [../examples/](../examples/)
- **Consider**: Use Claude instead for better UX ([CLAUDE_SETUP.md](./CLAUDE_SETUP.md))

---

**Last Updated**: 2025-01-17
