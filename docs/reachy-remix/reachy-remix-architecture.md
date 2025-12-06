# Reachy Remix - Technical Architecture Document

**Version:** 1.0  
**Date:** December 5, 2025  
**Status:** Architecture Review  
**Architect:** Winston

---

## 1. Architecture Overview

### 1.1 Design Philosophy

**Principles:**
- **Simple Core, Flexible Periphery** - Stable motion engine with pluggable input layers
- **Separation of Concerns** - UI, logic, and robot control are cleanly decoupled
- **Single-File Deployment** - All code in one file for maximum simplicity
- **Zero Persistence** - Stateless by design, eliminating save/load complexity
- **Extensible Foundation** - Architecture enables future voice/vision without refactoring

### 1.2 System Layers

```
┌─────────────────────────────────────────────────────┐
│           Gradio UI Layer (Presentation)             │
│  • Move Palette Buttons                             │
│  • Sequence Display                                 │
│  • Play Controls                                    │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│        Application Logic (Orchestration)            │
│  • State Management (IDLE/PLAYING/ERROR)            │
│  • Sequence Builder                                 │
│  • Input Validation                                 │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│         Motion Engine (Core Business Logic)         │
│  • Move → SDK Call Mapping                          │
│  • Sequence Execution                               │
│  • Micro-feedback Generation                        │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│      Reachy SDK Integration (Hardware Interface)    │
│  • ReachyWrapper                                    │
│  • SafeMotionController                             │
└─────────────────────────────────────────────────────┘
```

---

## 2. Core Components

### 2.1 Motion Engine

**Purpose:** Pure motion logic, independent of UI or input method.

**Interface:**
```python
class MotionEngine:
    """Core motion execution engine - UI-agnostic."""
    
    def __init__(self, robot: ReachyWrapper):
        self.robot = robot
        self.controller = SafeMotionController()
    
    def execute_move(self, move_id: str) -> bool:
        """Execute a single move. Returns success status."""
        pass
    
    def execute_sequence(self, sequence: List[str]) -> ExecutionResult:
        """Execute a full sequence with inter-move delays."""
        pass
    
    def get_micro_feedback(self, move_id: str) -> None:
        """Provide subtle acknowledgment after move completion."""
        pass
```

**Move Mapping:**
```python
MOVE_REGISTRY = {
    "wave": lambda: controller.wave_antennas(robot, count=2),
    "robot_pose": lambda: controller.transition_to_pose(
        robot, roll=0, pitch=0, yaw=0, duration=1.0, degrees=True
    ),
    "spin": lambda: [
        robot.move_head(yaw=-30, duration=0.5, degrees=True),
        robot.move_head(yaw=30, duration=0.5, degrees=True),
        robot.move_head(yaw=0, duration=0.5, degrees=True),
    ],
    "stretch": lambda: controller.transition_to_pose(
        robot, pitch=-15, left_antenna=0.8, right_antenna=-0.8, 
        duration=1.5, degrees=True
    ),
    "dab": lambda: [
        robot.move_head(roll=20, pitch=-10, yaw=15, duration=0.8, degrees=True),
        robot.move_antennas(left=-0.5, right=0.8, duration=0.8),
    ],
    "pause": lambda: time.sleep(0.5),
}
```

**Why this matters:**
- Voice engine later: `parse_command("Reachy, wave!") → execute_move("wave")`
- Vision engine later: `detect_gesture(frame) → execute_move("spin")`
- Same core logic, different input sources

---

### 2.2 State Management

