# MCP Tools Verification Guide

**Purpose**: Verify that all MCP (Model Context Protocol) servers are properly configured and accessible.

## MCP Servers Configured

Based on `mcp-config.json`, we have 3 active MCP servers:

1. **Postgres** - Database access
2. **GitHub** - Repository access
3. **Filesystem** - Project file access

## Verification Steps

### 1. Postgres MCP Server

**Test queries to run in Claude Code:**

```
Show me all sessions in the database
```

**Expected response**: Claude should query the sessions table and show the results.

```
How many tasks are pending in the database?
```

**Expected response**: Claude should query `SELECT COUNT(*) FROM tasks WHERE status = 'pending'`

```
Search for memories tagged with 'feature'
```

**Expected response**: Claude should query the memories table with tag filtering.

**Manual SQL verification:**
```bash
docker compose exec -T postgres psql -U webhook_user -d ai_webhook -c "SELECT COUNT(*) FROM sessions;"
```

### 2. GitHub MCP Server

**Test queries to run in Claude Code:**

```
What's the current branch in this repository?
```

**Expected response**: Claude should use git commands or GitHub API to get branch info.

```
List recent commits in this repository
```

**Expected response**: Claude should show commit history.

```
Show open issues in this repository
```

**Expected response**: Claude should query GitHub API for issues.

**Manual verification:**
```bash
# Test GitHub token
curl -H "Authorization: Bearer $(grep GITHUB_PERSONAL_ACCESS_TOKEN .env | cut -d '=' -f2)" \
  https://api.github.com/user
```

### 3. Filesystem MCP Server

**Test queries to run in Claude Code:**

```
List all Python files in the client directory
```

**Expected response**: Claude should list .py files in client/.

```
Show me the structure of the database schema
```

**Expected response**: Claude should read database/init.sql.

```
What configuration is in mcp-config.json?
```

**Expected response**: Claude should read and explain the MCP configuration.

**Manual verification:**
```bash
# MCP filesystem server should have access to:
ls -la /Users/tim/gameplan.ai/ai-webhook
```

## Configuration Details

### Postgres MCP
- **Server**: `@modelcontextprotocol/server-postgres`
- **Connection**: `postgresql://webhook_user:webhook_dev_password@localhost:5433/ai_webhook`
- **Status**: ✅ Database verified working (see test_connectivity.py results)

### GitHub MCP
- **Server**: `@modelcontextprotocol/server-github`
- **Authentication**: Uses `GITHUB_PERSONAL_ACCESS_TOKEN` from `.env`
- **Token set**: ✅ Yes (line 56 in .env)

### Filesystem MCP
- **Server**: `@modelcontextprotocol/server-filesystem`
- **Root path**: `/Users/tim/gameplan.ai/ai-webhook`
- **Access**: Read/write to project directory

## Troubleshooting

### If MCP servers don't respond:

1. **Restart Claude Code**
   ```bash
   # Exit current session and restart
   claude-code
   ```

2. **Check MCP server logs**
   - MCP servers run as background processes
   - Check for errors in terminal where Claude Code was launched

3. **Verify npx can access packages**
   ```bash
   npx -y @modelcontextprotocol/server-postgres --help
   npx -y @modelcontextprotocol/server-github --help
   npx -y @modelcontextprotocol/server-filesystem --help
   ```

4. **Test environment variables**
   ```bash
   grep DATABASE_URL .env
   grep GITHUB_PERSONAL_ACCESS_TOKEN .env
   ```

5. **Check MCP configuration**
   ```bash
   cat mcp-config.json | jq '.'
   ```

## Success Criteria

✅ All MCP servers respond to queries
✅ No error messages in MCP server logs
✅ Can access database through natural language
✅ Can query GitHub repository information
✅ Can read project files

## Next Steps After Verification

Once all MCP tools are verified:
1. Proceed to end-to-end webhook testing
2. Build session CLI tool
3. Create LLM documentation

## Notes

- MCP servers are configured to run via `npx -y` which auto-installs packages
- First access to each server may be slower while packages download
- GitHub MCP requires valid token with appropriate scopes (repo, read:org, read:user)
- Postgres MCP needs database to be running (verify with `docker compose ps`)
