"""
Collaborative Session Manager

Central coordinator for collaborative sessions. Handles:
- Session lifecycle (create, resume, pause, complete)
- Command routing to appropriate agents
- Batch command processing
- Agent coordination
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from .models.session import CollaborativeSession, AgentTask
from .agents.base_agent import BaseAgent, AgentResult
from .agents.conversation_processor import ConversationProcessorAgent
from .agents.memory_keeper import MemoryKeeperAgent


class SessionManager:
    """Manages collaborative sessions and coordinates agents"""

    def __init__(self):
        self.sessions: Dict[str, CollaborativeSession] = {}
        self.agents: List[BaseAgent] = []

        # Register default agents
        self._register_default_agents()

        print("📋 Session Manager initialized")
        print(f"   Registered agents: {[a.name for a in self.agents]}")

    def _register_default_agents(self):
        """Register default agents"""
        self.agents = [
            ConversationProcessorAgent(),
            MemoryKeeperAgent(),
            # More agents can be added here
        ]

    def process_command(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a collaborative session command from webhook

        Args:
            webhook_data: The webhook payload

        Returns:
            Response dictionary
        """
        command = webhook_data.get("command")
        session_id = webhook_data.get("session_id")
        data = webhook_data.get("data", {})
        feedback_mode = webhook_data.get("feedback_mode", "async")

        print(f"\n📬 Processing command: {command}")
        if session_id:
            print(f"   Session: {session_id}")

        # Handle session management commands
        if command in ["create_session", "resume_session", "list_sessions", "get_session_summary"]:
            return self._handle_session_command(command, session_id, data)

        # Handle batch commands
        if command == "batch":
            return self._handle_batch(session_id, data)

        # Get or load session
        session = self._get_session(session_id)
        if not session:
            return {
                "status": "error",
                "message": f"Session '{session_id}' not found. Create it first with create_session."
            }

        # Route to appropriate agent
        result = self._route_to_agent(command, data, session)

        # Build response
        response = {
            "type": "collaborative_session_response",
            "command": command,
            "session_id": session_id,
            "status": "success" if result.success else "error",
            "message": result.message,
            "data": result.data
        }

        if result.error:
            response["error"] = result.error

        return response

    def _handle_session_command(self, command: str, session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle session lifecycle commands"""
        if command == "create_session":
            return self._create_session(session_id, data)

        elif command == "resume_session":
            session = self._get_session(session_id)
            if not session:
                return {
                    "status": "error",
                    "message": f"Session '{session_id}' not found"
                }

            print(f"🔄 Resumed session: {session.title}")
            return {
                "status": "success",
                "message": f"Session '{session_id}' resumed",
                "data": session.get_summary()
            }

        elif command == "list_sessions":
            filter_status = data.get("filter", "all")
            limit = data.get("limit", 20)

            status_filter = None if filter_status == "all" else filter_status
            sessions = CollaborativeSession.list_sessions(status_filter, limit)

            print(f"📋 Listed {len(sessions)} sessions")
            return {
                "status": "success",
                "data": {
                    "sessions": sessions,
                    "count": len(sessions)
                }
            }

        elif command == "get_session_summary":
            session = self._get_session(session_id)
            if not session:
                return {
                    "status": "error",
                    "message": f"Session '{session_id}' not found"
                }

            return {
                "status": "success",
                "data": session.get_summary()
            }

        return {
            "status": "error",
            "message": f"Unknown session command: {command}"
        }

    def _create_session(self, session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new session"""
        # Check if already exists
        if session_id in self.sessions or CollaborativeSession.load(session_id):
            return {
                "status": "error",
                "message": f"Session '{session_id}' already exists. Use resume_session to continue."
            }

        title = data.get("title", "")
        participants = data.get("participants", [])
        context = data.get("context", "")

        session = CollaborativeSession(session_id, title, participants)
        session.context = context
        session.save()

        self.sessions[session_id] = session

        print(f"✨ Created session: {session.title}")
        print(f"   Participants: {', '.join(participants) if participants else 'none'}")

        return {
            "status": "success",
            "message": f"Session '{session_id}' created",
            "data": session.get_summary()
        }

    def _handle_batch(self, session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle batch of commands"""
        commands = data.get("commands", [])
        conversation_chunk = data.get("conversation_chunk")

        results = []

        # Process conversation chunk first if provided
        if conversation_chunk:
            chunk_result = self.process_command({
                "command": "append_conversation",
                "session_id": session_id,
                "data": {"conversation_chunk": conversation_chunk}
            })
            results.append(chunk_result)

        # Process each command
        session = self._get_session(session_id)
        if not session:
            return {
                "status": "error",
                "message": f"Session '{session_id}' not found"
            }

        for cmd in commands:
            command = cmd.get("command")
            cmd_data = cmd.get("data", {})

            result = self._route_to_agent(command, cmd_data, session)
            results.append({
                "command": command,
                "status": "success" if result.success else "error",
                "message": result.message
            })

        return {
            "status": "success",
            "message": f"Batch processed: {len(results)} commands",
            "data": {
                "results": results,
                "processed": len(results)
            }
        }

    def _route_to_agent(self, command: str, data: Dict[str, Any], session: CollaborativeSession) -> AgentResult:
        """Route command to appropriate agent"""
        # Find agent that can handle this command
        for agent in self.agents:
            if agent.can_handle(command, data):
                return agent.execute(command, data, session)

        # No agent found
        return AgentResult(
            success=False,
            error=f"No agent available to handle command: {command}"
        )

    def _get_session(self, session_id: str) -> Optional[CollaborativeSession]:
        """Get session, loading from disk if needed"""
        # Check in-memory cache
        if session_id in self.sessions:
            return self.sessions[session_id]

        # Try to load from disk
        session = CollaborativeSession.load(session_id)
        if session:
            self.sessions[session_id] = session
            return session

        return None


# Global session manager instance
_session_manager = None


def get_session_manager() -> SessionManager:
    """Get or create global session manager"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
