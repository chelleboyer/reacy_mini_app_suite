# Changelog

All notable changes to the Reachy Mini App Suite project.

## [Unreleased]

### Planned
- Story 1.4: OOBE Demo Menu with web UI
- Reachy Sings app implementation
- Karaoke Duet app implementation
- Duet Stage app implementation

## [0.2.0] - 2025-11-30

### Added - Story 1.3: SafeMotionController Gesture Library
- **8 pre-defined gestures:**
  - `nod_yes()` - Friendly yes gesture with configurable count and speed
  - `shake_no()` - Head shake for no response
  - `tilt_curious()` - Curious head tilt (left or right)
  - `wave_antennas()` - Synchronized or alternating antenna waves
  - `look_around()` - Scan environment left and right
  - `express_thinking()` - Thoughtful pose with head tilt

- **5 emotion expressions:**
  - `express_happy()` - Upward tilt with excited antenna wave
  - `express_sad()` - Downward gaze with drooping antennas
  - `express_curious()` - Head tilt with perked antennas
  - `express_confused()` - Alternating head tilts
  - `express_excited()` - Rapid movements and waves

- **Smooth transition helpers:**
  - `transition_to_pose()` - Move to custom pose with validation
  - `return_to_neutral()` - Reset to neutral position

- **New example scripts:**
  - `examples/gesture_demo.py` - Interactive storytelling sequence
  - `examples/test_gestures.py` - Comprehensive gesture validation

### Enhanced
- SafeMotionController now includes gesture library
- All gestures respect joint limits and velocity constraints
- Configurable speed multipliers for all gestures
- Synchronized and alternating antenna movement modes

### Testing
- Added 5 new unit tests for validation and clamping (9 total tests)
- Test coverage at 29%
- All gestures validated on physical robot

### Documentation
- Added API Reference documentation
- Added Getting Started guide
- Updated README with gesture examples
- Enhanced inline documentation

## [0.1.0] - 2025-11-30

### Added - Sprint 0: SDK Integration & ReachyWrapper
- **ReachyWrapper implementation:**
  - High-level API for robot control
  - Connection management with status logging
  - `move_head()` with full pose control (roll, pitch, yaw, x, y, z)
  - `move_antennas()` with proper ordering
  - `get_joint_positions()` returning head and antenna data
  - `get_head_pose()` returning 4x4 transformation matrix
  - `wake_up()` and `go_to_sleep()` animation sequences
  - Context manager support for automatic cleanup

- **SafeMotionController foundation:**
  - Joint limit validation for head and antennas
  - Angle clamping to safe ranges
  - Velocity-based duration calculation
  - Support for degrees and radians
  - Conservative default limits

- **Project infrastructure:**
  - Python package structure with src/ layout
  - pytest test suite (10 tests passing initially)
  - Development scripts (setup_dev.sh, run_tests.sh)
  - Comprehensive .gitignore for Python projects

- **Example scripts:**
  - `examples/test_wrapper.py` - Wrapper validation
  - `examples/simple_demo.py` - Basic movements

### Fixed
- NumPy version conflict between SDK (≥2.2.5) and opencv-python (<2.3.0)
- Test import errors by installing package in editable mode
- Invalid entry points in pyproject.toml (commented out until apps implemented)
- Audio device warnings with `no_media` backend option

### Dependencies
- reachy-mini SDK v1.1.2 integrated via pip
- NumPy 2.2.6
- SciPy 1.16.3
- MuJoCo 3.3.0 (dev dependency for simulation)

### Documentation
- SDK Integration Plan with multi-agent analysis
- Daemon Setup Guide with troubleshooting
- Workflow Summary documenting Sprint 0
- README with installation and usage instructions

### Testing
- 10 unit tests passing
- Physical robot validation on USB connection
- Daemon stability verified (PID 9880, stable throughout session)

## Project Milestones

### Sprint 0 - Foundation ✅ Complete
- [x] Story 1.1: SDK Integration
- [x] Story 1.2: ReachyWrapper Implementation
- [x] Story 1.3: SafeMotionController Gesture Library

### Sprint 1 - Interactive Features (In Progress)
- [ ] Story 1.4: OOBE Demo Menu
- [ ] Story 2.1: Reachy Sings App
- [ ] Story 2.2: Karaoke Duet App

### Future Sprints
- [ ] Sprint 2: Advanced Features
- [ ] Sprint 3: Polish & Performance

---

## Version Numbering

This project uses [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backwards-compatible)
- **PATCH**: Bug fixes (backwards-compatible)

## Release Notes Format

Each release includes:
- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements
