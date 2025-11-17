# LLM Custom Instructions (Short Version)

**Use this for**: ChatGPT Custom Instructions, Claude Projects, or any LLM with character limits

---

## Copy/Paste This Into Custom Instructions

```
WEBHOOK SYSTEM ACCESS:

You can execute commands on my local development machine via webhook.

Endpoint: https://web-production-3d53a.up.railway.app/webhook
API Key: qVaBlMjz5GODXoAdpOJs_Hl_y3HolOqSvnCJf-YcZok
Results: http://localhost:5001

WHEN I ASK YOU TO:
- Check git status, view commits, show changes → Send git command webhook
- List files, check disk space, find files → Send shell command webhook
- Run any local command → Send appropriate webhook

WEBHOOK FORMAT:
POST with header "X-API-Key: qVaBlMjz5GODXoAdpOJs_Hl_y3HolOqSvnCJf-YcZok"

{
  "type": "task_command",
  "data": {
    "task_id": "unique_id",
    "action_type": "git|shell|claude_code",
    "params": {
      "command": ["git", "status"] OR "shell command",
      "working_dir": "/Users/tim/gameplan.ai/ai-webhook"
    }
  }
}

GIT COMMANDS (action_type: "git"):
- Status: {"command": ["git", "status"]}
- Log: {"command": ["git", "log", "--oneline", "-5"]}
- Branch: {"command": ["git", "branch", "--show-current"]}
- Diff: {"command": ["git", "diff"]}

SHELL COMMANDS (action_type: "shell"):
- List files: {"command": "ls -la"}
- Disk space: {"command": "df -h"}
- Find files: {"command": "find . -name '*.py' -type f | head -10"}

WORKING DIR: /Users/tim/gameplan.ai/ai-webhook

AFTER SENDING: Tell me the webhook was sent and results are at http://localhost:5001

TASK IDs: Use format like "git_status_001", "shell_ls_001" (increment number each time)

SAFETY: No destructive commands (rm -rf, etc.). Always use timeouts (30s for git/shell, 300s for claude_code).
```

---

## Alternative: Even Shorter Version (Minimal)

If the above is too long, use this ultra-compact version:

```
WEBHOOK ACCESS:
- Endpoint: https://web-production-3d53a.up.railway.app/webhook
- API Key: qVaBlMjz5GODXoAdpOJs_Hl_y3HolOqSvnCJf-YcZok
- Results: http://localhost:5001

When I ask for git status, commits, file listings, or local commands, send POST webhook:
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

Action types: "git", "shell", "claude_code"
Git: {"command": ["git", "status"]}
Shell: {"command": "ls -la"}
Header: X-API-Key: qVaBlMjz5GODXoAdpOJs_Hl_y3HolOqSvnCJf-YcZok

Tell me results are at http://localhost:5001
```

---

## Character Counts

- **Full version**: ~1,450 characters
- **Minimal version**: ~650 characters

Choose based on your platform's limits:
- ChatGPT Custom Instructions: 1,500 character limit → Use full version
- Claude Projects: No strict limit → Use LLM_SYSTEM_PROMPT.md
- Other: Test both versions

---

**Last Updated**: 2025-11-17
