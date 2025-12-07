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
# THEME & STYLING - TTKBootstrap Inspired
# ============================================================

# TTKBootstrap-inspired theme definitions
TTKBOOTSTRAP_THEMES = {
    "cosmo": {
        "name": "Cosmo",
        "type": "light",
        "primary": "#2780E3",
        "secondary": "#373A3C",
        "success": "#3FB618",
        "info": "#9954BB",
        "warning": "#FF7518",
        "danger": "#FF0039",
        "bg": "#FFFFFF",
        "fg": "#373A3C",
    },
    "flatly": {
        "name": "Flatly",
        "type": "light",
        "primary": "#2C3E50",
        "secondary": "#95A5A6",
        "success": "#18BC9C",
        "info": "#3498DB",
        "warning": "#F39C12",
        "danger": "#E74C3C",
        "bg": "#FFFFFF",
        "fg": "#2C3E50",
    },
    "minty": {
        "name": "Minty",
        "type": "light",
        "primary": "#78C2AD",
        "secondary": "#F3969A",
        "success": "#56CC9D",
        "info": "#6CC3D5",
        "warning": "#FFCE67",
        "danger": "#FF7851",
        "bg": "#FFFFFF",
        "fg": "#5A5A5A",
    },
    "pulse": {
        "name": "Pulse",
        "type": "light",
        "primary": "#593196",
        "secondary": "#A991D4",
        "success": "#13B955",
        "info": "#009CDC",
        "warning": "#EBA31D",
        "danger": "#FC3939",
        "bg": "#FFFFFF",
        "fg": "#444444",
    },
    "solar": {
        "name": "Solar",
        "type": "dark",
        "primary": "#B58900",
        "secondary": "#2AA198",
        "success": "#859900",
        "info": "#268BD2",
        "warning": "#CB4B16",
        "danger": "#DC322F",
        "bg": "#002B36",
        "fg": "#839496",
    },
    "darkly": {
        "name": "Darkly",
        "type": "dark",
        "primary": "#375A7F",
        "secondary": "#444444",
        "success": "#00BC8C",
        "info": "#3498DB",
        "warning": "#F39C12",
        "danger": "#E74C3C",
        "bg": "#222222",
        "fg": "#AAAAAA",
    },
    "cyborg": {
        "name": "Cyborg",
        "type": "dark",
        "primary": "#2A9FD6",
        "secondary": "#555555",
        "success": "#77B300",
        "info": "#9933CC",
        "warning": "#FF8800",
        "danger": "#CC0000",
        "bg": "#060606",
        "fg": "#ADAFAE",
    },
    "superhero": {
        "name": "Superhero",
        "type": "dark",
        "primary": "#DF691A",
        "secondary": "#5BC0DE",
        "success": "#5CB85C",
        "info": "#5BC0DE",
        "warning": "#F0AD4E",
        "danger": "#D9534F",
        "bg": "#2B3E50",
        "fg": "#EBEBEB",
    },
    "vapor": {
        "name": "Vapor",
        "type": "dark",
        "primary": "#EA00D9",
        "secondary": "#0ABDC6",
        "success": "#711C91",
        "info": "#0ABDC6",
        "warning": "#EA00D9",
        "danger": "#F50057",
        "bg": "#1A1A2E",
        "fg": "#E5E5E5",
    }
}

# Current active theme (default to minty)
current_theme_name = "minty"

def create_theme(theme_name="minty"):
    """Create a Gradio theme based on TTKBootstrap themes."""
    theme_config = TTKBOOTSTRAP_THEMES.get(theme_name, TTKBOOTSTRAP_THEMES["minty"])
    
    # Base theme selection
    if theme_config["type"] == "dark":
        base_theme = gr.themes.Soft(
            primary_hue=gr.themes.colors.slate,
            secondary_hue=gr.themes.colors.slate,
            neutral_hue=gr.themes.colors.slate,
            font=gr.themes.GoogleFont("Fredoka One"),
            radius_size=gr.themes.sizes.radius_lg,
        )
    else:
        base_theme = gr.themes.Soft(
            primary_hue=gr.themes.colors.slate,
            secondary_hue=gr.themes.colors.orange,
            neutral_hue=gr.themes.colors.slate,
            font=gr.themes.GoogleFont("Fredoka One"),
            radius_size=gr.themes.sizes.radius_lg,
        )
    
    # Apply theme colors
    theme = base_theme.set(
        body_background_fill=theme_config["bg"],
        block_background_fill=theme_config["bg"] if theme_config["type"] == "dark" else "#FFFFFF",
        block_border_width="3px",
        block_border_color=theme_config["secondary"],
        block_shadow=f"4px 4px 0px {theme_config['secondary']}",
        button_primary_background_fill=theme_config["primary"],
        button_primary_background_fill_hover=theme_config["info"],
        button_primary_border_color=theme_config["secondary"],
        button_primary_text_color="#FFFFFF" if theme_config["type"] == "dark" else theme_config["fg"],
        button_secondary_background_fill=theme_config["warning"],
        button_secondary_border_color=theme_config["secondary"],
        button_secondary_text_color=theme_config["fg"],
    )
    
    return theme

