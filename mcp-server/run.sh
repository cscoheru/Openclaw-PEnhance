#!/bin/bash
# PEnhance MCP Server Runner
# Usage: ./run.sh or python3 penhance_mcp.py

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if mcp is installed
if ! python3 -c "import mcp" 2>/dev/null; then
    echo "Installing mcp package..."
    pip3 install mcp
fi

# Run the MCP server
cd "$SCRIPT_DIR"
exec python3 penhance_mcp.py
