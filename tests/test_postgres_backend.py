#!/usr/bin/env python3
"""
Test script for PostgreSQL storage backend
"""

import os
import sys
import time

# Set storage backend to postgres
os.environ['STORAGE_BACKEND'] = 'postgres'
os.environ['DATABASE_URL'] = 'postgresql://webhook_user:webhook_dev_password@localhost:5433/ai_webhook'

# Add client to path
sys.path.insert(0, 'client')

from storage.postgres_backend import PostgresBackend
from models.session import ConversationChunk, AgentTask

# Generate unique session ID for this test run
TEST_RUN_ID = str(int(time.time()))

def test_session_creation():
    """Test creating a new session"""
    print("\n=== Test 1: Session Creation ===")

    session_id = f"test_session_{TEST_RUN_ID}"
    session = PostgresBackend(session_id, "Test Session", ["Alice", "Bob"])
    session.context = "Testing the PostgreSQL backend"
    session.save()

    print(f"✅ Created session: {session.session_id}")
    print(f"   Title: {session.title}")
    print(f"   Participants: {session.participants}")

    return session

def test_conversation_chunk(session):
    """Test adding conversation chunks"""
    print("\n=== Test 2: Conversation Chunk ===")

    chunk = ConversationChunk(
        chunk_id=f"chunk_{TEST_RUN_ID}_001",
        content="Alice: I think we should build a new feature.\nBob: That sounds great!",
        format="dialogue",
        participants=["Alice", "Bob"]
    )

    chunk_id = session.add_conversation_chunk(chunk)
    print(f"✅ Added conversation chunk: {chunk_id}")

    return chunk_id

def test_memory_storage(session):
    """Test storing and retrieving memories"""
    print("\n=== Test 3: Memory Storage ===")

    # Store ideas
    session.add_memory(
        "idea",
        f"feature_new_dashboard_{TEST_RUN_ID}",
        {"description": "Build a new dashboard with metrics"},
        tags=["dashboard", "metrics"]
    )

    session.add_memory(
        "decision",
        f"tech_stack_react_{TEST_RUN_ID}",
        {"description": "Use React for the frontend"},
        tags=["frontend", "react"]
    )

    print("✅ Stored 2 memories")

    # Query memories
    ideas = session.query_memories(memory_type="idea", limit=10)
    print(f"   Found {len(ideas)} ideas")

    all_memories = session.query_memories(limit=10)
    print(f"   Found {len(all_memories)} total memories")

    # Get specific memory
    memory = session.get_memory(f"feature_new_dashboard_{TEST_RUN_ID}")
    if memory:
        print(f"   Retrieved memory: {memory['key']}")

def test_task_management(session):
    """Test task creation and management"""
    print("\n=== Test 4: Task Management ===")

    task = AgentTask(
        task_id=f"task_{TEST_RUN_ID}_001",
        agent_name="claude_code",
        task_type="code",
        data={"action": "create_dashboard", "framework": "react"}
    )

    task_id = session.add_task(task)
    print(f"✅ Created task: {task_id}")

    # List tasks
    tasks = session.list_tasks()
    print(f"   Found {len(tasks)} tasks")

    pending_tasks = session.list_tasks(status="pending")
    print(f"   Found {len(pending_tasks)} pending tasks")

def test_artifacts(session):
    """Test artifact storage"""
    print("\n=== Test 5: Artifacts ===")

    artifact_id = session.add_artifact(
        "code",
        f"Dashboard_{TEST_RUN_ID}.tsx",
        "import React from 'react';\n\nconst Dashboard = () => {\n  return <div>Dashboard</div>;\n};\n\nexport default Dashboard;",
        metadata={"format": "typescript", "framework": "react"}
    )

    print(f"✅ Created artifact: {artifact_id}")

    # List artifacts
    artifacts = session.list_artifacts()
    print(f"   Found {len(artifacts)} artifacts")

    # Get artifact
    artifact = session.get_artifact(artifact_id)
    if artifact:
        print(f"   Retrieved artifact: {artifact['metadata']['name']}")

def test_session_summary(session):
    """Test getting session summary"""
    print("\n=== Test 6: Session Summary ===")

    summary = session.get_summary()
    print(f"✅ Session: {summary['session_id']}")
    print(f"   Title: {summary['title']}")
    print(f"   Status: {summary['status']}")
    print(f"   Duration: {summary['duration_minutes']:.2f} minutes")
    print(f"   Stats:")
    for key, value in summary['stats'].items():
        print(f"     {key}: {value}")

def test_list_sessions():
    """Test listing all sessions"""
    print("\n=== Test 7: List Sessions ===")

    sessions = PostgresBackend.list_sessions(limit=10)
    print(f"✅ Found {len(sessions)} sessions")

    for session in sessions:
        print(f"   - {session['session_id']}: {session['title']}")

def test_load_session():
    """Test loading existing session"""
    print("\n=== Test 8: Load Session ===")

    session_id = f"test_session_{TEST_RUN_ID}"
    session = PostgresBackend.load(session_id)
    if session:
        print(f"✅ Loaded session: {session.session_id}")
        print(f"   Title: {session.title}")
        print(f"   Conversation chunks: {session.conversation_chunk_count}")
        print(f"   Memories: {session.memory_count}")
        print(f"   Tasks: {session.task_count}")
        print(f"   Artifacts: {session.artifact_count}")
        return session
    else:
        print("❌ Failed to load session")
        return None

def main():
    """Run all tests"""
    print("🧪 Testing PostgreSQL Storage Backend")
    print("=" * 50)

    try:
        # Initialize connection pool
        PostgresBackend.initialize_pool()
        print("✅ Database connection pool initialized")

        # Run tests
        session = test_session_creation()
        test_conversation_chunk(session)
        test_memory_storage(session)
        test_task_management(session)
        test_artifacts(session)
        test_session_summary(session)
        test_list_sessions()
        test_load_session()

        print("\n" + "=" * 50)
        print("🎉 All tests passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
