#!/bin/bash
# Development setup script

set -e

echo "Setting up Reachy Mini App Suite development environment..."
echo "============================================================"

# Check Python version
python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Python version: $python_version"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)"; then
    echo "Error: Python 3.10 or later is required"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install package in development mode
echo ""
echo "Installing package in development mode..."
pip install -e .

# Verify reachy_mini SDK installation
echo ""
echo "Verifying reachy_mini SDK installation..."
if python3 -c "from reachy_mini import ReachyMini; print('✓ SDK imported successfully')" 2>/dev/null; then
    echo "✓ Reachy Mini SDK is properly installed"
else
    echo "⚠ Warning: Could not import reachy_mini SDK"
    echo "  This might be okay if running in limited environment"
fi

echo ""
echo "============================================================"
echo "Setup complete!"
echo ""
echo "To start the daemon in simulation mode:"
echo "  reachy-mini-daemon --sim"
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run tests:"
echo "  ./scripts/run_tests.sh"
echo ""
echo "To run an app:"
echo "  python src/apps/oobe-demo-menu/main.py"
