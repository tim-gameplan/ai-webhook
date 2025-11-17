"""
GitHub Webhook Relay Server

This server receives GitHub webhook events and broadcasts them to connected clients via WebSocket.
Deploy this to a cloud platform (Railway, Render, Fly.io, etc.)
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import hmac
import hashlib
import json
import os
import asyncio
from typing import Set, Dict
from datetime import datetime

app = FastAPI(title="GitHub Webhook Relay")

# Store connected WebSocket clients
connected_clients: Set[WebSocket] = set()

# Store pending synchronous task requests
# Format: {task_id: asyncio.Future}
pending_sync_tasks: Dict[str, asyncio.Future] = {}

# Security configuration
# Note: .strip() prevents trailing whitespace issues when copy/pasting secrets
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "").strip()  # GitHub webhook signature verification
API_KEY = os.getenv("API_KEY", "").strip()  # Optional API key for custom webhooks

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature using HMAC-SHA256"""
    if not WEBHOOK_SECRET:
        print("⚠️  WARNING: GITHUB_WEBHOOK_SECRET not set - signature verification disabled!")
        return True  # Skip verification if no secret set

    if not signature:
        print("❌ Webhook rejected: Missing signature header")
        return False

    # GitHub sends signature as "sha256=<hash>"
    expected_signature = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    is_valid = hmac.compare_digest(signature, expected_signature)
    if not is_valid:
        print(f"❌ Webhook rejected: Invalid signature")

    return is_valid


def verify_api_key(request: Request) -> bool:
    """Verify API key for custom (non-GitHub) webhooks"""
    if not API_KEY:
        return True  # Skip API key check if not configured

    # Check for API key in Authorization header or X-API-Key header
    auth_header = request.headers.get("Authorization", "")
    api_key_header = request.headers.get("X-API-Key", "")

    provided_key = ""
    if auth_header.startswith("Bearer "):
        provided_key = auth_header[7:]
    elif api_key_header:
        provided_key = api_key_header

    if not provided_key:
        print("❌ Webhook rejected: Missing API key")
        return False

    is_valid = hmac.compare_digest(provided_key, API_KEY)
    if not is_valid:
        print("❌ Webhook rejected: Invalid API key")

    return is_valid


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "github-webhook-relay",
        "connected_clients": len(connected_clients),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for clients to connect and receive webhook events"""
    await websocket.accept()
    connected_clients.add(websocket)
    client_id = id(websocket)
    
    print(f"Client {client_id} connected. Total clients: {len(connected_clients)}")
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to GitHub webhook relay",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep connection alive and receive messages from client
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            if message.get("type") == "task_result":
                # Client sending back task results for synchronous mode
                task_id = message.get("task_id")
                if task_id in pending_sync_tasks:
                    # Resolve the pending future with the result
                    pending_sync_tasks[task_id].set_result(message)
                    print(f"✅ Received sync result for task: {task_id}")
            elif message.get("type") == "ping":
                # Heartbeat - echo back
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                # Unknown message type - echo back for compatibility
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected")
    except Exception as e:
        print(f"Client {client_id} error: {e}")
    finally:
        connected_clients.discard(websocket)
        print(f"Client {client_id} removed. Total clients: {len(connected_clients)}")


@app.post("/webhook")
async def github_webhook(request: Request):
    """
    GitHub webhook endpoint
    Configure this URL in GitHub: https://your-server.com/webhook
    Supports both GitHub webhooks (with signature) and custom webhooks (with API key)
    """
    # Get headers
    event_type = request.headers.get("X-GitHub-Event")
    signature = request.headers.get("X-Hub-Signature-256", "")
    delivery_id = request.headers.get("X-GitHub-Delivery")

    # Get raw body for signature verification
    body = await request.body()

    # Determine if this is a GitHub webhook or custom webhook
    is_github_webhook = bool(signature or event_type)

    # Verify based on webhook type
    if is_github_webhook:
        # GitHub webhook - verify signature
        if not verify_signature(body, signature):
            print(f"❌ Invalid signature for delivery {delivery_id}")
            return JSONResponse(
                status_code=403,
                content={"error": "Invalid webhook signature"}
            )
    else:
        # Custom webhook - verify API key
        if not verify_api_key(request):
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid or missing API key"}
            )
    
    # Parse JSON payload
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid JSON payload"}
        )

    # Check if this is a synchronous request
    sync_mode = payload.get("sync", False)
    task_id = None

    if sync_mode:
        # Extract task ID for synchronous mode
        task_id = payload.get("data", {}).get("task_id")
        if not task_id:
            return JSONResponse(
                status_code=400,
                content={"error": "Synchronous mode requires task_id in data"}
            )

    # Create webhook data package
    webhook_data = {
        "type": "webhook",
        "sync": sync_mode,  # Include sync flag for client
        "event": event_type,
        "delivery_id": delivery_id,
        "timestamp": datetime.utcnow().isoformat(),
        "payload": payload
    }

    print(f"Received {event_type or 'custom'} event (delivery: {delivery_id}, sync: {sync_mode})")
    print(f"Broadcasting to {len(connected_clients)} clients")

    # If synchronous mode, create a future to wait for result
    result_future = None
    if sync_mode:
        result_future = asyncio.Future()
        pending_sync_tasks[task_id] = result_future
        print(f"⏳ Waiting for sync result: {task_id}")

    # Broadcast to all connected clients
    disconnected = set()
    for client in connected_clients:
        try:
            await client.send_json(webhook_data)
        except Exception as e:
            print(f"Failed to send to client: {e}")
            disconnected.add(client)

    # Remove disconnected clients
    connected_clients.difference_update(disconnected)

    # If synchronous mode, wait for result
    if sync_mode and result_future:
        try:
            # Wait up to 30 seconds for task completion
            start_time = datetime.utcnow()
            result = await asyncio.wait_for(result_future, timeout=30.0)
            end_time = datetime.utcnow()
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)

            # Clean up
            if task_id in pending_sync_tasks:
                del pending_sync_tasks[task_id]

            # Return the actual task result
            return JSONResponse({
                "status": result.get("status", "completed"),
                "task_id": task_id,
                "output": result.get("output"),
                "execution_time_ms": execution_time_ms,
                "clients_notified": len(connected_clients)
            })

        except asyncio.TimeoutError:
            # Task didn't complete in time
            if task_id in pending_sync_tasks:
                del pending_sync_tasks[task_id]

            print(f"⏱️  Timeout waiting for task: {task_id}")
            return JSONResponse(
                status_code=504,
                content={
                    "status": "timeout",
                    "task_id": task_id,
                    "error": "Task execution exceeded 30 second timeout",
                    "message": "Task may still be running locally. Check results viewer."
                }
            )

    # Asynchronous mode - return immediately
    return JSONResponse({
        "status": "received",
        "event": event_type,
        "delivery_id": delivery_id,
        "clients_notified": len(connected_clients)
    })


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
