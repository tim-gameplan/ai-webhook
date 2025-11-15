# LLM Conversation Integration Guide

This guide explains how to integrate Large Language Models (LLMs) with the AI Webhook Relay system to capture, organize, and act on insights from conversations.

## Table of Contents

1. [Overview](#overview)
2. [Use Cases](#use-cases)
3. [Message Schema](#message-schema)
4. [Integration Steps](#integration-steps)
5. [LLM Prompt Examples](#llm-prompt-examples)
6. [Client Setup](#client-setup)
7. [Reviewing Insights](#reviewing-insights)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The LLM Conversation Integration allows AI assistants to send structured insights during conversations with humans. These insights are automatically captured, categorized, and made actionable.

**Data Flow:**
```
Human ↔ LLM Conversation
         ↓ (LLM identifies insight)
    Send Webhook
         ↓
  Relay Server (validates API key)
         ↓
 Local Client (processes & stores)
         ↓
  llm_insights/ directory
         ↓
   CLI Review Tool
```

**Insight Types:**
- **action_item** - Tasks that need to be done
- **idea** - New concepts, features, or approaches
- **decision** - Important choices made during conversation
- **question** - Open questions that need answers
- **note** - General observations or reminders
- **risk** - Potential problems or concerns

---

## Use Cases

### 1. Project Planning
**Scenario:** Discussing a new feature with an LLM
- LLM captures action items automatically
- High-priority tasks get flagged
- Suggested task files are generated

### 2. Knowledge Management
**Scenario:** Brainstorming session
- LLM logs all ideas with context
- Ideas are tagged and categorized
- Review and build upon ideas later

### 3. Decision Tracking
**Scenario:** Architecture discussions
- Important decisions are recorded
- Context is preserved
- Easy to review what was decided and why

### 4. Risk Identification
**Scenario:** Code review or security discussion
- LLM flags potential issues
- Risks are prioritized
- Follow-up actions suggested

---

## Message Schema

### Complete Schema

```json
{
  "type": "llm_conversation_insight",
  "version": "1.0",
  "timestamp": "2025-11-15T10:30:00Z",
  "conversation": {
    "id": "conv_abc123",
    "participant": "user_name",
    "context": "Brief description of what we're discussing"
  },
  "insight": {
    "type": "action_item",
    "priority": "high",
    "title": "Short, descriptive title",
    "content": "Detailed description of the insight",
    "tags": ["tag1", "tag2", "tag3"],
    "suggested_followup": "What should happen next"
  },
  "metadata": {
    "llm_model": "claude-sonnet-4",
    "confidence": 0.95,
    "source": "natural_conversation"
  }
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Must be "llm_conversation_insight" |
| `version` | string | Schema version (currently "1.0") |
| `timestamp` | string | ISO 8601 timestamp |
| `conversation.id` | string | Unique conversation identifier |
| `insight.type` | string | One of: action_item, idea, decision, question, note, risk |
| `insight.priority` | string | One of: high, medium, low |
| `insight.title` | string | Brief title (50 chars recommended) |
| `insight.content` | string | Detailed description |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `conversation.participant` | string | Who's in the conversation |
| `conversation.context` | string | What topic is being discussed |
| `insight.tags` | array | Categorization tags |
| `insight.suggested_followup` | string | Recommended next action |
| `metadata.llm_model` | string | Which LLM generated this |
| `metadata.confidence` | float | Confidence level (0.0-1.0) |
| `metadata.source` | string | How the insight was generated |

---

## Integration Steps

### Step 1: Get API Key

The webhook relay uses API key authentication for custom webhooks.

Your API key is configured in Railway. To send insights, you'll need this key.

### Step 2: Send Test Insight

Test the integration with a simple curl command:

```bash
curl -X POST https://web-production-3d53a.up.railway.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -d '{
    "type": "llm_conversation_insight",
    "version": "1.0",
    "timestamp": "2025-11-15T10:30:00Z",
    "conversation": {
      "id": "test_001",
      "participant": "user",
      "context": "Testing LLM integration"
    },
    "insight": {
      "type": "note",
      "priority": "medium",
      "title": "Test insight",
      "content": "This is a test of the LLM integration system.",
      "tags": ["test"]
    },
    "metadata": {
      "llm_model": "test",
      "source": "manual"
    }
  }'
```

### Step 3: Run Local Client

Start the webhook client to receive insights:

```bash
cd client
export RELAY_SERVER_URL="wss://web-production-3d53a.up.railway.app/ws"
python client.py
```

You should see the test insight appear in your terminal and be saved to `llm_insights/notes/`.

### Step 4: Integrate with Your LLM

Add insight-sending capability to your LLM workflow. See [LLM Prompt Examples](#llm-prompt-examples) below.

---

## LLM Prompt Examples

### For Claude (Anthropic)

Add this to your system prompt or conversation:

```
You are an AI assistant helping with [project/task]. During our conversation, you should
identify and record important insights by sending webhooks to our tracking system.

When you identify one of the following, send a structured webhook:
- Action items (tasks that need to be done)
- Ideas (new concepts, features, or approaches)
- Decisions (important choices we make)
- Questions (things that need answers)
- Risks (potential problems)

Use this webhook endpoint: https://web-production-3d53a.up.railway.app/webhook

Format your webhook as a JSON POST request with header X-API-Key: YOUR_API_KEY

Schema:
{
  "type": "llm_conversation_insight",
  "version": "1.0",
  "timestamp": "ISO8601_TIMESTAMP",
  "conversation": {
    "id": "unique_conversation_id",
    "participant": "user_name",
    "context": "what we're discussing"
  },
  "insight": {
    "type": "action_item|idea|decision|question|note|risk",
    "priority": "high|medium|low",
    "title": "brief title",
    "content": "detailed description",
    "tags": ["relevant", "tags"],
    "suggested_followup": "what should happen next"
  },
  "metadata": {
    "llm_model": "claude-sonnet-4",
    "confidence": 0.0-1.0,
    "source": "natural_conversation"
  }
}

Priority Guidelines:
- high: Urgent, blocks progress, or critical decision
- medium: Important but not urgent
- low: Nice to have, future consideration

Send insights proactively but don't overdo it - focus on genuinely valuable captures.
```

### For GPT (OpenAI)

```
System: You are a helpful AI assistant with the ability to record important insights
from conversations. When you identify action items, ideas, decisions, or risks, you
can log them to a tracking system.

Available Tool: send_insight
Parameters:
- type: "action_item" | "idea" | "decision" | "question" | "note" | "risk"
- priority: "high" | "medium" | "low"
- title: string (brief description)
- content: string (detailed explanation)
- tags: string[] (categorization)
- suggested_followup: string (optional next steps)

Use send_insight() when you identify something worth tracking. Be selective - focus
on insights that add real value.
```

---

## Client Setup

### Install Dependencies

```bash
# In the ai-webhook/client directory
pip install -r requirements.txt

# For the CLI tool
pip install -r ../tools/requirements.txt
```

### Run the Client

```bash
# Connect to production server
export RELAY_SERVER_URL="wss://web-production-3d53a.up.railway.app/ws"
python client.py
```

The client will:
- Connect to the relay server
- Listen for both GitHub webhooks and LLM insights
- Automatically categorize and store insights
- Display formatted output in the terminal

### Directory Structure

Insights are saved to:
```
llm_insights/
├── action_items/    # Tasks to do
├── ideas/           # New concepts
├── decisions/       # Choices made
├── questions/       # Open questions
├── notes/           # General observations
└── risks/           # Potential problems
```

Each file is named: `YYYYMMDD_HHMMSS_priority_title-slug.json`

---

## Reviewing Insights

### CLI Tool

The `insights_cli.py` tool provides powerful insight management:

**List all insights:**
```bash
python tools/insights_cli.py list
```

**Filter by type:**
```bash
python tools/insights_cli.py list --type action_item
```

**Filter by priority:**
```bash
python tools/insights_cli.py list --priority high
```

**Recent insights:**
```bash
python tools/insights_cli.py list --days 7
```

**Statistics:**
```bash
python tools/insights_cli.py stats
```

**Export:**
```bash
# Export to JSON
python tools/insights_cli.py export --format json --output my_insights.json

# Export to CSV
python tools/insights_cli.py export --format csv --output insights.csv

# Export to Markdown
python tools/insights_cli.py export --format markdown --output insights.md
```

**Clean up old insights:**
```bash
python tools/insights_cli.py clean
```

### Manual Review

Insights are stored as JSON files, so you can also:

```bash
# View raw JSON
cat llm_insights/action_items/20251115_103000_high_implement-rate-limiting.json

# Search for specific term
grep -r "rate limiting" llm_insights/

# List high-priority items
find llm_insights -name "*_high_*"
```

---

## Best Practices

### For LLM Developers

**1. Be Selective**
- Don't capture every statement
- Focus on actionable or significant insights
- Quality over quantity

**2. Provide Context**
- Fill in conversation.context with what's being discussed
- Use descriptive titles
- Add relevant tags

**3. Prioritize Appropriately**
- high: Urgent, blocking, or critical
- medium: Important but not urgent
- low: Nice to have, future consideration

**4. Suggest Follow-ups**
- What should happen next?
- Who should be notified?
- Related tasks or dependencies?

**5. Use Consistent IDs**
- Use the same conversation.id for related insights
- Makes it easy to track conversation threads
- Enables better organization

### For System Administrators

**1. Monitor Insight Volume**
- Use `insights_cli.py stats` regularly
- Watch for spam or misconfiguration
- Adjust LLM prompts if too noisy

**2. Regular Exports**
- Export insights weekly/monthly
- Back up to external systems
- Integrate with task management tools

**3. Clean Up Periodically**
- Archive old insights
- Remove duplicates
- Keep system performant

**4. Secure Your API Key**
- Rotate keys periodically
- Monitor for unauthorized use
- Revoke if compromised

---

## Troubleshooting

### Insights Not Appearing

**Check client is running:**
```bash
# Should show "Connected! Waiting for webhooks..."
python client/client.py
```

**Check webhook reached server:**
- Look at Railway logs
- Should see HTTP 200 response
- Verify API key is correct

**Check handler is loaded:**
- Client should show: "📁 LLM Insights directory: ..."
- If you see "⚠️ LLM insights handler not available", reinstall dependencies

### Validation Errors

**"Missing required field":**
- Check your JSON includes all required fields
- Verify field names match exactly (case-sensitive)

**"Invalid insight type":**
- Must be one of: action_item, idea, decision, question, note, risk
- Check for typos (e.g., "action-item" vs "action_item")

**"Invalid priority":**
- Must be: high, medium, or low
- All lowercase

### CLI Tool Issues

**"click package not installed":**
```bash
pip install -r tools/requirements.txt
```

**"No insights found":**
- Check llm_insights/ directory exists
- Verify client has received and saved insights
- Try `llm_insights/`

### Performance Issues

**Too many insights:**
- Use `insights_cli.py clean` to remove old ones
- Be more selective in LLM prompts
- Filter by priority when reviewing

**Slow client:**
- Insights are processed synchronously
- Consider batching if sending many at once
- Monitor client resource usage

---

## Examples

### Example 1: Action Item

```json
{
  "type": "llm_conversation_insight",
  "version": "1.0",
  "timestamp": "2025-11-15T14:30:00Z",
  "conversation": {
    "id": "feature_planning_001",
    "participant": "tim",
    "context": "Planning rate limiting feature"
  },
  "insight": {
    "type": "action_item",
    "priority": "high",
    "title": "Implement rate limiting for webhook endpoint",
    "content": "Add rate limiting to prevent abuse of the /webhook endpoint. User suggested using slowapi library. Should limit to 100 requests per hour per IP address.",
    "tags": ["security", "infrastructure", "rate-limiting"],
    "suggested_followup": "Create task: security-004-implement-rate-limiting"
  },
  "metadata": {
    "llm_model": "claude-sonnet-4",
    "confidence": 0.95,
    "source": "natural_conversation"
  }
}
```

### Example 2: Idea

```json
{
  "type": "llm_conversation_insight",
  "version": "1.0",
  "timestamp": "2025-11-15T15:45:00Z",
  "conversation": {
    "id": "brainstorm_session_042",
    "participant": "team",
    "context": "Brainstorming webhook visualization features"
  },
  "insight": {
    "type": "idea",
    "priority": "medium",
    "title": "Web dashboard for webhook visualization",
    "content": "Create a web-based dashboard that shows real-time webhook activity, with graphs of volume over time, event type breakdown, and a live feed of recent webhooks.",
    "tags": ["feature", "ui", "visualization", "dashboard"],
    "suggested_followup": "Create mockups, estimate effort"
  },
  "metadata": {
    "llm_model": "claude-sonnet-4",
    "confidence": 0.85,
    "source": "brainstorming"
  }
}
```

### Example 3: Risk

```json
{
  "type": "llm_conversation_insight",
  "version": "1.0",
  "timestamp": "2025-11-15T16:20:00Z",
  "conversation": {
    "id": "security_review_003",
    "participant": "tim",
    "context": "Reviewing webhook security implementation"
  },
  "insight": {
    "type": "risk",
    "priority": "high",
    "title": "API key transmitted in headers could be logged",
    "content": "The API key is sent in X-API-Key header with every request. If server logs include headers, the key could be exposed in log files. Need to ensure Railway logs don't capture sensitive headers.",
    "tags": ["security", "privacy", "logging"],
    "suggested_followup": "Verify Railway logging configuration, consider key rotation"
  },
  "metadata": {
    "llm_model": "claude-sonnet-4",
    "confidence": 0.90,
    "source": "security_review"
  }
}
```

---

## Integration with Other Systems

### Notion

Export insights to CSV and import to Notion database:
```bash
python tools/insights_cli.py export --format csv --output insights.csv
# Import insights.csv to Notion
```

### Task Management

High-priority action items can auto-generate task files. See `client/handlers/llm_insights.py` for implementation.

### Slack/Discord

Forward high-priority insights to team channels:
```python
# Add to llm_insights.py
if insight_type == "action_item" and priority == "high":
    send_to_slack(insight)
```

---

## API Reference

See `client/handlers/llm_insights.py` for complete implementation details.

**Key Functions:**
- `validate_llm_insight(webhook_data)` - Validates message schema
- `LLMInsightHandler.handle_insight(webhook_data)` - Processes and stores insight
- `LLMInsightHandler._suggest_task_creation(insight)` - Auto-task generation

---

## Contributing

Ideas for improving LLM integration:
- Additional insight types
- Better auto-categorization
- Integration with more tools
- Conversation threading
- Insight summarization

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development workflow.

---

*Last updated: 2025-11-15*