**State Machine:**
```python
from enum import Enum

class PlayState(Enum):
    IDLE = "idle"           # Ready for user input
    PLAYING = "playing"     # Executing sequence
    ERROR = "error"         # Recovery needed

class AppState:
    """Manages application state."""
    
    def __init__(self):
        self.current_state = PlayState.IDLE
        self.sequence: List[str] = []
        self.error_message: Optional[str] = None
    
    def can_play(self) -> bool:
        """Check if play action is allowed."""
        return (
            self.current_state == PlayState.IDLE 
            and len(self.sequence) > 0
        )
    
    def start_playing(self) -> None:
        """Transition to PLAYING state."""
        if self.can_play():
            self.current_state = PlayState.PLAYING
    
    def finish_playing(self) -> None:
        """Return to IDLE after execution."""
        self.current_state = PlayState.IDLE
    
    def set_error(self, message: str) -> None:
        """Enter ERROR state."""
        self.current_state = PlayState.ERROR
        self.error_message = message
```

**State Transitions:**
```
IDLE ─(add move)→ IDLE
IDLE ─(play with valid sequence)→ PLAYING
PLAYING ─(complete)→ IDLE
PLAYING ─(error)→ ERROR
ERROR ─(clear/undo)→ IDLE
```

---

### 2.3 Sequence Builder

**Purpose:** Manage the dance sequence list.

```python
class SequenceBuilder:
    """Manages sequence construction."""
    
    def __init__(self):
        self.moves: List[str] = []
    
    def add_move(self, move_id: str) -> str:
        """Add move to sequence. Returns updated display."""
        self.moves.append(move_id)
        return self.format_sequence()
    
    def undo_last(self) -> str:
        """Remove last move. Returns updated display."""
        if self.moves:
            self.moves.pop()
        return self.format_sequence()
    
    def clear_all(self) -> str:
        """Clear sequence. Returns empty state message."""
        self.moves = []
        return "Tap moves above to build your dance! 🎵"
    
    def format_sequence(self) -> str:
        """Format sequence for display with emojis."""
        if not self.moves:
            return "Tap moves above to build your dance! 🎵"
        
        emoji_map = {
            "wave": "👋",
            "robot_pose": "🤖",
            "spin": "💃",
            "stretch": "🙆",
            "dab": "🕺",
            "pause": "⏸",
        }
        
        emojis = [emoji_map.get(move, "❓") for move in self.moves]
        return f"Your Dance: {' '.join(emojis)}"
```

---

## 3. Gradio UI Architecture

### 3.1 Theme Configuration

```python
import gradio as gr

# Custom theme for kid-friendly interface
theme = gr.themes.Soft(
    primary_hue="violet",
    secondary_hue="orange",
    font=gr.themes.GoogleFont("Fredoka"),  # Playful, rounded font
    radius_size=gr.themes.sizes.radius_lg,
)

# Custom CSS for animations and hover effects
custom_css = """
.move-button {
    min-width: 80px !important;
    min-height: 80px !important;
    font-size: 2em !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.move-button:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.sequence-display {
    background: linear-gradient(135deg, #667eea22 0%, #764ba222 100%);
    padding: 25px;
    border-radius: 15px;
    font-size: 1.5em;
    text-align: center;
    min-height: 80px;
}

.control-button {
    min-width: 100px !important;
    min-height: 60px !important;
    font-size: 1.3em !important;
}

.status-message {
    font-size: 1.1em;
    padding: 15px;
    border-radius: 10px;
}
```

### 3.2 Layout Structure

```python
with gr.Blocks(theme=theme, css=custom_css) as app:
    # State management
    app_state = gr.State(AppState())
    
    gr.Markdown("# 🎵 Reachy Remix - Motion Builder")
    
    with gr.Row():
        # Left: Move Palette
        with gr.Column(scale=1):
            gr.Markdown("## 🎨 Moves")
            
            btn_wave = gr.Button("👋 Wave", elem_classes=["move-button"])
            btn_robot = gr.Button("🤖 Robot Pose", elem_classes=["move-button"])
            btn_spin = gr.Button("💃 Spin", elem_classes=["move-button"])
            btn_stretch = gr.Button("🙆 Stretch", elem_classes=["move-button"])
            btn_dab = gr.Button("🕺 Dab", elem_classes=["move-button"])
            btn_pause = gr.Button("⏸ Pause", elem_classes=["move-button"])
        
        # Center: Sequence Display
        with gr.Column(scale=2):
            gr.Markdown("## 🎬 Your Creation")
            
            sequence_display = gr.Markdown(
                "Tap moves above to build your dance! 🎵",
                elem_classes=["sequence-display"]
            )
        
        # Right: Controls
        with gr.Column(scale=1):
            gr.Markdown("## 🎮 Controls")
            
            btn_play = gr.Button("▶️ Play", elem_classes=["control-button"], variant="primary")
            btn_undo = gr.Button("↩️ Undo", elem_classes=["control-button"])
            btn_clear = gr.Button("🧹 Clear", elem_classes=["control-button"])
    
    # Status bar
    status_display = gr.Markdown("Ready! 🎉", elem_classes=["status-message"])
```

