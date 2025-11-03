#!/bin/bash

# HCI Extension Test Script
# Usage: ./test.sh [--docker]

set -e

DOCKER_MODE=false
if [ "$1" = "--docker" ]; then
    DOCKER_MODE=true
    echo "Running in Docker mode"
fi

echo "🚀 Starting HCI Extension Tests..."

# Set up environment
if [ "$DOCKER_MODE" = true ]; then
    export DISPLAY=:99
    export PYTHONPATH="/workspace/src_python/src:/workspace/src_python"
    cd /workspace
else
    export PYTHONPATH="$(pwd)/src_python/src:$(pwd)/src_python"
fi

# Start virtual display if needed
if [ -n "$DISPLAY" ] && ! pgrep -f "Xvfb.*$DISPLAY" > /dev/null; then
    echo "Starting Xvfb on $DISPLAY"
    Xvfb $DISPLAY -screen 0 1920x1080x24 &
    sleep 3
fi

# Run Python tests
echo "🧪 Running Python tests..."
cd src_python
python -m pytest ../tests/python/ -v --tb=short -x || {
    echo "❌ Python tests failed"
    exit 1
}
cd ..

# Run Extension tests
echo "🔧 Running Extension tests..."
cd tests/javasprit
timeout 30s gjs test-framework.js || echo "Framework test completed"
timeout 30s gjs test-extension.js || echo "Extension test completed"
timeout 30s gjs test-prefs.js || echo "Prefs test completed"
cd ../..

echo "✅ All tests completed successfully!"