# Reachy Mini SDK Integration Plan

**Date:** November 30, 2025  
**Sprint:** Foundation Sprint (Sprint 0)  
**Status:** 🟢 Ready for Implementation

---

## 🎯 Executive Summary

The **multi-agent team** has analyzed the Pollen Robotics `reachy_mini` SDK and determined a clear integration path for our app suite. The SDK is mature, well-documented, and installable via pip, making it an ideal **runtime dependency** rather than reference-only code.

### Key Findings

✅ **SDK is production-ready** (v1.1.2, Apache 2.0 license)  
✅ **Installable via pip**: `pip install reachy-mini`  
✅ **Clean Python API** with context managers and async support  
✅ **Daemon architecture** - our apps are SDK clients  
✅ **Examples available** in `src-reference/` for learning patterns  

### Recommendation

**Install `reachy_mini` as a proper pip dependency** and build our apps as thin clients on top of the SDK. This approach:
- Respects the "no runtime imports from `src-reference/`" rule
- Leverages battle-tested code from Pollen Robotics
- Enables easy updates via pip
- Maintains clear separation of concerns

---

## 📚 Agent Analysis

### 💻 Amelia (Dev): Technical Deep Dive

**SDK Structure:**
```python
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

# Basic usage pattern
with ReachyMini() as robot:
    pose = create_head_pose(z=10, roll=15, degrees=True, mm=True)
    robot.goto_target(head=pose, duration=2.0)
```

**Core Classes:**
- `ReachyMini` - Main robot control class
- `ZenohClient` - Communication layer (Zenoh protocol)
- `MediaManager` - Audio/video handling
- `Move` - Choreography/sequence system

**Key Methods:**
- `set_target()` - Immediate position setting
- `goto_target()` - Interpolated movement over duration
- `wake_up()` / `goto_sleep()` - Behavioral sequences
- `get_current_joint_positions()` - State reading
- `media.play_sound()` - Audio playback

**Safety Features Built-in:**
- Joint limit validation in daemon
- Smooth interpolation (min jerk, linear, ease, cartoon)
- Connection timeouts and health checks
- Gravity compensation mode available

### 🏗️ Winston (Architect): System Architecture

**Deployment Model:**

```
┌─────────────────────────────────────────┐
│  Our Apps (src/apps/*)                  │
│  ┌──────────────────────────────────┐   │
│  │  oobe-demo-menu                  │   │
│  │  reachy-sings                    │   │
│  │  karaoke-duet                    │   │
│  └──────────────────────────────────┘   │
│           ↓ (imports)                    │
│  ┌──────────────────────────────────┐   │
│  │  src/common/                     │   │
│  │  - ReachyWrapper (thin layer)    │   │
│  │  - SafeMotionController          │   │
│  └──────────────────────────────────┘   │
│           ↓ (imports)                    │
│  ┌──────────────────────────────────┐   │
│  │  reachy_mini SDK (pip package)   │   │
│  │  - ReachyMini class              │   │
│  │  - utils, media, motion          │   │
│  └──────────────────────────────────┘   │
│           ↓ (Zenoh protocol)             │
│  ┌──────────────────────────────────┐   │
│  │  reachy-mini-daemon              │   │
│  │  (separate process)              │   │
│  │  - Motor control                 │   │
│  │  - Kinematics                    │   │
│  │  - Hardware I/O                  │   │
│  └──────────────────────────────────┘   │
│           ↓                              │
│  ┌──────────────────────────────────┐   │
│  │  Hardware OR Simulation          │   │
│  │  - Real robot motors             │   │
│  │  - OR MuJoCo simulator           │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

**Key Architectural Decisions:**

1. **Client-Daemon Pattern**: Apps connect to daemon, don't control hardware directly
2. **Zenoh Communication**: High-performance pub-sub middleware (Eclipse Zenoh)
3. **Thin Wrapper Philosophy**: `ReachyWrapper` adds app-specific conveniences, not reimplementations
4. **Media Separation**: Audio/video handled by SDK's `MediaManager`

### 📊 Mary (Analyst): Dependency Analysis

**SDK Dependencies (from pyproject.toml):**

**Core (always needed):**
- `numpy>=2.2.5` - Math operations
- `scipy>=1.15.3` - Kinematics calculations
- `reachy_mini_motor_controller>=1.4.2` - Motor interface (Rust bindings)
- `eclipse-zenoh>=1.4.0` - Communication protocol
- `opencv-python<=5.0` - Camera support
- `fastapi` - Web server for daemon
- `uvicorn[standard]` - ASGI server

**Optional Dependencies:**
- `mujoco==3.3.0` - Simulation ([mujoco])
- `placo==0.9.14` - Advanced kinematics ([placo_kinematics])
- Wireless version support ([wireless-version])

**Our Requirements Strategy:**

```toml
# Add to our requirements.txt:
reachy-mini>=1.1.2
reachy-mini[mujoco]  # For development/testing in simulation

