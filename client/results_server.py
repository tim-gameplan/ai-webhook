"""
Results Viewer - Flask Web App

Simple web interface to view task results at http://localhost:5001
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
load_dotenv()

from client.storage.sqlite_backend import SimpleSQLiteBackend

app = Flask(__name__)
db = SimpleSQLiteBackend()


@app.route('/')
def index():
    """Show recent tasks"""
    tasks = db.get_recent_tasks(limit=20)

    # Convert tasks to dict for template
    task_list = []
    for task in tasks:
        task_dict = {
            'id': task[0],
            'command': task[1],
            'status': task[2],
            'input_data': json.loads(task[3]) if task[3] else {},
            'output_data': json.loads(task[4]) if task[4] else {},
            'error_message': task[5],
            'created_at': task[6],
            'started_at': task[7],
            'completed_at': task[8]
        }
        task_list.append(task_dict)

    return render_template('tasks.html', tasks=task_list)


@app.route('/api/task/<task_id>')
def get_task(task_id):
    """Get task details as JSON"""
    task = db.get_task(task_id)

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    task_dict = {
        'id': task[0],
        'command': task[1],
        'status': task[2],
        'input_data': json.loads(task[3]) if task[3] else {},
        'output_data': json.loads(task[4]) if task[4] else {},
        'error_message': task[5],
        'created_at': task[6],
        'started_at': task[7],
        'completed_at': task[8]
    }

    return jsonify(task_dict)


@app.route('/api/tasks')
def get_tasks():
    """Get all recent tasks as JSON"""
    limit = request.args.get('limit', 20, type=int)
    tasks = db.get_recent_tasks(limit=limit)

    task_list = []
    for task in tasks:
        task_dict = {
            'id': task[0],
            'command': task[1],
            'status': task[2],
            'created_at': task[6],
            'completed_at': task[8]
        }
        task_list.append(task_dict)

    return jsonify(task_list)


if __name__ == '__main__':
    print("=" * 60)
    print("Task Results Viewer")
    print("=" * 60)
    print("Server: http://localhost:5001")
    print("API: http://localhost:5001/api/tasks")
    print("=" * 60)
    print()

    app.run(host='0.0.0.0', port=5001, debug=True)
