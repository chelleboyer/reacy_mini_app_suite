# Reachy Remix - User Stories

**Epic:** Reachy Remix Motion Builder MVP  
**Sprint:** Sprint 1 (5-day sprint)  
**Story Points:** 21 total  
**Scrum Master:** Bob  
**Date:** December 6, 2025

---

## Story Breakdown

### Story 1: Gradio UI Shell + Theme Setup
**Priority:** P0 (Foundation)  
**Story Points:** 3  
**Assignee:** Amelia (DEV)  
**Dependencies:** None

**User Story:**
As a developer, I need a themed Gradio interface with all UI components laid out, so that we have a visual foundation for the motion builder.

**Acceptance Criteria:**

- [ ] **AC1.1:** Gradio app launches successfully with `python reachy_remix.py`
- [ ] **AC1.2:** Custom theme applied:
  - Primary hue: violet
  - Secondary hue: orange
  - Font: Fredoka (or similar playful font)
  - Large radius for rounded buttons
- [ ] **AC1.3:** Custom CSS loaded with:
  - `.move-button` class: min 80x80px, hover scale(1.05)
  - `.sequence-display` class: gradient background, centered text
  - `.control-button` class: min 100x60px
- [ ] **AC1.4:** Layout structure complete:
  - Left column: 6 move buttons (👋 Wave, 🤖 Robot, 💃 Spin, 🙆 Stretch, 🕺 Dab, ⏸ Pause)
  - Center column: Sequence display area
  - Right column: 3 control buttons (▶️ Play, ↩️ Undo, 🧹 Clear)
  - Bottom: Status message area
- [ ] **AC1.5:** All buttons are clickable but show placeholder behavior (e.g., print to console)
- [ ] **AC1.6:** App accessible at `http://localhost:7860` and auto-opens browser

**Technical Notes:**
```python
import gradio as gr

theme = gr.themes.Soft(
    primary_hue="violet",
    secondary_hue="orange",
    font=gr.themes.GoogleFont("Fredoka"),
    radius_size=gr.themes.sizes.radius_lg,
)

custom_css = """
.move-button { min-width: 80px !important; min-height: 80px !important; ... }
.sequence-display { background: linear-gradient(...); ... }
.control-button { min-width: 100px !important; ... }
"""

with gr.Blocks(theme=theme, css=custom_css) as app:
    # Layout implementation
    pass

app.launch(server_port=7860, inbrowser=True)
```

**Definition of Done:**
- Code runs without errors
- All 6 moves + 3 controls render correctly
- Theme and CSS apply visually
- Screenshot captured for UX review

---

### Story 2: Motion Engine + SDK Integration
**Priority:** P0 (Core Logic)  
**Story Points:** 5  
**Assignee:** Amelia (DEV)  
**Dependencies:** Story 1 complete

**User Story:**
As a developer, I need a MotionEngine class that executes moves via Reachy SDK, so that button clicks can trigger actual robot movements.

**Acceptance Criteria:**

- [ ] **AC2.1:** `MotionEngine` class implemented with:
  - `__init__(self, robot: ReachyWrapper)`
  - `execute_move(self, move_id: str) -> bool`
  - `execute_sequence(self, sequence: List[str]) -> ExecutionResult`
  - `get_micro_feedback(self, move_id: str) -> None`
- [ ] **AC2.2:** `MOVE_REGISTRY` dictionary maps all 6 moves:
  - `"wave"` → `controller.wave_antennas(robot, count=2)`
  - `"robot_pose"` → `controller.transition_to_pose(robot, roll=0, pitch=0, yaw=0)`
  - `"spin"` → Head yaw sequence: -30° → 30° → 0°
  - `"stretch"` → Pitch -15° + antennas extended
  - `"dab"` → Roll 20°, pitch -10°, yaw 15° + antenna asymmetry
  - `"pause"` → `time.sleep(0.5)`
- [ ] **AC2.3:** Robot connection established:
  - `ReachyWrapper` initialized with `media_backend="no_media"`
  - Connection verified before first move
  - Graceful error if robot unavailable
- [ ] **AC2.4:** `execute_sequence()` runs moves sequentially with 0.5s inter-move delay
- [ ] **AC2.5:** Micro-feedback implemented (e.g., subtle head nod after each move completion)
- [ ] **AC2.6:** Error handling:
  - Catch `RobotConnectionError` → return error status
  - Catch `MotionExecutionError` → log and continue or abort based on severity
- [ ] **AC2.7:** Unit tests:
  - `test_move_registry_completeness()` - All 6 moves callable
  - `test_execute_single_move_success()` - Single move executes
  - `test_execute_sequence_with_delay()` - Inter-move timing verified
  - `test_error_handling()` - Graceful failure on robot disconnect