# Initialize default theme
theme = create_theme(current_theme_name)

def get_custom_css(theme_name="minty"):
    """Generate custom CSS based on selected theme - Compact TTKBootstrap style."""
    theme_config = TTKBOOTSTRAP_THEMES.get(theme_name, TTKBOOTSTRAP_THEMES["minty"])
    is_dark = theme_config["type"] == "dark"
    
    # Card background for dark themes
    card_bg = f"rgba(255, 255, 255, 0.05)" if is_dark else "#FFFFFF"
    text_color = theme_config["fg"]
    bg_secondary = f"{theme_config['bg']}ee" if is_dark else "#f8f9fa"
    
    return f"""
@import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Noto+Color+Emoji&display=swap');

/* TTKBootstrap Compact Design with Emoji Support */
* {{
    font-family: 'Segoe UI', 'Noto Color Emoji', -apple-system, BlinkMacSystemFont, sans-serif !important;
}}

.gradio-container {{
    background: 
        radial-gradient(circle at 20% 50%, {theme_config["primary"]}15 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, {theme_config["info"]}15 0%, transparent 50%),
        radial-gradient(circle at 40% 20%, {theme_config["success"]}10 0%, transparent 50%),
        linear-gradient(135deg, {theme_config["bg"]} 0%, {theme_config["secondary"]}15 100%) !important;
    color: {text_color} !important;
    padding: 0 !important;
    min-height: 100vh !important;
    position: relative !important;
}}

.gradio-container::before {{
    content: '' !important;
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 100% !important;
    background: 
        repeating-linear-gradient(
            45deg,
            transparent,
            transparent 60px,
            {theme_config["primary"]}05 60px,
            {theme_config["primary"]}05 61px
        ) !important;
    pointer-events: none !important;
    z-index: 0 !important;
}}

.gradio-container > * {{
    position: relative !important;
    z-index: 1 !important;
}}

/* Compact Header */
.compact-header {{
    background: linear-gradient(90deg, {theme_config["primary"]} 0%, {theme_config["info"]} 100%) !important;
    padding: 10px 20px !important;
    border-bottom: 3px solid {theme_config["success"]} !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15) !important;
}}

.compact-header h2 {{
    margin: 0 !important;
    font-size: 1.3em !important;
    font-weight: 700 !important;
    color: white !important;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.2) !important;
}}

/* Compact Container */
.compact-container {{
    max-width: 1200px !important;
    margin: 0 auto !important;
    padding: 20px !important;
    background: {card_bg}dd !important;
    backdrop-filter: blur(10px) !important;
    border-radius: 15px !important;
    margin-top: 15px !important;
    margin-bottom: 15px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1) !important;
    border: 1px solid {theme_config["primary"]}30 !important;
}}

/* Sequence Display - Compact */
#sequence-card {{
    background: linear-gradient(135deg, {card_bg} 0%, {theme_config["primary"]}10 100%) !important;
    border: 2px solid {theme_config["primary"]}80 !important;
    border-radius: 10px !important;
    padding: 20px !important;
    margin: 15px 0 !important;
    min-height: 100px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
}}

/* Move Buttons - Compact with clear emojis */
button {{
    font-family: 'Segoe UI', 'Noto Color Emoji', sans-serif !important;
}}

.move-btn {{
    background: linear-gradient(135deg, {theme_config["primary"]} 0%, {theme_config["info"]} 100%) !important;
    border: 2px solid {theme_config["primary"]}cc !important;
    border-radius: 8px !important;
    padding: 12px 20px !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: white !important;
    transition: all 0.2s ease !important;
    min-height: 50px !important;
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15) !important;
}}

.move-btn:hover {{
    background: linear-gradient(135deg, {theme_config["info"]} 0%, {theme_config["success"]} 100%) !important;
    border-color: {theme_config["success"]} !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2) !important;
}}

.move-btn:active {{
    transform: translateY(0) !important;
}}

/* Control Buttons - Bootstrap size */
.btn-success {{
    background: linear-gradient(135deg, {theme_config["success"]} 0%, {theme_config["info"]} 100%) !important;
    border: 2px solid {theme_config["success"]} !important;
    color: white !important;
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15) !important;
    transition: all 0.2s ease !important;
}}

.btn-success:hover {{
    background: linear-gradient(135deg, {theme_config["info"]} 0%, {theme_config["success"]} 100%) !important;
    border-color: {theme_config["info"]} !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2) !important;
}}

.btn-warning {{
    background: linear-gradient(135deg, {theme_config["warning"]} 0%, {theme_config["primary"]} 100%) !important;
    border: 2px solid {theme_config["warning"]} !important;
    color: white !important;
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15) !important;
    transition: all 0.2s ease !important;
}}

.btn-warning:hover {{
    background: linear-gradient(135deg, {theme_config["primary"]} 0%, {theme_config["warning"]} 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2) !important;
}}

.btn-danger {{
    background: linear-gradient(135deg, {theme_config["danger"]} 0%, {theme_config["secondary"]} 100%) !important;
    border: 2px solid {theme_config["danger"]} !important;
    color: white !important;
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15) !important;
    transition: all 0.2s ease !important;
}}

.btn-danger:hover {{
    background: linear-gradient(135deg, {theme_config["secondary"]} 0%, {theme_config["danger"]} 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2) !important;
}}

/* Status Alert - Bootstrap compact */
.alert {{
    padding: 10px 15px !important;
    margin: 10px 0 !important;
    border-radius: 4px !important;
    border-left: 3px solid !important;
    font-size: 0.95rem !important;
}}

.alert-success {{
    background: {theme_config["success"]}20 !important;
    border-left-color: {theme_config["success"]} !important;
    color: {text_color} !important;
}}

.alert-info {{
    background: {theme_config["info"]}20 !important;
    border-left-color: {theme_config["info"]} !important;
    color: {text_color} !important;
}}

.alert-warning {{
    background: {theme_config["warning"]}20 !important;
    border-left-color: {theme_config["warning"]} !important;
    color: {text_color} !important;
}}

.alert-danger {{
    background: {theme_config["danger"]}20 !important;
    border-left-color: {theme_config["danger"]} !important;
    color: {text_color} !important;
}}

/* Grid Layout - Compact */
.btn-grid {{
    display: grid !important;
    grid-template-columns: repeat(3, 1fr) !important;
    gap: 10px !important;
    margin: 15px 0 !important;
}}

.control-grid {{
    display: grid !important;
    grid-template-columns: 1fr 2fr 1fr !important;
    gap: 10px !important;
    margin: 15px 0 !important;
}}

/* Section titles */
.section-title {{
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    color: {text_color} !important;
    margin: 20px 0 10px 0 !important;
    padding-left: 10px !important;
    border-left: 3px solid {theme_config["primary"]} !important;
}}

/* Force emoji rendering */
button, div, span, p, h1, h2, h3 {{
    font-family: 'Segoe UI', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji', sans-serif !important;
    text-rendering: optimizeLegibility !important;
    -webkit-font-smoothing: antialiased !important;
}}

/* Ensure button text shows emojis */
button span {{
    font-size: 1.1em !important;
    line-height: 1.5 !important;
}}

/* Emoji size in buttons */
.move-btn span, .btn-success span, .btn-warning span, .btn-danger span {{
    display: inline-block !important;
    vertical-align: middle !important;
}}

/* Gradio overrides for compact layout */
.gradio-container .main {{
    padding: 0 !important;
}}

.gradio-container .contain {{
    max-width: 100% !important;
}}

/* Override Gradio's button text truncation */
.gradio-container button {{
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
}}
"""

