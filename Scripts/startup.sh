#!/bin/bash
echo "=== UNREAL ENGINE DEDICATED SERVER STARTUP ==="
echo "Container started at: $(date)"
echo "User: $(whoami)"
echo "Working directory: $(pwd)"
echo ""

# Run diagnostics first
echo "Running diagnostics..."
./debug_server.sh

echo ""
echo "Starting game server..."
exec ./GameServer.sh