**Technical Notes:**
```python
from src.common.reachy.robot_wrapper import ReachyWrapper
from src.common.reachy.safe_motions import SafeMotionController
from dataclasses import dataclass
import time

@dataclass
class ExecutionResult:
    success: bool
    moves_completed: int
    error_message: Optional[str] = None

class MotionEngine:
    def __init__(self, robot: ReachyWrapper):
        self.robot = robot
        self.controller = SafeMotionController()
        self.MOVE_REGISTRY = {
            "wave": lambda: self.controller.wave_antennas(self.robot, count=2),
            # ... other moves
        }
    
    def execute_sequence(self, sequence: List[str]) -> ExecutionResult:
        moves_completed = 0
        try:
            for move_id in sequence:
                self.execute_move(move_id)
                self.get_micro_feedback(move_id)
                time.sleep(0.5)  # Inter-move delay
                moves_completed += 1
            return ExecutionResult(success=True, moves_completed=moves_completed)
        except Exception as e:
            return ExecutionResult(success=False, moves_completed=moves_completed, error_message=str(e))
```

**Definition of Done:**
- All unit tests pass
- Successfully executes all 6 moves on real/sim Reachy
- Error handling tested with disconnected robot
- Code reviewed by Winston (Architect)

---

### Story 3: State Management + Sequence Builder
**Priority:** P0 (Core Logic)  
**Story Points:** 5  
**Assignee:** Amelia (DEV)  
**Dependencies:** Story 1 complete

**User Story:**
As a user, I want to build a sequence by tapping moves and see it update instantly, so I can create my custom dance program.

**Acceptance Criteria:**

- [ ] **AC3.1:** `PlayState` enum implemented:
  - `IDLE`, `PLAYING`, `ERROR`
- [ ] **AC3.2:** `AppState` class implemented with:
  - `current_state: PlayState`
  - `sequence: List[str]`
  - `error_message: Optional[str]`
  - `can_play() -> bool` - Returns True only if IDLE and sequence not empty
  - `start_playing()` - Transitions IDLE → PLAYING
  - `finish_playing()` - Transitions PLAYING → IDLE
  - `set_error(message: str)` - Transitions to ERROR state
- [ ] **AC3.3:** `SequenceBuilder` class implemented with:
  - `add_move(move_id: str) -> str` - Adds move, returns formatted display
  - `undo_last() -> str` - Removes last move, returns updated display
  - `clear_all() -> str` - Clears sequence, returns empty state message
  - `format_sequence() -> str` - Converts move IDs to emoji display
- [ ] **AC3.4:** Emoji mapping correct:
  - wave → 👋, robot_pose → 🤖, spin → 💃, stretch → 🙆, dab → 🕺, pause → ⏸
- [ ] **AC3.5:** Empty state message: "Tap moves above to build your dance! 🎵"
- [ ] **AC3.6:** Sequence display format: "Your Dance: 👋 🤖 💃"
- [ ] **AC3.7:** Button click handlers connected:
  - Move buttons → `add_move()` → update `sequence_display`
  - Undo button → `undo_last()` → update `sequence_display`
  - Clear button → `clear_all()` → reset `sequence_display`
- [ ] **AC3.8:** State-based button disabling:
  - While PLAYING: all buttons disabled except status display
  - While IDLE: all buttons enabled
- [ ] **AC3.9:** Unit tests:
  - `test_state_transitions()` - Valid state machine flow
  - `test_can_play_validation()` - Play blocked when sequence empty
  - `test_add_move_updates_display()` - Emoji appears in sequence
  - `test_undo_removes_last()` - Last move removed correctly
  - `test_clear_resets_sequence()` - Sequence emptied

**Technical Notes:**
```python
from enum import Enum
from typing import List, Optional

class PlayState(Enum):
    IDLE = "idle"
    PLAYING = "playing"
    ERROR = "error"

class SequenceBuilder:
    def __init__(self):
        self.moves: List[str] = []
        self.emoji_map = {
            "wave": "👋", "robot_pose": "🤖", "spin": "💃",
            "stretch": "🙆", "dab": "🕺", "pause": "⏸"
        }
    
    def format_sequence(self) -> str:
        if not self.moves:
            return "Tap moves above to build your dance! 🎵"
        emojis = [self.emoji_map.get(m, "❓") for m in self.moves]
        return f"Your Dance: {' '.join(emojis)}"
```

**Definition of Done:**
- All unit tests pass
- Sequence updates instantly on button click (< 50ms)
- State machine prevents invalid operations
- Undo/Clear work reliably

---

### Story 4: Play Execution + Status Feedback
**Priority:** P0 (Core Feature)  
**Story Points:** 5  
**Assignee:** Amelia (DEV)  
**Dependencies:** Stories 2 & 3 complete

**User Story:**
As a user, I want to press Play and watch Reachy perform my sequence, with clear status messages, so I can see my creation come to life.

