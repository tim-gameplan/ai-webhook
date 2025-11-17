# File Reorganization Plan

## Current Issues
- 25+ markdown files in root directory (should be ~5-6)
- 8 test files in root (should be in tests/)
- Planning documents mixed with user docs
- Log files not properly gitignored

## Proposed Organization

### Root Directory (Keep Only Essential Files)
**User-facing docs:**
- README.md ✓
- CLAUDE.md ✓ (Claude Code instructions)
- CONTRIBUTING.md ✓
- CHANGELOG.md ✓
- MVP_QUICKSTART.md ✓ (main entry point)
- TEST_PLAN.md ✓

**Scripts:**
- start_mvp.sh ✓
- stop_mvp.sh ✓

**Source:**
- app.py ✓ (relay server)

**Config:**
- .env, .env.example ✓
- .gitignore ✓
- requirements.txt ✓
- Procfile, railway.json, render.yaml ✓
- docker-compose.yml ✓
- mcp-config.json ✓

### Move to docs/
**Architecture & Setup:**
- ARCHITECTURE.md → docs/ARCHITECTURE.md
- DATABASE_SETUP.md → docs/DATABASE_SETUP.md
- SECURITY_SETUP.md → docs/SECURITY_SETUP.md

### Move to docs/planning/
**Planning & Decision Docs (Archive):**
- ACTION_PLAN.md
- EXECUTION_PLAN.md
- MVP_CONTEXT.md
- MVP_EXECUTION_PLAN.md
- MVP_SUMMARY.md
- NEXT_STEPS.md
- PARALLEL_EXECUTION_PLAN.md
- PHASE1_COMPLETE.md
- PHASE1_VALIDATION_RESULTS.md
- POSTGRES_IMPLEMENTATION.md
- TASK_ROADMAP.md
- MCP_TOOLS_VERIFICATION.md
- FUTURE_TASKS.md

### Move to tests/
**All test files:**
- test_mvp.py
- test_sqlite_backend.py
- test_task_executor.py
- test_results_viewer.py
- test_webhooks_e2e.py
- test_connectivity.py
- test_postgres_backend.py
- test_deployment.py

### Archive (Move to archive/)
**Legacy scripts (pre-MVP):**
- start_client.sh → archive/start_client.sh
- run_client.py → archive/run_client.py

### Add to .gitignore
**Generated/Log files:**
- *.log
- client_output.log
- client.log
- test_results.db
- tasks.db
- *.db (all SQLite files)
- .DS_Store
- .client.pid
- .results.pid

## Directory Structure After Reorganization

```
ai-webhook/
├── README.md
├── CLAUDE.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── MVP_QUICKSTART.md
├── TEST_PLAN.md
├── app.py
├── start_mvp.sh
├── stop_mvp.sh
├── requirements.txt
├── .env.example
├── .gitignore
├── Procfile
├── railway.json
├── render.yaml
├── docker-compose.yml
├── mcp-config.json
│
├── client/
│   ├── client.py
│   ├── task_executor.py
│   ├── results_server.py
│   ├── storage/
│   │   └── sqlite_backend.py
│   ├── templates/
│   │   └── tasks.html
│   ├── agents/
│   ├── handlers/
│   └── models/
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DATABASE_SETUP.md
│   ├── SECURITY_SETUP.md
│   ├── LLM_ACTIONS.md
│   ├── CHATGPT_SETUP.md
│   ├── CLAUDE_SETUP.md
│   ├── GEMINI_SETUP.md
│   ├── deployment/
│   ├── worklogs/
│   └── planning/
│       ├── ACTION_PLAN.md
│       ├── EXECUTION_PLAN.md
│       ├── MVP_CONTEXT.md
│       ├── MVP_EXECUTION_PLAN.md
│       ├── MVP_SUMMARY.md
│       ├── NEXT_STEPS.md
│       ├── PARALLEL_EXECUTION_PLAN.md
│       ├── PHASE1_COMPLETE.md
│       ├── PHASE1_VALIDATION_RESULTS.md
│       ├── POSTGRES_IMPLEMENTATION.md
│       ├── TASK_ROADMAP.md
│       ├── MCP_TOOLS_VERIFICATION.md
│       └── FUTURE_TASKS.md
│
├── tests/
│   ├── test_mvp.py
│   ├── test_sqlite_backend.py
│   ├── test_task_executor.py
│   ├── test_results_viewer.py
│   ├── test_webhooks_e2e.py
│   ├── test_connectivity.py
│   ├── test_postgres_backend.py
│   └── test_deployment.py
│
├── examples/
│   ├── README.md
│   ├── git_status.json
│   ├── git_log.json
│   ├── shell_ls.json
│   ├── shell_echo.json
│   └── llm_prompts/
│
├── archive/
│   ├── start_client.sh
│   └── run_client.py
│
├── database/
├── llm_insights/
├── tools/
└── webhook_logs/
```

## Benefits
1. ✅ Clean root directory (only 14 files vs 48)
2. ✅ Clear separation: user docs vs planning docs
3. ✅ All tests in one place
4. ✅ Easier to find relevant files
5. ✅ Better gitignore coverage
6. ✅ Archive preserves history without clutter
