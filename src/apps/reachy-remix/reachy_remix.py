#!/usr/bin/env python3
"""
Reachy Remix - Scratch-Lite Motion Builder for Reachy Mini

A kid-friendly interface for building and executing dance sequences using
tap-to-add blocks. Single-file deployment with Gradio UI.

Architecture:
- UI Layer: Gradio Blocks with custom theme
- Logic Layer: State management & sequence building
- Engine Layer: Motion execution via Reachy SDK
- Hardware Layer: ReachyWrapper + SafeMotionController

Author: Reachy Dev Team
Date: December 6, 2025
Sprint: Story 1 - UI Shell + Theme
"""

import gradio as gr
from typing import List, Optional, Callable
from enum import Enum
from dataclasses import dataclass
import time
import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Story 2: Motion Engine + SDK Integration
try:
    from src.common.reachy.robot_wrapper import ReachyWrapper
    from src.common.reachy.safe_motions import SafeMotionController
    SDK_AVAILABLE = True
except ImportError:
    print("⚠️  Reachy SDK not available - running in demo mode")
    SDK_AVAILABLE = False
    ReachyWrapper = None
    SafeMotionController = None


# ============================================================
# THEME & STYLING
# ============================================================

# Custom Gradio theme - playful and kid-friendly
theme = gr.themes.Soft(
    primary_hue="violet",
    secondary_hue="orange",
    font=gr.themes.GoogleFont("Fredoka"),
    radius_size=gr.themes.sizes.radius_lg,
)

# Custom CSS for animations and enhanced styling
custom_css = """
/* Move buttons - large, colorful, tappable */
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

/* Sequence display - showcase area with gradient */
.sequence-display {
    background: linear-gradient(135deg, #667eea22 0%, #764ba222 100%);
    padding: 25px;
    border-radius: 15px;
    font-size: 1.5em;
    text-align: center;
    min-height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Control buttons - action buttons */
.control-button {
    min-width: 100px !important;
    min-height: 60px !important;
    font-size: 1.3em !important;
}

/* Status messages - clear feedback */
.status-message {
    font-size: 1.1em;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
}

.status-ready {
    background-color: rgba(59, 130, 246, 0.1);
}

.status-success {
    background-color: rgba(34, 197, 94, 0.1);
}

.status-error {
    background-color: rgba(239, 68, 68, 0.1);
}

.status-playing {
    background-color: rgba(168, 85, 247, 0.1);
}

/* Button disabled state */
.btn-disabled {
    opacity: 0.5;
    cursor: not-allowed;
    pointer-events: none;
}

/* Header styling */
.app-header {
    text-align: center;
    margin-bottom: 20px;
}
"""


# ============================================================
# MOTION ENGINE (Story 2)
# ============================================================

@dataclass
class ExecutionResult:
    """Result of sequence execution."""
    success: bool
    moves_completed: int
    error_message: Optional[str] = None


