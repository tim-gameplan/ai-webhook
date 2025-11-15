"""
Base Agent Class

All collaborative session agents inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class AgentResult:
    """Result returned by agent execution"""
    success: bool
    message: str = ""
    data: Dict[str, Any] = None
    artifact_id: Optional[str] = None
    artifact_path: Optional[str] = None
    updates_context: bool = False
    context_changes: Dict[str, Any] = None
    trigger_agents: list = None  # List of other agents to trigger
    error: Optional[str] = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if self.context_changes is None:
            self.context_changes = {}
        if self.trigger_agents is None:
            self.trigger_agents = []

    def to_dict(self):
        return asdict(self)


class BaseAgent(ABC):
    """
    Base class for all collaborative session agents.

    Agents process specific types of commands and can:
    - Access session state
    - Store data
    - Trigger other agents
    - Return results
    """

    def __init__(self, name: str):
        self.name = name
        self.created = datetime.utcnow().isoformat()

    @abstractmethod
    def can_handle(self, command: str, data: Dict[str, Any]) -> bool:
        """
        Determine if this agent can handle the given command.

        Args:
            command: The command name
            data: The command data

        Returns:
            True if agent can handle this command
        """
        pass

    @abstractmethod
    def execute(self, command: str, data: Dict[str, Any], session) -> AgentResult:
        """
        Execute the command.

        Args:
            command: The command to execute
            data: Command data
            session: The CollaborativeSession instance

        Returns:
            AgentResult with execution outcome
        """
        pass

    def log(self, message: str, level: str = "info"):
        """Log a message from this agent"""
        emoji = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "processing": "⚙️"
        }.get(level, "📝")

        print(f"{emoji} [{self.name}] {message}")

    def save_state(self, session, state: Dict[str, Any]):
        """Save agent state to session"""
        import json
        from pathlib import Path

        state_file = session.base_path / "agents" / f"{self.name}_state.json"
        state_data = {
            "agent": self.name,
            "timestamp": datetime.utcnow().isoformat(),
            "state": state
        }
        state_file.write_text(json.dumps(state_data, indent=2))

    def load_state(self, session) -> Optional[Dict[str, Any]]:
        """Load agent state from session"""
        import json
        from pathlib import Path

        state_file = session.base_path / "agents" / f"{self.name}_state.json"
        if state_file.exists():
            data = json.loads(state_file.read_text())
            return data.get("state")
        return None
