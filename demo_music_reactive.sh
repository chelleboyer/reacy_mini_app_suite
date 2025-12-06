#!/bin/bash
# Hardware Demo Launch Script for Music-Reactive Dance
# Run this to start the demo on physical Reachy Mini

echo "🎵🤖 Music-Reactive Dance - Hardware Demo"
echo "=========================================="
echo ""

cd /media/chelleboyer/11b2dbf1-e0cb-46fc-a13d-42068b6ab10c/code/reachy_mini_app_suite

# Check daemon
echo "✓ Checking Reachy daemon..."
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "  ✅ Daemon is running"
else
    echo "  ⚠️  Daemon not detected, but will try to connect anyway"
fi

echo ""
echo "✓ Audio devices available:"
./venv/bin/python -m src.apps.music-reactive.main --list-devices

echo ""
echo "🚀 Starting Music-Reactive Dance App..."
echo ""
echo "   Recommended: Use device 1 (Reachy Mini Audio)"
echo "   Command: ./venv/bin/python -m src.apps.music-reactive.main --device 1"
echo ""
echo "   Press Ctrl+C to stop"
echo ""
echo "=========================================="
echo ""

# Uncomment to auto-start with device 1:
# ./venv/bin/python -m src.apps.music-reactive.main --device 1
