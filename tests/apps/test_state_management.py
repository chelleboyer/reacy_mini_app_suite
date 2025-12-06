"""
Unit tests for Reachy Remix State Management

Story 3 - AC3.9: Unit test coverage for state management and sequence building
"""

import pytest
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "apps" / "reachy-remix"))

from reachy_remix import PlayState, AppState, SequenceBuilder


class TestPlayState:
    """Test PlayState enum."""
    
    def test_play_state_values(self):
        """Test PlayState has correct values."""
        assert PlayState.IDLE.value == "idle"
        assert PlayState.PLAYING.value == "playing"
        assert PlayState.ERROR.value == "error"


class TestAppState:
    """Test suite for AppState class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.state = AppState()
    
    def test_initial_state(self):
        """Test initial state is IDLE with empty sequence."""
        assert self.state.current_state == PlayState.IDLE
        assert self.state.sequence == []
        assert self.state.error_message is None
    
    def test_can_play_validation_empty_sequence(self):
        """AC3.9: Play blocked when sequence empty."""
        assert self.state.can_play() == False
    
    def test_can_play_validation_with_moves(self):
        """AC3.9: Play allowed when IDLE with moves."""
        self.state.sequence = ["wave", "spin"]
        assert self.state.can_play() == True
    
    def test_can_play_blocked_when_playing(self):
        """Test can_play returns False when already PLAYING."""
        self.state.sequence = ["wave"]
        self.state.current_state = PlayState.PLAYING
        assert self.state.can_play() == False
    
    def test_state_transitions_idle_to_playing(self):
        """AC3.9: Valid state machine flow - IDLE to PLAYING."""
        assert self.state.current_state == PlayState.IDLE
        
        self.state.start_playing()
        assert self.state.current_state == PlayState.PLAYING
        assert self.state.error_message is None
    
    def test_state_transitions_playing_to_idle(self):
        """AC3.9: Valid state machine flow - PLAYING to IDLE."""
        self.state.current_state = PlayState.PLAYING
        
        self.state.finish_playing()
        assert self.state.current_state == PlayState.IDLE
    
    def test_invalid_transition_raises_error(self):
        """Test invalid state transitions raise ValueError."""
        # Can't start playing when already playing
        self.state.current_state = PlayState.PLAYING
        with pytest.raises(ValueError):
            self.state.start_playing()
        
        # Can't finish playing when not playing
        self.state.current_state = PlayState.IDLE
        with pytest.raises(ValueError):
            self.state.finish_playing()
    
    def test_set_error_state(self):
        """Test transitioning to ERROR state."""
        self.state.set_error("Robot disconnected")
        
        assert self.state.current_state == PlayState.ERROR
        assert self.state.error_message == "Robot disconnected"
    
    def test_reset_from_error(self):
        """Test resetting from ERROR to IDLE."""
        self.state.set_error("Test error")
        assert self.state.current_state == PlayState.ERROR
        
        self.state.reset()
        assert self.state.current_state == PlayState.IDLE
        assert self.state.error_message is None


class TestSequenceBuilder:
    """Test suite for SequenceBuilder class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.builder = SequenceBuilder()
    
    def test_emoji_mapping_correct(self):
        """AC3.4: Emoji mapping is correct."""
        expected_map = {
            "wave": "👋",
            "robot_pose": "🤖",
            "spin": "💃",
            "stretch": "🙆",
            "dab": "🕺",
            "pause": "⏸",
        }
        assert self.builder.EMOJI_MAP == expected_map
    
    def test_empty_state_message(self):
        """AC3.5: Empty state message is correct."""
        expected = "Tap moves above to build your dance! 🎵"
        assert self.builder.EMPTY_MESSAGE == expected
        assert self.builder.format_sequence() == expected
    
    def test_add_move_updates_display(self):
        """AC3.9: Emoji appears in sequence when move added."""
        display = self.builder.add_move("wave")
        
        assert "👋" in display
        assert "Your Dance:" in display
        assert len(self.builder.moves) == 1
    
    def test_sequence_display_format(self):
        """AC3.6: Sequence display format is correct."""
        self.builder.add_move("wave")
        self.builder.add_move("robot_pose")
        self.builder.add_move("spin")
        
        display = self.builder.format_sequence()
        assert display == "Your Dance: 👋 🤖 💃"
    
    def test_undo_removes_last(self):
        """AC3.9: Last move removed correctly."""
        self.builder.add_move("wave")
        self.builder.add_move("spin")
        self.builder.add_move("dab")
        
        display = self.builder.undo_last()
        
        assert len(self.builder.moves) == 2
        assert "🕺" not in display  # Dab should be gone
        assert "👋" in display  # Wave should remain
        assert "💃" in display  # Spin should remain
    
    def test_undo_on_empty_sequence(self):
        """Test undo on empty sequence returns empty message."""
        display = self.builder.undo_last()
        assert display == self.builder.EMPTY_MESSAGE
    
    def test_clear_resets_sequence(self):
        """AC3.9: Sequence emptied correctly."""
        self.builder.add_move("wave")
        self.builder.add_move("spin")
        self.builder.add_move("dab")
        
        display = self.builder.clear_all()
        
        assert len(self.builder.moves) == 0
        assert display == self.builder.EMPTY_MESSAGE
    
    def test_get_sequence_returns_copy(self):
        """Test get_sequence returns a copy of moves list."""
        self.builder.add_move("wave")
        self.builder.add_move("spin")
        
        sequence = self.builder.get_sequence()
        
        # Modifying returned sequence shouldn't affect builder
        sequence.append("dab")
        assert len(self.builder.moves) == 2
        assert len(sequence) == 3
    
    def test_unknown_move_shows_question_mark(self):
        """Test unknown moves show ❓ emoji."""
        self.builder.moves.append("unknown_move")
        display = self.builder.format_sequence()
        
        assert "❓" in display
    
    def test_multiple_operations(self):
        """Test sequence of operations."""
        # Add several moves
        self.builder.add_move("wave")
        self.builder.add_move("spin")
        self.builder.add_move("dab")
        assert len(self.builder.moves) == 3
        
        # Undo last
        self.builder.undo_last()
        assert len(self.builder.moves) == 2
        
        # Add another
        self.builder.add_move("stretch")
        assert len(self.builder.moves) == 3
        assert self.builder.moves[-1] == "stretch"
        
        # Clear all
        self.builder.clear_all()
        assert len(self.builder.moves) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
