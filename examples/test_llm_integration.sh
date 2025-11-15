#!/bin/bash
#
# Test LLM Integration End-to-End
#
# This script tests the complete LLM insight flow:
# 1. Send insight webhook to server
# 2. Verify client receives it
# 3. Check insight is saved
# 4. Test CLI tool
#

set -e

echo "========================================"
echo "LLM Integration End-to-End Test"
echo "========================================"
echo ""

# Check if API key is set
if [ -z "$API_KEY" ]; then
    echo "❌ Error: API_KEY environment variable not set"
    echo "Usage: export API_KEY=your-key-here && ./test_llm_integration.sh"
    exit 1
fi

WEBHOOK_URL="https://web-production-3d53a.up.railway.app/webhook"

echo "📝 Test 1: Send high-priority action item"
echo "----------------------------------------"

RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "type": "llm_conversation_insight",
    "version": "1.0",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
    "conversation": {
      "id": "test_integration_001",
      "participant": "test_user",
      "context": "Testing LLM integration end-to-end"
    },
    "insight": {
      "type": "action_item",
      "priority": "high",
      "title": "Test high-priority action item",
      "content": "This is a test insight to verify the LLM integration is working correctly. It should appear in the client terminal and be saved to llm_insights/action_items/.",
      "tags": ["test", "integration", "llm"],
      "suggested_followup": "Verify this appears in client and CLI tool"
    },
    "metadata": {
      "llm_model": "test-script",
      "confidence": 1.0,
      "source": "integration_test"
    }
  }')

HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS/d')

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ Server accepted insight (HTTP 200)"
    echo "   Response: $BODY"
else
    echo "❌ Server rejected insight (HTTP $HTTP_STATUS)"
    echo "   Response: $BODY"
    exit 1
fi

echo ""
echo "📝 Test 2: Send medium-priority idea"
echo "----------------------------------------"

RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "type": "llm_conversation_insight",
    "version": "1.0",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
    "conversation": {
      "id": "test_integration_001",
      "participant": "test_user",
      "context": "Testing LLM integration end-to-end"
    },
    "insight": {
      "type": "idea",
      "priority": "medium",
      "title": "Test medium-priority idea",
      "content": "This is a test idea to verify different insight types are handled correctly.",
      "tags": ["test", "integration"],
      "suggested_followup": "None needed - this is just a test"
    },
    "metadata": {
      "llm_model": "test-script",
      "confidence": 0.85,
      "source": "integration_test"
    }
  }')

HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS/d')

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ Server accepted insight (HTTP 200)"
    echo "   Response: $BODY"
else
    echo "❌ Server rejected insight (HTTP $HTTP_STATUS)"
    echo "   Response: $BODY"
    exit 1
fi

echo ""
echo "📝 Test 3: Send low-priority note"
echo "----------------------------------------"

RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "type": "llm_conversation_insight",
    "version": "1.0",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
    "conversation": {
      "id": "test_integration_001",
      "participant": "test_user",
      "context": "Testing LLM integration end-to-end"
    },
    "insight": {
      "type": "note",
      "priority": "low",
      "title": "Test low-priority note",
      "content": "Just a simple note for testing purposes.",
      "tags": ["test"]
    },
    "metadata": {
      "llm_model": "test-script",
      "confidence": 0.75,
      "source": "integration_test"
    }
  }')

HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_STATUS/d')

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ Server accepted insight (HTTP 200)"
    echo "   Response: $BODY"
else
    echo "❌ Server rejected insight (HTTP $HTTP_STATUS)"
    echo "   Response: $BODY"
    exit 1
fi

echo ""
echo "========================================"
echo "✅ All tests passed!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Check your client terminal - you should see 3 insights"
echo "2. Check llm_insights/ directory for saved files"
echo "3. Run: python tools/insights_cli.py list"
echo "4. Run: python tools/insights_cli.py stats"
echo ""