# Do NOT add:
# - reachy-mini[wireless-version] (only needed on CM4 hardware)
# - reachy-mini[placo_kinematics] (optional advanced feature)
```

### 🧪 Murat (Test Architect): Testing Strategy

**Test Pyramid:**

```
         ╱────────────╲
        ╱   E2E Tests   ╲      ← Real hardware/sim integration
       ╱────────────────╲
      ╱  Integration      ╲    ← Apps + SDK + Mock daemon
     ╱──────────────────────╲
    ╱     Unit Tests          ╲ ← Our wrappers, utilities
   ╱────────────────────────────╲
```

**Testing Levels:**

1. **Unit Tests** (test our code, mock SDK):
   ```python
   def test_safe_motion_controller_clamps_values():
       controller = SafeMotionController()
       # Mock ReachyMini
       assert controller.clamp_joint(5.0, -1.0, 1.0) == 1.0
   ```

2. **Integration Tests** (use SDK + simulation):
   ```python
   @pytest.mark.integration
   def test_wrapper_connects_to_sim():
       # Requires daemon running in sim mode
       wrapper = ReachyWrapper()
       assert wrapper.is_connected()
   ```

3. **E2E Tests** (full app flow):
   ```python
   @pytest.mark.e2e
   def test_oobe_menu_launches_app():
       # Test complete user flow
       pass
   ```

**CI/CD Strategy:**
- Unit tests: Run on every commit (no daemon needed)
- Integration tests: Run with MuJoCo simulation in CI
- E2E tests: Manual/nightly on real hardware

### 📋 John (PM): Requirements & Risks

**Validated Requirements:**

| Requirement | Status | Notes |
|------------|--------|-------|
| CM4 compatibility | ✅ Confirmed | SDK designed for Pi CM4 |
| OOBE experience | ✅ Feasible | SDK has examples, media support |
| Multiple apps | ✅ Supported | Multiple SDK clients can connect |
| Safety controls | ✅ Built-in | Daemon enforces limits |
| HF integration | ⚠️ Custom | We must build HF client layer |

**Risk Assessment:**

🔴 **HIGH RISK:**
- **Hardware access for testing** - Do we have a robot or rely on sim?
  - *Mitigation:* Start with MuJoCo simulation, test patterns transferable to hardware

🟡 **MEDIUM RISK:**
- **Daemon management** - Apps assume daemon is running
  - *Mitigation:* Document daemon startup, add health checks, consider auto-spawn
- **Version compatibility** - SDK updates might break our code
  - *Mitigation:* Pin SDK version in requirements, test upgrades carefully

🟢 **LOW RISK:**
- **SDK stability** - v1.1.2 is mature, used in production apps
- **License compatibility** - Apache 2.0 allows commercial use

### 🏛️ Cloud Dragonborn (Game Architect): Integration Wisdom

*strokes beard sagely*

The daemon architecture reveals wisdom: **we are not the controller, we are the choreographer**. 

Our apps must:
1. **Trust the daemon** - it handles hardware safety, we handle experience
2. **Think in sequences** - not individual motor commands, but fluid movements
3. **Embrace async** - the SDK supports async patterns for responsive UX
4. **Layer behaviors** - simple motions → gestures → expressions → performances

Example pattern from conversation app:
```python
# Movement manager runs in background thread
movement_manager = MovementManager(robot)
movement_manager.start()

# Tools trigger movements asynchronously
movement_manager.play_emotion("happy")
```

We should adopt similar patterns for our apps.

---

## 🔧 Implementation Plan

### Phase 1: Foundation (This Sprint)

#### Story 1.1: Install SDK as Dependency
**Acceptance Criteria:**
- [ ] Add `reachy-mini>=1.1.2` to `requirements.txt`
- [ ] Add `reachy-mini[mujoco]` to `requirements-dev.txt`
- [ ] Update `scripts/setup_dev.sh` to install dependencies
- [ ] Document daemon startup in README
- [ ] Verify installation in clean virtualenv

**Implementation:**
```bash
# Update requirements.txt
echo "reachy-mini>=1.1.2" >> requirements.txt

