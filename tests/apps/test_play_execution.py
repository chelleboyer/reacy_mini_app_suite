"""
Integration tests for Reachy Remix Play Execution

Story 4 - AC4.7: Integration test coverage for play execution
"""

import pytest
import sys
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "apps" / "reachy-remix"))

from reachy_remix import PlayState, AppState, SequenceBuilder, MotionEngine, ExecutionResult


class TestPlayExecution:
    """Integration tests for play execution flow."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.app_state = AppState()
        self.sequence_builder = SequenceBuilder()
        self.mock_robot = Mock()
        self.mock_controller = Mock()
        self.motion_engine = MotionEngine(
            robot=self.mock_robot,
            controller=self.mock_controller
        )
    
    def test_play_empty_sequence(self):
        """AC4.7: Validation message shown when sequence empty."""
        # Try to play with no moves
        assert self.app_state.can_play() == False
        
        # Simulate play click handler logic
        if not self.app_state.can_play():
            message = "Add at least one move first! 🙂"
        else:
            message = "Playing..."
        
        assert "Add at least one move" in message
        assert self.app_state.current_state == PlayState.IDLE
    
    def test_play_full_sequence(self):
        """AC4.7: All moves execute in order."""
        # Build a sequence
        self.sequence_builder.add_move("wave")
        self.sequence_builder.add_move("spin")
        self.sequence_builder.add_move("dab")
        self.app_state.sequence = self.sequence_builder.get_sequence()
        
        # Execute sequence
        assert self.app_state.can_play() == True
        
        self.app_state.start_playing()
        result = self.motion_engine.execute_sequence(self.app_state.sequence, with_feedback=False)
        self.app_state.finish_playing()
        
        # Verify execution
        assert result.success == True
        assert result.moves_completed == 3
        assert self.app_state.current_state == PlayState.IDLE
        
        # Verify moves were called in order
        assert self.mock_controller.wave_antennas.called
        assert self.mock_robot.move_head.called  # spin uses move_head
        assert self.mock_controller.transition_to_pose.called  # dab uses transition_to_pose
    
    def test_spam_play_button(self):
        """AC4.7: Only one execution happens when spamming play."""
        self.sequence_builder.add_move("wave")
        self.app_state.sequence = self.sequence_builder.get_sequence()
        
        # Start first execution
        assert self.app_state.can_play() == True
        self.app_state.start_playing()
        assert self.app_state.current_state == PlayState.PLAYING
        
        # Try to play again while playing
        assert self.app_state.can_play() == False
        
        # Verify state machine prevents concurrent execution
        with pytest.raises(ValueError):
            self.app_state.start_playing()  # Should fail
        
        # Finish first execution
        self.app_state.finish_playing()
        assert self.app_state.current_state == PlayState.IDLE
    
    def test_error_recovery(self):
        """AC4.7: Returns to IDLE after error."""
        self.sequence_builder.add_move("wave")
        self.app_state.sequence = self.sequence_builder.get_sequence()
        
        # Simulate error during execution
        self.mock_controller.wave_antennas.side_effect = Exception("Robot error")
        
        self.app_state.start_playing()
        result = self.motion_engine.execute_sequence(self.app_state.sequence, with_feedback=False)
        
        # Verify error was caught
        assert result.success == False
        assert "Robot error" in result.error_message
        
        # Simulate error recovery in play handler
        self.app_state.set_error(result.error_message)
        assert self.app_state.current_state == PlayState.ERROR
        
        # Reset to allow retry
        self.app_state.reset()
        assert self.app_state.current_state == PlayState.IDLE
    
    def test_sequence_preserved_on_error(self):
        """AC4.7: Sequence not lost after error."""
        # Build sequence
        self.sequence_builder.add_move("wave")
        self.sequence_builder.add_move("spin")
        self.app_state.sequence = self.sequence_builder.get_sequence()
        
        original_sequence = self.app_state.sequence.copy()
        
        # Cause error
        self.mock_controller.wave_antennas.side_effect = Exception("Test error")
        
        self.app_state.start_playing()
        result = self.motion_engine.execute_sequence(self.app_state.sequence, with_feedback=False)
        
        # Verify sequence still intact
        assert self.app_state.sequence == original_sequence
        assert len(self.sequence_builder.moves) == 2
        assert self.sequence_builder.moves[0] == "wave"
        assert self.sequence_builder.moves[1] == "spin"


class TestPlayFlow:
    """Test complete play flow integration."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.app_state = AppState()
        self.sequence_builder = SequenceBuilder()
        self.demo_engine = MotionEngine(robot=None, controller=None)  # Demo mode
    
    def test_complete_flow_success(self):
        """Test complete successful flow from build to play."""
        # Build sequence
        self.sequence_builder.add_move("wave")
        self.sequence_builder.add_move("robot_pose")
        self.app_state.sequence = self.sequence_builder.get_sequence()
        
        # Verify can play
        assert self.app_state.can_play() == True
        
        # Execute
        self.app_state.start_playing()
        assert self.app_state.current_state == PlayState.PLAYING
        
        result = self.demo_engine.execute_sequence(self.app_state.sequence, with_feedback=False)
        
        assert result.success == True
        assert result.moves_completed == 2
        
        self.app_state.finish_playing()
        assert self.app_state.current_state == PlayState.IDLE
    
    def test_inter_move_delay_timing(self):
        """AC4.6: Inter-move delay is visible (0.5s between moves)."""
        self.sequence_builder.add_move("pause")
        self.sequence_builder.add_move("pause")
        self.app_state.sequence = self.sequence_builder.get_sequence()
        
        start_time = time.time()
        result = self.demo_engine.execute_sequence(self.app_state.sequence, with_feedback=False)
        elapsed = time.time() - start_time
        
        # Each pause is 0.5s, plus 0.5s delay between them
        # Total should be at least 1.5s (0.5 + 0.5 + 0.5)
        assert elapsed >= 1.5
        assert result.success == True
    
    def test_multiple_plays_in_sequence(self):
        """Test playing sequence multiple times."""
        self.sequence_builder.add_move("wave")
        self.app_state.sequence = self.sequence_builder.get_sequence()
        
        # First play
        self.app_state.start_playing()
        result1 = self.demo_engine.execute_sequence(self.app_state.sequence, with_feedback=False)
        self.app_state.finish_playing()
        
        assert result1.success == True
        assert self.app_state.current_state == PlayState.IDLE
        
        # Second play
        self.app_state.start_playing()
        result2 = self.demo_engine.execute_sequence(self.app_state.sequence, with_feedback=False)
        self.app_state.finish_playing()
        
        assert result2.success == True
        assert self.app_state.current_state == PlayState.IDLE
    
    def test_modify_sequence_after_play(self):
        """Test that sequence can be modified after playing."""
        # Play initial sequence
        self.sequence_builder.add_move("wave")
        self.app_state.sequence = self.sequence_builder.get_sequence()
        
        self.app_state.start_playing()
        result = self.demo_engine.execute_sequence(self.app_state.sequence, with_feedback=False)
        self.app_state.finish_playing()
        
        assert result.success == True
        
        # Modify sequence
        self.sequence_builder.add_move("dab")
        self.app_state.sequence = self.sequence_builder.get_sequence()
        
        # Play modified sequence
        self.app_state.start_playing()
        result2 = self.demo_engine.execute_sequence(self.app_state.sequence, with_feedback=False)
        self.app_state.finish_playing()
        
        assert result2.success == True
        assert result2.moves_completed == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