---

## 4. SDK Integration

### 4.1 Reachy Wrapper Usage

We use the existing `ReachyWrapper` and `SafeMotionController` from `src/common/reachy/`:

```python
from src.common.reachy.robot_wrapper import ReachyWrapper
from src.common.reachy.safe_motions import SafeMotionController

# Initialize robot connection
robot = ReachyWrapper(media_backend="no_media")
robot.connect()
robot.wake_up()

controller = SafeMotionController()
```

**Available Methods:**
- `robot.move_head(roll, pitch, yaw, duration, degrees=True)` - Head positioning
- `robot.move_antennas(left, right, duration)` - Antenna control
- `controller.wave_antennas(robot, count, speed)` - Gesture
- `controller.nod_yes(robot, count, speed)` - Gesture
- `controller.transition_to_pose(robot, ...)` - Safe pose transitions
- `controller.return_to_neutral(robot)` - Reset position

### 4.2 Safety Validation

All moves use `SafeMotionController` which enforces:
- Joint angle limits (validated against hardware specs)
- Safe movement speeds
- No extreme torque requirements
- Smooth transitions between poses

**Pre-validated moves:**
- ✅ Wave (antenna wave, gentle)
- ✅ Robot Pose (neutral stance)
- ✅ Spin (head rotation, controlled speed)
- ✅ Stretch (pitch + antenna extension, safe angles)
- ✅ Dab (combined roll/pitch/yaw, kid-friendly)
- ✅ Pause (no motion, just delay)

---

## 5. Execution Flow

### 5.1 Add Move Flow

```
User taps "👋 Wave"
    ↓
Button click handler
    ↓
sequence_builder.add_move("wave")
    ↓
Update sequence_display with emojis
    ↓
(Optional) Subtle animation: emoji bounces in
    ↓
Return to IDLE state
```

### 5.2 Play Sequence Flow

```
User clicks "▶️ Play"
    ↓
Check state.can_play()
    ├─ False → Display "Add at least one move first 🙂"
    └─ True → Continue
        ↓
    state.start_playing()
        ↓
    Disable all buttons (prevent spam)
        ↓
    motion_engine.execute_sequence(state.sequence)
        ├─ For each move:
        │   ├─ Execute move via SDK
        │   ├─ Wait for completion
        │   ├─ Optional: micro-feedback (nod/blink)
        │   └─ Inter-move delay (0.5s)
        └─ Complete
        ↓
    state.finish_playing()
        ↓
    Re-enable buttons
        ↓
    Display "Sequence complete! 🎉"
```

### 5.3 Error Handling

```python
try:
    motion_engine.execute_sequence(sequence)
except RobotConnectionError as e:
    state.set_error("Robot disconnected. Please reconnect.")
    status_display.update("⚠️ Robot disconnected")
except MotionExecutionError as e:
    state.set_error(f"Motion failed: {e}")
    status_display.update("⚠️ Something went wrong, try again!")
finally:
    state.finish_playing()
    enable_buttons()
```

---

## 6. Future Extensibility

### 6.1 Voice Engine (Phase 2)