class MotionEngine:
    """Core motion execution engine - UI-agnostic.
    
    Executes individual moves and full sequences via Reachy SDK.
    Designed to be extensible for future voice/vision inputs.
    """
    
    def __init__(self, robot=None, controller=None):
        """Initialize motion engine with robot connection.
        
        Args:
            robot: ReachyWrapper instance (optional for demo mode)
            controller: SafeMotionController instance (optional)
        """
        self.robot = robot
        self.controller = controller
        self.demo_mode = (robot is None)
        
        # Move registry - maps move IDs to execution functions
        self.MOVE_REGISTRY = {
            "wave": self._move_wave,
            "robot_pose": self._move_robot_pose,
            "spin": self._move_spin,
            "stretch": self._move_stretch,
            "dab": self._move_dab,
            "pause": self._move_pause,
        }
    
    def _move_wave(self):
        """Execute wave gesture."""
        if self.demo_mode:
            print("  [DEMO] 👋 Wave")
            time.sleep(1.0)
        else:
            self.controller.wave_antennas(self.robot, count=2, speed=1.0)
    
    def _move_robot_pose(self):
        """Execute neutral robot pose."""
        if self.demo_mode:
            print("  [DEMO] 🤖 Robot Pose")
            time.sleep(1.0)
        else:
            self.controller.transition_to_pose(
                self.robot, 
                roll=0, pitch=0, yaw=0,
                left_antenna=0, right_antenna=0,
                duration=1.0, 
                degrees=True
            )
    
    def _move_spin(self):
        """Execute spin motion (head rotation sequence)."""
        if self.demo_mode:
            print("  [DEMO] 💃 Spin")
            time.sleep(1.5)
        else:
            # Look left
            self.robot.move_head(yaw=-30, duration=0.5, degrees=True)
            time.sleep(0.5)
            # Look right
            self.robot.move_head(yaw=30, duration=0.5, degrees=True)
            time.sleep(0.5)
            # Center
            self.robot.move_head(yaw=0, duration=0.5, degrees=True)
            time.sleep(0.5)
    
    def _move_stretch(self):
        """Execute stretch motion (pitch + antenna extension)."""
        if self.demo_mode:
            print("  [DEMO] 🙆 Stretch")
            time.sleep(1.5)
        else:
            self.controller.transition_to_pose(
                self.robot,
                pitch=-15,
                left_antenna=0.8,
                right_antenna=-0.8,
                duration=1.5,
                degrees=True
            )
    
    def _move_dab(self):
        """Execute dab motion (roll + pitch + yaw combo)."""
        if self.demo_mode:
            print("  [DEMO] 🕺 Dab")
            time.sleep(1.0)
        else:
            self.controller.transition_to_pose(
                self.robot,
                roll=20, pitch=-10, yaw=15,
                left_antenna=-0.5, right_antenna=0.8,
                duration=0.8,
                degrees=True
            )
    
    def _move_pause(self):
        """Execute pause (no motion, just delay)."""
        if self.demo_mode:
            print("  [DEMO] ⏸ Pause")
        time.sleep(0.5)
    
    def execute_move(self, move_id: str) -> bool:
        """Execute a single move.
        
        Args:
            move_id: Move identifier from MOVE_REGISTRY
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            Exception: Propagates exceptions from move execution for error handling
        """
        if move_id not in self.MOVE_REGISTRY:
            raise ValueError(f"Unknown move: {move_id}")
        
        move_func = self.MOVE_REGISTRY[move_id]
        move_func()
        return True
    
    def get_micro_feedback(self, move_id: str):
        """Provide subtle acknowledgment after move completion.
        
        Args:
            move_id: Move identifier that was just executed
        """
        if self.demo_mode:
            return
        
        try:
            # Subtle head nod as acknowledgment
            self.controller.nod_yes(self.robot, count=1, speed=2.0)
        except Exception as e:
            print(f"[WARN] Micro-feedback failed: {e}")
    
    def execute_sequence(self, sequence: List[str], with_feedback: bool = True) -> ExecutionResult:
        """Execute a full sequence of moves.
        
        Args:
            sequence: List of move IDs to execute in order
            with_feedback: Whether to provide micro-feedback between moves
            
        Returns:
            ExecutionResult with success status and details
        """
        moves_completed = 0
        
        print(f"\n▶️  Executing sequence: {len(sequence)} moves")
        
        try:
            for i, move_id in enumerate(sequence):
                print(f"  [{i+1}/{len(sequence)}] {move_id}")
                
                # Execute move (catching exceptions to provide detailed error messages)
                try:
                    success = self.execute_move(move_id)
                    if not success:
                        return ExecutionResult(
                            success=False,
                            moves_completed=moves_completed,
                            error_message=f"Move '{move_id}' failed"
                        )
                except Exception as move_error:
                    # Capture underlying error details
                    return ExecutionResult(
                        success=False,
                        moves_completed=moves_completed,
                        error_message=str(move_error)
                    )
                
                moves_completed += 1
                
                # Micro-feedback (except after last move)
                if with_feedback and i < len(sequence) - 1 and not self.demo_mode:
                    self.get_micro_feedback(move_id)
                
                # Inter-move delay
                time.sleep(0.5)
            
            print(f"✅ Sequence complete: {moves_completed} moves\n")
            return ExecutionResult(
                success=True,
                moves_completed=moves_completed
            )
            
        except Exception as e:
            error_msg = f"Sequence execution error: {str(e)}"
            print(f"[ERROR] {error_msg}")
            return ExecutionResult(
                success=False,
                moves_completed=moves_completed,
                error_message=error_msg
            )


# ============================================================
# PLACEHOLDER HANDLERS (Story 3-4 - State management)
# ============================================================

def on_move_click(move_name: str):
    """Placeholder handler for move button clicks."""
    print(f"[DEBUG] Move clicked: {move_name}")
    return f"Added {move_name} to sequence (Story 3)"


def on_play_click():
    """Placeholder handler for play button."""
    print("[DEBUG] Play clicked")
    return "Play functionality coming in Story 4"


def on_undo_click():
    """Placeholder handler for undo button."""
    print("[DEBUG] Undo clicked")
    return "Undo functionality coming in Story 3"


def on_clear_click():
    """Placeholder handler for clear button."""
    print("[DEBUG] Clear clicked")
    return "Clear functionality coming in Story 3"


# ============================================================
# GRADIO UI LAYOUT
# ============================================================