# Update requirements-dev.txt  
echo "reachy-mini[mujoco]>=1.1.2" >> requirements-dev.txt

# Test installation
./scripts/setup_dev.sh
source venv/bin/activate
python -c "from reachy_mini import ReachyMini; print('SDK imported successfully')"
```

#### Story 1.2: Implement ReachyWrapper
**Acceptance Criteria:**
- [ ] `ReachyWrapper.__init__()` creates `ReachyMini` instance
- [ ] `ReachyWrapper.connect()` validates connection to daemon
- [ ] `ReachyWrapper.is_connected()` checks daemon health
- [ ] `ReachyWrapper.move_to_pose()` wraps `goto_target()`
- [ ] `ReachyWrapper.get_joint_positions()` wraps SDK method
- [ ] Add connection retry logic with exponential backoff
- [ ] Add proper error handling and logging

**Implementation Pattern:**
```python
# src/common/reachy/robot_wrapper.py
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose
import logging

class ReachyWrapper:
    def __init__(self, localhost_only=True, media_backend="default"):
        self.logger = logging.getLogger(__name__)
        self._robot = None
        self._config = {
            "localhost_only": localhost_only,
            "media_backend": media_backend,
        }
    
    def connect(self, timeout=5.0):
        """Connect to Reachy Mini daemon."""
        try:
            self._robot = ReachyMini(
                localhost_only=self._config["localhost_only"],
                timeout=timeout,
                media_backend=self._config["media_backend"],
            )
            self.logger.info("Connected to Reachy Mini daemon")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect: {e}")
            return False
    
    def is_connected(self):
        """Check if connected to daemon."""
        if self._robot is None:
            return False
        try:
            status = self._robot.client.get_status()
            return status is not None
        except:
            return False
    
    # ... rest of wrapper methods
```

#### Story 1.3: Update SafeMotionController
**Acceptance Criteria:**
- [ ] Use SDK's built-in safety features
- [ ] Add validation layer for app-specific constraints
- [ ] Implement smooth motion helpers (wave, nod, etc.)
- [ ] Add emergency stop capability
- [ ] Document safety philosophy

**Pattern:**
```python
# src/common/reachy/safe_motions.py
from reachy_mini.utils import create_head_pose

class SafeMotionController:
    # SDK handles joint limits, we add behavioral constraints
    
    MAX_SPEED_DEG_PER_SEC = 30.0  # Conservative for OOBE
    MIN_DURATION = 0.5  # Minimum movement time
    
    def smooth_wave(self, robot):
        """Safe waving gesture."""
        poses = [
            create_head_pose(roll=15, degrees=True),
            create_head_pose(roll=-15, degrees=True),
            create_head_pose(roll=0, degrees=True),
        ]
        for pose in poses:
            robot.goto_target(head=pose, duration=0.8, method="minjerk")
```

#### Story 1.4: Create Basic Demo
**Acceptance Criteria:**
- [ ] Simple script demonstrates connection
- [ ] Performs wave gesture
- [ ] Plays a sound
- [ ] Handles keyboard interrupt gracefully
- [ ] Works in both simulation and real hardware modes

**Example:**
```python
# examples/basic_demo.py
from src.common.reachy.robot_wrapper import ReachyWrapper
from src.common.reachy.safe_motions import SafeMotionController

def main():
    wrapper = ReachyWrapper()
    if not wrapper.connect():
        print("Failed to connect. Is daemon running?")
        return
    
    controller = SafeMotionController()
    
    try:
        print("Waking up...")
        wrapper.robot.wake_up()
        
        print("Waving...")
        controller.smooth_wave(wrapper.robot)
        
        print("Going to sleep...")
        wrapper.robot.goto_sleep()
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        wrapper.disconnect()

if __name__ == "__main__":
    main()
