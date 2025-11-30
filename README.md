# Reachy Mini App Suite

A suite of delightful Python applications for Reachy Mini robots, designed for an exceptional out-of-box experience (OOBE).

## Overview

This project provides a collection of independent, CM4-friendly apps that make Reachy Mini accessible and fun for non-technical users while remaining extensible for developers.

### Current Status

✅ **Sprint 0 Complete** - SDK integration and wrapper implementation finished
- Reachy Mini SDK v1.1.2 integrated via pip
- `ReachyWrapper` provides high-level robot control API
- Physical hardware tested and validated (USB connection)
- Daemon running stably on real robot
- Test infrastructure in place (10 tests passing, 32% coverage)

### Featured Apps (Planned)

- **OOBE Demo Menu** - Main launcher and demo hub for first-time users
- **Reachy Sings** - Robot singing performances in various styles
- **Karaoke Duet** - Sing along with Reachy, with lyrics on your phone
- **Duet Stage** - Two-Reachy synchronized performances

## Project Structure

```
reachy_mini_app_suite/
├── src/                    # Application code
│   ├── apps/              # Individual apps
│   │   ├── oobe-demo-menu/
│   │   ├── reachy-sings/
│   │   ├── karaoke-duet/
│   │   └── duet-stage/
│   └── common/            # Shared utilities
│       ├── core/          # Config, logging, HTTP client
│       ├── reachy/        # Robot control wrappers
│       └── ui/            # Web UI helpers
├── src-reference/         # Reference code (read-only)
│   ├── reachy_mini/
│   ├── reachy_mini_conversation_app/
│   └── reachy-mini-motor-controller/
├── tests/                 # Test suites
├── docs/                  # Documentation
└── scripts/              # Development tools
```

## Quick Start

### Prerequisites

- Python 3.10 or later
- Reachy Mini robot (or simulator)
- CM4 (Raspberry Pi Compute Module 4) for deployment

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd reachy_mini_app_suite

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Starting the Reachy Daemon

The daemon must be running to control the robot:

```bash
# For physical robot connected via USB
reachy-mini-daemon --usb /dev/ttyACM0 --headless

# For simulation mode (requires MuJoCo)
reachy-mini-daemon --port 8000 --headless

# Check daemon status
ps aux | grep reachy-mini-daemon
```

See `docs/daemon-setup.md` for detailed setup and troubleshooting.

### Using ReachyWrapper

Quick example to control the robot:

```python
from src.common.reachy.robot_wrapper import ReachyWrapper

# Connect and use the robot
with ReachyWrapper(media_backend="no_media") as robot:
    # Wake up the robot
    robot.wake_up()
    
    # Move head (roll, pitch, yaw in degrees)
    robot.move_head(yaw=-30, duration=1.5)  # Look left
    robot.move_head(yaw=30, duration=1.5)   # Look right
    
    # Move antennas (positions in radians)
    robot.move_antennas(left=0.8, right=-0.8, duration=0.4)
    
    # Get current state
    head_joints, antenna_joints = robot.get_joint_positions()
    pose = robot.get_head_pose()
```

Run the demo:
```bash
python examples/simple_demo.py
```

### Running Apps (Coming Soon)

Individual apps are planned but not yet implemented:

```bash
# OOBE Demo Menu (planned)
python src/apps/oobe-demo-menu/main.py

# Reachy Sings (planned)
python src/apps/reachy-sings/main.py

# Karaoke Duet (planned)
python src/apps/karaoke-duet/main.py

# Duet Stage (planned)
python src/apps/duet-stage/main.py
```

## Development

### Design Principles

1. **Independence** - Each app is self-contained with its own entry point
2. **Shared Utilities** - Common functionality lives in `src/common/`
3. **Safe Hardware Interaction** - Respect joint limits and safe movement speeds
4. **OOBE First** - Designed for non-technical users
5. **HF Integration** - Heavy compute offloaded to Hugging Face services

### Reference Code

The `src-reference/` directory contains official Pollen Robotics repositories for reference:
- Read and learn from this code
- Copy and adapt small snippets as needed
- **Do NOT import from src-reference/ at runtime**

All runtime imports must come from:
- Python standard library
- Dependencies in `requirements.txt`
- Our own code in `src/`

### Testing

```bash
# Run all tests
pytest tests/

# Run specific test suite
pytest tests/apps/
pytest tests/common/

# Run with coverage
pytest --cov=src tests/

# Test the wrapper on physical robot
python examples/test_wrapper.py
```

Current test coverage: 32% (10 tests passing)

## Documentation

- [PRE-PRD](docs/pre-prd.reachy-app-suite.md) - Vision and high-level goals
- [Assistant Instructions](docs/assistant-instructions.md) - Development guidelines
- [SDK Integration Plan](docs/sprint-artifacts/sdk-integration-plan.md) - Detailed technical analysis
- [Daemon Setup Guide](docs/daemon-setup.md) - Setup and troubleshooting
- [Workflow Summary](docs/sprint-artifacts/workflow-init-summary.md) - Sprint 0 progress

## Contributing

This project follows the guidelines in `docs/assistant-instructions.md`. Key points:

- Keep app code in `src/apps/` and `src/common/`
- Treat `src-reference/` as read-only
- Maintain runtime independence from reference code
- Update documentation for new features

## License

[To be determined]

## Contact

Pollen Robotics - [contact@pollen-robotics.com](mailto:contact@pollen-robotics.com)
