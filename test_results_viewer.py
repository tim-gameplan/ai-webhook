"""
Test script for Results Viewer.

Creates sample data and verifies the Flask app works.
"""

import os
import json
import sys
from pathlib import Path
import tempfile
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from client.storage.sqlite_backend import SimpleSQLiteBackend
from client.task_executor import TaskExecutor


def create_sample_data():
    """Create sample tasks in database for testing"""
    print("🧪 Creating sample data for Results Viewer\n")

    # Use test database
    test_db = "test_results.db"
    executor = TaskExecutor(test_db)

    try:
        # Create a few sample tasks
        print("Creating sample tasks...")

        # Task 1: Successful git status
        executor.handle_task({
            "task_id": "sample_git_001",
            "action_type": "git",
            "params": {
                "command": ["git", "status"],
                "working_dir": os.getcwd()
            }
        })
        print("✅ Created git status task")

        # Task 2: Successful git log
        executor.handle_task({
            "task_id": "sample_git_002",
            "action_type": "git",
            "params": {
                "command": ["git", "log", "--oneline", "-3"],
                "working_dir": os.getcwd()
            }
        })
        print("✅ Created git log task")

        # Task 3: Successful shell echo
        executor.handle_task({
            "task_id": "sample_shell_001",
            "action_type": "shell",
            "params": {
                "command": "echo 'Hello from Results Viewer test!'"
            }
        })
        print("✅ Created shell echo task")

        # Task 4: Failed task (invalid directory)
        executor.handle_task({
            "task_id": "sample_error_001",
            "action_type": "git",
            "params": {
                "command": ["git", "status"],
                "working_dir": "/nonexistent/path"
            }
        })
        print("✅ Created failed task")

        print(f"\n📊 Created 4 sample tasks in {test_db}")
        print(f"\n🌐 You can now view them at: http://localhost:5001")
        print(f"   (Start the server with: python3 client/results_server.py)")

        executor.close()

    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        executor.close()


if __name__ == "__main__":
    create_sample_data()
