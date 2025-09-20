#!/bin/bash
# debug_server.sh - Comprehensive UE Server Diagnostics

echo "========================================="
echo "UNREAL ENGINE SERVER DIAGNOSTICS"
echo "========================================="

PROJECT_NAME="${PROJECT_NAME:-EvolutionGame}"
BUILD_CONFIG="${BUILD_CONFIG:-Shipping}"

echo "1. Environment Variables:"
echo "   PROJECT_NAME: $PROJECT_NAME"
echo "   BUILD_CONFIG: $BUILD_CONFIG"
echo "   UE_MAP: $UE_MAP"
echo "   UE_PORT: $UE_PORT"
echo ""

echo "2. File System Structure:"
find /home/ue-server -type f -name "*Server*" 2>/dev/null | head -10
echo ""

echo "3. Content Analysis:"
echo "   Looking for .pak files..."
find /home/ue-server -name "*.pak" -type f 2>/dev/null | while read pak; do
    echo "   Found: $pak ($(du -h "$pak" | cut -f1))"
done

if [[ -z "$(find /home/ue-server -name "*.pak" -type f 2>/dev/null)" ]]; then
    echo "   ERROR: No .pak files found!"
fi
echo ""

echo "4. Project Files:"
find /home/ue-server -name "*.uproject" -type f 2>/dev/null | while read proj; do
    echo "   Found: $proj"
done
echo ""

echo "5. Binary Analysis:"
SERVER_BINARY=$(find /home/ue-server -name "*Server-Linux-*" -type f ! -name "*.target" ! -name "*.sym" ! -name "*.debug" 2>/dev/null | head -1)
if [[ -n "$SERVER_BINARY" ]]; then
    echo "   Binary: $SERVER_BINARY"
    echo "   Size: $(du -h "$SERVER_BINARY" | cut -f1)"
    echo "   Permissions: $(ls -la "$SERVER_BINARY")"
    echo "   File type: $(file "$SERVER_BINARY")"
    echo ""
    echo "   Dependencies (first 15):"
    ldd "$SERVER_BINARY" 2>/dev/null | head -15 || echo "   Could not check dependencies"
    echo ""
    echo "   Missing dependencies:"
    ldd "$SERVER_BINARY" 2>&1 | grep "not found" || echo "   No missing dependencies found"
else
    echo "   ERROR: No server binary found!"
    echo "   Available files in Binaries/Linux:"
    find /home/ue-server -path "*/Binaries/Linux/*" -type f 2>/dev/null
fi
echo ""

echo "6. Available Maps/Levels:"
find /home/ue-server -name "*.umap" -type f 2>/dev/null | head -10 | while read map; do
    echo "   Found map: $map"
done
echo ""

echo "7. Memory and Resources:"
echo "   Available memory: $(free -h | grep Mem | awk '{print $7}')"
echo "   Disk space: $(df -h / | tail -1 | awk '{print $4}')"
echo ""

echo "8. Testing Binary Execution:"
if [[ -n "$SERVER_BINARY" ]]; then
    echo "   Testing with -help flag..."
    timeout 10s "$SERVER_BINARY" -help 2>&1 | head -5 || echo "   Binary test failed or timed out"
fi
echo ""

echo "9. Log Directory Status:"
ls -la /var/log/ue/ 2>/dev/null || echo "   Log directory not accessible"
echo ""

echo "========================================="
echo "DIAGNOSTICS COMPLETE"
echo "========================================="