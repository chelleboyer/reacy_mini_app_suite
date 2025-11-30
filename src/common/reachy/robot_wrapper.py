"""High-level wrapper for Reachy Mini robot control.

This module provides a simplified interface to the Reachy Mini robot,
abstracting common operations and providing safety features.

Uses the reachy_mini SDK (installed separately via pip).
"""

import logging
import time
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import numpy.typing as npt

from ..core import setup_logger

try:
    from reachy_mini import ReachyMini
    from reachy_mini.utils import create_head_pose
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False
    ReachyMini = None
    create_head_pose = None


class ReachyWrapper:
    """High-level wrapper for Reachy Mini control.
    
    This class provides a simplified, safer interface to the Reachy Mini robot,
    with built-in safety limits and common motion patterns.
    
    Usage:
        with ReachyWrapper() as robot:
            robot.wake_up()
            robot.move_head(pitch=0.1, yaw=0.0, duration=1.0)
    """
    
    def __init__(
        self,
        localhost_only: bool = True,
        spawn_daemon: bool = False,
        use_sim: bool = False,
        timeout: float = 5.0,
        media_backend: str = "no_media",
        log_level: str = "INFO",
    ):
        """Initialize Reachy wrapper.
        
        Args:
            localhost_only: Only connect to localhost daemons
            spawn_daemon: Spawn a daemon to control the robot
            use_sim: Use simulated robot (if spawn_daemon is True)
            timeout: Connection timeout in seconds
            media_backend: Media backend ("default", "gstreamer", "no_media")
            log_level: Logging level
        """
        self.logger = setup_logger(__name__, level=log_level)
        
        # Store init params
        self._localhost_only = localhost_only
        self._spawn_daemon = spawn_daemon
        self._use_sim = use_sim
        self._timeout = timeout
        self._media_backend = media_backend
        
        # Will be initialized in connect()
        self._robot: Optional[Any] = None
        self._is_connected = False
        
    def connect(self) -> None:
        """Connect to the Reachy Mini robot.
        
        Raises:
            ImportError: If reachy_mini package is not installed
            RuntimeError: If connection fails
        """
        if not SDK_AVAILABLE:
            self.logger.error("reachy_mini package not found. Please install it separately.")
            raise ImportError(
                "reachy_mini package is required. "
                "Install it with: pip install reachy_mini"
            )
        
        try:
            self.logger.info("Connecting to Reachy Mini daemon...")
            self._robot = ReachyMini(
                localhost_only=self._localhost_only,
                spawn_daemon=self._spawn_daemon,
                use_sim=self._use_sim,
                timeout=self._timeout,
                media_backend=self._media_backend,
                log_level="INFO",
            )
            self._is_connected = True
            
            # Get status info
            status = self._robot.client.get_status()
            sim_mode = status.get('simulation_enabled', 'unknown')
            self.logger.info(f"Connected to Reachy Mini (simulation={sim_mode})")
        except Exception as e:
            self.logger.error(f"Failed to connect to Reachy Mini: {e}")
            raise RuntimeError(f"Connection failed: {e}")
    
    def disconnect(self) -> None:
        """Disconnect from the robot."""
        if self._robot is not None:
            self.logger.info("Disconnecting from Reachy Mini...")
            try:
                # Clean shutdown
                if hasattr(self._robot, "media"):
                    self._robot.media.close()
                if hasattr(self._robot, "client"):
                    self._robot.client.disconnect()
            except Exception as e:
                self.logger.warning(f"Error during disconnect: {e}")
            finally:
                self._robot = None
                self._is_connected = False
    
    def __enter__(self) -> "ReachyWrapper":
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.disconnect()
    
    @property
    def is_connected(self) -> bool:
        """Check if robot is connected."""
        return self._is_connected and self._robot is not None
    
    def _check_connected(self) -> None:
        """Raise error if not connected."""
        if not self.is_connected:
            raise RuntimeError("Robot not connected. Call connect() first.")
    
    def wake_up(self) -> None:
        """Move robot to wake-up position with animation."""
        self._check_connected()
        self.logger.info("Waking up robot...")
        
        try:
            # Use built-in wake_up method
            self._robot.wake_up()
            self.logger.info("Wake-up complete")
        except Exception as e:
            self.logger.error(f"Wake-up failed: {e}")
            raise
    
    def go_to_sleep(self) -> None:
        """Move robot to sleep position."""
        self._check_connected()
        self.logger.info("Putting robot to sleep...")
        
        try:
            self._robot.goto_sleep()
            self.logger.info("Sleep complete")
        except Exception as e:
            self.logger.error(f"Go to sleep failed: {e}")
            raise
    
    def move_head(
        self,
        roll: float = 0.0,
        pitch: float = 0.0,
        yaw: float = 0.0,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        duration: float = 1.0,
        degrees: bool = True,
        mm: bool = False,
    ) -> None:
        """Move head to specified position and orientation.
        
        Args:
            roll: Roll angle (rotation around x-axis)
            pitch: Pitch angle (rotation around y-axis)
            yaw: Yaw angle (rotation around z-axis)
            x: X position offset
            y: Y position offset
            z: Z position offset
            duration: Movement duration in seconds
            degrees: Whether angles are in degrees (True) or radians (False)
            mm: Whether positions are in millimeters (True) or meters (False)
        """
        self._check_connected()
        
        try:
            head_pose = create_head_pose(
                x=x, y=y, z=z,
                roll=roll,
                pitch=pitch,
                yaw=yaw,
                degrees=degrees,
                mm=mm,
            )
            self._robot.goto_target(head=head_pose, duration=duration)
        except Exception as e:
            self.logger.error(f"Move head failed: {e}")
            raise
    
    def move_antennas(
        self,
        left: float = 0.0,
        right: float = 0.0,
        duration: float = 1.0,
    ) -> None:
        """Move antennas to specified positions.
        
        Args:
            left: Left antenna position (radians)
            right: Right antenna position (radians)
            duration: Movement duration in seconds
        """
        self._check_connected()
        
        try:
            # SDK expects [right, left] order
            self._robot.goto_target(antennas=[right, left], duration=duration)
        except Exception as e:
            self.logger.error(f"Move antennas failed: {e}")
            raise
    
    def get_joint_positions(self) -> Tuple[List[float], List[float]]:
        """Get current joint positions.
        
        Returns:
            Tuple of (head_joint_positions, antenna_positions)
        """
        self._check_connected()
        
        try:
            return self._robot.get_current_joint_positions()
        except Exception as e:
            self.logger.error(f"Get joint positions failed: {e}")
            raise
    
    def get_head_pose(self) -> npt.NDArray[np.float64]:
        """Get current head pose as 4x4 transformation matrix.
        
        Returns:
            4x4 numpy array representing head pose
        """
        self._check_connected()
        
        try:
            return self._robot.get_current_head_pose()
        except Exception as e:
            self.logger.error(f"Get head pose failed: {e}")
            raise
    
    def get_robot(self) -> Any:
        """Get direct access to underlying ReachyMini instance.
        
        Use this for advanced operations not covered by the wrapper.
        
        Returns:
            The underlying ReachyMini instance
            
        Raises:
            RuntimeError: If not connected
        """
        self._check_connected()
        return self._robot