# Initialize default CSS
custom_css = get_custom_css(current_theme_name)



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
            "nod_yes": self._move_nod_yes,
            "shake_no": self._move_shake_no,
            "wave": self._move_wave,
            "happy": self._move_happy,
            "excited": self._move_excited,
            "look_around": self._move_look_around,
        }
    
    def _move_nod_yes(self):
        """Execute nod yes gesture."""
        if self.demo_mode:
            print("  [DEMO] 👍 Nod Yes")
            time.sleep(1.5)
        else:
            self.controller.nod_yes(self.robot, count=2, speed=1.5)
    
    def _move_shake_no(self):
        """Execute shake no gesture."""
        if self.demo_mode:
            print("  [DEMO] 👎 Shake No")
            time.sleep(1.5)
        else:
            self.controller.shake_no(self.robot, count=2, speed=1.5)
    
    def _move_wave(self):
        """Execute wave antennas gesture."""
        if self.demo_mode:
            print("  [DEMO] 👋 Wave")
            time.sleep(2.0)
        else:
            self.controller.wave_antennas(self.robot, count=2, synchronized=True)
    
    def _move_happy(self):
        """Execute happy expression."""
        if self.demo_mode:
            print("  [DEMO] 😊 Happy")
            time.sleep(1.5)
        else:
            self.controller.express_happy(self.robot)
    
    def _move_excited(self):
        """Execute excited expression."""
        if self.demo_mode:
            print("  [DEMO] 🎉 Excited")
            time.sleep(1.5)
        else:
            self.controller.express_excited(self.robot)
    
    def _move_look_around(self):
        """Execute look around gesture."""
        if self.demo_mode:
            print("  [DEMO] 👀 Look Around")
            time.sleep(2.0)
        else:
            self.controller.look_around(self.robot, speed=1.0)
    
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
        # Delegate to generator but consume all
        result = None
        for _, res in self.execute_sequence_generator(sequence, with_feedback):
            result = res
        return result

    def execute_sequence_generator(self, sequence: List[str], with_feedback: bool = True):
        """Execute a full sequence of moves, yielding progress.
        
        Args:
            sequence: List of move IDs to execute in order
            with_feedback: Whether to provide micro-feedback between moves
            
        Yields:
            Tuple[int, ExecutionResult]: (current_index, result_so_far)
        """
        moves_completed = 0
        print(f"\n▶️  Executing sequence: {len(sequence)} moves")
        
        try:
            for i, move_id in enumerate(sequence):
                print(f"  [{i+1}/{len(sequence)}] {move_id}")
                
                # Yield BEFORE execution (index i)
                yield i, ExecutionResult(success=True, moves_completed=moves_completed)
                
                # Execute move (catching exceptions to provide detailed error messages)
                try:
                    success = self.execute_move(move_id)
                    if not success:
                        yield i, ExecutionResult(
                            success=False,
                            moves_completed=moves_completed,
                            error_message=f"Move '{move_id}' failed"
                        )
                        return
                except Exception as move_error:
                    # Capture underlying error details
                    yield i, ExecutionResult(
                        success=False,
                        moves_completed=moves_completed,
                        error_message=str(move_error)
                    )
                    return
                
                moves_completed += 1
                
                # Micro-feedback (except after last move)
                if with_feedback and i < len(sequence) - 1 and not self.demo_mode:
                    self.get_micro_feedback(move_id)
                
                # Inter-move delay
                time.sleep(0.5)
            
            print(f"✅ Sequence complete: {moves_completed} moves\n")
            # Yield completion (index -1 or len)
            yield -1, ExecutionResult(
                success=True,
                moves_completed=moves_completed
            )
            
        except Exception as e:
            error_msg = f"Sequence execution error: {str(e)}"
            print(f"[ERROR] {error_msg}")
            yield moves_completed, ExecutionResult(
                success=False,
                moves_completed=moves_completed,
                error_message=error_msg
            )