**Acceptance Criteria:**

- [ ] **AC4.1:** Play button click handler implemented:
  - Check `state.can_play()` before executing
  - If False: display "Add at least one move first 🙂"
  - If True: proceed with execution
- [ ] **AC4.2:** Execution flow:
  - `state.start_playing()` - Transition to PLAYING
  - Disable all buttons
  - Update status: "Playing your dance... 🎵"
  - Call `motion_engine.execute_sequence(state.sequence)`
  - Re-enable buttons after completion
  - `state.finish_playing()` - Transition back to IDLE
- [ ] **AC4.3:** Status messages during execution:
  - Before: "Ready! 🎉"
  - During: "Playing your dance... 🎵"
  - Success: "Sequence complete! 🎉"
  - Error: "⚠️ Something went wrong, try again!"
- [ ] **AC4.4:** Spam prevention:
  - Clicking Play while PLAYING state does nothing (button disabled)
  - State machine blocks concurrent execution attempts
- [ ] **AC4.5:** Error recovery:
  - On robot error: display error message, return to IDLE
  - Sequence remains intact (not cleared on error)
  - User can retry by pressing Play again
- [ ] **AC4.6:** Inter-move delay visible:
  - 0.5s pause between each move
  - Robot completes each move fully before next
- [ ] **AC4.7:** Integration tests:
  - `test_play_empty_sequence()` - Validation message shown
  - `test_play_full_sequence()` - All moves execute in order
  - `test_spam_play_button()` - Only one execution happens
  - `test_error_recovery()` - Returns to IDLE after error
  - `test_sequence_preserved_on_error()` - Sequence not lost

**Technical Notes:**
```python
def on_play_click(app_state: AppState, sequence_builder: SequenceBuilder):
    if not app_state.can_play():
        return gr.update(value="Add at least one move first 🙂")
    
    try:
        app_state.start_playing()
        # Disable buttons here
        
        result = motion_engine.execute_sequence(app_state.sequence)
        
        if result.success:
            status = "Sequence complete! 🎉"
        else:
            status = f"⚠️ {result.error_message}"
            
    except Exception as e:
        status = "⚠️ Something went wrong, try again!"
        app_state.set_error(str(e))
    finally:
        app_state.finish_playing()
        # Re-enable buttons here
    
    return gr.update(value=status)

btn_play.click(
    fn=on_play_click,
    inputs=[app_state, sequence_builder],
    outputs=[status_display]
)
```

**Definition of Done:**
- Play executes full sequence without errors
- Spam prevention verified (button disabled during execution)
- Status messages clear and encouraging
- Error handling tested with mock failures
- Performance: Play response < 150ms

---

### Story 5: Visual Polish + Animations
**Priority:** P1 (Enhancement)  
**Story Points:** 3  
**Assignee:** Amelia (DEV)  
**Reviewer:** Sally (UX)  
**Dependencies:** Stories 1-4 complete

**User Story:**
As a kid, I want the interface to feel alive and responsive, so the app is fun and engaging to use.

**Acceptance Criteria:**

- [ ] **AC5.1:** Move button hover effects working:
  - Scale up to 1.05x on hover
  - Smooth transition (0.2s ease)
  - Subtle box-shadow on hover
- [ ] **AC5.2:** Sequence display animations:
  - New emoji "bounces in" when added (subtle scale animation)
  - Sequence container wiggles slightly when Play pressed
- [ ] **AC5.3:** Button state visual feedback:
  - Play button changes to "⏸️ Playing..." with different color during execution
  - Disabled buttons appear visually grayed out
  - Undo button disabled when sequence empty
- [ ] **AC5.4:** Status message styling:
  - Success messages: green background tint
  - Error messages: orange/red background tint
  - Ready state: neutral/blue tint
- [ ] **AC5.5:** Responsive layout:
  - Works on tablet-sized screens (768px+)
  - Buttons remain tappable on touch devices
- [ ] **AC5.6:** Loading states:
  - Spinner or animation while robot connects
  - Clear "Connecting to Reachy..." message on startup
- [ ] **AC5.7:** UX review:
  - Sally confirms visual hierarchy is clear
  - Color contrast meets accessibility standards (WCAG AA)
  - Animations don't cause motion sickness (subtle, not jarring)

**Technical Notes:**
```css
/* Enhanced CSS animations */
@keyframes bounceIn {
    0% { transform: scale(0.3); opacity: 0; }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); opacity: 1; }
}

.sequence-emoji {
    animation: bounceIn 0.4s ease;
}

.sequence-display.wiggle {
    animation: wiggle 0.5s ease;
}

@keyframes wiggle {
    0%, 100% { transform: rotate(0deg); }
    25% { transform: rotate(-2deg); }
    75% { transform: rotate(2deg); }
}

.btn-disabled {
    opacity: 0.5;
    cursor: not-allowed;
    pointer-events: none;
}
```

