#!/usr/bin/env python3
"""
End-to-End Webhook Testing Script

Tests the complete flow:
GitHub/API → Relay Server → WebSocket → Client → Postgres

Usage:
    python3 test_webhooks_e2e.py
"""
import os
import sys
import json
import requests
import time
from datetime import datetime
from pathlib import Path

# Load environment
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

# Configuration
# Extract base URL from WebSocket URL
ws_url = os.getenv('RELAY_SERVER_URL', 'wss://web-production-3d53a.up.railway.app/ws')
base_url = ws_url.replace('wss://', 'https://').replace('ws://', 'http://').replace('/ws', '')
WEBHOOK_URL = f"{base_url}/webhook"
API_KEY = os.getenv('API_KEY')

if not API_KEY:
    print("❌ API_KEY not found in .env")
    sys.exit(1)

print("=" * 70)
print("End-to-End Webhook Testing")
print("=" * 70)
print(f"Webhook URL: {WEBHOOK_URL}")
print(f"API Key: {API_KEY[:10]}...")
print()

# Test session ID
SESSION_ID = f"e2e_test_{int(time.time())}"

def send_webhook(payload: dict, description: str) -> bool:
    """Send webhook and check response"""
    print(f"\n{'=' * 70}")
    print(f"TEST: {description}")
    print(f"{'=' * 70}")
    print(f"Payload:")
    print(json.dumps(payload, indent=2))

    try:
        response = requests.post(
            WEBHOOK_URL,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": API_KEY
            },
            json=payload,
            timeout=10
        )

        print(f"\nResponse Status: {response.status_code}")

        if response.status_code == 200:
            try:
                resp_data = response.json()
                print(f"Response:")
                print(json.dumps(resp_data, indent=2))
                print("✅ SUCCESS")
                return True
            except:
                print(f"Response Text: {response.text}")
                print("✅ SUCCESS (non-JSON response)")
                return True
        else:
            print(f"❌ FAILED - Status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ FAILED - Exception: {e}")
        return False

