"""
Unit tests for Reachy Remix Motion Engine

Story 2 - AC2.7: Unit test coverage for motion engine
"""

import pytest
import sys
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "apps" / "reachy-remix"))

from reachy_remix import MotionEngine, ExecutionResult


class TestMotionEngine:
    """Test suite for MotionEngine class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        # Create mock robot and controller
        self.mock_robot = Mock()
        self.mock_controller = Mock()
        
        # Create engine with mocks
        self.engine = MotionEngine(
            robot=self.mock_robot,
            controller=self.mock_controller
        )
        
        # Create demo mode engine
        self.demo_engine = MotionEngine(robot=None, controller=None)
    
    def test_move_registry_completeness(self):
        """AC2.7: All 6 moves are callable."""
        expected_moves = ["wave", "robot_pose", "spin", "stretch", "dab", "pause"]
        
        for move in expected_moves:
            assert move in self.engine.MOVE_REGISTRY
            assert callable(self.engine.MOVE_REGISTRY[move])
    
    def test_execute_single_move_success(self):
        """AC2.7: Single move executes successfully."""
        result = self.engine.execute_move("wave")
        
        assert result == True
        assert self.mock_controller.wave_antennas.called
    
    def test_execute_unknown_move_fails(self):
        """Test that unknown moves raise ValueError."""
        with pytest.raises(ValueError, match="Unknown move: unknown_move"):
            self.engine.execute_move("unknown_move")
    
    def test_execute_sequence_with_delay(self):
        """AC2.7: Inter-move timing verified."""
        sequence = ["wave", "spin"]
        
        start_time = time.time()
        result = self.engine.execute_sequence(sequence, with_feedback=False)
        elapsed = time.time() - start_time
        
        # Should take at least 0.5s delay between moves
        # Plus execution time (mocked, so ~instant)
        assert elapsed >= 0.5
        assert result.success == True
        assert result.moves_completed == 2
    
    def test_error_handling_sequence_failure(self):
        """AC2.7: Graceful failure on robot disconnect."""
        # Make controller raise exception
        self.mock_controller.wave_antennas.side_effect = Exception("Connection lost")
        
        result = self.engine.execute_sequence(["wave"])
        
        assert result.success == False
        assert result.moves_completed == 0
        assert "Connection lost" in result.error_message
    
    def test_demo_mode_no_robot_calls(self):
        """Test demo mode executes without calling robot."""
        result = self.demo_engine.execute_sequence(["wave", "spin", "dab"], with_feedback=False)
        
        assert result.success == True
        assert result.moves_completed == 3
        # No robot methods should be called
    
    def test_execution_result_dataclass(self):
        """Test ExecutionResult structure."""
        result = ExecutionResult(
            success=True,
            moves_completed=5,
            error_message=None
        )
        
        assert result.success == True
        assert result.moves_completed == 5
        assert result.error_message is None
    
    def test_micro_feedback_called_between_moves(self):
        """Test micro-feedback is called between moves (not after last)."""
        sequence = ["wave", "spin", "dab"]
        
        result = self.engine.execute_sequence(sequence, with_feedback=True)
        
        # Micro-feedback should be called 2 times (not after last move)
        assert self.mock_controller.nod_yes.call_count == 2
    
    def test_micro_feedback_skipped_in_demo_mode(self):
        """Test micro-feedback doesn't execute in demo mode."""
        result = self.demo_engine.execute_sequence(["wave", "spin"], with_feedback=True)
        
        assert result.success == True
        # No nod_yes calls since no controller
    
    def test_all_moves_execute(self):
        """Test each individual move can execute."""
        moves = ["wave", "robot_pose", "spin", "stretch", "dab", "pause"]
        
        for move in moves:
            result = self.demo_engine.execute_move(move)
            assert result == True, f"Move '{move}' failed to execute"
    
    def test_sequence_stops_on_first_failure(self):
        """Test sequence execution stops on first move failure."""
        # Make second move fail
        self.mock_controller.transition_to_pose.side_effect = Exception("Motor error")
        
        sequence = ["wave", "robot_pose", "spin"]  # Should stop at robot_pose
        result = self.engine.execute_sequence(sequence, with_feedback=False)
        
        assert result.success == False
        assert result.moves_completed == 1  # Only wave completed
        assert "Motor error" in result.error_message  # Error message includes the underlying exception


class TestMoveExecutions:
    """Test individual move implementations."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.mock_robot = Mock()
        self.mock_controller = Mock()
        self.engine = MotionEngine(
            robot=self.mock_robot,
            controller=self.mock_controller
        )
    
    def test_wave_move(self):
        """Test wave move calls correct SDK method."""
        self.engine._move_wave()
        
        self.mock_controller.wave_antennas.assert_called_once_with(
            self.mock_robot, count=2, speed=1.0
        )
    
    def test_robot_pose_move(self):
        """Test robot pose returns to neutral."""
        self.engine._move_robot_pose()
        
        self.mock_controller.transition_to_pose.assert_called_once()
        call_args = self.mock_controller.transition_to_pose.call_args
        assert call_args[1]['roll'] == 0
        assert call_args[1]['pitch'] == 0
        assert call_args[1]['yaw'] == 0
    
    def test_spin_move(self):
        """Test spin executes head rotation sequence."""
        self.engine._move_spin()
        
        # Should call move_head 3 times (left, right, center)
        assert self.mock_robot.move_head.call_count == 3
    
    def test_stretch_move(self):
        """Test stretch extends antennas and tilts head."""
        self.engine._move_stretch()
        
        call_args = self.mock_controller.transition_to_pose.call_args
        assert call_args[1]['pitch'] == -15
        assert call_args[1]['left_antenna'] == 0.8
        assert call_args[1]['right_antenna'] == -0.8
    
    def test_dab_move(self):
        """Test dab executes combined pose."""
        self.engine._move_dab()
        
        call_args = self.mock_controller.transition_to_pose.call_args
        assert call_args[1]['roll'] == 20
        assert call_args[1]['pitch'] == -10
        assert call_args[1]['yaw'] == 15
    
    def test_pause_move(self):
        """Test pause executes delay without motion."""
        start_time = time.time()
        self.engine._move_pause()
        elapsed = time.time() - start_time
        
        # Should pause for 0.5 seconds
        assert elapsed >= 0.5
        # No robot methods should be called
        assert not self.mock_robot.called
        assert not self.mock_controller.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
