"""
SQLite Backend for MVP Task Storage

Simple file-based storage with no configuration needed.
Replaces PostgreSQL for lightweight MVP deployment.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
import os


class SimpleSQLiteBackend:
    """
    Lightweight SQLite backend for task storage.

    Stores tasks in a single SQLite database file with automatic
    schema creation and simple CRUD operations.
    """

    def __init__(self, db_path=None):
        """
        Initialize SQLite connection and create schema.

        Args:
            db_path: Path to SQLite database file.
                     If None, uses SQLITE_PATH from environment or './tasks.db'
        """
        if db_path is None:
            db_path = os.getenv('SQLITE_PATH', './tasks.db')

        self.db_path = db_path

        # Create parent directory if needed
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # Connect to database (creates file if doesn't exist)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)

        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON")

        # Create schema if needed
        self._init_schema()

        print(f"📦 SQLite backend initialized: {db_path}")

    def _init_schema(self):
        """Create tables if they don't exist"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                command TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                input_data TEXT,
                output_data TEXT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)

        # Create indexes for common queries
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_created
            ON tasks(created_at DESC)
        """)

        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_status
            ON tasks(status)
        """)

        self.conn.commit()

    def create_task(self, task_id: str, command: str, input_data: str):
        """
        Create a new task.

        Args:
            task_id: Unique identifier for task
            command: Action type (git, shell, claude_code)
            input_data: JSON string of input parameters

        Returns:
            None

        Raises:
            sqlite3.IntegrityError: If task_id already exists
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (id, command, status, input_data, created_at)
            VALUES (?, ?, 'pending', ?, CURRENT_TIMESTAMP)
        """, (task_id, command, input_data))
        self.conn.commit()

    def update_task(self, task_id: str, status: str,
                    output_data: str = None, error: str = None):
        """
        Update task status and results.

        Args:
            task_id: Task to update
            status: New status (running, completed, failed)
            output_data: JSON string of results (optional)
            error: Error message if failed (optional)

        Returns:
            None
        """
        cursor = self.conn.cursor()

        # Build UPDATE query dynamically
        updates = ["status = ?"]
        params = [status]

        if output_data is not None:
            updates.append("output_data = ?")
            params.append(output_data)

        if error is not None:
            updates.append("error_message = ?")
            params.append(error)

        # Update timestamps
        if status == 'running':
            updates.append("started_at = CURRENT_TIMESTAMP")
        elif status in ('completed', 'failed'):
            updates.append("completed_at = CURRENT_TIMESTAMP")

        params.append(task_id)

        query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        self.conn.commit()

    def get_task(self, task_id: str):
        """
        Retrieve task by ID.

        Args:
            task_id: Task to retrieve

        Returns:
            tuple: Task row or None if not found
                   (id, command, status, input_data, output_data,
                    error_message, created_at, started_at, completed_at)
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        return cursor.fetchone()

    def get_recent_tasks(self, limit: int = 10):
        """
        Get most recent tasks.

        Args:
            limit: Maximum number of tasks to return

        Returns:
            list: List of task tuples, newest first
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM tasks
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()

    def get_tasks_by_status(self, status: str, limit: int = 10):
        """
        Get tasks by status.

        Args:
            status: Status to filter by
            limit: Maximum number to return

        Returns:
            list: List of task tuples
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM tasks
            WHERE status = ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (status, limit))
        return cursor.fetchall()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("📦 SQLite connection closed")