**Architecture:**
```python
class VoiceEngine:
    """Converts voice commands to motion sequences."""
    
    def __init__(self, motion_engine: MotionEngine):
        self.motion_engine = motion_engine
    
    def parse_command(self, audio: bytes) -> List[str]:
        """Convert speech to move IDs."""
        # Example: "Reachy, wave then spin"
        # → ["wave", "spin"]
        pass
    
    def execute_voice_command(self, audio: bytes) -> None:
        """Parse and execute voice command."""
        moves = self.parse_command(audio)
        self.motion_engine.execute_sequence(moves)
```

**Gradio Integration:**
```python
# Add to existing UI (no core refactor)
with gr.Column():
    gr.Markdown("## 🎤 Voice Control")
    audio_input = gr.Audio(source="microphone")
    btn_voice = gr.Button("Speak Command")
    
    btn_voice.click(
        fn=voice_engine.execute_voice_command,
        inputs=[audio_input],
        outputs=[status_display]
    )
```

### 6.2 Vision Engine (Phase 3)

**Architecture:**
```python
class VisionEngine:
    """Detects gestures from camera and maps to moves."""
    
    def __init__(self, motion_engine: MotionEngine):
        self.motion_engine = motion_engine
        self.gesture_detector = MediaPipeHands()  # or similar
    
    def detect_gesture(self, frame: np.ndarray) -> Optional[str]:
        """Detect gesture in frame, return move ID."""
        # Example: Hand wave → "wave"
        #          Arms up → "stretch"
        pass
    
    def mirror_mode(self, video_stream) -> None:
        """Real-time: watch user, copy moves."""
        while True:
            frame = video_stream.read()
            move = self.detect_gesture(frame)
            if move:
                self.motion_engine.execute_move(move)
```

**Key Principle:** All engines feed the same `MotionEngine`. The core never changes.

---

## 7. Technical Specifications

### 7.1 Dependencies

**Required:**
```
gradio>=4.0.0
reachy-mini  # Reachy SDK
numpy
```

**Standard Library:**
```python
import time
from enum import Enum
from typing import List, Optional, Callable
from dataclasses import dataclass
```

### 7.2 Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| Play button response | < 150ms | Time from click to first motor command |
| UI update latency | < 50ms | Time from button click to display update |
| Sequence execution | 0.5s inter-move delay | Configurable per move |
| State machine overhead | < 10ms | State transition time |
| Memory footprint | < 100MB | Total RAM usage (excluding Gradio) |

### 7.3 File Structure

**Single-file deployment:**
```
reachy_remix.py        # Main application (entire implementation)
```

**Imports existing modules:**
```python
from src.common.reachy.robot_wrapper import ReachyWrapper
from src.common.reachy.safe_motions import SafeMotionController
```

---

## 8. Testing Strategy

### 8.1 Unit Tests

```python
# test_motion_engine.py
def test_move_registry():
    """Verify all moves are mapped correctly."""
    assert "wave" in MOVE_REGISTRY
    assert callable(MOVE_REGISTRY["wave"])

def test_state_transitions():
    """Verify state machine logic."""
    state = AppState()
    assert state.current_state == PlayState.IDLE
    
    state.sequence = ["wave"]
    assert state.can_play() == True
    
    state.start_playing()
    assert state.current_state == PlayState.PLAYING
    assert state.can_play() == False  # Can't play while playing
```

### 8.2 Integration Tests

```python
# test_integration.py
def test_full_sequence_execution(mock_robot):
    """Test complete add-play-clear cycle."""
    engine = MotionEngine(mock_robot)
    builder = SequenceBuilder()
    
    # Build sequence
    builder.add_move("wave")
    builder.add_move("spin")
    
    # Execute
    result = engine.execute_sequence(builder.moves)
    
    assert result.success == True
    assert mock_robot.move_count == 2

def test_spam_prevention():
    """Verify Play button can't be spammed."""
    state = AppState()
    state.sequence = ["wave"]
    
    state.start_playing()
    assert state.can_play() == False
    
    # Attempt to play again should be blocked
    with pytest.raises(InvalidStateError):
        state.start_playing()
```

