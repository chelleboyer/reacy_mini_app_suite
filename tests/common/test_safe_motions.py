"""Tests for safe motion controller."""

import pytest
import numpy as np

from common.reachy import SafeMotionController


def test_safe_motion_init():
    """Test SafeMotionController initialization."""
    controller = SafeMotionController()
    assert controller is not None
    assert controller.max_velocity > 0


def test_validate_head_angles_valid():
    """Test validation of valid head angles."""
    controller = SafeMotionController()
    is_valid, violations = controller.validate_head_angles(0.0, 0.0, 0.0)
    assert is_valid
    assert len(violations) == 0


def test_validate_head_angles_invalid():
    """Test validation of invalid head angles."""
    controller = SafeMotionController()
    # Exceed pitch limit
    is_valid, violations = controller.validate_head_angles(0.0, 5.0, 0.0)
    assert not is_valid
    assert len(violations) > 0


def test_clamp_head_angles():
    """Test clamping of head angles."""
    controller = SafeMotionController()
    # Test clamping of excessive angles
    roll, pitch, yaw = controller.clamp_head_angles(10.0, 10.0, 10.0)
    
    # All should be clamped to within limits
    assert roll <= controller.head_limits["roll"][1]
    assert pitch <= controller.head_limits["pitch"][1]
    assert yaw <= controller.head_limits["yaw"][1]


def test_validate_antenna_positions():
    """Test validation of antenna positions."""
    controller = SafeMotionController()
    is_valid, violations = controller.validate_antenna_positions(0.0, 0.0)
    assert is_valid
    assert len(violations) == 0


def test_clamp_antenna_positions():
    """Test clamping of antenna positions."""
    controller = SafeMotionController()
    # Test clamping of excessive positions
    left, right = controller.clamp_antenna_positions(10.0, -10.0)
    
    # Should be clamped to within limits
    assert controller.antenna_limits[0] <= left <= controller.antenna_limits[1]
    assert controller.antenna_limits[0] <= right <= controller.antenna_limits[1]


def test_calculate_safe_duration():
    """Test safe duration calculation."""
    controller = SafeMotionController()
    
    # Test with small angular distance
    duration = controller.calculate_safe_duration(0.1)
    assert duration >= 0.5  # Minimum duration
    
    # Test with large angular distance
    duration = controller.calculate_safe_duration(2.0)
    assert duration >= 2.0 / controller.max_velocity


def test_validate_head_angles_degrees():
    """Test validation with degrees."""
    controller = SafeMotionController()
    
    # Valid angles in degrees
    is_valid, violations = controller.validate_head_angles(10, 15, 20, degrees=True)
    assert is_valid
    assert len(violations) == 0
    
    # Invalid angles in degrees
    is_valid, violations = controller.validate_head_angles(50, 60, 100, degrees=True)
    assert not is_valid
    assert len(violations) == 3


def test_clamp_head_angles_degrees():
    """Test clamping with degrees."""
    controller = SafeMotionController()
    
    # Test clamping with degrees
    roll, pitch, yaw = controller.clamp_head_angles(50, 60, 100, degrees=True)
    
    # Convert limits to degrees for comparison
    roll_limit_deg = np.rad2deg(controller.head_limits["roll"][1])
    pitch_limit_deg = np.rad2deg(controller.head_limits["pitch"][1])
    yaw_limit_deg = np.rad2deg(controller.head_limits["yaw"][1])
    
    assert roll <= roll_limit_deg
    assert pitch <= pitch_limit_deg
    assert yaw <= yaw_limit_deg


def test_calculate_safe_duration():
    """Test safe duration calculation."""
    controller = SafeMotionController()
    duration = controller.calculate_safe_duration(np.pi / 2)
    assert duration > 0
    assert duration >= 0.5  # At least minimum duration
