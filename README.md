# GitHub Webhook Relay

A webhook relay system that enables local machines to receive GitHub webhook events through a cloud-hosted relay server.

**New to this project?** → See [CONTRIBUTING.md](CONTRIBUTING.md) for complete onboarding guide

## Architecture

```
GitHub Event → Cloud Relay Server → WebSocket → Local Client
```

- **Server** (`app.py`): FastAPI-based relay that receives webhooks and broadcasts via WebSocket
- **Client** (`client/`): Local client that connects to relay and processes webhook events

## Quick Start

### 1. Deploy Server

**Railway** (Recommended):
```bash
railway login
railway init
railway up
railway domain  # Get your deployment URL
```

**Render**: Connect your GitHub repo via Render dashboard (uses `render.yaml`)

### 2. Configure GitHub Webhook

1. Go to your repo → Settings → Webhooks → Add webhook
2. **Payload URL**: `https://your-deployed-server.com/webhook`
3. **Content type**: `application/json`
4. **Secret**: Set a secret and add it to your server's `GITHUB_WEBHOOK_SECRET` env var
5. **Events**: Select events or "Send me everything"
6. Click "Add webhook"

### 3. Run Local Client

```bash
cd client
pip install -r requirements.txt

export RELAY_SERVER_URL="wss://your-app.railway.app/ws"
python client.py
```

Now when GitHub events occur, they'll appear instantly in your local terminal!

### 4. (Optional) Send LLM Conversation Insights

Integrate with AI assistants to capture insights from conversations:

```python
# See examples/send_insight.py for full example
import requests

requests.post(
    "https://your-app.railway.app/webhook",
    headers={"X-API-Key": "your-api-key"},
    json={
        "type": "llm_conversation_insight",
        "version": "1.0",
        "timestamp": "2025-11-15T10:30:00Z",
        "conversation": {"id": "conv_001", "context": "Planning new features"},
        "insight": {
            "type": "action_item",
            "priority": "high",
            "title": "Implement rate limiting",
            "content": "Add rate limiting to webhook endpoint",
            "tags": ["security"]
        },
        "metadata": {"llm_model": "claude", "confidence": 0.95}
    }
)
```

Review insights with the CLI tool:
```bash
python tools/insights_cli.py list --priority high
python tools/insights_cli.py stats
```

**See [docs/LLM_INTEGRATION.md](docs/LLM_INTEGRATION.md) for complete guide.**

## Development

### Run Server Locally

```bash
pip install -r requirements.txt
python app.py
```

Server runs on `http://localhost:8000`

### Run Client Locally

```bash
cd client
pip install -r requirements.txt

export RELAY_SERVER_URL="ws://localhost:8000/ws"
python client.py
```

### Test Webhook Endpoint

```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: ping" \
  -d '{"zen": "test", "hook_id": 123}'
```

## Configuration

### Server Environment Variables

- `PORT` - Server port (default: 8000)
- `GITHUB_WEBHOOK_SECRET` - Webhook signature verification secret (optional but recommended)
- `ENVIRONMENT` - Environment indicator (development/production)

### Client Environment Variables

- `RELAY_SERVER_URL` - WebSocket URL of relay server (required)
  - Local: `ws://localhost:8000/ws`
  - Production: `wss://your-app.railway.app/ws`

## Customizing Event Handlers

Edit `client/client.py` to add custom logic for different GitHub events:

```python
def handle_webhook(data: dict):
    event_type = data.get("event")
    payload = data.get("payload")

    if event_type == "push":
        # Trigger deployment, run tests, etc.
        subprocess.run(["./deploy.sh"])

    elif event_type == "pull_request":
        # Auto-review, generate descriptions, etc.
        subprocess.run(["./review-pr.sh", str(payload["number"])])
```

## Features

- Real-time webhook delivery to local machine
- Automatic reconnection with retry logic
- Webhook signature verification (HMAC-SHA256)
- Support for multiple simultaneous clients
- Automatic event logging to `webhook_logs/`
- Heartbeat mechanism to maintain connections

## Use Cases

**GitHub Webhooks:**
- Trigger local scripts on GitHub events
- Build custom CI/CD pipelines
- Auto-generate PR descriptions/reviews
- Real-time repository activity monitoring

**LLM Conversation Insights:**
- Capture action items from AI conversations
- Track ideas and decisions automatically
- Organize conversation insights by type and priority
- Review and act on insights via CLI tool
- Integration with AI workflows

## Security

- Always use `GITHUB_WEBHOOK_SECRET` in production
- Use WSS (not WS) for production WebSocket connections
- Logs are stored locally in `webhook_logs/` - review .gitignore settings

See [SECURITY_SETUP.md](SECURITY_SETUP.md) for detailed security configuration.

## Documentation

- **[CONTRIBUTING.md](CONTRIBUTING.md)** - New engineer onboarding guide
- **[CLAUDE.md](CLAUDE.md)** - Architecture details and development patterns (for Claude Code)
- **[SECURITY_SETUP.md](SECURITY_SETUP.md)** - Security configuration and testing
- **[docs/deployment/](docs/deployment/)** - Deployment guides and reports
- **[docs/worklogs/](docs/worklogs/)** - Development session logs
- **[FUTURE_TASKS.md](FUTURE_TASKS.md)** - Roadmap of planned improvements

## License

MIT
