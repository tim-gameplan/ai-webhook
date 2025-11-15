"""
GitHub Webhook Client

Run this on your local machine to receive webhook events from the relay server.
Supports both GitHub webhooks and LLM conversation insights.
"""

import asyncio
import websockets
import json
import os
from datetime import datetime
from pathlib import Path

# Import LLM insights handler
try:
    from handlers.llm_insights import LLMInsightHandler, validate_llm_insight
    llm_handler = LLMInsightHandler()
    LLM_HANDLER_AVAILABLE = True
except ImportError:
    print("⚠️  LLM insights handler not available")
    LLM_HANDLER_AVAILABLE = False

# Import session manager for collaborative sessions
try:
    from session_manager import get_session_manager
    session_manager = get_session_manager()
    SESSION_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Session manager not available: {e}")
    SESSION_MANAGER_AVAILABLE = False

# Configuration
SERVER_URL = os.getenv("RELAY_SERVER_URL", "ws://localhost:8000/ws")
LOG_DIR = Path("webhook_logs")
LOG_DIR.mkdir(exist_ok=True)


def log_webhook(event_type: str, payload: dict):
    """Save webhook data to a log file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = LOG_DIR / f"{timestamp}_{event_type}.json"
    
    with open(filename, "w") as f:
        json.dump(payload, f, indent=2)
    
    print(f"📝 Saved to {filename}")


def handle_webhook(data: dict):
    """Process incoming webhook data"""
    if data.get("type") == "connection":
        print(f"✅ {data['message']}")
        return

    if data.get("type") == "pong":
        return  # Heartbeat response

    # Handle collaborative session commands
    if data.get("type") == "collaborative_session_command":
        if SESSION_MANAGER_AVAILABLE:
            response = session_manager.process_command(data)

            # Display response
            if response.get("status") == "success":
                print(f"✅ {response.get('message', 'Command successful')}")
            else:
                print(f"❌ {response.get('message', 'Command failed')}")
                if response.get("error"):
                    print(f"   Error: {response['error']}")
        else:
            print("⚠️  Received collaborative session command but session manager not available")
        return

    # Handle LLM conversation insights
    if data.get("type") == "llm_conversation_insight":
        if LLM_HANDLER_AVAILABLE:
            # Validate insight structure
            is_valid, error = validate_llm_insight(data)
            if not is_valid:
                print(f"❌ Invalid LLM insight: {error}")
                return

            # Process the insight
            llm_handler.handle_insight(data)
        else:
            print("⚠️  Received LLM insight but handler not available")
        return

    if data.get("type") != "webhook":
        print(f"⚠️  Unknown message type: {data.get('type')}")
        return

    # Handle GitHub webhooks
    event_type = data.get("event")
    delivery_id = data.get("delivery_id")
    payload = data.get("payload", {})

    print(f"\n🔔 Received GitHub webhook:")
    print(f"   Event: {event_type}")
    print(f"   Delivery ID: {delivery_id}")
    print(f"   Timestamp: {data.get('timestamp')}")

    # Log the webhook
    log_webhook(event_type, data)

    # Handle specific events
    if event_type == "push":
        handle_push_event(payload)
    elif event_type == "pull_request":
        handle_pr_event(payload)
    elif event_type == "issues":
        handle_issue_event(payload)
    else:
        print(f"   Action: {payload.get('action', 'N/A')}")


def handle_push_event(payload: dict):
    """Handle push events"""
    ref = payload.get("ref", "")
    commits = payload.get("commits", [])
    pusher = payload.get("pusher", {}).get("name", "unknown")
    
    print(f"   Branch: {ref}")
    print(f"   Pusher: {pusher}")
    print(f"   Commits: {len(commits)}")
    
    if commits:
        for commit in commits[:3]:  # Show first 3 commits
            print(f"      - {commit.get('message', '').split(chr(10))[0]}")


def handle_pr_event(payload: dict):
    """Handle pull request events"""
    action = payload.get("action")
    pr = payload.get("pull_request", {})
    pr_number = pr.get("number")
    title = pr.get("title")
    user = pr.get("user", {}).get("login")
    
    print(f"   Action: {action}")
    print(f"   PR #{pr_number}: {title}")
    print(f"   Author: {user}")


def handle_issue_event(payload: dict):
    """Handle issue events"""
    action = payload.get("action")
    issue = payload.get("issue", {})
    issue_number = issue.get("number")
    title = issue.get("title")
    user = issue.get("user", {}).get("login")
    
    print(f"   Action: {action}")
    print(f"   Issue #{issue_number}: {title}")
    print(f"   User: {user}")


async def connect_with_retry(max_retries: int = None, retry_delay: int = 5):
    """Connect to relay server with automatic retry"""
    retry_count = 0
    
    while max_retries is None or retry_count < max_retries:
        try:
            print(f"\n🔌 Connecting to relay server: {SERVER_URL}")
            
            async with websockets.connect(SERVER_URL) as websocket:
                print("✅ Connected! Waiting for webhooks...\n")
                retry_count = 0  # Reset on successful connection
                
                # Send periodic heartbeat
                async def heartbeat():
                    while True:
                        await asyncio.sleep(30)
                        try:
                            await websocket.send(json.dumps({"type": "ping"}))
                        except:
                            break
                
                heartbeat_task = asyncio.create_task(heartbeat())
                
                try:
                    async for message in websocket:
                        try:
                            data = json.loads(message)
                            handle_webhook(data)
                        except json.JSONDecodeError:
                            print(f"⚠️  Invalid JSON received: {message}")
                        except Exception as e:
                            print(f"❌ Error handling webhook: {e}")
                finally:
                    heartbeat_task.cancel()
                    
        except websockets.exceptions.ConnectionClosed:
            print("⚠️  Connection closed by server")
        except Exception as e:
            print(f"❌ Connection error: {e}")
        
        if max_retries is None or retry_count < max_retries:
            retry_count += 1
            print(f"🔄 Retrying in {retry_delay} seconds... (attempt {retry_count})")
            await asyncio.sleep(retry_delay)
        else:
            print("❌ Max retries reached. Exiting.")
            break


async def main():
    """Main entry point"""
    print("=" * 60)
    print("GitHub Webhook Client")
    print("=" * 60)
    print(f"Server: {SERVER_URL}")
    print(f"Log Directory: {LOG_DIR.absolute()}")
    print("=" * 60)
    
    await connect_with_retry()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Client stopped by user")
