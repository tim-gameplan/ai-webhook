"""
Handler for LLM conversation insights

Processes structured insights from LLM conversations and stores them
in an organized format for later review and action.
"""

from datetime import datetime
from pathlib import Path
import json
from typing import Dict, Optional


class LLMInsightHandler:
    """Handler for LLM conversation insights"""

    def __init__(self, base_dir: str = "llm_insights"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

        # Create subdirectories by insight type
        self.type_dirs = {
            "action_item": self.base_dir / "action_items",
            "idea": self.base_dir / "ideas",
            "decision": self.base_dir / "decisions",
            "question": self.base_dir / "questions",
            "note": self.base_dir / "notes",
            "risk": self.base_dir / "risks"
        }

        for dir_path in self.type_dirs.values():
            dir_path.mkdir(exist_ok=True)

        print(f"📁 LLM Insights directory: {self.base_dir.absolute()}")

    def handle_insight(self, webhook_data: dict) -> None:
        """Process and store LLM insight"""
        insight = webhook_data.get("insight", {})
        conversation = webhook_data.get("conversation", {})

        insight_type = insight.get("type", "note")
        priority = insight.get("priority", "medium")
        conv_id = conversation.get("id", "unknown")

        # Generate filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        title_slug = self._slugify(insight.get("title", "untitled"))[:50]
        filename = f"{timestamp}_{priority}_{title_slug}.json"

        # Determine directory
        type_dir = self.type_dirs.get(insight_type, self.base_dir / "notes")
        filepath = type_dir / filename

        # Save insight
        with open(filepath, 'w') as f:
            json.dump(webhook_data, f, indent=2)

        # Log to console
        self._log_insight(insight, conversation, str(filepath))

        # Auto-generate task suggestion for high-priority action items
        if insight_type == "action_item" and priority == "high":
            self._suggest_task_creation(insight, conversation)

    def _log_insight(self, insight: dict, conversation: dict, filepath: str) -> None:
        """Pretty print insight to console"""
        type_emoji = {
            "action_item": "✅",
            "idea": "💡",
            "decision": "🎯",
            "question": "❓",
            "note": "📝",
            "risk": "⚠️"
        }

        insight_type = insight.get("type", "note")
        priority = insight.get("priority", "medium")
        title = insight.get("title", "Untitled")
        content = insight.get("content", "")
        context = conversation.get("context", "")

        emoji = type_emoji.get(insight_type, "📌")
        priority_marker = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"

        print(f"\n{emoji} {priority_marker} {insight_type.replace('_', ' ').upper()}: {title}")
        if context:
            print(f"   📍 Context: {context}")

        # Print content (truncated if long)
        if content:
            content_preview = content if len(content) <= 150 else content[:147] + "..."
            print(f"   💬 {content_preview}")

        if insight.get('tags'):
            tags_str = ", ".join(insight['tags'])
            print(f"   🏷️  Tags: {tags_str}")

        if insight.get('suggested_followup'):
            print(f"   💭 Suggested: {insight['suggested_followup']}")

        print(f"   💾 Saved: {filepath}")

    def _suggest_task_creation(self, insight: dict, conversation: dict) -> None:
        """Suggest task file creation for high-priority action items"""
        followup = insight.get("suggested_followup", "")
        title = insight.get("title", "")

        print(f"\n   🤖 HIGH PRIORITY ACTION ITEM DETECTED")
        print(f"   📋 Consider creating a task file in tasks/ directory")

        if followup:
            print(f"   💡 Suggestion: {followup}")

        # Extract tags to suggest category
        tags = insight.get("tags", [])
        category_map = {
            "security": "security",
            "feature": "feature",
            "bug": "bugfix",
            "infrastructure": "devops",
            "deployment": "devops",
            "docs": "docs",
            "documentation": "docs",
            "test": "test",
            "testing": "test",
            "performance": "perf",
            "refactor": "refactor"
        }

        suggested_category = None
        for tag in tags:
            if tag.lower() in category_map:
                suggested_category = category_map[tag.lower()]
                break

        if suggested_category:
            # Find next task number (would need to scan tasks/ directory)
            print(f"   📝 Suggested category: {suggested_category}")

    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug"""
        import re
        # Convert to lowercase and replace non-alphanumeric with hyphens
        slug = re.sub(r'[^a-z0-9]+', '-', text.lower())
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        return slug


def validate_llm_insight(webhook_data: dict) -> tuple[bool, Optional[str]]:
    """
    Validate LLM insight webhook structure

    Returns (is_valid, error_message)
    """
    required_fields = ["type", "version", "timestamp", "conversation", "insight"]

    # Check top-level fields
    for field in required_fields:
        if field not in webhook_data:
            return False, f"Missing required field: {field}"

    # Check conversation fields
    conversation = webhook_data.get("conversation", {})
    if not conversation.get("id"):
        return False, "Missing conversation.id"

    # Check insight fields
    insight = webhook_data.get("insight", {})
    required_insight_fields = ["type", "priority", "title", "content"]
    for field in required_insight_fields:
        if field not in insight:
            return False, f"Missing insight.{field}"

    # Validate insight type
    valid_types = ["action_item", "idea", "decision", "question", "note", "risk"]
    if insight["type"] not in valid_types:
        return False, f"Invalid insight type: {insight['type']}. Must be one of: {valid_types}"

    # Validate priority
    valid_priorities = ["high", "medium", "low"]
    if insight["priority"] not in valid_priorities:
        return False, f"Invalid priority: {insight['priority']}. Must be one of: {valid_priorities}"

    return True, None
