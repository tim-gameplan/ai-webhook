-- AI Webhook Collaborative Sessions Database Schema
-- PostgreSQL 15+

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search

-- ============================================================================
-- SESSIONS
-- ============================================================================

CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    participants JSONB DEFAULT '[]'::jsonb,
    context TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed')),

    -- Timestamps
    created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_activity TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,

    -- Counters (denormalized for performance)
    conversation_chunk_count INTEGER DEFAULT 0,
    memory_count INTEGER DEFAULT 0,
    task_count INTEGER DEFAULT 0,
    artifact_count INTEGER DEFAULT 0,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_last_activity ON sessions(last_activity DESC);
CREATE INDEX idx_sessions_participants ON sessions USING GIN(participants);

COMMENT ON TABLE sessions IS 'Collaborative sessions where LLMs and humans work together';

-- ============================================================================
-- CONVERSATION CHUNKS
-- ============================================================================

CREATE TABLE conversation_chunks (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    chunk_id TEXT NOT NULL,

    -- Content
    content TEXT NOT NULL,  -- Can be large (voice transcripts)
    format TEXT NOT NULL DEFAULT 'dialogue' CHECK (format IN ('dialogue', 'summary', 'transcript')),

    -- Metadata
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    participants JSONB DEFAULT '[]'::jsonb,
    extracted_items JSONB DEFAULT '{}'::jsonb,  -- Ideas, decisions, questions extracted by LLM
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(session_id, chunk_id)
);

CREATE INDEX idx_conversation_session ON conversation_chunks(session_id, created DESC);
CREATE INDEX idx_conversation_format ON conversation_chunks(format);

-- Full-text search on conversation content
CREATE INDEX idx_conversation_content_fts ON conversation_chunks USING GIN(to_tsvector('english', content));

COMMENT ON TABLE conversation_chunks IS 'Conversation chunks from voice/chat sessions';

-- ============================================================================
-- MEMORIES
-- ============================================================================

CREATE TABLE memories (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,

    -- Memory identification
    type TEXT NOT NULL CHECK (type IN ('idea', 'decision', 'question', 'action_item', 'context', 'preference', 'fact', 'risk')),
    key TEXT NOT NULL,  -- User-provided key for easy retrieval

    -- Content
    content JSONB NOT NULL,  -- Flexible structure
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Timestamps
    created TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(session_id, key)
);

CREATE INDEX idx_memories_session ON memories(session_id, created DESC);
CREATE INDEX idx_memories_type ON memories(type);
CREATE INDEX idx_memories_tags ON memories USING GIN(tags);
CREATE INDEX idx_memories_session_type ON memories(session_id, type);

-- Full-text search on memory content
CREATE INDEX idx_memories_content_fts ON memories USING GIN(to_tsvector('english', content::text));

COMMENT ON TABLE memories IS 'Memories extracted from conversations or explicitly stored';

-- ============================================================================
-- TASKS (Agent Work Queue)
-- ============================================================================

CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,

    -- Agent assignment
    agent_name TEXT NOT NULL,  -- claude_code, codex, gemini_cli, researcher, etc.
    task_type TEXT NOT NULL,   -- code, research, document, analysis, prd, etc.

    -- Status
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'claimed', 'running', 'completed', 'failed', 'cancelled')),
    priority INTEGER DEFAULT 0,  -- Higher = more important

    -- Task definition
    input_data JSONB NOT NULL,  -- Task parameters

    -- Execution tracking
    process_id INTEGER,          -- PID of spawned process
    claimed_by TEXT,             -- Which control agent claimed this
    claimed_at TIMESTAMPTZ,
    started TIMESTAMPTZ,
    completed TIMESTAMPTZ,

    -- Results
    output_data JSONB,           -- Task results
    artifacts TEXT[] DEFAULT ARRAY[]::TEXT[],  -- IDs of created artifacts
    error_message TEXT,

    -- Timestamps
    created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tasks_session ON tasks(session_id, created DESC);
CREATE INDEX idx_tasks_status ON tasks(status, priority DESC, created ASC);
CREATE INDEX idx_tasks_agent ON tasks(agent_name, status);
CREATE INDEX idx_tasks_session_status ON tasks(session_id, status);

COMMENT ON TABLE tasks IS 'Task queue for agent work delegation';

-- ============================================================================
-- ARTIFACTS
-- ============================================================================