# ============================================================
# STATE MANAGEMENT (Story 3)
# ============================================================

class PlayState(Enum):
    """Playback state machine states."""
    IDLE = "idle"
    PLAYING = "playing"
    ERROR = "error"


class AppState:
    """Application state manager.
    
    Manages playback state and enforces state machine transitions.
    """
    
    def __init__(self):
        """Initialize app state."""
        self.current_state = PlayState.IDLE
        self.sequence: List[str] = []
        self.error_message: Optional[str] = None
    
    def can_play(self) -> bool:
        """Check if sequence can be played.
        
        Returns:
            True if in IDLE state and sequence is not empty
        """
        return self.current_state == PlayState.IDLE and len(self.sequence) > 0
    
    def start_playing(self) -> None:
        """Transition from IDLE to PLAYING state."""
        if self.current_state == PlayState.IDLE:
            self.current_state = PlayState.PLAYING
            self.error_message = None
        else:
            raise ValueError(f"Cannot start playing from {self.current_state}")
    
    def finish_playing(self) -> None:
        """Transition from PLAYING to IDLE state."""
        if self.current_state == PlayState.PLAYING:
            self.current_state = PlayState.IDLE
        else:
            raise ValueError(f"Cannot finish playing from {self.current_state}")
    
    def set_error(self, message: str) -> None:
        """Transition to ERROR state with message.
        
        Args:
            message: Error message to store
        """
        self.current_state = PlayState.ERROR
        self.error_message = message
    
    def reset(self) -> None:
        """Reset to IDLE state (for error recovery)."""
        self.current_state = PlayState.IDLE
        self.error_message = None


