"""Safe motion controller with limits and validation.

This module provides safety features for robot motions, including
joint limit checking, velocity limits, and smooth interpolation.
"""

import logging
from typing import List, Optional, Tuple

import numpy as np

from ..core import setup_logger


class SafeMotionController:
    """Controller for safe robot motions with limits.
    
    This class enforces safety constraints on robot movements,
    including joint limits, velocity limits, and smooth acceleration.
    """
    
    # Conservative joint limits (radians)
    # Based on typical Reachy Mini specs, adjusted for safety
    DEFAULT_HEAD_LIMITS = {
        "roll": (-0.3, 0.3),      # ±17 degrees
        "pitch": (-0.5, 0.5),     # ±29 degrees
        "yaw": (-0.8, 0.8),       # ±46 degrees
    }
    
    DEFAULT_ANTENNA_LIMITS = (-3.14, 3.14)  # Full range
    
    # Maximum velocities (radians/second)
    DEFAULT_MAX_VELOCITY = 1.0  # Conservative default
    
    def __init__(
        self,
        head_limits: Optional[dict] = None,
        antenna_limits: Optional[Tuple[float, float]] = None,
        max_velocity: float = DEFAULT_MAX_VELOCITY,
        log_level: str = "INFO",
    ):
        """Initialize safe motion controller.
        
        Args:
            head_limits: Custom head joint limits (dict with roll, pitch, yaw)
            antenna_limits: Custom antenna limits (tuple of min, max)
            max_velocity: Maximum angular velocity in rad/s
            log_level: Logging level
        """
        self.logger = setup_logger(__name__, level=log_level)
        
        self.head_limits = head_limits or self.DEFAULT_HEAD_LIMITS.copy()
        self.antenna_limits = antenna_limits or self.DEFAULT_ANTENNA_LIMITS
        self.max_velocity = max_velocity
    
    def validate_head_angles(
        self,
        roll: float,
        pitch: float,
        yaw: float,
        degrees: bool = False,
    ) -> Tuple[bool, List[str]]:
        """Validate head angles against limits.
        
        Args:
            roll: Roll angle
            pitch: Pitch angle
            yaw: Yaw angle
            degrees: Whether angles are in degrees
            
        Returns:
            Tuple of (is_valid, list_of_violations)
        """
        if degrees:
            roll = np.deg2rad(roll)
            pitch = np.deg2rad(pitch)
            yaw = np.deg2rad(yaw)
        
        violations = []
        
        # Check roll
        if not (self.head_limits["roll"][0] <= roll <= self.head_limits["roll"][1]):
            violations.append(
                f"Roll {roll:.2f} rad outside limits "
                f"{self.head_limits['roll']}"
            )
        
        # Check pitch
        if not (self.head_limits["pitch"][0] <= pitch <= self.head_limits["pitch"][1]):
            violations.append(
                f"Pitch {pitch:.2f} rad outside limits "
                f"{self.head_limits['pitch']}"
            )
        
        # Check yaw
        if not (self.head_limits["yaw"][0] <= yaw <= self.head_limits["yaw"][1]):
            violations.append(
                f"Yaw {yaw:.2f} rad outside limits "
                f"{self.head_limits['yaw']}"
            )
        
        is_valid = len(violations) == 0
        return is_valid, violations
    
    def validate_antenna_positions(
        self,
        left: float,
        right: float,
    ) -> Tuple[bool, List[str]]:
        """Validate antenna positions against limits.
        
        Args:
            left: Left antenna position (radians)
            right: Right antenna position (radians)
            
        Returns:
            Tuple of (is_valid, list_of_violations)
        """
        violations = []
        
        if not (self.antenna_limits[0] <= left <= self.antenna_limits[1]):
            violations.append(
                f"Left antenna {left:.2f} rad outside limits "
                f"{self.antenna_limits}"
            )
        
        if not (self.antenna_limits[0] <= right <= self.antenna_limits[1]):
            violations.append(
                f"Right antenna {right:.2f} rad outside limits "
                f"{self.antenna_limits}"
            )
        
        is_valid = len(violations) == 0
        return is_valid, violations
    
    def clamp_head_angles(
        self,
        roll: float,
        pitch: float,
        yaw: float,
        degrees: bool = False,
    ) -> Tuple[float, float, float]:
        """Clamp head angles to safe limits.
        
        Args:
            roll: Roll angle
            pitch: Pitch angle
            yaw: Yaw angle
            degrees: Whether angles are in degrees
            
        Returns:
            Tuple of (clamped_roll, clamped_pitch, clamped_yaw) in same units as input
        """
        if degrees:
            roll = np.deg2rad(roll)
            pitch = np.deg2rad(pitch)
            yaw = np.deg2rad(yaw)
        
        # Clamp each angle
        roll = np.clip(roll, *self.head_limits["roll"])
        pitch = np.clip(pitch, *self.head_limits["pitch"])
        yaw = np.clip(yaw, *self.head_limits["yaw"])
        
        if degrees:
            roll = np.rad2deg(roll)
            pitch = np.rad2deg(pitch)
            yaw = np.rad2deg(yaw)
        
        return roll, pitch, yaw
    
    def clamp_antenna_positions(
        self,
        left: float,
        right: float,
    ) -> Tuple[float, float]:
        """Clamp antenna positions to safe limits.
        
        Args:
            left: Left antenna position (radians)
            right: Right antenna position (radians)
            
        Returns:
            Tuple of (clamped_left, clamped_right)
        """
        left = np.clip(left, *self.antenna_limits)
        right = np.clip(right, *self.antenna_limits)
        return left, right
    
    def calculate_safe_duration(
        self,
        angular_distance: float,
        min_duration: float = 0.5,
    ) -> float:
        """Calculate safe movement duration based on angular distance.
        
        Args:
            angular_distance: Angular distance to travel (radians)
            min_duration: Minimum duration (seconds)
            
        Returns:
            Safe duration in seconds
        """
        # Calculate duration based on max velocity
        required_duration = angular_distance / self.max_velocity
        
        # Apply minimum duration for smooth motion
        safe_duration = max(required_duration, min_duration)
        
        return safe_duration
