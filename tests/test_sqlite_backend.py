"""
Test script for SQLite backend.

Verifies that all CRUD operations work correctly.
"""

import os
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from client.storage.sqlite_backend import SimpleSQLiteBackend
import tempfile


def test_sqlite_backend():
    """Run all SQLite backend tests"""

    print("🧪 Testing SQLite Backend\n")

    # Use temporary database for testing
    test_db = tempfile.mktemp(suffix='.db')
    db = SimpleSQLiteBackend(test_db)

    try:
        # Test 1: Create task
        print("Test 1: Create task...")
        task_id = "test_001"
        command = "git"
        input_data = json.dumps({"command": ["git", "status"]})

        db.create_task(task_id, command, input_data)
        print("✅ Task created")

        # Test 2: Retrieve task
        print("\nTest 2: Retrieve task...")
        task = db.get_task(task_id)
        assert task is not None, "Task not found"
        assert task[0] == task_id, "Task ID mismatch"
        assert task[1] == command, "Command mismatch"
        assert task[2] == 'pending', "Status should be pending"
        print(f"✅ Task retrieved: {task[0]}, status={task[2]}")

        # Test 3: Update to running
        print("\nTest 3: Update status to running...")
        db.update_task(task_id, 'running')
        task = db.get_task(task_id)
        assert task[2] == 'running', "Status should be running"
        assert task[7] is not None, "started_at should be set"
        print(f"✅ Task updated: status={task[2]}")

        # Test 4: Update to completed with output
        print("\nTest 4: Update to completed with output...")
        output_data = json.dumps({
            "stdout": "On branch main\nnothing to commit",
            "stderr": "",
            "returncode": 0
        })
        db.update_task(task_id, 'completed', output_data=output_data)
        task = db.get_task(task_id)
        assert task[2] == 'completed', "Status should be completed"
        assert task[4] is not None, "output_data should be set"
        assert task[8] is not None, "completed_at should be set"
        print(f"✅ Task completed: {task[0]}")

        # Test 5: Create failed task
        print("\nTest 5: Create failed task...")
        db.create_task("test_002", "shell", '{"command": "invalid"}')
        db.update_task("test_002", 'failed', error="Command not found")
        task = db.get_task("test_002")
        assert task[2] == 'failed', "Status should be failed"
        assert task[5] is not None, "error_message should be set"
        print(f"✅ Failed task created")

        # Test 6: Get recent tasks
        print("\nTest 6: Get recent tasks...")
        recent = db.get_recent_tasks(limit=10)
        assert len(recent) == 2, f"Should have 2 tasks, got {len(recent)}"
        # Verify we got both tasks (order may vary if created at same timestamp)
        task_ids = {task[0] for task in recent}
        assert task_ids == {"test_001", "test_002"}, "Should retrieve both test tasks"
        print(f"✅ Retrieved {len(recent)} recent tasks")

        # Test 7: Get by status
        print("\nTest 7: Get tasks by status...")
        completed = db.get_tasks_by_status('completed')
        assert len(completed) == 1, "Should have 1 completed task"
        failed = db.get_tasks_by_status('failed')
        assert len(failed) == 1, "Should have 1 failed task"
        print(f"✅ Filtered by status: {len(completed)} completed, {len(failed)} failed")

        print("\n" + "="*60)
        print("✅ ALL SQLITE BACKEND TESTS PASSED")
        print("="*60)

    finally:
        db.close()
        # Clean up test database
        if os.path.exists(test_db):
            os.remove(test_db)
            print(f"🧹 Cleaned up test database")


if __name__ == "__main__":
    test_sqlite_backend()
