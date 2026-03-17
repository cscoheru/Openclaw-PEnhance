#!/bin/bash
# PEnhance Proxy Stop Script

echo "Stopping PEnhance Proxy..."
pkill -f "penhance_proxy.py" 2>/dev/null

sleep 1

if pgrep -f "penhance_proxy.py" > /dev/null; then
    echo "❌ Failed to stop PEnhance Proxy"
    exit 1
else
    echo "✅ PEnhance Proxy stopped"
fi
