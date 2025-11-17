#!/bin/bash

# Stop MVP - Voice LLM to Local Action System
# This script stops all running services

echo "========================================"
echo "Stopping MVP Services"
echo "========================================"
echo ""

# Stop webhook client
if [ -f .client.pid ]; then
    CLIENT_PID=$(cat .client.pid)
    if ps -p $CLIENT_PID > /dev/null 2>&1; then
        echo "🛑 Stopping webhook client (PID: $CLIENT_PID)..."
        kill $CLIENT_PID
        sleep 1
        # Force kill if still running
        if ps -p $CLIENT_PID > /dev/null 2>&1; then
            kill -9 $CLIENT_PID 2>/dev/null || true
        fi
        echo "✅ Webhook client stopped"
    else
        echo "⚠️  Webhook client not running"
    fi
    rm .client.pid
else
    echo "⚠️  No webhook client PID file found"
fi

# Stop results server
if [ -f .results.pid ]; then
    RESULTS_PID=$(cat .results.pid)
    if ps -p $RESULTS_PID > /dev/null 2>&1; then
        echo "🛑 Stopping results viewer (PID: $RESULTS_PID)..."
        kill $RESULTS_PID
        sleep 1
        # Force kill if still running
        if ps -p $RESULTS_PID > /dev/null 2>&1; then
            kill -9 $RESULTS_PID 2>/dev/null || true
        fi
        echo "✅ Results viewer stopped"
    else
        echo "⚠️  Results viewer not running"
    fi
    rm .results.pid
else
    echo "⚠️  No results viewer PID file found"
fi

echo ""
echo "========================================"
echo "✅ All services stopped"
echo "========================================"
echo ""
echo "💡 To start again:"
echo "   ./start_mvp.sh"
echo ""
