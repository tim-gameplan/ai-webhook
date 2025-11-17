# LLM Actions Reference

Complete reference guide for triggering local actions from mobile LLMs (ChatGPT, Claude, Gemini).

## Overview

This system allows you to send task commands from your phone via voice LLMs, which execute locally on your development machine.

**Flow**:
```
You (mobile) → Voice LLM → Webhook → Relay Server → Local Client → Task Executor → SQLite
                                                                           ↓
                                                    Results Viewer (:5001)
```

---

## Webhook Format

All task commands use this structure:

```json
{
  "type": "task_command",
  "data": {
    "task_id": "unique_identifier",
    "action_type": "git|shell|claude_code",
    "params": {
      "command": "...",
      "working_dir": "/path/to/directory",
      "timeout": 30
    }
  }
}
```

### Fields

- **type** (required): Must be `"task_command"`
- **data.task_id** (required): Unique identifier for this task (used to query results later)
- **data.action_type** (required): Type of action to execute (`git`, `shell`, or `claude_code`)
- **data.params** (required): Parameters specific to the action type

---

## Action Types

### 1. Git Commands

Execute git commands in a repository.

**Action Type**: `git`

**Parameters**:
- `command` (array): Git command as array (e.g., `["git", "status"]`)
- `working_dir` (string, optional): Path to git repository (defaults to current directory)
- `timeout` (number, optional): Timeout in seconds (default: 30)

**Example - Git Status**:
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

**Example - Git Log**:
```json
{
  "type": "task_command",
  "data": {
    "task_id": "git_log_001",
    "action_type": "git",
    "params": {
      "command": ["git", "log", "--oneline", "-10"],
      "working_dir": "/Users/tim/gameplan.ai/ai-webhook"
    }
  }
}
```

**Example - Git Diff**:
```json
{
  "type": "task_command",
  "data": {
    "task_id": "git_diff_001",
    "action_type": "git",
    "params": {
      "command": ["git", "diff", "HEAD~1"],
      "working_dir": "/Users/tim/gameplan.ai/ai-webhook"
    }
  }
}
```

**Security**: Commands must start with `"git"` to prevent command injection.

---

### 2. Shell Commands

Execute arbitrary shell commands.

**Action Type**: `shell`

**Parameters**:
- `command` (string or array): Shell command to execute
- `working_dir` (string, optional): Working directory (defaults to current directory)
- `timeout` (number, optional): Timeout in seconds (default: 30)

**Example - Echo**:
```json
{
  "type": "task_command",
  "data": {
    "task_id": "shell_echo_001",
    "action_type": "shell",
    "params": {
      "command": "echo 'Task executed from mobile!'"
    }
  }
}
```

**Example - List Files**:
```json
{
  "type": "task_command",
  "data": {
    "task_id": "shell_ls_001",
    "action_type": "shell",
    "params": {
      "command": ["ls", "-la"],
      "working_dir": "/Users/tim/gameplan.ai/ai-webhook"
    }
  }
}
```

**Example - Check Disk Space**:
```json
{
  "type": "task_command",
  "data": {
    "task_id": "shell_df_001",
    "action_type": "shell",
    "params": {
      "command": "df -h"
    }
  }
}
```

**Security Warning**: Be careful with shell commands. Avoid passing user input directly. Prefer array format over string format when possible.

---

### 3. Claude Code (Future)

Execute Claude Code CLI commands.

**Action Type**: `claude_code`

**Parameters**:
- `prompt` (string): Prompt for Claude Code
- `working_dir` (string, optional): Working directory
- `timeout` (number, optional): Timeout in seconds (default: 300)

**Example - Code Review**:
```json
{
  "type": "task_command",
  "data": {
    "task_id": "claude_review_001",
    "action_type": "claude_code",
    "params": {
      "prompt": "Review my latest changes",
      "working_dir": "/Users/tim/gameplan.ai/ai-webhook",
      "timeout": 300
    }
  }
}
```

**Note**: Requires Claude Code CLI to be installed. See: https://claude.ai/code

---

## Common Use Cases

