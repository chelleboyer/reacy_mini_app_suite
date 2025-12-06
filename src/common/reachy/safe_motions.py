"""Safe motion controller with limits, validation, and gesture library.

This module provides safety features for robot motions, including
joint limit checking, velocity limits, smooth interpolation, and
pre-defined gestures and expressions for common interactions.
"""

import logging
import time
from typing import List, Optional, Tuple, TYPE_CHECKING

import numpy as np

from ..core import setup_logger

if TYPE_CHECKING:
    from .robot_wrapper import ReachyWrapper


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
    
    # ============================================================
    # GESTURE LIBRARY
    # ============================================================
    
    def nod_yes(self, robot: "ReachyWrapper", count: int = 2, speed: float = 1.0) -> None:
        """Perform a 'yes' nodding gesture.
        
        Args:
            robot: ReachyWrapper instance to control
            count: Number of nods
            speed: Speed multiplier (higher = faster)
        """
        base_duration = 0.4 / speed
        pitch_down = 15  # degrees
        pitch_up = -10
        
        self.logger.info(f"Performing 'yes' nod gesture ({count} times)")
        
        for i in range(count):
            # Nod down
            robot.move_head(pitch=pitch_down, duration=base_duration, degrees=True)
            time.sleep(base_duration)
            
            # Nod up
            robot.move_head(pitch=pitch_up, duration=base_duration, degrees=True)
            time.sleep(base_duration)
        
        # Return to neutral
        robot.move_head(pitch=0, duration=base_duration, degrees=True)
        time.sleep(base_duration)
    
    def shake_no(self, robot: "ReachyWrapper", count: int = 2, speed: float = 1.0) -> None:
        """Perform a 'no' head shaking gesture.
        
        Args:
            robot: ReachyWrapper instance to control
            count: Number of shakes
            speed: Speed multiplier (higher = faster)
        """
        base_duration = 0.3 / speed
        yaw_left = -25  # degrees
        yaw_right = 25
        
        self.logger.info(f"Performing 'no' shake gesture ({count} times)")
        
        for i in range(count):
            # Shake left
            robot.move_head(yaw=yaw_left, duration=base_duration, degrees=True)
            time.sleep(base_duration)
            
            # Shake right
            robot.move_head(yaw=yaw_right, duration=base_duration, degrees=True)
            time.sleep(base_duration)
        
        # Return to neutral
        robot.move_head(yaw=0, duration=base_duration, degrees=True)
        time.sleep(base_duration)
    
    def tilt_curious(self, robot: "ReachyWrapper", direction: str = "right") -> None:
        """Perform a curious head tilt.
        
        Args:
            robot: ReachyWrapper instance to control
            direction: 'left' or 'right'
        """
        tilt_angle = 15 if direction == "right" else -15
        duration = 0.6
        
        self.logger.info(f"Performing curious tilt to {direction}")
        
        # Tilt head
        robot.move_head(roll=tilt_angle, duration=duration, degrees=True)
        time.sleep(duration)
        
        # Hold for a moment
        time.sleep(0.5)
        
        # Return to neutral
        robot.move_head(roll=0, duration=duration, degrees=True)
        time.sleep(duration)
    
    def wave_antennas(
        self, 
        robot: "ReachyWrapper", 
        count: int = 3, 
        speed: float = 1.0,
        synchronized: bool = True
    ) -> None:
        """Wave the antennas in a friendly gesture.
        
        Args:
            robot: ReachyWrapper instance to control
            count: Number of waves
            speed: Speed multiplier (higher = faster)
            synchronized: If True, antennas move together; if False, alternating
        """
        base_duration = 0.3 / speed
        amplitude = 0.8  # radians
        
        self.logger.info(f"Waving antennas ({count} times, {'synchronized' if synchronized else 'alternating'})")
        
        for i in range(count):
            if synchronized:
                # Both antennas move together
                robot.move_antennas(left=amplitude, right=-amplitude, duration=base_duration)
                time.sleep(base_duration)
                robot.move_antennas(left=-amplitude, right=amplitude, duration=base_duration)
                time.sleep(base_duration)
            else:
                # Alternating wave
                robot.move_antennas(left=amplitude, right=0, duration=base_duration)
                time.sleep(base_duration)
                robot.move_antennas(left=0, right=-amplitude, duration=base_duration)
                time.sleep(base_duration)
        
        # Return to neutral
        robot.move_antennas(left=0, right=0, duration=base_duration)
        time.sleep(base_duration)
    
    def look_around(self, robot: "ReachyWrapper", speed: float = 1.0) -> None:
        """Look around by scanning left and right.
        
        Args:
            robot: ReachyWrapper instance to control
            speed: Speed multiplier (higher = faster)
        """
        base_duration = 1.0 / speed
        yaw_angle = 40  # degrees
        
        self.logger.info("Performing look around gesture")
        
        # Look left
        robot.move_head(yaw=-yaw_angle, duration=base_duration, degrees=True)
        time.sleep(base_duration + 0.5)
        
        # Look right
        robot.move_head(yaw=yaw_angle, duration=base_duration * 1.5, degrees=True)
        time.sleep(base_duration * 1.5 + 0.5)
        
        # Return to center
        robot.move_head(yaw=0, duration=base_duration, degrees=True)
        time.sleep(base_duration)
    
    def express_thinking(self, robot: "ReachyWrapper") -> None:
        """Express a 'thinking' pose with head tilt and antenna positioning.
        
        Args:
            robot: ReachyWrapper instance to control
        """
        self.logger.info("Expressing 'thinking' pose")
        
        # Tilt head slightly, look up
        robot.move_head(roll=10, pitch=-8, duration=0.8, degrees=True)
        time.sleep(0.8)
        
        # Position antennas in contemplative pose
        robot.move_antennas(left=0.3, right=-0.3, duration=0.5)
        time.sleep(0.5)
        
        # Hold pose
        time.sleep(1.5)
        
        # Return to neutral
        robot.move_head(roll=0, pitch=0, duration=0.8, degrees=True)
        robot.move_antennas(left=0, right=0, duration=0.5)
        time.sleep(0.8)
    
    # ============================================================
    # EXPRESSION PRESETS
    # ============================================================
    
    def express_happy(self, robot: "ReachyWrapper") -> None:
        """Express happiness with upward head tilt and antenna wave.
        
        Args:
            robot: ReachyWrapper instance to control
        """
        self.logger.info("Expressing 'happy' emotion")
        
        # Slight upward tilt
        robot.move_head(pitch=-12, duration=0.6, degrees=True)
        time.sleep(0.6)
        
        # Excited antenna wave
        self.wave_antennas(robot, count=2, speed=1.5, synchronized=True)
        
        # Return to neutral with slight tilt
        robot.move_head(pitch=-5, duration=0.5, degrees=True)
        time.sleep(0.5)
    
    def express_sad(self, robot: "ReachyWrapper") -> None:
        """Express sadness with downward head tilt and drooping antennas.
        
        Args:
            robot: ReachyWrapper instance to control
        """
        self.logger.info("Expressing 'sad' emotion")
        
        # Look down
        robot.move_head(pitch=15, duration=1.0, degrees=True)
        time.sleep(1.0)
        
        # Droop antennas
        robot.move_antennas(left=-0.3, right=0.3, duration=0.8)
        time.sleep(0.8)
        
        # Hold pose
        time.sleep(1.5)
        
        # Return to neutral slowly
        robot.move_head(pitch=0, duration=1.2, degrees=True)
        robot.move_antennas(left=0, right=0, duration=1.0)
        time.sleep(1.2)
    
    def express_curious(self, robot: "ReachyWrapper") -> None:
        """Express curiosity with head tilt and perked antennas.
        
        Args:
            robot: ReachyWrapper instance to control
        """
        self.logger.info("Expressing 'curious' emotion")
        
        # Quick head tilt
        robot.move_head(roll=15, pitch=-8, duration=0.5, degrees=True)
        time.sleep(0.5)
        
        # Perk up antennas
        robot.move_antennas(left=0.5, right=-0.5, duration=0.4)
        time.sleep(0.4)
        
        # Hold curious pose
        time.sleep(1.0)
        
        # Return to neutral
        robot.move_head(roll=0, pitch=0, duration=0.6, degrees=True)
        robot.move_antennas(left=0, right=0, duration=0.5)
        time.sleep(0.6)
    
    def express_confused(self, robot: "ReachyWrapper") -> None:
        """Express confusion with alternating head tilts.
        
        Args:
            robot: ReachyWrapper instance to control
        """
        self.logger.info("Expressing 'confused' emotion")
        
        # Tilt left
        robot.move_head(roll=-12, duration=0.4, degrees=True)
        time.sleep(0.5)
        
        # Tilt right
        robot.move_head(roll=12, duration=0.5, degrees=True)
        time.sleep(0.6)
        
        # Back to left with antennas
        robot.move_head(roll=-12, duration=0.4, degrees=True)
        robot.move_antennas(left=-0.3, right=0.3, duration=0.4)
        time.sleep(0.8)
        
        # Return to neutral
        robot.move_head(roll=0, duration=0.5, degrees=True)
        robot.move_antennas(left=0, right=0, duration=0.5)
        time.sleep(0.5)
    
    def express_excited(self, robot: "ReachyWrapper") -> None:
        """Express excitement with rapid movements and antenna waves.
        
        Args:
            robot: ReachyWrapper instance to control
        """
        self.logger.info("Expressing 'excited' emotion")
        
        # Quick nod
        self.nod_yes(robot, count=2, speed=2.0)
        
        # Rapid antenna wave
        self.wave_antennas(robot, count=3, speed=2.0, synchronized=True)
        
        # Slight upward tilt
        robot.move_head(pitch=-8, duration=0.4, degrees=True)
        time.sleep(0.4)
    
    # ============================================================
    # SINGING-SPECIFIC GESTURES
    # ============================================================
    
    def singing_sway(
        self,
        robot: "ReachyWrapper",
        duration: float = 2.0,
        magnitude: float = 10.0
    ) -> None:
        """Gentle swaying motion for singing (side to side).
        
        Args:
            robot: ReachyWrapper instance to control
            duration: Duration of one complete sway cycle
            magnitude: Sway angle in degrees
        """
        self.logger.info(f"Singing sway (duration={duration}s, magnitude={magnitude}°)")
        
        half_duration = duration / 2
        
        # Sway right
        robot.move_head(roll=magnitude, duration=half_duration, degrees=True)
        time.sleep(half_duration)
        
        # Sway left
        robot.move_head(roll=-magnitude, duration=duration, degrees=True)
        time.sleep(duration)
        
        # Return to center
        robot.move_head(roll=0, duration=half_duration, degrees=True)
        time.sleep(half_duration)
    
    def singing_lean_forward(
        self,
        robot: "ReachyWrapper",
        duration: float = 1.0,
        intensity: float = 0.8
    ) -> None:
        """Lean forward dramatically (e.g., belt out a note).
        
        Args:
            robot: ReachyWrapper instance to control
            duration: Duration to hold the lean
            intensity: Lean intensity (0.0 to 1.0)
        """
        angle = -15 * intensity  # Negative pitch = forward
        self.logger.info(f"Singing lean forward (angle={angle}°, duration={duration}s)")
        
        # Lean forward
        robot.move_head(pitch=angle, duration=0.4, degrees=True)
        robot.move_antennas(left=0.5, right=-0.5, duration=0.4)
        time.sleep(0.4)
        
        # Hold
        time.sleep(duration)
        
        # Return
        robot.move_head(pitch=0, duration=0.6, degrees=True)
        robot.move_antennas(left=0, right=0, duration=0.6)
        time.sleep(0.6)
    
    def singing_dramatic_pause(
        self,
        robot: "ReachyWrapper",
        duration: float = 1.5
    ) -> None:
        """Dramatic pause with head tilt (suspense before big note).
        
        Args:
            robot: ReachyWrapper instance to control
            duration: Duration of the pause
        """
        self.logger.info(f"Singing dramatic pause ({duration}s)")
        
        # Tilt head slightly, antennas perk up
        robot.move_head(roll=8, pitch=-5, duration=0.5, degrees=True)
        robot.move_antennas(left=0.6, right=-0.6, duration=0.5)
        time.sleep(0.5)
        
        # Hold the pose
        time.sleep(duration)
        
        # Quick return to neutral
        robot.move_head(roll=0, pitch=0, duration=0.3, degrees=True)
        robot.move_antennas(left=0, right=0, duration=0.3)
        time.sleep(0.3)
    
    def singing_big_finish(self, robot: "ReachyWrapper") -> None:
        """Triumphant ending gesture for song finale.
        
        Args:
            robot: ReachyWrapper instance to control
        """
        self.logger.info("Singing BIG FINISH!")
        
        # Build up - lean back
        robot.move_head(pitch=10, duration=0.8, degrees=True)
        time.sleep(0.8)
        
        # FINALE - arms up (antennas), look up
        robot.move_head(pitch=-20, duration=0.4, degrees=True)
        robot.move_antennas(left=0.9, right=-0.9, duration=0.4)
        time.sleep(0.5)
        
        # Hold triumphant pose
        time.sleep(1.5)
        
        # Slow, satisfied return to neutral
        robot.move_head(pitch=0, duration=1.0, degrees=True)
        robot.move_antennas(left=0, right=0, duration=1.0)
        time.sleep(1.0)
    
    def singing_bashful_bow(self, robot: "ReachyWrapper") -> None:
        """Shy/bashful bow after performance (aww, shucks).
        
        Args:
            robot: ReachyWrapper instance to control
        """
        self.logger.info("Singing bashful bow")
        
        # Look down shyly
        robot.move_head(pitch=15, roll=8, duration=0.8, degrees=True)
        robot.move_antennas(left=-0.3, right=0.3, duration=0.8)
        time.sleep(1.2)
        
        # Quick peek up
        robot.move_head(pitch=5, duration=0.4, degrees=True)
        time.sleep(0.6)
        
        # Back to shy
        robot.move_head(pitch=12, duration=0.5, degrees=True)
        time.sleep(1.0)
        
        # Finally return to neutral
        robot.move_head(pitch=0, roll=0, duration=0.8, degrees=True)
        robot.move_antennas(left=0, right=0, duration=0.8)
        time.sleep(0.8)
    
    # ============================================================
    # SMOOTH TRANSITIONS
    # ============================================================
    
    def transition_to_pose(
        self,
        robot: "ReachyWrapper",
        roll: float = 0,
        pitch: float = 0,
        yaw: float = 0,
        left_antenna: float = 0,
        right_antenna: float = 0,
        duration: float = 1.0,
        degrees: bool = True,
    ) -> None:
        """Smoothly transition to a specific pose.
        
        Args:
            robot: ReachyWrapper instance to control
            roll: Target roll angle
            pitch: Target pitch angle
            yaw: Target yaw angle
            left_antenna: Target left antenna position (radians)
            right_antenna: Target right antenna position (radians)
            duration: Transition duration in seconds
            degrees: Whether head angles are in degrees
        """
        # Validate and clamp angles
        if degrees:
            roll, pitch, yaw = self.clamp_head_angles(roll, pitch, yaw, degrees=True)
        else:
            roll, pitch, yaw = self.clamp_head_angles(roll, pitch, yaw, degrees=False)
        
        left_antenna, right_antenna = self.clamp_antenna_positions(left_antenna, right_antenna)
        
        self.logger.debug(f"Transitioning to pose: roll={roll}, pitch={pitch}, yaw={yaw}")
        
        # Execute movements simultaneously
        robot.move_head(roll=roll, pitch=pitch, yaw=yaw, duration=duration, degrees=degrees)
        robot.move_antennas(left=left_antenna, right=right_antenna, duration=duration)
        time.sleep(duration)
    
    def return_to_neutral(self, robot: "ReachyWrapper", duration: float = 1.0) -> None:
        """Return robot to neutral pose.
        
        Args:
            robot: ReachyWrapper instance to control
            duration: Transition duration in seconds
        """
        self.logger.info("Returning to neutral pose")
        self.transition_to_pose(robot, duration=duration, degrees=True)
