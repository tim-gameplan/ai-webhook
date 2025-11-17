"""
Task Executor for MVP

Executes tasks locally (git, shell, claude_code) and stores results in SQLite.
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from client.storage.sqlite_backend import SimpleSQLiteBackend


class TaskExecutor:
    """
    Executes tasks locally and manages their lifecycle in the database.

    Supports three action types:
    - git: Execute git commands
    - shell: Execute shell commands
    - claude_code: Spawn Claude Code CLI
    """

    def __init__(self, db_path=None):
        """
        Initialize task executor.

        Args:
            db_path: Path to SQLite database (optional, uses env var)
        """
        self.db = SimpleSQLiteBackend(db_path)
        print("⚙️  Task executor initialized")

    def handle_task(self, task_data: dict) -> dict:
        """
        Main entry point for task execution.

        Args:
            task_data: Task command data with structure:
                {
                    "task_id": "unique_id",
                    "action_type": "git|shell|claude_code",
                    "params": {
                        "command": [...] or "string",
                        "working_dir": "/path/to/dir",
                        "timeout": 30
                    }
                }

        Returns:
            dict: Result with status, task_id, and result/error
        """
        task_id = task_data.get('task_id')
        action_type = task_data.get('action_type')
        params = task_data.get('params', {})

        if not task_id:
            return {
                'status': 'error',
                'error': 'Missing task_id'
            }

        if not action_type:
            return {
                'status': 'error',
                'task_id': task_id,
                'error': 'Missing action_type'
            }

        # Create task in database
        try:
            input_data_json = json.dumps({
                'action_type': action_type,
                'params': params
            })
            self.db.create_task(task_id, action_type, input_data_json)
        except Exception as e:
            return {
                'status': 'error',
                'task_id': task_id,
                'error': f'Failed to create task in database: {str(e)}'
            }

        # Update to running
        self.db.update_task(task_id, 'running')

        # Execute based on action type
        try:
            if action_type == 'git':
                result = self._execute_git(params)
            elif action_type == 'shell':
                result = self._execute_shell(params)
            elif action_type == 'claude_code':
                result = self._execute_claude_code(params)
            else:
                result = {
                    'success': False,
                    'error': f'Unknown action type: {action_type}'
                }

            # Update task in database
            if result.get('success'):
                output_data_json = json.dumps(result)
                self.db.update_task(task_id, 'completed', output_data=output_data_json)
                return {
                    'status': 'success',
                    'task_id': task_id,
                    'result': result
                }
            else:
                error_msg = result.get('error', 'Unknown error')
                self.db.update_task(task_id, 'failed', error=error_msg)
                return {
                    'status': 'failed',
                    'task_id': task_id,
                    'error': error_msg
                }

        except Exception as e:
            error_msg = f'Execution error: {str(e)}'
            self.db.update_task(task_id, 'failed', error=error_msg)
            return {
                'status': 'failed',
                'task_id': task_id,
                'error': error_msg
            }

    def _execute_git(self, params: dict) -> dict:
        """
        Execute git command.

        Args:
            params: {
                "command": ["git", "status"],
                "working_dir": "/path/to/repo",
                "timeout": 30
            }

        Returns:
            dict: {success, stdout, stderr, returncode, error}
        """
        command = params.get('command', [])
        working_dir = params.get('working_dir', os.getcwd())
        timeout = params.get('timeout', 30)

        if not command:
            return {
                'success': False,
                'error': 'Missing command parameter'
            }

        # Validate working directory
        if not os.path.isdir(working_dir):
            return {
                'success': False,
                'error': f'Working directory does not exist: {working_dir}'
            }

        # Ensure command is a list
        if isinstance(command, str):
            command = command.split()

        # Security: Ensure first element is 'git'
        if not command or command[0] != 'git':
            return {
                'success': False,
                'error': 'Git commands must start with "git"'
            }

        try:
            result = subprocess.run(
                command,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=False  # Security: no shell injection
            )

            return {
                'success': True,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f'Command timed out after {timeout} seconds'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Git execution error: {str(e)}'
            }

    def _execute_shell(self, params: dict) -> dict:
        """
        Execute shell command.

        Args:
            params: {
                "command": "echo test" or ["echo", "test"],
                "working_dir": "/path/to/dir",
                "timeout": 30
            }

        Returns:
            dict: {success, stdout, stderr, returncode, error}
        """
        command = params.get('command')
        working_dir = params.get('working_dir', os.getcwd())
        timeout = params.get('timeout', 30)

        if not command:
            return {
                'success': False,
                'error': 'Missing command parameter'
            }

        # Validate working directory
        if not os.path.isdir(working_dir):
            return {
                'success': False,
                'error': f'Working directory does not exist: {working_dir}'
            }

        try:
            # Support both string and list commands
            if isinstance(command, list):
                result = subprocess.run(
                    command,
                    cwd=working_dir,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    shell=False
                )
            else:
                result = subprocess.run(
                    command,
                    cwd=working_dir,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    shell=True
                )

            return {
                'success': True,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f'Command timed out after {timeout} seconds'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Shell execution error: {str(e)}'
            }

    def _execute_claude_code(self, params: dict) -> dict:
        """
        Execute Claude Code CLI.

        Args:
            params: {
                "prompt": "Review my latest changes",
                "working_dir": "/path/to/repo",
                "timeout": 300
            }

        Returns:
            dict: {success, stdout, stderr, returncode, error}
        """
        prompt = params.get('prompt')
        working_dir = params.get('working_dir', os.getcwd())
        timeout = params.get('timeout', 300)  # 5 min default for Claude Code

        if not prompt:
            return {
                'success': False,
                'error': 'Missing prompt parameter'
            }

        # Validate working directory
        if not os.path.isdir(working_dir):
            return {
                'success': False,
                'error': f'Working directory does not exist: {working_dir}'
            }

        # Check if Claude Code CLI is available
        try:
            subprocess.run(
                ['claude', '--version'],
                capture_output=True,
                timeout=5
            )
        except FileNotFoundError:
            return {
                'success': False,
                'error': 'Claude Code CLI not found. Install from: https://claude.ai/code'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to verify Claude Code CLI: {str(e)}'
            }

        try:
            # Execute Claude Code with prompt
            result = subprocess.run(
                ['claude', prompt],
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=False
            )

            return {
                'success': True,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f'Claude Code timed out after {timeout} seconds'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Claude Code execution error: {str(e)}'
            }

    def close(self):
        """Close database connection"""
        self.db.close()
