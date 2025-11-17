# Database Setup Guide

## Quick Start

### 1. Start PostgreSQL with Docker Compose

```bash
# Copy environment template
cp .env.example .env

# Edit .env if needed (defaults work for local development)

# Start database
docker compose up -d postgres

# Check status
docker compose ps

# View logs
docker compose logs -f postgres
```

### 2. Verify Database

```bash
# Connect to database
docker compose exec postgres psql -U webhook_user -d ai_webhook

# Inside psql, run:
\dt  # List tables
\d sessions  # Describe sessions table
SELECT * FROM agents;  # View registered agents
\q  # Quit
```

### 3. (Optional) Start PgAdmin

```bash
# Start PgAdmin for web-based management
docker compose --profile tools up -d pgadmin

# Access at: http://localhost:5050
# Login: admin@localhost / admin

# Add server:
# - Name: AI Webhook
# - Host: postgres
# - Port: 5432
# - Database: ai_webhook
# - Username: webhook_user
# - Password: webhook_dev_password
```

## Database Schema

### Tables

**sessions** - Collaborative sessions
- Tracks conversation metadata
- Participants, status, timestamps
- Counters for chunks, memories, tasks

**conversation_chunks** - Large conversation text from voice mode
- Dialogue, summaries, or full transcripts
- Extracted items (ideas, decisions)
- Full-text search enabled

**memories** - Extracted knowledge from conversations
- Ideas, decisions, questions, facts
- Tagged for easy retrieval
- Queryable by type and tags

**tasks** - Agent work queue
- Tasks delegated to background agents
- Status tracking (pending → claimed → running → completed)
- Process IDs, results, artifacts

**artifacts** - Generated outputs
- Code, documents, reports, PRDs
- Linked to tasks and sessions
- Full-text searchable

**agents** - Registry of available agents
- Claude Code, Codex, Gemini CLI, etc.
- Capabilities, max concurrent tasks
- Status and heartbeat tracking

### Key Features

**1. Full-Text Search**
```sql
-- Search conversations
SELECT * FROM conversation_chunks
WHERE to_tsvector('english', content) @@ plainto_tsquery('english', 'carbon tracking');

-- Search memories
SELECT * FROM memories
WHERE to_tsvector('english', content::text) @@ plainto_tsquery('english', 'PWA decision');
```

**2. Atomic Task Claiming**
```sql
-- Agents can atomically claim work without conflicts
SELECT * FROM claim_task('claude_code', 'control_agent_1');
```

**3. Session Activity Tracking**
- Automatically updates `last_activity` when data changes
- Triggers maintain consistency

## MCP Tools Setup

### PostgreSQL MCP Server

Provides direct database access to Claude Code.

**Setup:**
1. MCP server auto-connects to database
2. Use natural language to query/modify data
3. Available operations:
   - Query sessions, tasks, memories
   - Update task status
   - Create new artifacts
   - Search conversations

**Example usage:**
```
You: "Show me all active sessions"
Claude: [Uses MCP postgres tool to query active_sessions view]

You: "What tasks are pending for claude_code agent?"
Claude: [Queries tasks table with filters]

You: "Mark task code_001 as completed"
Claude: [Updates task status]
```

### GitHub MCP Server

Provides GitHub API access.

**Setup:**
1. Get GitHub personal access token
2. Export: `export GITHUB_TOKEN=your_token`
3. MCP server auto-connects

**Example usage:**
```
You: "Create an issue for implementing rate limiting"
Claude: [Uses GitHub MCP to create issue]

You: "What PRs are open?"
Claude: [Queries PR list]
```

### Filesystem MCP Server

Provides file access (already has this by default but MCP formalizes it).

## Management Commands

### Docker Compose Commands

```bash
# Start all services
docker compose up -d

# Start specific service
docker compose up -d postgres

# Stop all services
docker compose down

# Stop and remove volumes (⚠️ deletes data)
docker compose down -v

# Restart service
docker compose restart postgres

# View logs
docker compose logs -f postgres

# Execute SQL
docker compose exec postgres psql -U webhook_user -d ai_webhook -c "SELECT COUNT(*) FROM sessions;"
```

### Backup & Restore

```bash
# Backup database
docker compose exec -T postgres pg_dump -U webhook_user ai_webhook > backup.sql

# Restore database
docker compose exec -T postgres psql -U webhook_user ai_webhook < backup.sql
```

### Reset Database

```bash
# Stop and remove database
docker compose down postgres

# Remove volume
docker volume rm ai-webhook_postgres_data

# Restart (will reinitialize)
docker compose up -d postgres
```

## Connection Details

### From Host Machine

```bash
# Environment variables
export PGHOST=localhost
export PGPORT=5432
export PGUSER=webhook_user
export PGPASSWORD=webhook_dev_password
export PGDATABASE=ai_webhook

# psql
psql

# Python
import psycopg2
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    user="webhook_user",
    password="webhook_dev_password",
    database="ai_webhook"
)
```

### From Docker Container

```bash
# Inside another container on same network
postgresql://webhook_user:webhook_dev_password@postgres:5432/ai_webhook
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs postgres

# Check if port 5432 is already in use
lsof -i :5432

# If port conflict, change in .env:
POSTGRES_PORT=5433
```

### Connection Refused

```bash
# Wait for health check
docker compose ps

# Should show "healthy" status
# If unhealthy, check logs
```

### Permission Denied

```bash
# Reset volume permissions
docker compose down -v
docker compose up -d
```

## Production Considerations

When moving to production:

1. **Change passwords** - Use strong, random passwords
2. **Use managed database** - Railway, Supabase, AWS RDS
3. **Enable SSL** - Require encrypted connections
4. **Set up backups** - Automated daily backups
5. **Monitor connections** - Set connection limits
6. **Add replication** - For high availability

## Next Steps

1. ✅ Database running
2. ✅ Schema initialized
3. ⏭ Implement PostgreSQL storage backend
4. ⏭ Migrate from JSON files
5. ⏭ Test with MCP tools
