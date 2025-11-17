"""
PostgreSQL Storage Backend for Collaborative Sessions

Implements the same interface as the JSON file-based storage but uses PostgreSQL.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2 import pool

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class PostgresBackend:
    """PostgreSQL storage backend for collaborative sessions"""

    _connection_pool = None

    @classmethod
    def initialize_pool(cls, database_url: str = None, min_conn: int = 1, max_conn: int = 10):
        """Initialize connection pool"""
        if cls._connection_pool is None:
            db_url = database_url or os.getenv('DATABASE_URL')
            if not db_url:
                raise ValueError("DATABASE_URL not set")

            cls._connection_pool = psycopg2.pool.ThreadedConnectionPool(
                min_conn, max_conn, db_url
            )

    @classmethod
    @contextmanager
    def get_connection(cls):
        """Get database connection from pool"""
        if cls._connection_pool is None:
            cls.initialize_pool()

        conn = cls._connection_pool.getconn()
        try:
            yield conn
        finally:
            cls._connection_pool.putconn(conn)

    def __init__(self, session_id: str, title: str = "", participants: List[str] = None):
        """Initialize session (load from DB or create new)"""
        self.session_id = session_id

        # Try to load existing session
        existing = self.load(session_id)
        if existing:
            # Copy attributes from existing session
            for attr in ['title', 'participants', 'context', 'status', 'created',
                        'last_activity', 'completed_at', 'conversation_chunk_count',
                        'memory_count', 'task_count', 'artifact_count']:
                setattr(self, attr, getattr(existing, attr))
        else:
            # Create new session
            self.title = title or session_id
            self.participants = participants or []
            self.context = ""
            self.status = "active"
            self.created = datetime.utcnow()
            self.last_activity = datetime.utcnow()
            self.completed_at = None
            self.conversation_chunk_count = 0
            self.memory_count = 0
            self.task_count = 0
            self.artifact_count = 0

            # Insert into database
            self._create_session()

    def _create_session(self):
        """Create new session in database"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO sessions (
                        id, title, participants, context, status, created, last_activity
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    self.session_id,
                    self.title,
                    Json(self.participants),
                    self.context,
                    self.status,
                    self.created,
                    self.last_activity
                ))
                conn.commit()

    def add_conversation_chunk(self, chunk) -> str:
        """Add conversation chunk to database"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO conversation_chunks (
                        session_id, chunk_id, content, format, start_time, end_time,
                        participants, extracted_items, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (session_id, chunk_id) DO UPDATE
                    SET content = EXCLUDED.content,
                        extracted_items = EXCLUDED.extracted_items
                """, (
                    self.session_id,
                    chunk.chunk_id,
                    chunk.content,
                    chunk.format,
                    chunk.start_time,
                    chunk.end_time,
                    Json(chunk.participants),
                    Json(chunk.extracted_items),
                    Json(chunk.metadata)
                ))

                # Update counter
                cur.execute("""
                    UPDATE sessions
                    SET conversation_chunk_count = conversation_chunk_count + 1
                    WHERE id = %s
                """, (self.session_id,))

                conn.commit()

        self.conversation_chunk_count += 1
        return chunk.chunk_id

    def add_memory(self, memory_type: str, key: str, content: Any, tags: List[str] = None) -> str:
        """Store a memory in database"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO memories (
                        session_id, type, key, content, tags
                    ) VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (session_id, key) DO UPDATE
                    SET content = EXCLUDED.content,
                        tags = EXCLUDED.tags,
                        type = EXCLUDED.type
                """, (
                    self.session_id,
                    memory_type,
                    key,
                    Json(content),
                    tags or []
                ))

                # Update counter
                cur.execute("""
                    UPDATE sessions
                    SET memory_count = (
                        SELECT COUNT(*) FROM memories WHERE session_id = %s
                    )
                    WHERE id = %s
                """, (self.session_id, self.session_id))

                conn.commit()

        return key

    def get_memory(self, key: str) -> Optional[Dict]:
        """Retrieve memory by key"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT type, key, content, tags, created
                    FROM memories
                    WHERE session_id = %s AND key = %s
                """, (self.session_id, key))

                row = cur.fetchone()
                if row:
                    return {
                        'type': row['type'],
                        'key': row['key'],
                        'content': row['content'],
                        'tags': row['tags'],
                        'timestamp': row['created'].isoformat(),
                        'session_id': self.session_id
                    }
        return None

    def query_memories(self, memory_type: Optional[str] = None, tags: List[str] = None, limit: int = 10) -> List[Dict]:
        """Query memories with filters"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = "SELECT type, key, content, tags, created FROM memories WHERE session_id = %s"
                params = [self.session_id]

                if memory_type:
                    query += " AND type = %s"
                    params.append(memory_type)

                if tags:
                    query += " AND tags && %s"
                    params.append(tags)

                query += " ORDER BY created DESC LIMIT %s"
                params.append(limit)

                cur.execute(query, params)

                memories = []
                for row in cur.fetchall():
                    memories.append({
                        'type': row['type'],
                        'key': row['key'],
                        'content': row['content'],
                        'tags': row['tags'],
                        'timestamp': row['created'].isoformat(),
                        'session_id': self.session_id
                    })

                return memories

    def add_task(self, task) -> str:
        """Add agent task to database"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO tasks (
                        id, session_id, agent_name, task_type, status, input_data
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    task.task_id,
                    self.session_id,
                    task.agent_name,
                    task.task_type,
                    task.status,
                    Json(task.data)
                ))

                # Update counter
                cur.execute("""
                    UPDATE sessions
                    SET task_count = task_count + 1
                    WHERE id = %s
                """, (self.session_id,))

                conn.commit()

        self.task_count += 1
        return task.task_id

    def get_task(self, task_id: str):
        """Get task by ID"""
        from models.session import AgentTask

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, agent_name, task_type, status, input_data,
                           output_data, error_message, created, started, completed
                    FROM tasks
                    WHERE id = %s
                """, (task_id,))

                row = cur.fetchone()
                if row:
                    return AgentTask(
                        task_id=row['id'],
                        agent_name=row['agent_name'],
                        task_type=row['task_type'],
                        status=row['status'],
                        data=row['input_data'],
                        created=row['created'].isoformat() if row['created'] else None,
                        started=row['started'].isoformat() if row['started'] else None,
                        completed=row['completed'].isoformat() if row['completed'] else None,
                        result=row['output_data'],
                        error=row['error_message']
                    )
        return None

    def update_task(self, task):
        """Update task status/result"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE tasks
                    SET status = %s,
                        started = %s,
                        completed = %s,
                        output_data = %s,
                        error_message = %s
                    WHERE id = %s
                """, (
                    task.status,
                    task.started,
                    task.completed,
                    Json(task.result) if task.result else None,
                    task.error,
                    task.task_id
                ))
                conn.commit()

    def list_tasks(self, status: Optional[str] = None) -> List:
        """List all tasks, optionally filtered by status"""
        from models.session import AgentTask

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if status:
                    cur.execute("""
                        SELECT id, agent_name, task_type, status, input_data,
                               output_data, error_message, created, started, completed
                        FROM tasks
                        WHERE session_id = %s AND status = %s
                        ORDER BY created DESC
                    """, (self.session_id, status))
                else:
                    cur.execute("""
                        SELECT id, agent_name, task_type, status, input_data,
                               output_data, error_message, created, started, completed
                        FROM tasks
                        WHERE session_id = %s
                        ORDER BY created DESC
                    """, (self.session_id,))

                tasks = []
                for row in cur.fetchall():
                    tasks.append(AgentTask(
                        task_id=row['id'],
                        agent_name=row['agent_name'],
                        task_type=row['task_type'],
                        status=row['status'],
                        data=row['input_data'],
                        created=row['created'].isoformat() if row['created'] else None,
                        started=row['started'].isoformat() if row['started'] else None,
                        completed=row['completed'].isoformat() if row['completed'] else None,
                        result=row['output_data'],
                        error=row['error_message']
                    ))

                return tasks

    def add_artifact(self, artifact_type: str, name: str, content: str, metadata: Dict = None) -> str:
        """Add artifact to database"""
        artifact_id = f"{artifact_type}_{name}"

        # Determine format from metadata
        format_type = metadata.get("format") if metadata else "text"

        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO artifacts (
                        id, session_id, type, name, content, format, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE
                    SET content = EXCLUDED.content,
                        metadata = EXCLUDED.metadata
                """, (
                    artifact_id,
                    self.session_id,
                    artifact_type,
                    name,
                    content,
                    format_type,
                    Json(metadata or {})
                ))

                # Update counter
                cur.execute("""
                    UPDATE sessions
                    SET artifact_count = (
                        SELECT COUNT(*) FROM artifacts WHERE session_id = %s
                    )
                    WHERE id = %s
                """, (self.session_id, self.session_id))

                conn.commit()

        return artifact_id

    def get_artifact(self, artifact_id: str) -> Optional[Dict]:
        """Get artifact content and metadata"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, type, name, content, format, metadata, created
                    FROM artifacts
                    WHERE id = %s
                """, (artifact_id,))

                row = cur.fetchone()
                if row:
                    return {
                        "metadata": {
                            "id": row['id'],
                            "type": row['type'],
                            "name": row['name'],
                            "format": row['format'],
                            "created": row['created'].isoformat(),
                            "metadata": row['metadata']
                        },
                        "content": row['content']
                    }
        return None

    def list_artifacts(self) -> List[Dict]:
        """List all artifacts"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, type, name, format, metadata, created
                    FROM artifacts
                    WHERE session_id = %s
                    ORDER BY created DESC
                """, (self.session_id,))

                artifacts = []
                for row in cur.fetchall():
                    artifacts.append({
                        "id": row['id'],
                        "type": row['type'],
                        "name": row['name'],
                        "format": row['format'],
                        "created": row['created'].isoformat(),
                        "metadata": row['metadata']
                    })

                return artifacts

    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
        self.save()

    def get_summary(self) -> Dict:
        """Get session summary"""
        return {
            "session_id": self.session_id,
            "title": self.title,
            "participants": self.participants,
            "context": self.context,
            "status": self.status,
            "created": self.created.isoformat() if isinstance(self.created, datetime) else self.created,
            "last_activity": self.last_activity.isoformat() if isinstance(self.last_activity, datetime) else self.last_activity,
            "duration_minutes": self._calculate_duration(),
            "stats": {
                "conversation_chunks": self.conversation_chunk_count,
                "memories": self.memory_count,
                "tasks": self.task_count,
                "artifacts": self.artifact_count,
                "active_tasks": len(self.list_tasks("running"))
            }
        }

    def _calculate_duration(self) -> float:
        """Calculate session duration in minutes"""
        if self.completed_at:
            end = self.completed_at if isinstance(self.completed_at, datetime) else datetime.fromisoformat(str(self.completed_at).replace('Z', ''))
        else:
            end = self.last_activity if isinstance(self.last_activity, datetime) else datetime.fromisoformat(str(self.last_activity).replace('Z', ''))

        start = self.created if isinstance(self.created, datetime) else datetime.fromisoformat(str(self.created).replace('Z', ''))
        return (end - start).total_seconds() / 60

    def save(self):
        """Save session metadata"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE sessions
                    SET title = %s,
                        participants = %s,
                        context = %s,
                        status = %s,
                        last_activity = %s,
                        completed_at = %s
                    WHERE id = %s
                """, (
                    self.title,
                    Json(self.participants),
                    self.context,
                    self.status,
                    self.last_activity,
                    self.completed_at,
                    self.session_id
                ))
                conn.commit()

    @classmethod
    def load(cls, session_id: str) -> Optional['PostgresBackend']:
        """Load existing session from database"""
        with cls.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, title, participants, context, status, created,
                           last_activity, completed_at, conversation_chunk_count,
                           memory_count, task_count, artifact_count
                    FROM sessions
                    WHERE id = %s
                """, (session_id,))

                row = cur.fetchone()
                if not row:
                    return None

                # Create instance without calling __init__
                instance = cls.__new__(cls)
                instance.session_id = row['id']
                instance.title = row['title']
                instance.participants = row['participants']
                instance.context = row['context']
                instance.status = row['status']
                instance.created = row['created']
                instance.last_activity = row['last_activity']
                instance.completed_at = row['completed_at']
                instance.conversation_chunk_count = row['conversation_chunk_count']
                instance.memory_count = row['memory_count']
                instance.task_count = row['task_count']
                instance.artifact_count = row['artifact_count']

                return instance

    @classmethod
    def list_sessions(cls, status_filter: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """List all sessions"""
        with cls.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if status_filter:
                    cur.execute("""
                        SELECT id as session_id, title, participants, status, created, last_activity,
                               conversation_chunk_count, memory_count, task_count, artifact_count
                        FROM sessions
                        WHERE status = %s
                        ORDER BY last_activity DESC
                        LIMIT %s
                    """, (status_filter, limit))
                else:
                    cur.execute("""
                        SELECT id as session_id, title, participants, status, created, last_activity,
                               conversation_chunk_count, memory_count, task_count, artifact_count
                        FROM sessions
                        ORDER BY last_activity DESC
                        LIMIT %s
                    """, (limit,))

                sessions = []
                for row in cur.fetchall():
                    sessions.append({
                        'session_id': row['session_id'],
                        'title': row['title'],
                        'participants': row['participants'],
                        'status': row['status'],
                        'created': row['created'].isoformat(),
                        'last_activity': row['last_activity'].isoformat(),
                        'conversation_chunk_count': row['conversation_chunk_count'],
                        'memory_count': row['memory_count'],
                        'task_count': row['task_count'],
                        'artifact_count': row['artifact_count']
                    })

                return sessions