**Gradio Component Updates:**
```python
# Dynamic button variant
btn_play = gr.Button(
    value="▶️ Play",
    variant="primary",
    interactive=True  # Will be toggled based on state
)

# Status with color coding
status_display = gr.Markdown(
    value="Ready! 🎉",
    elem_classes=["status-message", "status-ready"]
)
```

**Definition of Done:**
- All animations smooth (60 fps)
- Hover states work on desktop
- Touch interactions work on tablet
- Sally approves visual design
- No console errors
- Screenshot/video demo captured

---

## Testing Checklist

### Functional Testing
- [ ] All 6 moves execute correctly on Reachy
- [ ] Sequence builds accurately (moves added in order)
- [ ] Undo removes correct move
- [ ] Clear empties entire sequence
- [ ] Play button validation works (empty sequence blocked)
- [ ] Spam clicking Play doesn't cause issues
- [ ] Robot error handling works (disconnect scenario)

### Performance Testing
- [ ] Play response < 150ms
- [ ] UI update latency < 50ms
- [ ] No memory leaks during extended use (30+ sequences)
- [ ] Gradio app startup < 5 seconds

### UX Testing
- [ ] Buttons are large enough for kids (80x80px minimum)
- [ ] Emoji display is clear and readable
- [ ] Status messages are encouraging and clear
- [ ] Theme is playful and engaging
- [ ] Animations are subtle, not distracting

### Integration Testing
- [ ] Full workflow: Add 5 moves → Play → Undo 2 → Play → Clear
- [ ] Error recovery: Disconnect robot → Play → Reconnect → Retry
- [ ] State machine: Verify no invalid state transitions possible

---

## Sprint Plan

### Day 1 (Friday, Dec 6)
- **Morning:** Story 1 (Gradio UI shell)
- **Afternoon:** Story 1 complete + begin Story 2 (Motion Engine)

### Day 2 (Monday, Dec 9)
- **Morning:** Story 2 complete (SDK integration + testing)
- **Afternoon:** Story 3 (State management + Sequence builder)

### Day 3 (Tuesday, Dec 10)
- **Morning:** Story 3 complete + begin Story 4 (Play execution)
- **Afternoon:** Story 4 integration testing

### Day 4 (Wednesday, Dec 11)
- **Morning:** Story 5 (Visual polish)
- **Afternoon:** Full system testing

### Day 5 (Thursday, Dec 12)
- **Morning:** Bug fixes + final testing
- **Afternoon:** Demo + retrospective

---

## Acceptance Testing Scenarios

### Scenario 1: First-Time User
1. User opens app
2. Sees friendly empty state message
3. Taps "👋 Wave" button
4. Emoji appears in sequence display
5. Adds 3 more moves
6. Presses Play
7. Watches Reachy perform sequence
8. Sees success message

**Expected:** Seamless experience, no confusion

### Scenario 2: Error Recovery
1. User builds 5-move sequence
2. Robot disconnects mid-execution
3. Error message appears
4. User reconnects robot
5. Presses Play again
6. Sequence executes successfully

**Expected:** No data loss, clear error communication

### Scenario 3: Sequence Editing
1. User builds 8-move sequence
2. Realizes last 3 moves are wrong
3. Clicks Undo 3 times
4. Adds 2 different moves
5. Plays updated sequence

**Expected:** Undo works reliably, display updates correctly

---

## Definition of Done (Epic)

**MVP is complete when:**
- ✅ All 21 story points delivered
- ✅ All acceptance criteria met
- ✅ All unit and integration tests passing
- ✅ Performance targets achieved (< 150ms Play response)
- ✅ UX review approved by Sally
- ✅ Architecture review confirmed by Winston
- ✅ Demo successful with real Reachy hardware
- ✅ Code reviewed and merged to main branch
- ✅ Documentation updated (README with usage instructions)

---

## Risk Register

| Risk | Mitigation | Owner |
|------|------------|-------|
| Robot SDK breaking changes | Use existing ReachyWrapper (stable) | Amelia |
| Gradio theme not rendering | Test on multiple browsers, fallback theme | Amelia |
| Performance issues on slow hardware | Profile early, optimize bottlenecks | Amelia |
| Kids find interface confusing | Quick user test mid-sprint | Sally |
| State machine edge cases | Comprehensive unit tests | Murat |

---

**Stories Ready for Sprint:** ✅ Yes  
**Backlog Refinement Date:** December 6, 2025  
**Sprint Start:** December 6, 2025 (Today)  
**Sprint End:** December 12, 2025  
**Sprint Review:** December 12, 2025, 3:00 PM

---

**Next Action:** Amelia begins Story 1 (Gradio UI shell + theme setup)