def create_app():
    """Create and configure the Gradio application."""
    
    with gr.Blocks(title="🎵 Reachy Remix") as app:
        
        # Header
        gr.Markdown(
            """
            # 🎵 Reachy Remix - Motion Builder
            
            **Build your dance sequence, then watch Reachy perform it!**
            """,
            elem_classes=["app-header"]
        )
        
        with gr.Row():
            # ========================================
            # LEFT COLUMN: Move Palette
            # ========================================
            with gr.Column(scale=1):
                gr.Markdown("## 🎨 Moves")
                gr.Markdown("*Tap to add to your sequence*")
                
                btn_wave = gr.Button(
                    "👋 Wave",
                    elem_classes=["move-button"],
                    variant="secondary"
                )
                
                btn_robot = gr.Button(
                    "🤖 Robot Pose",
                    elem_classes=["move-button"],
                    variant="secondary"
                )
                
                btn_spin = gr.Button(
                    "💃 Spin",
                    elem_classes=["move-button"],
                    variant="secondary"
                )
                
                btn_stretch = gr.Button(
                    "🙆 Stretch",
                    elem_classes=["move-button"],
                    variant="secondary"
                )
                
                btn_dab = gr.Button(
                    "🕺 Dab",
                    elem_classes=["move-button"],
                    variant="secondary"
                )
                
                btn_pause = gr.Button(
                    "⏸ Pause",
                    elem_classes=["move-button"],
                    variant="secondary"
                )
            
            # ========================================
            # CENTER COLUMN: Sequence Display
            # ========================================
            with gr.Column(scale=2):
                gr.Markdown("## 🎬 Your Creation")
                
                sequence_display = gr.Markdown(
                    "Tap moves above to build your dance! 🎵",
                    elem_classes=["sequence-display"]
                )
                
                gr.Markdown("*Your dance sequence will appear here*")
            
            # ========================================
            # RIGHT COLUMN: Controls
            # ========================================
            with gr.Column(scale=1):
                gr.Markdown("## 🎮 Controls")
                
                btn_play = gr.Button(
                    "▶️ Play",
                    elem_classes=["control-button"],
                    variant="primary"
                )
                
                btn_undo = gr.Button(
                    "↩️ Undo",
                    elem_classes=["control-button"]
                )
                
                btn_clear = gr.Button(
                    "🧹 Clear",
                    elem_classes=["control-button"]
                )
        
        # ========================================
        # STATUS BAR (Bottom)
        # ========================================
        status_display = gr.Markdown(
            "Ready! 🎉",
            elem_classes=["status-message", "status-ready"]
        )
        
        # ========================================
        # EVENT HANDLERS (Placeholders for Story 1)
        # ========================================
        
        # Move button clicks
        btn_wave.click(
            fn=lambda: on_move_click("Wave"),
            outputs=[status_display]
        )
        
        btn_robot.click(
            fn=lambda: on_move_click("Robot Pose"),
            outputs=[status_display]
        )
        
        btn_spin.click(
            fn=lambda: on_move_click("Spin"),
            outputs=[status_display]
        )
        
        btn_stretch.click(
            fn=lambda: on_move_click("Stretch"),
            outputs=[status_display]
        )
        
        btn_dab.click(
            fn=lambda: on_move_click("Dab"),
            outputs=[status_display]
        )
        
        btn_pause.click(
            fn=lambda: on_move_click("Pause"),
            outputs=[status_display]
        )
        
        # Control button clicks
        btn_play.click(
            fn=on_play_click,
            outputs=[status_display]
        )
        
        btn_undo.click(
            fn=on_undo_click,
            outputs=[status_display]
        )
        
        btn_clear.click(
            fn=on_clear_click,
            outputs=[status_display]
        )
    
    return app


# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    print("🎵 Reachy Remix - Motion Builder")
    print("=" * 50)
    print("Sprint Status: Story 1 ✅ | Story 2 🚧")
    
    # Initialize robot connection (optional)
    robot = None
    controller = None
    
    if SDK_AVAILABLE:
        print("Reachy SDK available - attempting connection...")
        try:
            # Try to connect to robot (will fail gracefully if not available)
            robot = ReachyWrapper(media_backend="no_media")
            robot.connect()
            robot.wake_up()
            controller = SafeMotionController()
            print("✅ Robot connected!")
        except Exception as e:
            print(f"⚠️  Robot not available: {e}")
            print("Running in DEMO mode")
            robot = None
            controller = None
    else:
        print("Running in DEMO mode (SDK not installed)")
    
    # Initialize motion engine
    global motion_engine
    motion_engine = MotionEngine(robot=robot, controller=controller)
    
    print("=" * 50)
    print("Story 2: Motion Engine active")
    print("  - 6 moves mapped to Reachy SDK")
    print("  - Demo mode: works without robot")
    print("  - Test: Run sequence manually")
    print("=" * 50)
    
    # Optional: Test sequence execution
    if motion_engine.demo_mode:
        print("\n🧪 Demo Test: Executing sample sequence...")
        test_sequence = ["wave", "spin", "dab"]
        result = motion_engine.execute_sequence(test_sequence, with_feedback=False)
        print(f"Test result: {'✅ Success' if result.success else '❌ Failed'}")
        print()
    
    app = create_app()
    
    # Apply theme after creation (Gradio 6.0 pattern)
    app.theme = theme
    
    # Launch Gradio app
    app.launch(
        server_name="0.0.0.0",  # Accessible on network
        server_port=7860,
        share=False,  # Local only for security
        inbrowser=True,  # Auto-open browser
        show_error=True,
    )
