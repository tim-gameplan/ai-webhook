"""
Memory Keeper Agent

Handles memory storage and retrieval for collaborative sessions.
Allows LLMs to store and retrieve context across conversations.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Dict, Any
from agents.base_agent import BaseAgent, AgentResult


class MemoryKeeperAgent(BaseAgent):
    """Manages session memories"""

    def __init__(self):
        super().__init__("memory_keeper")

    def can_handle(self, command: str, data: Dict[str, Any]) -> bool:
        return command in ["store_memory", "retrieve_memory", "query_memories"]

    def execute(self, command: str, data: Dict[str, Any], session) -> AgentResult:
        """Execute memory command"""
        if command == "store_memory":
            return self._store_memory(data, session)
        elif command == "retrieve_memory":
            return self._retrieve_memory(data, session)
        elif command == "query_memories":
            return self._query_memories(data, session)

        return AgentResult(success=False, error=f"Unknown command: {command}")

    def _store_memory(self, data: Dict[str, Any], session) -> AgentResult:
        """Store a memory"""
        memory_type = data.get("type", "general")
        key = data.get("key")
        content = data.get("content")
        tags = data.get("tags", [])

        if not key:
            # Auto-generate key if not provided
            key = f"{memory_type}_{session.memory_count + 1}"

        # Store in session
        session.add_memory(memory_type, key, content, tags)

        self.log(f"Stored memory: {key} (type: {memory_type})", "success")

        return AgentResult(
            success=True,
            message=f"Memory '{key}' stored",
            data={"key": key, "type": memory_type}
        )

    def _retrieve_memory(self, data: Dict[str, Any], session) -> AgentResult:
        """Retrieve a specific memory by key"""
        key = data.get("key")

        if not key:
            return AgentResult(success=False, error="Memory key required")

        memory = session.get_memory(key)

        if not memory:
            return AgentResult(
                success=False,
                error=f"Memory '{key}' not found"
            )

        self.log(f"Retrieved memory: {key}", "success")

        return AgentResult(
            success=True,
            message=f"Memory '{key}' retrieved",
            data={"memory": memory}
        )

    def _query_memories(self, data: Dict[str, Any], session) -> AgentResult:
        """Query memories with filters"""
        filter_data = data.get("filter", {})
        memory_type = filter_data.get("type")
        tags = filter_data.get("tags", [])
        limit = data.get("limit", 10)

        memories = session.query_memories(memory_type, tags, limit)

        self.log(f"Found {len(memories)} memories", "success")

        return AgentResult(
            success=True,
            message=f"Found {len(memories)} memories",
            data={
                "memories": memories,
                "count": len(memories)
            }
        )