### Check Repository Status
```json
{
  "type": "task_command",
  "data": {
    "task_id": "status_check_001",
    "action_type": "git",
    "params": {
      "command": ["git", "status", "--short"],
      "working_dir": "/path/to/repo"
    }
  }
}
```

### View Recent Commits
```json
{
  "type": "task_command",
  "data": {
    "task_id": "recent_commits_001",
    "action_type": "git",
    "params": {
      "command": ["git", "log", "--oneline", "--graph", "-20"],
      "working_dir": "/path/to/repo"
    }
  }
}
```

### Check Server Status
```json
{
  "type": "task_command",
  "data": {
    "task_id": "server_status_001",
    "action_type": "shell",
    "params": {
      "command": "curl -s http://localhost:8000/"
    }
  }
}
```

### Run Tests
```json
{
  "type": "task_command",
  "data": {
    "task_id": "run_tests_001",
    "action_type": "shell",
    "params": {
      "command": "pytest tests/",
      "working_dir": "/path/to/project",
      "timeout": 120
    }
  }
}
```

---

## Viewing Results

Results are stored in SQLite and can be viewed at:

**Web Viewer**: http://localhost:5001

**API Endpoints**:
- `GET /` - Web interface showing recent tasks
- `GET /api/task/<task_id>` - Get specific task as JSON
- `GET /api/tasks?limit=20` - Get recent tasks as JSON

**Example - Query via API**:
```bash
curl http://localhost:5001/api/task/git_status_001
```

**Response**:
```json
{
  "id": "git_status_001",
  "command": "git",
  "status": "completed",
  "input_data": {
    "action_type": "git",
    "params": {
      "command": ["git", "status"],
      "working_dir": "/Users/tim/gameplan.ai/ai-webhook"
    }
  },
  "output_data": {
    "success": true,
    "stdout": "On branch main\nYour branch is up to date...",
    "stderr": "",
    "returncode": 0
  },
  "error_message": null,
  "created_at": "2025-01-17 10:30:00",
  "completed_at": "2025-01-17 10:30:02"
}
```

---

## Error Handling

### Invalid Working Directory
```json
{
  "status": "failed",
  "error": "Working directory does not exist: /invalid/path"
}
```

### Command Timeout
```json
{
  "status": "failed",
  "error": "Command timed out after 30 seconds"
}
```

### Git Command Restriction
```json
{
  "status": "failed",
  "error": "Git commands must start with 'git'"
}
```

---

## Best Practices

### 1. Use Descriptive Task IDs
```
✅ Good: "git_status_myproject_20250117_1030"
❌ Bad: "task1"
```

### 2. Set Appropriate Timeouts
```json
{
  "timeout": 30    // Quick commands (git, ls)
  "timeout": 120   // Tests
  "timeout": 300   // Claude Code, complex operations
}
```

### 3. Specify Working Directory
```json
{
  "working_dir": "/Users/tim/gameplan.ai/ai-webhook"  // ✅ Explicit
  // vs relying on default
}
```

### 4. Use Array Format for Commands
```json
{
  "command": ["git", "log", "-10"]  // ✅ Safe, no shell injection
  // vs
  "command": "git log -10"          // ⚠️ Works but less safe
}
```

---

## Troubleshooting

### Task Not Executing
1. Check webhook client is running: `ps aux | grep client.py`
2. Check relay server connection in client logs
3. Verify API key in `.env` file

### Task Shows as Failed
1. Check error message in results viewer
2. Verify working directory exists
3. Check command syntax
4. Verify timeout is sufficient

### Can't See Results
1. Ensure results server is running: `python3 client/results_server.py`
2. Check task ID matches exactly
3. Verify database path in `.env`: `SQLITE_PATH=./tasks.db`

---

## Next Steps

- **ChatGPT Setup**: See [CHATGPT_SETUP.md](./CHATGPT_SETUP.md)
- **Claude Setup**: See [CLAUDE_SETUP.md](./CLAUDE_SETUP.md)
- **Gemini Setup**: See [GEMINI_SETUP.md](./GEMINI_SETUP.md)
- **Examples**: See [examples/](../examples/) directory

---

**Last Updated**: 2025-01-17
