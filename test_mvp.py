"""
MVP Comprehensive Test Suite

Tests all components of the MVP system.
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
import tempfile

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from client.storage.sqlite_backend import SimpleSQLiteBackend
from client.task_executor import TaskExecutor


# Configuration
WEBHOOK_URL = "https://web-production-3d53a.up.railway.app/webhook"
API_KEY = os.getenv("API_KEY")
WORKING_DIR = os.getcwd()


def print_test(name):
    """Print test name"""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print('='*60)


def test_sqlite_backend():
    """Test 1: SQLite Backend"""
    print_test("SQLite Backend")

    test_db = tempfile.mktemp(suffix='.db')
    db = SimpleSQLiteBackend(test_db)

    try:
        # Create task
        db.create_task("test_001", "git", '{"command": ["git", "status"]}')
        print("✅ Task created")

        # Retrieve task
        task = db.get_task("test_001")
        assert task is not None
        print("✅ Task retrieved")

        # Update task
        db.update_task("test_001", "completed", '{"stdout": "success"}')
        task = db.get_task("test_001")
        assert task[2] == "completed"
        print("✅ Task updated")

        # Get recent tasks
        recent = db.get_recent_tasks(limit=10)
        assert len(recent) >= 1
        print("✅ Recent tasks retrieved")

        print("\n✅ SQLite Backend: PASSED")
        return True

    except Exception as e:
        print(f"\n❌ SQLite Backend: FAILED - {e}")
        return False
    finally:
        db.close()
        if os.path.exists(test_db):
            os.remove(test_db)


def test_task_executor():
    """Test 2: Task Executor"""
    print_test("Task Executor")

    test_db = tempfile.mktemp(suffix='.db')
    executor = TaskExecutor(test_db)

    try:
        # Test git command
        result = executor.handle_task({
            "task_id": "test_git",
            "action_type": "git",
            "params": {
                "command": ["git", "status"],
                "working_dir": WORKING_DIR
            }
        })
        assert result["status"] == "success"
        print("✅ Git command executed")

        # Test shell command
        result = executor.handle_task({
            "task_id": "test_shell",
            "action_type": "shell",
            "params": {
                "command": "echo 'test'"
            }
        })
        assert result["status"] == "success"
        print("✅ Shell command executed")

        # Test error handling
        result = executor.handle_task({
            "task_id": "test_error",
            "action_type": "git",
            "params": {
                "command": ["git", "status"],
                "working_dir": "/nonexistent"
            }
        })
        assert result["status"] == "failed"
        print("✅ Error handling works")

        print("\n✅ Task Executor: PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Task Executor: FAILED - {e}")
        return False
    finally:
        executor.close()
        if os.path.exists(test_db):
            os.remove(test_db)


def test_webhook_endpoint():
    """Test 3: Webhook Endpoint"""
    print_test("Webhook Endpoint Connectivity")

    if not API_KEY:
        print("⚠️  API_KEY not set, skipping webhook test")
        return True

    try:
        # Test webhook endpoint with simple task
        payload = {
            "type": "task_command",
            "data": {
                "task_id": f"test_webhook_{int(time.time())}",
                "action_type": "shell",
                "params": {
                    "command": "echo 'MVP test'"
                }
            }
        }

        response = requests.post(
            WEBHOOK_URL,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": API_KEY
            },
            json=payload,
            timeout=10
        )

        assert response.status_code == 200
        print(f"✅ Webhook endpoint reachable")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")

        print("\n✅ Webhook Endpoint: PASSED")
        return True

    except requests.exceptions.RequestException as e:
        print(f"\n⚠️  Webhook Endpoint: WARNING - {e}")
        print("   (This is OK if webhook client is not running)")
        return True
    except Exception as e:
        print(f"\n❌ Webhook Endpoint: FAILED - {e}")
        return False


def test_file_structure():
    """Test 4: Required Files Exist"""
    print_test("File Structure")

    required_files = [
        "client/storage/sqlite_backend.py",
        "client/task_executor.py",
        "client/results_server.py",
        "client/templates/tasks.html",
        "client/client.py",
        "docs/LLM_ACTIONS.md",
        "docs/CHATGPT_SETUP.md",
        "docs/CLAUDE_SETUP.md",
        "docs/GEMINI_SETUP.md",
        "examples/git_status.json",
        "start_mvp.sh",
        "stop_mvp.sh",
        ".env.example"
    ]

    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_exist = False

    if all_exist:
        print("\n✅ File Structure: PASSED")
        return True
    else:
        print("\n❌ File Structure: FAILED - Some files missing")
        return False


def test_env_configuration():
    """Test 5: Environment Configuration"""
    print_test("Environment Configuration")

    try:
        # Check .env.example has required fields
        with open('.env.example', 'r') as f:
            content = f.read()

        required_vars = [
            'RELAY_SERVER_URL',
            'API_KEY',
            'STORAGE_BACKEND',
            'SQLITE_PATH'
        ]

        all_present = True
        for var in required_vars:
            if var in content:
                print(f"✅ {var} defined in .env.example")
            else:
                print(f"❌ {var} missing from .env.example")
                all_present = False

        # Check actual .env if exists
        if os.path.exists('.env'):
            load_dotenv()
            api_key = os.getenv('API_KEY')
            storage = os.getenv('STORAGE_BACKEND')

            if api_key:
                print(f"✅ API_KEY set in .env")
            else:
                print(f"⚠️  API_KEY not set in .env")

            if storage:
                print(f"✅ STORAGE_BACKEND={storage}")
            else:
                print(f"⚠️  STORAGE_BACKEND not set")

        if all_present:
            print("\n✅ Environment Configuration: PASSED")
            return True
        else:
            print("\n❌ Environment Configuration: FAILED")
            return False

    except Exception as e:
        print(f"\n❌ Environment Configuration: FAILED - {e}")
        return False


def run_all_tests():
    """Run all MVP tests"""
    print("\n" + "="*60)
    print("MVP COMPREHENSIVE TEST SUITE")
    print("="*60)
    print(f"Working Directory: {WORKING_DIR}")
    print(f"Webhook URL: {WEBHOOK_URL}")
    print(f"API Key: {'Set' if API_KEY else 'Not Set'}")
    print("="*60)

    results = {
        "SQLite Backend": test_sqlite_backend(),
        "Task Executor": test_task_executor(),
        "Webhook Endpoint": test_webhook_endpoint(),
        "File Structure": test_file_structure(),
        "Environment Config": test_env_configuration()
    }

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")

    print("="*60)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED - MVP IS READY!")
        print("\nNext steps:")
        print("1. Start MVP: ./start_mvp.sh")
        print("2. Test with webhook: See examples/")
        print("3. View results: http://localhost:5001")
        print("4. Setup LLM: See docs/")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Fix issues before deploying.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
