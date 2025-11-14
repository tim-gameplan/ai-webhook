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
from typing import Set
from datetime import datetime

app = FastAPI(title="GitHub Webhook Relay")

# Store connected WebSocket clients
connected_clients: Set[WebSocket] = set()

# Optional webhook secret for verification
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify GitHub webhook signature"""
    if not WEBHOOK_SECRET:
        return True  # Skip verification if no secret set
    
    if not signature:
        return False
    
    # GitHub sends signature as "sha256=<hash>"
    expected_signature = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


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
        
        # Keep connection alive and receive heartbeat/pings
        while True:
            data = await websocket.receive_text()
            # Echo back for heartbeat
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
    """
    # Get headers
    event_type = request.headers.get("X-GitHub-Event")
    signature = request.headers.get("X-Hub-Signature-256", "")
    delivery_id = request.headers.get("X-GitHub-Delivery")
    
    # Get raw body for signature verification
    body = await request.body()
    
    # Verify signature if secret is configured
    if not verify_signature(body, signature):
        print(f"Invalid signature for delivery {delivery_id}")
        return JSONResponse(
            status_code=403,
            content={"error": "Invalid signature"}
        )
    
    # Parse JSON payload
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid JSON payload"}
        )
    
    # Create webhook data package
    webhook_data = {
        "type": "webhook",
        "event": event_type,
        "delivery_id": delivery_id,
        "timestamp": datetime.utcnow().isoformat(),
        "payload": payload
    }
    
    print(f"Received {event_type} event (delivery: {delivery_id})")
    print(f"Broadcasting to {len(connected_clients)} clients")
    
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
