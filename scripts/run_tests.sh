#!/bin/bash
# Quick test runner for development

set -e

echo "Running Reachy Mini App Suite tests..."
echo "========================================"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run tests with pytest
echo ""
echo "Running pytest..."
pytest tests/ -v --cov=src --cov-report=term-missing

echo ""
echo "Tests complete!"