CREATE TABLE artifacts (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    task_id TEXT REFERENCES tasks(id) ON DELETE SET NULL,

    -- Artifact details
    type TEXT NOT NULL,  -- code, document, research, prd, report, etc.
    name TEXT NOT NULL,
    content TEXT,        -- Can be very large
    format TEXT,         -- markdown, python, json, etc.

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_artifacts_session ON artifacts(session_id, created DESC);
CREATE INDEX idx_artifacts_task ON artifacts(task_id);
CREATE INDEX idx_artifacts_type ON artifacts(type);

-- Full-text search on artifact content
CREATE INDEX idx_artifacts_content_fts ON artifacts USING GIN(to_tsvector('english', content));

COMMENT ON TABLE artifacts IS 'Generated artifacts (code, documents, reports, etc.)';

-- ============================================================================
-- AGENTS (Registry of Available Agents)
-- ============================================================================

CREATE TABLE agents (
    name TEXT PRIMARY KEY,
    type TEXT NOT NULL,  -- code, research, document, analysis
    command TEXT NOT NULL,  -- How to spawn this agent
    max_concurrent INTEGER DEFAULT 1,
    capabilities JSONB DEFAULT '[]'::jsonb,

    -- Status
    status TEXT NOT NULL DEFAULT 'offline' CHECK (status IN ('available', 'busy', 'offline', 'error')),
    current_tasks INTEGER DEFAULT 0,
    last_heartbeat TIMESTAMPTZ,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_agents_status ON agents(status);
CREATE INDEX idx_agents_type ON agents(type);

COMMENT ON TABLE agents IS 'Registry of available background agents';

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update last_activity on session when related data changes
CREATE OR REPLACE FUNCTION update_session_activity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE sessions
    SET last_activity = NOW()
    WHERE id = NEW.session_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_conversation_update_activity
    AFTER INSERT ON conversation_chunks
    FOR EACH ROW
    EXECUTE FUNCTION update_session_activity();

CREATE TRIGGER trg_memory_update_activity
    AFTER INSERT ON memories
    FOR EACH ROW
    EXECUTE FUNCTION update_session_activity();

CREATE TRIGGER trg_task_update_activity
    AFTER INSERT OR UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_session_activity();

-- Update task.updated timestamp
CREATE OR REPLACE FUNCTION update_updated_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_tasks_updated
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_timestamp();

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Active sessions with stats
CREATE OR REPLACE VIEW active_sessions AS
SELECT
    s.*,
    COUNT(DISTINCT t.id) FILTER (WHERE t.status = 'running') as active_tasks,
    COUNT(DISTINCT t.id) FILTER (WHERE t.status = 'pending') as pending_tasks
FROM sessions s
LEFT JOIN tasks t ON t.session_id = s.id
WHERE s.status = 'active'
GROUP BY s.id;

COMMENT ON VIEW active_sessions IS 'Active sessions with current task counts';

-- Task queue view (for agents to claim work)
CREATE OR REPLACE VIEW task_queue AS
SELECT
    t.*,
    s.title as session_title
FROM tasks t
JOIN sessions s ON s.id = t.session_id
WHERE t.status = 'pending'
ORDER BY t.priority DESC, t.created ASC;

COMMENT ON VIEW task_queue IS 'Pending tasks ordered by priority';

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Claim a task (atomic operation for agents)
CREATE OR REPLACE FUNCTION claim_task(
    p_agent_name TEXT,
    p_control_agent TEXT
) RETURNS TABLE(task_id TEXT, input_data JSONB) AS $$
DECLARE
    v_task_id TEXT;
BEGIN
    -- Atomically claim the highest priority pending task
    UPDATE tasks
    SET
        status = 'claimed',
        claimed_by = p_control_agent,
        claimed_at = NOW()
    WHERE id = (
        SELECT id FROM tasks
        WHERE status = 'pending'
          AND agent_name = p_agent_name
        ORDER BY priority DESC, created ASC
        LIMIT 1
        FOR UPDATE SKIP LOCKED
    )
    RETURNING id INTO v_task_id;

    IF v_task_id IS NOT NULL THEN
        RETURN QUERY
        SELECT t.id, t.input_data
        FROM tasks t
        WHERE t.id = v_task_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION claim_task IS 'Atomically claim a task for execution';

-- ============================================================================
-- SAMPLE DATA (for testing)
-- ============================================================================

-- Insert sample agent
INSERT INTO agents (name, type, command, max_concurrent, capabilities)
VALUES
    ('claude_code', 'code', 'claude-code', 2, '["python", "javascript", "refactoring"]'::jsonb),
    ('researcher', 'research', 'python agents/researcher.py', 3, '["web_search", "competitive_analysis"]'::jsonb),
    ('gemini_cli', 'general', 'gemini', 1, '["general_purpose", "code", "research"]'::jsonb)
ON CONFLICT (name) DO NOTHING;

-- Grant permissions (adjust as needed)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO webhook_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO webhook_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO webhook_user;