def verify_in_database(session_id: str):
    """Verify data was stored in Postgres"""
    print(f"\n{'=' * 70}")
    print("DATABASE VERIFICATION")
    print(f"{'=' * 70}")

    sys.path.insert(0, str(Path(__file__).parent / 'client'))

    try:
        from storage.postgres_backend import PostgresBackend

        # Initialize pool
        PostgresBackend.initialize_pool()

        with PostgresBackend.get_connection() as conn:
            with conn.cursor() as cur:
                # Check session exists
                cur.execute('SELECT COUNT(*) FROM sessions WHERE id = %s', (session_id,))
                session_count = cur.fetchone()[0]

                if session_count == 0:
                    print(f"❌ Session '{session_id}' not found in database")
                    return False

                print(f"✅ Session '{session_id}' found")

                # Check related data
                cur.execute('SELECT COUNT(*) FROM conversation_chunks WHERE session_id = %s', (session_id,))
                chunk_count = cur.fetchone()[0]
                print(f"   - Conversation chunks: {chunk_count}")

                cur.execute('SELECT COUNT(*) FROM memories WHERE session_id = %s', (session_id,))
                memory_count = cur.fetchone()[0]
                print(f"   - Memories: {memory_count}")

                cur.execute('SELECT COUNT(*) FROM tasks WHERE session_id = %s', (session_id,))
                task_count = cur.fetchone()[0]
                print(f"   - Tasks: {task_count}")

                cur.execute('SELECT COUNT(*) FROM artifacts WHERE session_id = %s', (session_id,))
                artifact_count = cur.fetchone()[0]
                print(f"   - Artifacts: {artifact_count}")

                return True

    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_tests():
    """Run all webhook tests"""
    results = []

    # Test 1: Create Session
    results.append(send_webhook({
        "type": "collaborative_session_command",
        "command": "create_session",
        "session_id": SESSION_ID,
        "data": {
            "title": "E2E Test Session",
            "participants": ["claude", "test_user"]
        }
    }, "Create Session"))

    time.sleep(1)

    # Test 2: Store Conversation Chunk
    results.append(send_webhook({
        "type": "collaborative_session_command",
        "command": "conversation_chunk",
        "session_id": SESSION_ID,
        "data": {
            "chunk_id": "chunk_001",
            "content": """
User: I want to build a carbon tracking feature for our app
Claude: That's a great idea! Let me help you think through the requirements:
1. What data points do you want to track?
2. How should users input their carbon usage?
3. Do you need historical tracking and trends?

User: Yes, we need all of that. Can you help me design the database schema?
Claude: Absolutely! Let's start with a user_activities table...
            """.strip(),
            "format": "dialogue",
            "extracted_items": {
                "ideas": ["Carbon tracking feature", "Historical trends"],
                "questions": ["What data points to track?", "How should users input data?"]
            }
        }
    }, "Store Conversation Chunk"))

    time.sleep(1)

    # Test 3: Store Memory (Idea)
    results.append(send_webhook({
        "type": "collaborative_session_command",
        "command": "store_memory",
        "session_id": SESSION_ID,
        "data": {
            "type": "idea",
            "key": "carbon_tracking_feature",
            "content": {
                "description": "Add carbon footprint tracking to help users monitor their environmental impact",
                "priority": "high",
                "components": ["database schema", "API endpoints", "UI dashboard"]
            },
            "tags": ["sustainability", "feature", "high-priority"]
        }
    }, "Store Memory - Idea"))

    time.sleep(1)

    # Test 4: Store Memory (Decision)
    results.append(send_webhook({
        "type": "collaborative_session_command",
        "command": "store_memory",
        "session_id": SESSION_ID,
        "data": {
            "type": "decision",
            "key": "database_choice",
            "content": {
                "decision": "Use Postgres with JSONB for flexible carbon data storage",
                "rationale": "Allows structured queries while maintaining flexibility for different activity types",
                "alternatives_considered": ["MongoDB", "MySQL"]
            },
            "tags": ["architecture", "database"]
        }
    }, "Store Memory - Decision"))

    time.sleep(1)

    # Test 5: Delegate Task
    results.append(send_webhook({
        "type": "collaborative_session_command",
        "command": "delegate_task",
        "session_id": SESSION_ID,
        "data": {
            "task_id": "task_schema_design",
            "agent_name": "claude_code",
            "task_type": "code",
            "description": "Design database schema for carbon tracking feature",
            "priority": 1,
            "input_data": {
                "requirements": [
                    "Track different activity types (transport, energy, food)",
                    "Support user-defined custom activities",
                    "Store carbon coefficients for calculations",
                    "Enable historical queries and trend analysis"
                ],
                "deliverables": [
                    "SQL migration file",
                    "SQLAlchemy models",
                    "API endpoint specifications"
                ]
            }
        }
    }, "Delegate Task to Agent"))

    time.sleep(1)

    # Test 6: Add Artifact
    results.append(send_webhook({
        "type": "collaborative_session_command",
        "command": "add_artifact",
        "session_id": SESSION_ID,
        "data": {
            "artifact_id": "artifact_schema_v1",
            "name": "Carbon Tracking Schema",
            "type": "code",
            "format": "sql",
            "content": """
-- Carbon Tracking Schema
CREATE TABLE activity_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    carbon_coefficient DECIMAL(10, 4),
    unit VARCHAR(20)
);

CREATE TABLE user_activities (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    activity_type_id INTEGER REFERENCES activity_types(id),
    amount DECIMAL(10, 2),
    carbon_footprint DECIMAL(10, 4),
    recorded_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_activities_user ON user_activities(user_id, recorded_at);
            """.strip(),
            "metadata": {
                "version": "1.0",
                "created_by": "claude",
                "relates_to_task": "task_schema_design"
            }
        }
    }, "Add Artifact - Code"))

    time.sleep(1)

    # Test 7: Batch Command
    results.append(send_webhook({
        "type": "collaborative_session_command",
        "command": "batch",
        "session_id": SESSION_ID,
        "data": {
            "commands": [
                {
                    "command": "store_memory",
                    "data": {
                        "type": "question",
                        "key": "api_rate_limiting",
                        "content": {
                            "question": "Should we implement rate limiting for the carbon tracking API?",
                            "context": "High-frequency tracking might cause load issues"
                        },
                        "tags": ["api", "performance"]
                    }
                },
                {
                    "command": "store_memory",
                    "data": {
                        "type": "action_item",
                        "key": "implement_rate_limiting",
                        "content": {
                            "action": "Implement API rate limiting",
                            "owner": "backend_team",
                            "due_date": "2025-12-01"
                        },
                        "tags": ["todo", "backend"]
                    }
                }
            ]
        }
    }, "Batch Commands"))

    # Summary
    print(f"\n{'=' * 70}")
    print("TEST SUMMARY")
    print(f"{'=' * 70}")
    total = len(results)
    passed = sum(results)
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")

    if passed == total:
        print("\n✅ ALL WEBHOOK TESTS PASSED")
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED")
        return False

    # Verify in database
    print("\n" + "=" * 70)
    print("Waiting 2 seconds for data to propagate...")
    print("=" * 70)
    time.sleep(2)

    if verify_in_database(SESSION_ID):
        print("\n✅ DATABASE VERIFICATION PASSED")
        print("\n" + "=" * 70)
        print("🎉 END-TO-END TEST COMPLETE - ALL SYSTEMS OPERATIONAL")
        print("=" * 70)
        return True
    else:
        print("\n❌ DATABASE VERIFICATION FAILED")
        return False

if __name__ == "__main__":
    print("\n⚠️  NOTE: Make sure the client is running before executing this test!")
    print("         Run: python3 client/client.py")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\nTest cancelled")
        sys.exit(0)

    success = run_tests()
    sys.exit(0 if success else 1)
