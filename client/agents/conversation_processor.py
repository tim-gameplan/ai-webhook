"""
Conversation Processor Agent

Handles large conversation chunks sent by LLMs, including:
- Saving raw conversation
- Extracting structured items
- Building full transcript
- Optional re-analysis
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Dict, Any
from datetime import datetime
from agents.base_agent import BaseAgent, AgentResult
from models.session import ConversationChunk


class ConversationProcessorAgent(BaseAgent):
    """Processes and stores conversation chunks"""

    def __init__(self):
        super().__init__("conversation_processor")

    def can_handle(self, command: str, data: Dict[str, Any]) -> bool:
        return command == "append_conversation"

    def execute(self, command: str, data: Dict[str, Any], session) -> AgentResult:
        """Process conversation chunk"""
        chunk_data = data.get("conversation_chunk", {})

        # Generate chunk ID
        chunk_id = f"{session.conversation_chunk_count + 1:03d}_{datetime.utcnow().strftime('%H%M%S')}"

        # Create conversation chunk
        chunk = ConversationChunk(
            chunk_id=chunk_id,
            start_time=chunk_data.get("start_time"),
            end_time=chunk_data.get("end_time"),
            format=chunk_data.get("format", "dialogue"),
            content=chunk_data.get("content", ""),
            participants=chunk_data.get("participants", session.participants),
            extracted_items=chunk_data.get("extracted_items", {}),
            metadata=chunk_data.get("metadata", {})
        )

        # Save to session
        session.add_conversation_chunk(chunk)

        content_size = len(chunk.content)
        self.log(f"Saved conversation chunk {chunk_id} ({content_size} chars)", "success")

        # Process extracted items if provided
        items_processed = 0
        if chunk.extracted_items:
            items_processed = self._process_extracted_items(chunk.extracted_items, session)

        # Build response
        result = AgentResult(
            success=True,
            message=f"Conversation chunk {chunk_id} processed",
            data={
                "chunk_id": chunk_id,
                "content_size": content_size,
                "extracted_items_processed": items_processed
            }
        )

        return result

    def _process_extracted_items(self, extracted: Dict[str, Any], session) -> int:
        """Process extracted items from conversation"""
        count = 0

        # Process ideas
        for idea in extracted.get("ideas", []):
            if isinstance(idea, str):
                session.add_memory("idea", f"idea_{session.memory_count + 1}", idea, tags=["extracted"])
            else:
                session.add_memory("idea", f"idea_{session.memory_count + 1}", idea, tags=["extracted"])
            count += 1

        # Process decisions
        for decision in extracted.get("decisions", []):
            if isinstance(decision, str):
                session.add_memory("decision", f"decision_{session.memory_count + 1}", decision, tags=["extracted"])
            else:
                session.add_memory("decision", f"decision_{session.memory_count + 1}", decision, tags=["extracted"])
            count += 1

        # Process questions
        for question in extracted.get("questions", []):
            session.add_memory("question", f"question_{session.memory_count + 1}", question, tags=["extracted"])
            count += 1

        # Process action items
        for action in extracted.get("action_items", []):
            session.add_memory("action_item", f"action_{session.memory_count + 1}", action, tags=["extracted"])
            count += 1

        if count > 0:
            self.log(f"Extracted and stored {count} items from conversation", "success")

        return count
