# Example Webhook Payloads

This directory contains example webhook payloads for testing the MVP system.

## Usage

Send any example to the webhook endpoint:

```bash
# Replace YOUR_API_KEY with your actual API key from .env
API_KEY="YOUR_API_KEY"

curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d @examples/git_status.json
```

Or load from environment:

```bash
source .env
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d @examples/git_log.json
```

## Examples

### Git Commands

- **git_status.json** - Check repository status
- **git_log.json** - View recent commits with graph

### Shell Commands

- **shell_ls.json** - List files in directory
- **shell_echo.json** - Echo a message

## Viewing Results

After sending a webhook, view results at:

- **Web UI**: http://localhost:5001
- **API**: http://localhost:5001/api/task/<task_id>

Example:
```bash
curl http://localhost:5001/api/task/git_status_001
```

## Creating Custom Examples

1. Copy an existing example
2. Modify the `task_id`, `action_type`, and `params`
3. Save with descriptive filename
4. Test with curl

Example template:

```json
{
  "type": "task_command",
  "data": {
    "task_id": "unique_id_here",
    "action_type": "git|shell|claude_code",
    "params": {
      "command": [...],
      "working_dir": "/path/to/directory",
      "timeout": 30
    }
  }
}
```

## Next Steps

- **Setup Guide**: [docs/LLM_ACTIONS.md](../docs/LLM_ACTIONS.md)
- **ChatGPT**: [docs/CHATGPT_SETUP.md](../docs/CHATGPT_SETUP.md)
- **Claude**: [docs/CLAUDE_SETUP.md](../docs/CLAUDE_SETUP.md)
- **Gemini**: [docs/GEMINI_SETUP.md](../docs/GEMINI_SETUP.md)
