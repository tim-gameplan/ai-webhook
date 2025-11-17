#!/bin/bash

# Start MVP - Voice LLM to Local Action System
# This script starts all required services for the MVP

set -e  # Exit on error

echo "========================================"
echo "Starting MVP: Voice LLM → Local Actions"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "   Copy .env.example and configure:"
    echo "   cp .env.example .env"
    exit 1
fi

# Load environment variables
source .env

# Check if API_KEY is set
if [ -z "$API_KEY" ]; then
    echo "❌ Error: API_KEY not set in .env"
    exit 1
fi

echo "✅ Configuration loaded"
echo ""

# Check Python dependencies
echo "📦 Checking dependencies..."
if ! python3 -c "import websockets, dotenv, flask" 2>/dev/null; then
    echo "⚠️  Missing dependencies. Installing..."
    pip3 install -q websockets python-dotenv flask
    echo "✅ Dependencies installed"
else
    echo "✅ All dependencies present"
fi
echo ""

# Create necessary directories
mkdir -p webhook_logs
mkdir -p client/templates

# Initialize SQLite database if needed
if [ ! -f "$SQLITE_PATH" ] && [ "$SQLITE_PATH" != "" ]; then
    echo "📦 Initializing SQLite database at $SQLITE_PATH..."
    python3 -c "from client.storage.sqlite_backend import SimpleSQLiteBackend; SimpleSQLiteBackend('$SQLITE_PATH')"
    echo "✅ Database initialized"
    echo ""
fi

# Start webhook client in background
echo "🚀 Starting webhook client..."
nohup python3 -u client/client.py > client_output.log 2>&1 &
CLIENT_PID=$!
echo $CLIENT_PID > .client.pid
echo "   PID: $CLIENT_PID"
echo "   Logs: client_output.log"
echo ""

# Wait for client to initialize
sleep 2

# Check if client is running
if ! ps -p $CLIENT_PID > /dev/null; then
    echo "❌ Client failed to start. Check client_output.log"
    exit 1
fi

# Start results viewer in background
echo "🌐 Starting results viewer..."
nohup python3 client/results_server.py > results_server.log 2>&1 &
RESULTS_PID=$!
echo $RESULTS_PID > .results.pid
echo "   PID: $RESULTS_PID"
echo "   URL: http://localhost:5001"
echo "   Logs: results_server.log"
echo ""

# Wait for results server to start
sleep 2

# Check if results server is running
if ! ps -p $RESULTS_PID > /dev/null; then
    echo "❌ Results server failed to start. Check results_server.log"
    kill $CLIENT_PID 2>/dev/null || true
    exit 1
fi

echo "========================================"
echo "✅ MVP is running!"
echo "========================================"
echo ""
echo "📊 Services:"
echo "   • Webhook Client: PID $CLIENT_PID"
echo "   • Results Viewer: http://localhost:5001"
echo ""
echo "📖 Documentation:"
echo "   • Action Reference: docs/LLM_ACTIONS.md"
echo "   • ChatGPT Setup: docs/CHATGPT_SETUP.md"
echo "   • Claude Setup: docs/CLAUDE_SETUP.md"
echo ""
echo "🧪 Test it:"
echo "   curl -X POST https://web-production-3d53a.up.railway.app/webhook \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -H \"X-API-Key: $API_KEY\" \\"
echo "     -d @examples/git_status.json"
echo ""
echo "📜 View logs:"
echo "   tail -f client_output.log"
echo "   tail -f results_server.log"
echo ""
echo "🛑 Stop all services:"
echo "   ./stop_mvp.sh"
echo ""
