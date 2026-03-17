#!/bin/bash
# PEnhance Proxy Startup Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$SCRIPT_DIR"

# Check if already running
if pgrep -f "penhance_proxy.py" > /dev/null; then
    echo "PEnhance Proxy is already running"
    echo "To stop: pkill -f penhance_proxy.py"
    exit 0
fi

# Start proxy
echo "Starting PEnhance Proxy..."
nohup python3 penhance_proxy.py > "$PROJECT_DIR/logs/proxy.log" 2>&1 &

sleep 2

# Verify it started
if curl -s http://127.0.0.1:8080/health > /dev/null 2>&1; then
    echo "✅ PEnhance Proxy started successfully"
    echo "   Health: http://127.0.0.1:8080/health"
    echo "   Stats:  http://127.0.0.1:8080/stats"
    echo "   Logs:   $PROJECT_DIR/logs/proxy.log"
else
    echo "❌ Failed to start PEnhance Proxy"
    echo "Check logs: $PROJECT_DIR/logs/proxy.log"
    exit 1
fi
