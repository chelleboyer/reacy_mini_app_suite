# Getting Started with Reachy Mini App Suite

This guide will help you get up and running with the Reachy Mini App Suite.

## Prerequisites

- **Hardware:** Reachy Mini robot (physical or simulation)
- **OS:** Linux (tested on Raspberry Pi OS)
- **Python:** 3.10 or later
- **Connection:** USB cable for physical robot, or MuJoCo for simulation

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/chelleboyer/reacy_mini_app_suite.git
cd reachy_mini_app_suite
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install runtime dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt

# Install package in editable mode
pip install -e .
```

### 4. Verify Installation

```bash
# Check SDK is installed
python -c "from reachy_mini import ReachyMini; print('SDK OK')"

# Run tests
pytest tests/
```

## Starting the Daemon

The Reachy Mini daemon must be running to control the robot.

### Physical Robot (USB)

```bash
# Start daemon for USB-connected robot
reachy-mini-daemon --usb /dev/ttyACM0 --headless

# Keep it running in the background
nohup reachy-mini-daemon --usb /dev/ttyACM0 --headless > daemon.log 2>&1 &
```

### Simulation Mode

```bash
# Requires MuJoCo
pip install reachy-mini[mujoco]

# Start daemon in simulation
reachy-mini-daemon --port 8000 --headless
```

### Verify Daemon

```bash
# Check if daemon is running
ps aux | grep reachy-mini-daemon

# Check daemon health
curl http://localhost:8000/health
```

## Your First Program

Create a file `hello_reachy.py`:

```python
from src.common.reachy.robot_wrapper import ReachyWrapper
from src.common.reachy.safe_motions import SafeMotionController

# Connect to robot
with ReachyWrapper(media_backend="no_media") as robot:
    controller = SafeMotionController()
    
    print("Connected to Reachy!")
    
    # Wake up
    robot.wake_up()
    
    # Wave hello
    controller.wave_antennas(robot, count=3)
    controller.nod_yes(robot, count=1)
    
    # Show excitement
    controller.express_happy(robot)
    
    print("Done!")
```

Run it:

```bash
python hello_reachy.py
```

## Running Examples

The `examples/` directory contains demonstrations:

```bash
# Simple movements
python examples/simple_demo.py

# Gesture showcase
python examples/gesture_demo.py

# Comprehensive test
python examples/test_gestures.py

# Wrapper validation
python examples/test_wrapper.py
```

## Project Structure

```
reachy_mini_app_suite/
├── src/
│   ├── common/
│   │   ├── core/           # Config, logging
│   │   ├── reachy/         # Robot control
│   │   │   ├── robot_wrapper.py      # High-level API
│   │   │   └── safe_motions.py       # Gestures & safety
│   │   └── ui/             # Web UI helpers
│   └── apps/               # Individual applications
├── examples/               # Demo scripts
├── tests/                  # Test suite
├── docs/                   # Documentation
└── src-reference/          # SDK reference code (read-only)
```

## Common Tasks

### Check Robot Status

```python
from src.common.reachy.robot_wrapper import ReachyWrapper

with ReachyWrapper(media_backend="no_media") as robot:
    head_joints, antennas = robot.get_joint_positions()
    print(f"Head joints: {head_joints}")
    print(f"Antennas: {antennas}")
    
    pose = robot.get_head_pose()
    print(f"Head pose:\n{pose}")
```

### Execute Safe Movements

```python
from src.common.reachy.safe_motions import SafeMotionController

controller = SafeMotionController()

# Validate before moving
is_valid, violations = controller.validate_head_angles(
    roll=50, pitch=60, yaw=100, degrees=True
)
if not is_valid:
    print("Unsafe angles:", violations)

# Clamp to safe limits
roll, pitch, yaw = controller.clamp_head_angles(
    50, 60, 100, degrees=True
)
print(f"Safe angles: roll={roll}, pitch={pitch}, yaw={yaw}")
```

### Create Custom Gestures

```python
def custom_greeting(robot, controller):
    """Custom greeting gesture."""
    # Look at person
    robot.move_head(pitch=-10, duration=0.8, degrees=True)
    
    # Wave antennas
    controller.wave_antennas(robot, count=2, synchronized=True)
    
    # Nod
    controller.nod_yes(robot, count=1, speed=1.2)
    
    # Happy expression
    controller.express_happy(robot)
    
    # Return to neutral
    controller.return_to_neutral(robot)

# Use it
with ReachyWrapper(media_backend="no_media") as robot:
    controller = SafeMotionController()
    robot.wake_up()
    custom_greeting(robot, controller)
```

## Troubleshooting

### Daemon Won't Start

```bash
# Check if port is in use
sudo lsof -i :8000

# Check USB device
ls -l /dev/ttyACM*

# View daemon logs
tail -f daemon.log
```

### Connection Failed

```bash
# Verify daemon is running
curl http://localhost:8000/health

# Check firewall
sudo ufw status

# Try different port
reachy-mini-daemon --usb /dev/ttyACM0 --port 8001 --headless
```

### Import Errors

```bash
# Reinstall in editable mode
pip install -e .

# Check package is installed
pip list | grep reachy

# Verify PYTHONPATH
python -c "import sys; print('\n'.join(sys.path))"
```

### Audio Warnings

If you see audio device warnings but don't need audio:

```python
# Use no_media backend
robot = ReachyWrapper(media_backend="no_media")
```

### Robot Not Moving

1. Check daemon is running: `ps aux | grep reachy-mini-daemon`
2. Check USB connection: `ls -l /dev/ttyACM*`
3. Check joint positions: `robot.get_joint_positions()`
4. Try wake_up: `robot.wake_up()`
5. Check daemon logs: `tail -f daemon.log`

## Next Steps

- Read the [API Reference](api-reference.md) for detailed documentation
- Check [Daemon Setup Guide](daemon-setup.md) for advanced configuration
- Explore [SDK Integration Plan](sprint-artifacts/sdk-integration-plan.md) for architecture details
- Review example scripts in `examples/` directory

## Getting Help

- **Issues:** https://github.com/chelleboyer/reacy_mini_app_suite/issues
- **Reachy SDK Docs:** See `src-reference/reachy_mini/docs/`
- **Logs:** Check `daemon.log` for daemon issues

## Safety Reminders

- Always use `SafeMotionController` for motion validation
- Test new movements in simulation first
- Keep robot workspace clear
- Use reasonable movement speeds
- Monitor first runs of new gestures
- Emergency stop: Ctrl+C or power off robot

Happy coding! 🤖
