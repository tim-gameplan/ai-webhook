#!/usr/bin/env python3
"""
Example: Send LLM Conversation Insight

This script demonstrates how to send a structured insight to the webhook relay system.
Use this as a template for integrating LLM insights into your own applications.
"""

import requests
import json
from datetime import datetime
import os
import sys

# Configuration
WEBHOOK_URL = "https://web-production-3d53a.up.railway.app/webhook"
API_KEY = os.getenv("API_KEY", "")  # Get from environment variable

if not API_KEY:
    print("Error: API_KEY environment variable not set")
    print("Usage: export API_KEY=your-key-here && python send_insight.py")
    sys.exit(1)


def send_insight(
    insight_type: str,
    priority: str,
    title: str,
    content: str,
    conversation_id: str,
    conversation_context: str = "",
    tags: list = None,
    suggested_followup: str = "",
    participant: str = "user",
    llm_model: str = "custom",
    confidence: float = 1.0
):
    """
    Send an insight to the webhook relay

    Args:
        insight_type: One of: action_item, idea, decision, question, note, risk
        priority: One of: high, medium, low
        title: Brief descriptive title
        content: Detailed explanation
        conversation_id: Unique ID for this conversation
        conversation_context: What's being discussed
        tags: List of categorization tags
        suggested_followup: Recommended next steps
        participant: Who's in the conversation
        llm_model: Which LLM generated this
        confidence: Confidence level (0.0-1.0)

    Returns:
        Response object from requests
    """

    # Build the payload
    payload = {
        "type": "llm_conversation_insight",
        "version": "1.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "conversation": {
            "id": conversation_id,
            "participant": participant,
        },
        "insight": {
            "type": insight_type,
            "priority": priority,
            "title": title,
            "content": content,
        },
        "metadata": {
            "llm_model": llm_model,
            "confidence": confidence,
            "source": "programmatic"
        }
    }

    # Add optional fields
    if conversation_context:
        payload["conversation"]["context"] = conversation_context

    if tags:
        payload["insight"]["tags"] = tags

    if suggested_followup:
        payload["insight"]["suggested_followup"] = suggested_followup

    # Send the webhook
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }

    try:
        response = requests.post(WEBHOOK_URL, headers=headers, json=payload)
        response.raise_for_status()

        print(f"✅ Insight sent successfully!")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")

        return response

    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending insight: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        raise


# Example usage
if __name__ == "__main__":
    print("Sending example LLM conversation insight...\n")

    # Example 1: High-priority action item
    send_insight(
        insight_type="action_item",
        priority="high",
        title="Implement rate limiting for webhook endpoint",
        content=(
            "The /webhook endpoint currently has no rate limiting, which could allow "
            "abuse or DoS attacks. We should implement rate limiting using a library "
            "like slowapi to limit requests per IP address (suggested: 100/hour)."
        ),
        conversation_id="example_conv_001",
        conversation_context="Security improvements for webhook system",
        tags=["security", "infrastructure", "rate-limiting"],
        suggested_followup="Create task: security-004-implement-rate-limiting",
        participant="example_user",
        llm_model="example-script",
        confidence=0.95
    )

    print("\n" + "="*80 + "\n")

    # Example 2: Medium-priority idea
    send_insight(
        insight_type="idea",
        priority="medium",
        title="Add web dashboard for webhook visualization",
        content=(
            "A web-based dashboard could provide real-time visibility into webhook "
            "activity. Features could include: volume graphs over time, event type "
            "breakdown, live feed of recent webhooks, connection status for clients, "
            "and basic analytics."
        ),
        conversation_id="example_conv_001",
        conversation_context="Brainstorming future features",
        tags=["feature", "ui", "visualization", "dashboard"],
        suggested_followup="Create mockups and estimate development effort",
        participant="example_user",
        llm_model="example-script",
        confidence=0.80
    )

    print("\n" + "="*80 + "\n")

    # Example 3: Low-priority note
    send_insight(
        insight_type="note",
        priority="low",
        title="User prefers detailed logging",
        content=(
            "During our conversation, the user expressed preference for detailed "
            "logging output that includes emoji markers for easy visual scanning. "
            "This style should be maintained in future features."
        ),
        conversation_id="example_conv_001",
        conversation_context="User interface preferences",
        tags=["ux", "logging", "preferences"],
        participant="example_user",
        llm_model="example-script",
        confidence=0.90
    )

    print("\n✨ All examples sent! Check your client terminal or llm_insights/ directory.\n")