class SequenceBuilder:
    """Sequence building and display formatting.
    
    Manages the move sequence and converts to emoji display format.
    """
    
    # Emoji mapping for moves
    EMOJI_MAP = {
        "nod_yes": "👍",
        "shake_no": "👎",
        "wave": "👋",
        "happy": "😊",
        "excited": "🎉",
        "look_around": "👀",
    }
    
    # Empty state message
    EMPTY_MESSAGE = "Tap moves above to build your dance! 🎵"
    
    def __init__(self):
        """Initialize sequence builder."""
        self.moves: List[str] = []
        self._version = 0  # Version counter to force Gradio updates
    
    def add_move(self, move_id: str) -> str:
        """Add a move to the sequence.
        
        Args:
            move_id: Move identifier to add
            
        Returns:
            Formatted sequence display string
        """
        self.moves.append(move_id)
        self._version += 1  # Increment to force Gradio refresh
        return self.format_sequence()
    
    def undo_last(self) -> str:
        """Remove the last move from sequence.
        
        Returns:
            Updated sequence display string
        """
        if self.moves:
            self.moves.pop()
        self._version += 1  # Increment to force Gradio refresh
        return self.format_sequence()
    
    def clear_all(self) -> str:
        """Clear entire sequence.
        
        Returns:
            Empty state message
        """
        self.moves.clear()
        self._version += 1  # Increment to force Gradio refresh
        return self.format_sequence()
    
    def format_sequence(self, current_index: int = -1) -> str:
        """Format sequence with compact, attractive display.
        
        Args:
            current_index: Index of currently playing move (-1 for none)
        
        Returns:
            Formatted HTML with smart highlighting
        """
        if not self.moves:
            return f'''
            <div style="text-align: center; padding: 40px; font-size: 1.3em; color: #888; 
                        background: #FFFFFF;
                        border-radius: 20px; border: 3px dashed #000000;">
                🎶 {self.EMPTY_MESSAGE}
            </div>
            '''
        
        # Map for display names
        move_names = {
            "nod_yes": "Nod Yes",
            "shake_no": "Shake No",
            "wave": "Wave",
            "look_around": "Look Around",
            "happy": "Happy",
            "excited": "Excited"
        }
        
        # Create compact emoji row with smart sizing
        emojis = [self.EMOJI_MAP.get(move, "❓") for move in self.moves]
        emoji_parts = []
        
        for i, emoji in enumerate(emojis):
            is_current = (i == current_index)
            is_past = (current_index >= 0 and i < current_index)
            
            # Size and style based on state
            if is_current:
                # Currently playing - BIG and glowing
                style = '''font-size: 3.5em; margin: 0 8px; display: inline-block;
                          animation: bounce-glow 0.6s ease-in-out infinite;
                          filter: drop-shadow(0 0 5px #32CD32);
                          transform: translateY(-5px);'''
            elif is_past:
                # Already played - small and faded
                style = 'font-size: 2em; margin: 0 6px; display: inline-block; opacity: 0.3;'
            else:
                # Waiting or idle - normal size
                style = f'font-size: 2.5em; margin: 0 8px; display: inline-block; opacity: {0.5 if current_index >= 0 else 1.0};'
            
            emoji_parts.append(f'<span style="{style}">{emoji}</span>')
        
        emoji_html = ''.join(emoji_parts)
        
        # Progress bar (visual indicator)
        progress_bar = ""
        if current_index >= 0:
            progress_pct = ((current_index + 1) / len(self.moves)) * 100
            current_move_name = move_names.get(self.moves[current_index], self.moves[current_index])
            progress_bar = f'''
            <div style="margin: 15px 0;">
                <div style="background: #EEE; border-radius: 10px; height: 12px; overflow: hidden; border: 2px solid #000;">
                    <div style="background: #32CD32; 
                                height: 100%; width: {progress_pct}%; 
                                transition: width 0.3s ease;"></div>
                </div>
                <p style="font-size: 1.1em; font-weight: bold; color: #000; margin-top: 8px;">
                    ▶️ Now Playing: {current_move_name} ({current_index + 1}/{len(self.moves)})
                </p>
            </div>
            '''
        
        # Compact header
        header = f'''
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <span style="font-size: 1.2em; font-weight: bold; color: #000;">🎵 Your Dance</span>
            <span style="background: #FFD700; padding: 6px 12px; border-radius: 20px; border: 2px solid #000;
                         font-size: 0.9em; font-weight: bold; color: #000;">{len(self.moves)} moves</span>
        </div>
        '''
        
        # Return compact, beautiful design
        return f'''
        <div style="padding: 25px; 
                    background: #FFFFFF; 
                    border-radius: 18px; 
                    border: 3px solid #000000;
                    box-shadow: 6px 6px 0px #000000;">
            {header}
            {progress_bar}
            <div style="overflow-x: auto; white-space: nowrap; padding: 15px 5px; 
                        background: #F0F8FF; border-radius: 12px; border: 2px solid #000;
                        scrollbar-width: thin; scrollbar-color: #000 transparent;">
                {emoji_html}
            </div>
        </div>
        <style>
        @keyframes bounce-glow {{
            0%, 100% {{ transform: translateY(-5px); filter: drop-shadow(0 0 5px #32CD32); }}
            50% {{ transform: translateY(-10px); filter: drop-shadow(0 0 10px #32CD32); }}
        }}
        </style>
        <!-- v{self._version} -->
        '''
    
    def get_sequence(self) -> List[str]:
        """Get current move sequence.
        
        Returns:
            List of move IDs
        """
        return self.moves.copy()


