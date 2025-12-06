# API Reference

Complete reference for the Reachy Mini App Suite APIs.

## Table of Contents

- [ReachyWrapper](#reachywrapper)
- [SafeMotionController](#safemotioncontroller)
- [Configuration](#configuration)
- [Logging](#logging)

---

## ReachyWrapper

High-level wrapper for controlling Reachy Mini robots.

### Class: `ReachyWrapper`

```python
from common.reachy.robot_wrapper import ReachyWrapper
```

#### Constructor

```python
ReachyWrapper(
    host: str = "localhost",
    port: int = 8000,
    media_backend: str = "pyaudio",
    log_level: str = "INFO"
)
```

**Parameters:**
- `host` (str): Daemon hostname. Default: "localhost"
- `port` (int): Daemon port. Default: 8000
- `media_backend` (str): Audio backend ("pyaudio", "sounddevice", "no_media"). Default: "pyaudio"
- `log_level` (str): Logging level. Default: "INFO"

**Example:**
```python
with ReachyWrapper(media_backend="no_media") as robot:
    robot.wake_up()
```

#### Methods

##### `connect() -> bool`

Connect to the Reachy Mini daemon.

**Returns:** `bool` - True if connection successful

**Example:**
```python
robot = ReachyWrapper()
if robot.connect():
    print("Connected!")
```

##### `disconnect() -> None`

Disconnect from the daemon and cleanup resources.

##### `move_head(roll=0, pitch=0, yaw=0, x=0, y=0, z=0, duration=1.0, degrees=True, mm=True) -> None`

Move the robot's head to a target pose.

**Parameters:**
- `roll` (float): Roll angle. Default: 0
- `pitch` (float): Pitch angle. Default: 0
- `yaw` (float): Yaw angle. Default: 0
- `x` (float): X position offset. Default: 0
- `y` (float): Y position offset. Default: 0
- `z` (float): Z position offset. Default: 0
- `duration` (float): Movement duration in seconds. Default: 1.0
- `degrees` (bool): Use degrees for angles. Default: True
- `mm` (bool): Use millimeters for positions. Default: True

**Example:**
```python
# Look left
robot.move_head(yaw=-30, duration=1.5, degrees=True)

# Tilt head
robot.move_head(roll=15, pitch=-10, duration=1.0, degrees=True)
```

##### `move_antennas(left=0, right=0, duration=1.0) -> None`

Move the robot's antennas.

**Parameters:**
- `left` (float): Left antenna position in radians. Default: 0
- `right` (float): Right antenna position in radians. Default: 0
- `duration` (float): Movement duration in seconds. Default: 1.0

**Example:**
```python
# Wave antennas
robot.move_antennas(left=0.8, right=-0.8, duration=0.5)
```

##### `get_joint_positions() -> Tuple[np.ndarray, np.ndarray]`

Get current joint positions.

**Returns:** Tuple of (head_joints, antenna_joints)
- `head_joints` (ndarray): 7 head Stewart platform joints
- `antenna_joints` (ndarray): 2 antenna positions

**Example:**
```python
head, antennas = robot.get_joint_positions()
print(f"Head joints: {head}")
print(f"Antennas: {antennas}")
```

##### `get_head_pose() -> np.ndarray`

Get current head pose as 4x4 transformation matrix.

**Returns:** `ndarray` - 4x4 homogeneous transformation matrix

##### `wake_up() -> None`

Execute wake-up animation sequence.

##### `go_to_sleep() -> None`

Execute sleep animation sequence.

---

## SafeMotionController

Controller for safe robot motions with gesture library.

### Class: `SafeMotionController`

```python
from common.reachy.safe_motions import SafeMotionController
```

#### Constructor

```python
SafeMotionController(
    head_limits: Optional[dict] = None,
    antenna_limits: Optional[Tuple[float, float]] = None,
    max_velocity: float = 1.0,
    log_level: str = "INFO"
)
```

**Parameters:**
- `head_limits` (dict): Custom head joint limits. Default: conservative limits
- `antenna_limits` (tuple): Custom antenna limits. Default: (-π, π)
- `max_velocity` (float): Maximum angular velocity in rad/s. Default: 1.0
- `log_level` (str): Logging level. Default: "INFO"

**Example:**
```python
controller = SafeMotionController()
```

#### Validation Methods

##### `validate_head_angles(roll, pitch, yaw, degrees=False) -> Tuple[bool, List[str]]`

Validate head angles against safety limits.

**Returns:** Tuple of (is_valid, list_of_violations)

##### `clamp_head_angles(roll, pitch, yaw, degrees=False) -> Tuple[float, float, float]`

Clamp head angles to safe limits.

**Returns:** Tuple of (clamped_roll, clamped_pitch, clamped_yaw)

##### `validate_antenna_positions(left, right) -> Tuple[bool, List[str]]`

Validate antenna positions against limits.

##### `clamp_antenna_positions(left, right) -> Tuple[float, float]`

Clamp antenna positions to safe limits.

#### Gesture Methods

##### `nod_yes(robot, count=2, speed=1.0) -> None`

Perform a 'yes' nodding gesture.

**Parameters:**
- `robot` (ReachyWrapper): Robot instance
- `count` (int): Number of nods. Default: 2
- `speed` (float): Speed multiplier. Default: 1.0

**Example:**
```python
controller.nod_yes(robot, count=3, speed=1.5)
```

##### `shake_no(robot, count=2, speed=1.0) -> None`

Perform a 'no' head shaking gesture.

##### `tilt_curious(robot, direction="right") -> None`

Perform a curious head tilt.

**Parameters:**
- `direction` (str): "left" or "right". Default: "right"

##### `wave_antennas(robot, count=3, speed=1.0, synchronized=True) -> None`

Wave the antennas.

**Parameters:**
- `count` (int): Number of waves. Default: 3
- `speed` (float): Speed multiplier. Default: 1.0
- `synchronized` (bool): Synchronized or alternating. Default: True

##### `look_around(robot, speed=1.0) -> None`

Look around by scanning left and right.

##### `express_thinking(robot) -> None`

Express a 'thinking' pose.

#### Expression Methods

##### `express_happy(robot) -> None`

Express happiness with upward tilt and antenna wave.

##### `express_sad(robot) -> None`

Express sadness with downward tilt and drooping antennas.

##### `express_curious(robot) -> None`

Express curiosity with head tilt and perked antennas.

##### `express_confused(robot) -> None`

Express confusion with alternating head tilts.

##### `express_excited(robot) -> None`

Express excitement with rapid movements.

#### Transition Methods

##### `transition_to_pose(robot, roll=0, pitch=0, yaw=0, left_antenna=0, right_antenna=0, duration=1.0, degrees=True) -> None`

Smoothly transition to a specific pose with validation.

**Example:**
```python
controller.transition_to_pose(
    robot,
    roll=10, pitch=-5, yaw=20,
    left_antenna=0.5, right_antenna=-0.5,
    duration=1.5,
    degrees=True
)
```

##### `return_to_neutral(robot, duration=1.0) -> None`

Return robot to neutral pose.

---

## Configuration

Manage application configuration.

### Class: `Config`

```python
from common.core.config import Config
```

Load and manage configuration from JSON files with environment variable support.

**Example:**
```python
config = Config.load("config.json")
print(config.get("robot.host", default="localhost"))
```

---

## Logging

Consistent logging setup.

### Function: `setup_logger`

```python
from common.core.logger import setup_logger

logger = setup_logger(__name__, level="INFO")
logger.info("Application started")
```

**Parameters:**
- `name` (str): Logger name (typically `__name__`)
- `level` (str): Log level ("DEBUG", "INFO", "WARNING", "ERROR"). Default: "INFO"

---

## Complete Example

```python
from common.reachy.robot_wrapper import ReachyWrapper
from common.reachy.safe_motions import SafeMotionController

# Connect to robot
with ReachyWrapper(media_backend="no_media") as robot:
    controller = SafeMotionController()
    
    # Wake up
    robot.wake_up()
    
    # Perform gestures
    controller.wave_antennas(robot, count=2)
    controller.nod_yes(robot, count=1)
    
    # Show emotions
    controller.express_happy(robot)
    controller.express_curious(robot)
    
    # Custom pose
    controller.transition_to_pose(
        robot,
        roll=10, pitch=-5, yaw=15,
        left_antenna=0.3, right_antenna=-0.3,
        duration=1.5,
        degrees=True
    )
    
    # Return to neutral
    controller.return_to_neutral(robot)
```
