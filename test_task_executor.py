"""
Test script for Task Executor.

Verifies that task execution works for git and shell commands.
"""

import os
import json
import sys
from pathlib import Path
import tempfile

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from client.task_executor import TaskExecutor


def test_task_executor():
    """Run all task executor tests"""

    print("🧪 Testing Task Executor\n")

    # Use temporary database for testing
    test_db = tempfile.mktemp(suffix='.db')
    executor = TaskExecutor(test_db)

    try:
        # Test 1: Execute git status
        print("Test 1: Execute git status...")
        result = executor.handle_task({
            "task_id": "test_git_001",
            "action_type": "git",
            "params": {
                "command": ["git", "status"],
                "working_dir": os.getcwd()
            }
        })
        assert result.get("status") == "success", f"Git command failed: {result.get('error')}"
        assert result.get("result", {}).get("returncode") == 0, "Git status should return 0"
        print("✅ Git status executed successfully")

        # Test 2: Execute git log
        print("\nTest 2: Execute git log...")
        result = executor.handle_task({
            "task_id": "test_git_002",
            "action_type": "git",
            "params": {
                "command": ["git", "log", "--oneline", "-5"],
                "working_dir": os.getcwd()
            }
        })
        assert result.get("status") == "success", f"Git log failed: {result.get('error')}"
        print("✅ Git log executed successfully")

        # Test 3: Execute shell command (echo)
        print("\nTest 3: Execute shell command (echo)...")
        result = executor.handle_task({
            "task_id": "test_shell_001",
            "action_type": "shell",
            "params": {
                "command": "echo 'Hello from task executor'"
            }
        })
        assert result.get("status") == "success", f"Shell command failed: {result.get('error')}"
        assert "Hello from task executor" in result.get("result", {}).get("stdout", "")
        print("✅ Shell command executed successfully")

        # Test 4: Execute shell command (ls)
        print("\nTest 4: Execute shell command (ls)...")
        result = executor.handle_task({
            "task_id": "test_shell_002",
            "action_type": "shell",
            "params": {
                "command": ["ls", "-la"],
                "working_dir": os.getcwd()
            }
        })
        assert result.get("status") == "success", f"Shell ls failed: {result.get('error')}"
        print("✅ Shell ls executed successfully")

        # Test 5: Handle invalid working directory
        print("\nTest 5: Handle invalid working directory...")
        result = executor.handle_task({
            "task_id": "test_error_001",
            "action_type": "git",
            "params": {
                "command": ["git", "status"],
                "working_dir": "/nonexistent/directory"
            }
        })
        assert result.get("status") == "failed", "Should fail with invalid directory"
        assert "does not exist" in result.get("error", "").lower()
        print("✅ Invalid directory handled correctly")

        # Test 6: Verify tasks stored in database
        print("\nTest 6: Verify tasks stored in database...")
        recent_tasks = executor.db.get_recent_tasks(limit=10)
        assert len(recent_tasks) == 5, f"Should have 5 tasks, got {len(recent_tasks)}"

        # Check that we have completed and failed tasks
        completed_tasks = executor.db.get_tasks_by_status('completed')
        failed_tasks = executor.db.get_tasks_by_status('failed')
        assert len(completed_tasks) == 4, f"Should have 4 completed tasks, got {len(completed_tasks)}"
        assert len(failed_tasks) == 1, f"Should have 1 failed task, got {len(failed_tasks)}"
        print("✅ All tasks stored correctly in database")

        print("\n" + "="*60)
        print("✅ ALL TASK EXECUTOR TESTS PASSED")
        print("="*60)

    finally:
        executor.close()
        # Clean up test database
        if os.path.exists(test_db):
            os.remove(test_db)
            print(f"🧹 Cleaned up test database")


if __name__ == "__main__":
    test_task_executor()
