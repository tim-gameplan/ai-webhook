# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a GitHub webhook relay system that enables local machines to receive GitHub webhook events through a cloud-hosted relay server. The architecture consists of two components:

- **Server** (`app.py`): FastAPI-based relay server that receives GitHub webhooks and broadcasts them to connected clients via WebSocket
- **Client** (`client/client.py`): Local WebSocket client that connects to the relay server and processes incoming webhook events

**Data Flow**: GitHub Event → Cloud Relay Server (`/webhook` endpoint) → WebSocket → Local Client

## Development Commands

### Server Development
```bash
# Install server dependencies
pip install -r requirements.txt

# Run server locally
python app.py
# Server runs on http://localhost:8000

# Run server with custom port
PORT=3000 python app.py
```

### Client Development
```bash
# Install client dependencies
cd client
pip install -r requirements.txt

# Run client (connects to local server)
RELAY_SERVER_URL="ws://localhost:8000/ws" python client.py

# Run client (connects to deployed server)
RELAY_SERVER_URL="wss://your-app.railway.app/ws" python client.py
```

### Testing
```bash
# Test server health
curl http://localhost:8000/

# Test webhook endpoint
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: ping" \
  -d '{"zen": "test", "hook_id": 123}'

# Test with signature verification (if GITHUB_WEBHOOK_SECRET is set)
# See server/app.py:35-50 for signature verification logic
```

### Deployment

**Railway**:
```bash
cd server
railway login
railway init
railway up
railway domain  # Get deployment URL
```

**Render**: Push to GitHub and connect via Render dashboard (uses `render.yaml`)

## Architecture Notes

### WebSocket Connection Management
- Server maintains a set of connected clients (`server/app.py:21`)
- Clients auto-reconnect with exponential backoff (`client/client.py:108-155`)
- Heartbeat mechanism prevents connection timeouts (30-second intervals)
- Disconnected clients are automatically removed from the broadcast list

### Webhook Signature Verification
The server supports optional GitHub webhook signature verification:
- Set `GITHUB_WEBHOOK_SECRET` environment variable to enable
- Verification logic in `app.py:35-50`
- Uses HMAC-SHA256 comparison via `hmac.compare_digest()` to prevent timing attacks

### Event Broadcasting
When a webhook is received (`app.py:99-159`):
1. Server verifies signature (if secret configured)
2. Wraps payload with metadata (event type, delivery ID, timestamp)
3. Broadcasts to all connected WebSocket clients
4. Removes any clients that fail to receive
5. Returns status including number of clients notified

### Client Event Handling
The client provides customizable event handlers for different GitHub events:
- `handle_push_event()` - Process push events (`client/client.py:67-79`)
- `handle_pr_event()` - Process pull request events (`client/client.py:82-92`)
- `handle_issue_event()` - Process issue events (`client/client.py:95-105`)

Add custom logic in these handlers or create new ones in `handle_webhook()` (`client/client.py:31-64`)

### Logging
All webhook events are automatically saved to `webhook_logs/` directory with format: `{timestamp}_{event_type}.json`

## Configuration

**Server Environment Variables** (`.env` or deployment platform):
- `PORT` - Server port (default: 8000)
- `GITHUB_WEBHOOK_SECRET` - Optional webhook signature verification secret
- `ENVIRONMENT` - Optional environment indicator

**Client Environment Variables**:
- `RELAY_SERVER_URL` - WebSocket URL of relay server (required)
  - Local: `ws://localhost:8000/ws`
  - Production: `wss://your-app.railway.app/ws`

## Common Patterns

### Adding a New Event Handler
```python
# In client/client.py, add to handle_webhook():
elif event_type == "deployment":
    handle_deployment_event(payload)

# Then implement the handler:
def handle_deployment_event(payload: dict):
    environment = payload.get("deployment", {}).get("environment")
    print(f"   Environment: {environment}")
    # Add custom logic here
```

### Triggering External Scripts
```python
# In client event handlers
import subprocess

def handle_push_event(payload: dict):
    # Trigger local script when code is pushed
    subprocess.run(["./deploy.sh", payload.get("ref")])
```

## Important Implementation Details

- **Security**: Always use `GITHUB_WEBHOOK_SECRET` in production to verify webhook authenticity
- **WebSocket Protocol**: Client sends periodic pings; server responds with pongs to maintain connection
- **Error Handling**: Both server and client gracefully handle disconnections and malformed messages
- **Multiple Clients**: Server supports broadcasting to multiple simultaneous local clients
- **JSON Logging**: All webhook data is preserved in structured JSON format for audit/replay

## GitHub Webhook Configuration

When setting up GitHub webhooks, configure:
- **Payload URL**: `https://your-deployed-server.com/webhook`
- **Content type**: `application/json`
- **Secret**: Match your `GITHUB_WEBHOOK_SECRET` environment variable
- **Events**: Select specific events or "Send me everything"
