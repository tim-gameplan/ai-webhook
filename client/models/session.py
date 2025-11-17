"""
Collaborative Session Models

Represents a collaborative session where LLMs and humans work together,
with support for conversation capture, memory storage, and agent tasks.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import json
from dataclasses import dataclass, asdict, field


@dataclass
class ConversationChunk:
    """Represents a chunk of conversation"""
    chunk_id: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    format: str = "dialogue"  # dialogue, summary, transcript
    content: str = ""
    participants: List[str] = field(default_factory=list)
    extracted_items: Dict[str, List[Any]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self):
        return asdict(self)


@dataclass
class AgentTask:
    """Represents a task delegated to an agent"""
    task_id: str
    agent_name: str
    task_type: str
    data: Dict[str, Any]
    status: str = "pending"  # pending, in_progress, completed, failed
    created: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started: Optional[str] = None
    completed: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self):
        return asdict(self)


class CollaborativeSession:
    """
    Manages a collaborative session with conversation capture,
    memory storage, and agent task management.
    """

    def __init__(self, session_id: str, title: str = "", participants: List[str] = None):
        self.session_id = session_id
        self.title = title or session_id
        self.participants = participants or []
        self.context = ""
        self.status = "active"  # active, paused, completed

        # Timestamps
        self.created = datetime.utcnow().isoformat()
        self.last_activity = datetime.utcnow().isoformat()
        self.completed_at: Optional[str] = None

        # Counters
        self.conversation_chunk_count = 0
        self.memory_count = 0
        self.task_count = 0
        self.artifact_count = 0

        # Setup directory structure
        self.base_path = Path("sessions") / session_id
        self._setup_directories()

    def _setup_directories(self):
        """Create directory structure for session"""
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (self.base_path / "conversation").mkdir(exist_ok=True)
        (self.base_path / "extracted").mkdir(exist_ok=True)
        (self.base_path / "memories").mkdir(exist_ok=True)
        (self.base_path / "tasks").mkdir(exist_ok=True)
        (self.base_path / "artifacts").mkdir(exist_ok=True)
        (self.base_path / "agents").mkdir(exist_ok=True)

    def add_conversation_chunk(self, chunk: ConversationChunk) -> str:
        """Add a conversation chunk to the session"""
        # Save chunk
        chunk_path = self.base_path / "conversation" / f"chunk_{chunk.chunk_id}.json"
        chunk_path.write_text(json.dumps(chunk.to_dict(), indent=2))

        # Append to full transcript
        transcript_path = self.base_path / "conversation" / "full_transcript.txt"
        with open(transcript_path, 'a') as f:
            f.write(f"\n\n--- Chunk {chunk.chunk_id} ({chunk.timestamp}) ---\n")
            f.write(chunk.content)

        self.conversation_chunk_count += 1
        self.update_activity()

        return chunk.chunk_id

    def add_memory(self, memory_type: str, key: str, content: Any, tags: List[str] = None) -> str:
        """Store a memory"""
        memory = {
            "type": memory_type,
            "key": key,
            "content": content,
            "tags": tags or [],
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": self.session_id
        }

        # Save memory file
        memory_file = self.base_path / "memories" / f"{key}.json"
        memory_file.write_text(json.dumps(memory, indent=2))

        # Update extracted items index
        extracted_file = self.base_path / "extracted" / f"{memory_type}s.json"
        extracted_items = []
        if extracted_file.exists():
            extracted_items = json.loads(extracted_file.read_text())

        extracted_items.append({
            "key": key,
            "content": content,
            "timestamp": memory["timestamp"]
        })
        extracted_file.write_text(json.dumps(extracted_items, indent=2))

        self.memory_count += 1
        self.update_activity()

        return key

    def get_memory(self, key: str) -> Optional[Dict]:
        """Retrieve a memory by key"""
        memory_file = self.base_path / "memories" / f"{key}.json"
        if memory_file.exists():
            return json.loads(memory_file.read_text())
        return None

    def query_memories(self, memory_type: Optional[str] = None, tags: List[str] = None, limit: int = 10) -> List[Dict]:
        """Query memories with filters"""
        memories = []

        for memory_file in (self.base_path / "memories").glob("*.json"):
            memory = json.loads(memory_file.read_text())

            # Filter by type
            if memory_type and memory.get("type") != memory_type:
                continue

            # Filter by tags
            if tags:
                memory_tags = set(memory.get("tags", []))
                if not any(tag in memory_tags for tag in tags):
                    continue

            memories.append(memory)

        # Sort by timestamp, newest first
        memories.sort(key=lambda m: m.get("timestamp", ""), reverse=True)

        return memories[:limit]

    def add_task(self, task: AgentTask) -> str:
        """Add an agent task"""
        task_file = self.base_path / "tasks" / f"{task.task_id}.json"
        task_file.write_text(json.dumps(task.to_dict(), indent=2))

        self.task_count += 1
        self.update_activity()

        return task.task_id

    def get_task(self, task_id: str) -> Optional[AgentTask]:
        """Get task by ID"""
        task_file = self.base_path / "tasks" / f"{task_id}.json"
        if task_file.exists():
            data = json.loads(task_file.read_text())
            return AgentTask(**data)
        return None

    def update_task(self, task: AgentTask):
        """Update task status/result"""
        task_file = self.base_path / "tasks" / f"{task.task_id}.json"
        task_file.write_text(json.dumps(task.to_dict(), indent=2))
        self.update_activity()

    def list_tasks(self, status: Optional[str] = None) -> List[AgentTask]:
        """List all tasks, optionally filtered by status"""
        tasks = []

        for task_file in (self.base_path / "tasks").glob("*.json"):
            data = json.loads(task_file.read_text())
            task = AgentTask(**data)

            if status is None or task.status == status:
                tasks.append(task)

        # Sort by created time
        tasks.sort(key=lambda t: t.created, reverse=True)

        return tasks

    def add_artifact(self, artifact_type: str, name: str, content: str, metadata: Dict = None) -> str:
        """Add an artifact (document, report, etc.)"""
        artifact_id = f"{artifact_type}_{name}"

        # Determine file extension
        ext = {
            "markdown": ".md",
            "json": ".json",
            "text": ".txt",
            "html": ".html"
        }.get(metadata.get("format") if metadata else None, ".txt")

        # Save artifact
        artifact_file = self.base_path / "artifacts" / f"{artifact_id}{ext}"
        artifact_file.write_text(content)

        # Save metadata
        artifact_meta = {
            "id": artifact_id,
            "type": artifact_type,
            "name": name,
            "file": str(artifact_file.name),
            "created": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }

        meta_file = self.base_path / "artifacts" / f"{artifact_id}_meta.json"
        meta_file.write_text(json.dumps(artifact_meta, indent=2))

        self.artifact_count += 1
        self.update_activity()

        return artifact_id

    def get_artifact(self, artifact_id: str) -> Optional[Dict]:
        """Get artifact content and metadata"""
        meta_file = self.base_path / "artifacts" / f"{artifact_id}_meta.json"
        if not meta_file.exists():
            return None

        metadata = json.loads(meta_file.read_text())
        artifact_file = self.base_path / "artifacts" / metadata["file"]

        if artifact_file.exists():
            return {
                "metadata": metadata,
                "content": artifact_file.read_text()
            }

        return None

    def list_artifacts(self) -> List[Dict]:
        """List all artifacts"""
        artifacts = []

        for meta_file in (self.base_path / "artifacts").glob("*_meta.json"):
            metadata = json.loads(meta_file.read_text())
            artifacts.append(metadata)

        artifacts.sort(key=lambda a: a.get("created", ""), reverse=True)

        return artifacts

    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow().isoformat()
        self.save()

    def get_summary(self) -> Dict:
        """Get session summary"""
        return {
            "session_id": self.session_id,
            "title": self.title,
            "participants": self.participants,
            "context": self.context,
            "status": self.status,
            "created": self.created,
            "last_activity": self.last_activity,
            "duration_minutes": self._calculate_duration(),
            "stats": {
                "conversation_chunks": self.conversation_chunk_count,
                "memories": self.memory_count,
                "tasks": self.task_count,
                "artifacts": self.artifact_count,
                "active_tasks": len(self.list_tasks("in_progress"))
            }
        }

    def _calculate_duration(self) -> float:
        """Calculate session duration in minutes"""
        if self.completed_at:
            end = datetime.fromisoformat(self.completed_at.replace('Z', ''))
        else:
            end = datetime.fromisoformat(self.last_activity.replace('Z', ''))

        start = datetime.fromisoformat(self.created.replace('Z', ''))
        return (end - start).total_seconds() / 60

    def save(self):
        """Save session metadata"""
        session_file = self.base_path / "session.json"
        session_data = {
            "session_id": self.session_id,
            "title": self.title,
            "participants": self.participants,
            "context": self.context,
            "status": self.status,
            "created": self.created,
            "last_activity": self.last_activity,
            "completed_at": self.completed_at,
            "conversation_chunk_count": self.conversation_chunk_count,
            "memory_count": self.memory_count,
            "task_count": self.task_count,
            "artifact_count": self.artifact_count
        }

        session_file.write_text(json.dumps(session_data, indent=2))

    @classmethod
    def load(cls, session_id: str) -> Optional['CollaborativeSession']:
        """Load existing session"""
        session_file = Path("sessions") / session_id / "session.json"

        if not session_file.exists():
            return None

        data = json.loads(session_file.read_text())

        session = cls.__new__(cls)
        session.session_id = data["session_id"]
        session.title = data["title"]
        session.participants = data["participants"]
        session.context = data.get("context", "")
        session.status = data["status"]
        session.created = data["created"]
        session.last_activity = data["last_activity"]
        session.completed_at = data.get("completed_at")
        session.conversation_chunk_count = data.get("conversation_chunk_count", 0)
        session.memory_count = data.get("memory_count", 0)
        session.task_count = data.get("task_count", 0)
        session.artifact_count = data.get("artifact_count", 0)
        session.base_path = Path("sessions") / session_id

        return session

    @classmethod
    def list_sessions(cls, status_filter: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """List all sessions"""
        sessions = []
        sessions_dir = Path("sessions")

        if not sessions_dir.exists():
            return []

        for session_dir in sessions_dir.iterdir():
            if not session_dir.is_dir():
                continue

            session_file = session_dir / "session.json"
            if not session_file.exists():
                continue

            data = json.loads(session_file.read_text())

            # Filter by status
            if status_filter and data.get("status") != status_filter:
                continue

            sessions.append(data)

        # Sort by last activity
        sessions.sort(key=lambda s: s.get("last_activity", ""), reverse=True)

        return sessions[:limit]