### 8.3 UI Tests

```python
# test_ui.py
def test_button_responsiveness():
    """Test UI updates within latency targets."""
    start = time.time()
    sequence_display.update("👋 🤖")
    latency = time.time() - start
    
    assert latency < 0.05  # 50ms target

def test_theme_application():
    """Verify custom theme loads correctly."""
    app = create_app()
    assert app.theme.primary_hue == "violet"
    assert "Fredoka" in app.theme.font.google
```

---

## 9. Deployment

### 9.1 Launch Command

```bash
python reachy_remix.py
```

### 9.2 Gradio Configuration

```python
if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",  # Accessible on network
        server_port=7860,
        share=False,  # Local only for security
        inbrowser=True,  # Auto-open browser
    )
```

### 9.3 Environment Requirements

- Python 3.8+
- Reachy Mini daemon running (if using real hardware)
- Network access to Reachy (default: localhost)

---

## 10. Architecture Decision Records

### ADR-001: Single-File Deployment

**Decision:** Implement entire app in one Python file.

**Rationale:**
- Simplifies deployment (single file to copy)
- Reduces cognitive overhead for educators
- Easier to share and modify
- Aligns with "radical simplicity" goal

**Trade-offs:**
- File will be ~500-800 lines (manageable)
- Less modular than multi-file
- Accepted for MVP; can refactor later if needed

### ADR-002: No Persistence Layer

**Decision:** No save/load functionality, sessions are ephemeral.

**Rationale:**
- Eliminates complexity of file I/O, databases
- Fits use case: kids experiment, not preserve
- "Every session is a fresh canvas" becomes a feature
- Can add later if user research demands it

### ADR-003: Engine Pattern for Extensibility

**Decision:** Separate MotionEngine from UI, prepare for future input modes.

**Rationale:**
- Voice/vision are strategic differentiators
- Refactoring later would be costly
- Clean interfaces now = plug-and-play later
- Minimal overhead (<50 lines for abstraction)

**Validation:** Can add VoiceEngine with zero MotionEngine changes.

---

## 11. Risk Analysis

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Robot connection drops mid-sequence | High | Medium | Add reconnection logic, graceful degradation |
| Play button spam causes motion overlap | High | High | **✅ SOLVED:** State machine prevents concurrent execution |
| Kids tap too fast, UI lags | Medium | Medium | Debounce button clicks, async UI updates |
| Move executions take longer than expected | Low | Low | Add timeout detection, skip to next move |
| Theme doesn't render on older browsers | Low | Low | Fallback to Gradio default theme |

---

## 12. Success Criteria

**Architecture is approved when:**

✅ All components have clear interfaces  
✅ SDK integration is validated with existing wrappers  
✅ State machine prevents invalid operations  
✅ Future voice/vision extension is feasible without refactor  
✅ Performance targets are achievable (< 150ms response)  
✅ File structure supports single-file deployment  
✅ Team consensus: architecture is simple yet extensible  

---

## 13. Next Steps

**Immediate:**
1. **Architecture Review** (This document) - Get team sign-off
2. **Story Breakdown** - Bob creates implementation stories
3. **Proof of Concept** - Build minimal version (3 moves, basic UI)

**Implementation Sprint:**
1. Story 1: Gradio UI shell + theme
2. Story 2: MotionEngine + SDK integration
3. Story 3: State machine + sequence builder
4. Story 4: Visual polish + animations
5. Story 5: Testing + acceptance validation

**Post-MVP:**
- User testing with kids (validate fun factor)
- Performance profiling
- Voice engine prototype

---

**Architecture Status:** ✅ READY FOR REVIEW

**Review with:** John (PM), Bob (SM), Amelia (DEV), Murat (TEA), Sally (UX)

**Expected feedback cycle:** 24-48 hours → Iterate → Approve → Begin implementation