```

### Phase 2: OOBE Implementation (Next Sprint)

#### Story 2.1: Web UI with FastAPI
- Implement `SimpleWebServer` using FastAPI
- Serve static HTML/CSS/JS for OOBE menu
- Add WebSocket support for real-time updates

#### Story 2.2: OOBE Menu App
- Create button grid for app selection
- Implement app launching mechanism
- Add status indicators

#### Story 2.3: Simple Demo Moves
- Wave hello
- Nod yes/no
- Look around
- Happy/sad expressions

### Phase 3: Advanced Features (Future Sprints)

- Reachy Sings app with HF integration
- Karaoke Duet with lyrics sync
- Multi-robot coordination for Duet Stage

---

## 📝 Updated Project Structure

```
reachy_mini_app_suite/
├── requirements.txt              # ← ADD: reachy-mini>=1.1.2
├── requirements-dev.txt          # ← ADD: reachy-mini[mujoco]
├── src/
│   ├── apps/
│   │   └── oobe-demo-menu/
│   │       └── main.py          # ← UPDATE: Use ReachyWrapper
│   └── common/
│       ├── core/
│       │   ├── config.py        # ← UPDATE: Add daemon config
│       │   └── logger.py        # ← Already good
│       └── reachy/
│           ├── robot_wrapper.py # ← IMPLEMENT: Wrap SDK
│           └── safe_motions.py  # ← UPDATE: Use SDK utils
├── tests/
│   ├── conftest.py              # ← ADD: Pytest fixtures
│   ├── common/
│   │   ├── test_robot_wrapper.py  # ← NEW
│   │   └── test_safe_motions.py   # ← UPDATE
│   └── integration/             # ← NEW: Integration tests
│       └── test_sdk_connection.py
├── examples/                    # ← NEW: Quick demos
│   └── basic_demo.py
└── docs/
    ├── daemon-setup.md          # ← NEW: How to run daemon
    └── sdk-integration-plan.md  # ← This document
```

---

## 🚀 Getting Started (Developer Quick Start)

### 1. Install Dependencies
```bash
cd reachy_mini_app_suite
./scripts/setup_dev.sh
source venv/bin/activate
```

### 2. Start the Daemon (Simulation)
```bash
# Terminal 1: Start daemon in simulation mode
reachy-mini-daemon --sim
```

### 3. Run Example
```bash
# Terminal 2: Run example app
python examples/basic_demo.py
```

### 4. For Real Hardware
```bash
# On the CM4 or connected via USB
reachy-mini-daemon  # Auto-detects hardware

# From your dev machine (if wireless)
reachy-mini-daemon --no-localhost-only  # Allow network connections
```

---

## 📖 Key SDK Documentation

**From `src-reference/reachy_mini/`:**
- `README.md` - Installation and overview
- `docs/python-sdk.md` - Full SDK API reference
- `docs/rest-api.md` - HTTP API (if we need it)
- `examples/minimal_demo.py` - Simplest usage
- `examples/reachy_compliant_demo.py` - Compliance mode
- `examples/sequence.py` - Choreography patterns

**Online Resources:**
- GitHub: https://github.com/pollen-robotics/reachy_mini
- PyPI: https://pypi.org/project/reachy-mini/
- Pollen Robotics: https://www.pollen-robotics.com/reachy-mini/

---

## ✅ Decision Log

| Decision | Rationale | Date |
|----------|-----------|------|
| Install SDK via pip | Production-ready, maintained, Apache 2.0 license | Nov 30, 2025 |
| Keep `src-reference/` for learning | Good for examples, not for runtime | Nov 30, 2025 |
| Use daemon architecture | SDK's design, allows multiple clients | Nov 30, 2025 |
| Start with MuJoCo simulation | Enables testing without hardware | Nov 30, 2025 |
| Thin wrapper philosophy | Leverage SDK, don't reimplement | Nov 30, 2025 |

---

## 🎯 Success Criteria

**Sprint 0 Complete When:**
- [ ] SDK installed and importable
- [ ] `ReachyWrapper` connects to daemon
- [ ] Basic demo runs in simulation
- [ ] Tests pass (at least unit tests)
- [ ] Documentation updated
- [ ] Team can run examples locally

**Ready for Sprint 1 (OOBE) When:**
- [ ] All Story 1.x acceptance criteria met
- [ ] Integration tests passing with sim
- [ ] PRE-PRD updated with SDK learnings
- [ ] Architecture doc drafted

---

## 🧙 BMad Master: Final Recommendations

Based on the team's analysis:

1. **APPROVE** installing `reachy_mini` as runtime dependency
2. **PROCEED** with thin wrapper approach in `src/common/reachy/`
3. **PRIORITIZE** getting basic connection + movement working
4. **DEFER** advanced features (HF, singing) until foundation solid
5. **DOCUMENT** daemon setup clearly for team

**Next Action:** Implement Story 1.1 - Install SDK as Dependency

---

*Document prepared by the BMad Multi-Agent Team*  
*Lead: BMad Master 🧙*  
*Contributors: Amelia 💻, Winston 🏗️, Mary 📊, Murat 🧪, John 📋, Cloud Dragonborn 🏛️*