# ============================================================
# GRADIO UI LAYOUT
# ============================================================

def create_app():
    """Create and configure the Gradio application."""
    
    # Initialize state (Story 3)
    app_state = AppState()
    sequence_builder = SequenceBuilder()
    
    # Handler functions with state management
    def on_move_click(move_id: str):
        """Handle move button click - adds move to sequence."""
        display = sequence_builder.add_move(move_id)
        app_state.sequence = sequence_builder.get_sequence()
        move_names = {"nod_yes": "Nod Yes", "shake_no": "Shake No", "wave": "Wave", "look_around": "Look Around", "happy": "Happy", "excited": "Excited"}
        move_name = move_names.get(move_id, move_id)
        print(f"[DEBUG] Added move: {move_id}")
        print(f"[DEBUG] Total moves: {len(sequence_builder.moves)}")
        # AC5.3: Enable undo button when moves exist
        status_html = f'<div class="alert alert-success">✅ <strong>{move_name}</strong> added! ({len(sequence_builder.moves)} moves)</div>'
        return (
            gr.update(value=display),
            gr.update(value=status_html),
            gr.update(interactive=True)  # Undo button enabled
        )
    
    def on_undo_click():
        """Handle undo button click - removes last move."""
        display = sequence_builder.undo_last()
        app_state.sequence = sequence_builder.get_sequence()
        if sequence_builder.moves:
            status_html = f'<div class="alert alert-info">↩️ Undone! ({len(sequence_builder.moves)} moves left)</div>'
        else:
            status_html = '<div class="alert alert-warning">ℹ️ Sequence empty - add moves! 🎵</div>'
        print(f"[DEBUG] Undo clicked, remaining moves: {len(sequence_builder.moves)}")
        # AC5.3: Return button states (undo disabled when empty)
        return (
            gr.update(value=display),
            gr.update(value=status_html),
            gr.update(interactive=len(sequence_builder.moves) > 0)  # Undo button state
        )
    
    def on_clear_click():
        """Handle clear button click - clears all moves."""
        display = sequence_builder.clear_all()
        app_state.sequence = sequence_builder.get_sequence()
        app_state.reset()  # Reset any error state
        print(f"[DEBUG] Clear clicked")
        status_html = '<div class="alert alert-warning">🗑️ <strong>Cleared!</strong> Ready for new sequence.</div>'
        # AC5.3: Disable undo button after clear
        return (
            gr.update(value=display),
            gr.update(value=status_html),
            gr.update(interactive=False)  # Undo button disabled
        )
    
    def on_play_click():
        """Handle play button click - executes sequence."""
        # AC4.1: Check if can play
        if not app_state.can_play():
            status_html = '<div class="alert alert-warning">⚠️ Add at least one move first!</div>'
            yield (
                sequence_builder.format_sequence(),
                status_html,
                gr.update(value="▶️ Play Sequence", interactive=True),
                gr.update(interactive=False), # undo
                gr.update(interactive=True)   # clear
            )
            return
        
        status = "Ready! 🎉"
        try:
            # AC4.2: Start playing
            app_state.start_playing()
            print(f"[PLAYBACK] Starting sequence of {len(app_state.sequence)} moves")
            
            # Disable play button during playback
            status_html = '<div class="alert alert-info">🎵 <strong>Starting...</strong> Get ready! 🕺</div>'
            yield (
                sequence_builder.format_sequence(-1),
                status_html,
                gr.update(value="🎬 Playing...", interactive=False),
                gr.update(interactive=False), # undo disabled
                gr.update(interactive=False)  # clear disabled
            )
            
            # Execute full sequence with generator
            result = None
            for current_index, partial_result in motion_engine.execute_sequence_generator(app_state.sequence, with_feedback=True):
                result = partial_result
                
                if not result.success:
                    break
                
                # Update UI for current move
                if current_index >= 0 and current_index < len(app_state.sequence):
                    progress_pct = int(((current_index + 1) / len(app_state.sequence)) * 100)
                    status_html = f'<div class="alert alert-info">💃 <strong>Move {current_index + 1}/{len(app_state.sequence)}</strong> ({progress_pct}%)</div>'
                    yield (
                        sequence_builder.format_sequence(current_index),
                        status_html,
                        gr.update(value="🎬 Playing...", interactive=False),
                        gr.update(interactive=False),
                        gr.update(interactive=False)
                    )
            
            # AC4.3: Status messages based on result
            if result and result.success:
                status = '<div class="alert alert-success">🎉 <strong>Success!</strong> Awesome dance!</div>'
            else:
                error_msg = result.error_message if result else "Unknown error"
                status = f'<div class="alert alert-danger">⚠️ <strong>Error:</strong> {error_msg}</div>'
                app_state.set_error(error_msg)
            
        except Exception as e:
            # AC4.5: Error recovery
            status = f'<div class="alert alert-danger">❌ <strong>Error:</strong> {str(e)}</div>'
            app_state.set_error(str(e))
        
        finally:
            # AC4.2: Finish playing and return to IDLE
            if app_state.current_state == PlayState.PLAYING:
                app_state.finish_playing()
            elif app_state.current_state == PlayState.ERROR:
                # Reset from error to allow retry
                app_state.reset()
        
        # AC5.3: Return play button to normal state
        yield (
            sequence_builder.format_sequence(-1),
            status,
            gr.update(value="▶️ Play Sequence", interactive=True),
            gr.update(interactive=True), # undo enabled
            gr.update(interactive=True)  # clear enabled
        )
    
    def on_theme_change(theme_name):
        """Handle theme change - note: requires page refresh for full effect."""
        global current_theme_name, theme, custom_css
        current_theme_name = theme_name
        theme = create_theme(theme_name)
        custom_css = get_custom_css(theme_name)
        
        theme_display = TTKBOOTSTRAP_THEMES[theme_name]["name"]
        
        # Return updated CSS style tag and confirmation message
        return (
            gr.update(value=f"<style id='custom-theme-style'>{custom_css}</style>"),
            gr.update(value=f"""
            <div style="padding: 10px 15px; background: linear-gradient(90deg, {TTKBOOTSTRAP_THEMES[theme_name]['primary']} 0%, {TTKBOOTSTRAP_THEMES[theme_name]['info']} 100%); 
                        border-radius: 6px; color: white; text-align: center; box-shadow: 0 2px 6px rgba(0,0,0,0.2);">
                <strong>✨ Theme: {theme_display}</strong> - Refresh page to apply fully
            </div>
            """)
        )
    
    with gr.Blocks(title="🎵 Reachy Remix") as app:
        
        # Inject custom CSS
        css_element = gr.HTML(f"<style id='custom-theme-style'>{custom_css}</style>")
        
        # Compact Header
        with gr.Row(elem_classes=["compact-header"]):
            with gr.Column(scale=3):
                gr.HTML('<h2>🎵 Reachy Remix - Dance Builder</h2>')
            with gr.Column(scale=1):
                theme_selector = gr.Dropdown(
                    choices=list(TTKBOOTSTRAP_THEMES.keys()),
                    value=current_theme_name,
                    label="🎨 Theme",
                    interactive=True,
                    container=False
                )
                theme_info = gr.HTML(
                    f'<div style="font-size: 0.75em; opacity: 0.9; padding: 3px; color: white;">Current: <strong>{TTKBOOTSTRAP_THEMES[current_theme_name]["name"]}</strong></div>'
                )
        
        # Main container
        with gr.Column(elem_classes=["compact-container"]):
            
            # Sequence Display
            gr.HTML('<div class="section-title">📋 Your Sequence</div>')
            sequence_display = gr.HTML(
                '<div id="sequence-card" style="text-align: center; padding: 25px; font-size: 1.2em;">Tap moves below to build your dance! 🎵</div>'
            )
            
            # Move Buttons
            gr.HTML('<div class="section-title">🎨 Moves</div>')
            with gr.Row(elem_classes=["btn-grid"]):
                btn_nod = gr.Button(value="👍 Nod Yes", elem_classes=["move-btn"])
                btn_shake = gr.Button(value="👎 Shake No", elem_classes=["move-btn"])
                btn_wave = gr.Button(value="👋 Wave", elem_classes=["move-btn"])
            with gr.Row(elem_classes=["btn-grid"]):
                btn_look = gr.Button(value="👀 Look", elem_classes=["move-btn"])
                btn_happy = gr.Button(value="😊 Happy", elem_classes=["move-btn"])
                btn_excited = gr.Button(value="🎉 Excited", elem_classes=["move-btn"])
            
            # Controls
            gr.HTML('<div class="section-title">🎮 Controls</div>')
            with gr.Row(elem_classes=["control-grid"]):
                btn_undo = gr.Button(value="↩️ Undo", elem_classes=["btn-warning"], interactive=False)
                btn_play = gr.Button(value="▶️ Play Sequence", elem_classes=["btn-success"], variant="primary")
                btn_clear = gr.Button(value="🗑️ Clear", elem_classes=["btn-danger"])
            
            # Status
            status_display = gr.HTML(
                '<div class="alert alert-success">✅ <strong>Ready!</strong> Select moves to start.</div>'
            )
        
        # ========================================
        # EVENT HANDLERS
        # ========================================
        
        # Theme selector - updates CSS instantly
        theme_selector.change(fn=on_theme_change, inputs=[theme_selector], outputs=[css_element, theme_info])
        
        # Move button clicks
        btn_nod.click(fn=lambda: on_move_click("nod_yes"), outputs=[sequence_display, status_display, btn_undo])
        btn_shake.click(fn=lambda: on_move_click("shake_no"), outputs=[sequence_display, status_display, btn_undo])
        btn_wave.click(fn=lambda: on_move_click("wave"), outputs=[sequence_display, status_display, btn_undo])
        btn_look.click(fn=lambda: on_move_click("look_around"), outputs=[sequence_display, status_display, btn_undo])
        btn_happy.click(fn=lambda: on_move_click("happy"), outputs=[sequence_display, status_display, btn_undo])
        btn_excited.click(fn=lambda: on_move_click("excited"), outputs=[sequence_display, status_display, btn_undo])
        
        # Control button clicks
        btn_play.click(fn=on_play_click, outputs=[sequence_display, status_display, btn_play, btn_undo, btn_clear])
        btn_undo.click(fn=on_undo_click, outputs=[sequence_display, status_display, btn_undo])
        btn_clear.click(fn=on_clear_click, outputs=[sequence_display, status_display, btn_undo])
    
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
    
    # Optional: Test sequence execution (disabled for quick startup)
    # if motion_engine.demo_mode:
    #     print("\n🧪 Demo Test: Executing sample sequence...")
    #     test_sequence = ["nod_yes", "wave", "happy"]
    #     result = motion_engine.execute_sequence(test_sequence, with_feedback=False)
    #     print(f"Test result: {'✅ Success' if result.success else '❌ Failed'}")
    #     print()
    
    app = create_app()
    
    # Launch Gradio app
    app.launch(
        server_name="0.0.0.0",  # Accessible on network
        server_port=7860,
        share=False,  # Local only for security
        inbrowser=True,  # Auto-open browser
        show_error=True,
    )
