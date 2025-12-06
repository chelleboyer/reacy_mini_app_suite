# Reachy Mini Daemon Setup Guide

The Reachy Mini daemon is a background service that manages all communication with the robot's hardware (or simulation). Your apps connect to this daemon as clients.

## Prerequisites

- Python 3.10 or later
- `reachy-mini` package installed (included in our requirements)
- For simulation: `git-lfs` installed on your system

## Quick Start

### 1. Simulation Mode (No Hardware Required)

Perfect for development and testing:

```bash
# Start daemon in simulation mode
reachy-mini-daemon --sim

# Optional: Add objects to the scene
reachy-mini-daemon --sim --scene minimal
```

You should see a MuJoCo window with Reachy Mini. The daemon is now ready to accept connections.

**Note for macOS users:**
```bash
# On macOS, you need to use mjpython
mjpython -m reachy_mini.daemon.app.main --sim
```

### 2. Real Hardware (USB Connection)

For the "lite" version connected via USB:

```bash
# Auto-detect serial port
reachy-mini-daemon

# Or specify port manually
reachy-mini-daemon -p /dev/ttyACM0  # Linux
reachy-mini-daemon -p /dev/cu.usbmodemXXXXX  # macOS
```

### 3. Wireless Version (Embedded CM4)

For Reachy Mini with embedded Raspberry Pi:

```bash
# On the robot's CM4
reachy-mini-daemon --no-localhost-only

# From your computer
# Connect to the robot's IP address
# (SDK will auto-discover on local network)
```

## Daemon Options

```bash
# Connection security
--localhost-only      # Only accept localhost connections (default)
--no-localhost-only   # Accept connections from any IP on network

# Simulation
--sim                 # Run in simulation mode
--scene <empty|minimal>  # Choose simulation scene (default: empty)
--headless           # Run MuJoCo without GUI

# Advanced
--serialport <port>   # Specify serial port for hardware
--check-collision     # Enable collision detection (simulation only)
--kinematics-engine <engine>  # Choose IK engine (default: AnalyticalKinematics)
```

## Verifying the Daemon

Once the daemon is running, you can test connectivity:

```python
from reachy_mini import ReachyMini

# This will connect to the daemon
with ReachyMini() as robot:
    status = robot.client.get_status()
    print(f"Connected! Simulation mode: {status['simulation_enabled']}")
```

Or from the command line:

```bash
# Check daemon status via REST API
curl http://localhost:8000/api/status
```

## Troubleshooting

### "Could not connect to daemon"

1. **Is the daemon running?**
   ```bash
   # Check for daemon process
   ps aux | grep reachy-mini-daemon
   ```

2. **Is the port correct?**
   - Default port is `8000`
   - Check for port conflicts: `lsof -i :8000`

3. **Firewall blocking connection?**
   - For `--no-localhost-only`, ensure firewall allows port 8000

### "Serial port not found" (Hardware)

```bash
# List available serial ports
# Linux:
ls /dev/ttyACM* /dev/ttyUSB*

# macOS:
ls /dev/cu.*

# Verify USB connection
lsusb  # Should show Dynamixel device
```

### MuJoCo window not appearing (Simulation)

```bash
# Install MuJoCo extras if missing
pip install reachy-mini[mujoco]

# Check OpenGL support
python -c "import mujoco; print('MuJoCo OK')"

# Try headless mode if display issues
reachy-mini-daemon --sim --headless
```

## Daemon Lifecycle

### Starting

The daemon can be started manually (as above) or programmatically:

```python
from reachy_mini import ReachyMini

# Auto-spawn daemon in simulation mode
robot = ReachyMini(spawn_daemon=True, use_sim=True)
```

### Stopping

```bash
# Ctrl+C in the terminal where daemon is running
# Or kill the process
pkill -f reachy-mini-daemon
```

### Running as Service (Production)

For Reachy Mini wireless version, the daemon runs as a systemd service:

```bash
# Check status
sudo systemctl status reachy-mini-daemon

# Start/stop
sudo systemctl start reachy-mini-daemon
sudo systemctl stop reachy-mini-daemon

# View logs
sudo journalctl -u reachy-mini-daemon -f
```

## Development Workflow

### Recommended Setup (Two Terminals)

**Terminal 1: Daemon**
```bash
cd reachy_mini_app_suite
source venv/bin/activate
reachy-mini-daemon --sim
```

**Terminal 2: Your App**
```bash
cd reachy_mini_app_suite
source venv/bin/activate
python src/apps/oobe-demo-menu/main.py
```

### Testing Without Restarting Daemon

The daemon stays running; your app connects and disconnects. You can:
- Edit your app code
- Restart your app
- Run multiple apps simultaneously (they share the daemon)

The daemon only needs restarting if:
- You want to switch between sim and hardware
- The daemon crashes or behaves unexpectedly
- You're changing daemon-level configuration

## REST API (Alternative to SDK)

The daemon also exposes a REST API if you prefer HTTP:

```bash
# Get current state
curl http://localhost:8000/api/state/full

# Set target position (requires proper JSON structure)
curl -X POST http://localhost:8000/api/target/head \
  -H "Content-Type: application/json" \
  -d '{"pose": [...]}'
```

See `src-reference/reachy_mini/docs/rest-api.md` for full API documentation.

## Architecture Diagram

```
┌──────────────────────────────────────┐
│  Your Apps                           │
│  (multiple apps can connect)         │
└────────────┬─────────────────────────┘
             │ Zenoh protocol
             │ (localhost or network)
┌────────────▼─────────────────────────┐
│  reachy-mini-daemon                  │
│  ┌──────────────────────────────┐    │
│  │ Web Server (FastAPI)         │    │
│  │ - REST API on :8000          │    │
│  └──────────────────────────────┘    │
│  ┌──────────────────────────────┐    │
│  │ Zenoh Server                 │    │
│  │ - Pub/sub messaging          │    │
│  └──────────────────────────────┘    │
│  ┌──────────────────────────────┐    │
│  │ Control Loop                 │    │
│  │ - Kinematics                 │    │
│  │ - Joint limits               │    │
│  │ - Interpolation              │    │
│  └──────────────────────────────┘    │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│  Hardware OR MuJoCo Simulation       │
└──────────────────────────────────────┘
```

## Additional Resources

- **SDK Documentation**: `src-reference/reachy_mini/docs/python-sdk.md`
- **REST API**: `src-reference/reachy_mini/docs/rest-api.md`
- **Examples**: `src-reference/reachy_mini/examples/`
- **Official Repo**: https://github.com/pollen-robotics/reachy_mini

## Support

If you encounter issues:

1. Check daemon logs for error messages
2. Verify SDK version: `pip show reachy-mini`
3. Test with minimal example: `src-reference/reachy_mini/examples/minimal_demo.py`
4. Open issue on GitHub: https://github.com/pollen-robotics/reachy_mini/issues
