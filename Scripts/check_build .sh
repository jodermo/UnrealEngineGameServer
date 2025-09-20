#!/bin/bash
# Run this to see what actually got copied during the build

echo "=== Checking what was copied during Docker build ==="

# Check if the container exists first
if ! docker-compose ps | grep -q ue-game-server; then
    echo "Starting container temporarily..."
    docker-compose up -d ue-game-server
    sleep 5
fi

echo ""
echo "1. Checking build logs for content copying:"
docker-compose logs ue-game-server 2>&1 | grep -E "(Copying|Found|pak|ucas|utoc)" | head -20

echo ""
echo "2. Checking what's actually in the Content/Paks directory:"
docker-compose exec ue-game-server find /home/ue-server -name "*.pak" -o -name "*.ucas" -o -name "*.utoc" 2>/dev/null || echo "No .pak/.ucas/.utoc files found"

echo ""
echo "3. Checking what binaries were copied:"
docker-compose exec ue-game-server ls -la /home/ue-server/EvolutionGameServer/Binaries/Linux/

echo ""
echo "4. Checking Content directory structure:"
docker-compose exec ue-game-server find /home/ue-server/EvolutionGameServer/Content -type f 2>/dev/null | head -10 || echo "Content directory is empty"

echo ""
echo "5. Checking if build_temp was processed during build:"
docker-compose logs ue-game-server 2>&1 | grep -A 5 -B 5 "build_temp"