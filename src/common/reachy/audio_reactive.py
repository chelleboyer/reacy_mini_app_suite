"""Audio-reactive motion system for synchronized robot choreography.

This module provides real-time audio analysis and motion generation,
enabling the robot to move in sync with music, speech, or singing.
Adapted from the HeadWobbler pattern in reachy_mini_conversation_app.
"""

import time
import queue
import logging
import threading
from typing import Callable, Optional, Tuple
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

logger = logging.getLogger(__name__)


@dataclass
class AudioFeatures:
    """Extracted audio features for motion generation."""
    amplitude: float  # 0.0 to 1.0
    beat_strength: float  # 0.0 to 1.0
    frequency_content: float  # 0.0 to 1.0 (low to high)
    timestamp: float  # seconds since start


class AudioAnalyzer:
    """Analyzes audio chunks and extracts motion-relevant features."""
    
    def __init__(self, sample_rate: int = 24000, hop_size: int = 512):
        """Initialize the audio analyzer.
        
        Args:
            sample_rate: Audio sample rate in Hz
            hop_size: Number of samples per analysis hop
        """
        self.sample_rate = sample_rate
        self.hop_size = hop_size
        self.hop_duration = hop_size / sample_rate  # seconds per hop
        
        # Simple beat detection state
        self._energy_history = []
        self._max_history_size = 43  # ~1 second at 43 hops
        
        logger.info(f"AudioAnalyzer initialized: {sample_rate}Hz, hop={hop_size} ({self.hop_duration*1000:.1f}ms)")
    
    def analyze_chunk(self, audio_data: NDArray[np.int16], timestamp: float) -> AudioFeatures:
        """Analyze a chunk of audio and extract features.
        
        Args:
            audio_data: Audio samples as int16 array
            timestamp: Current timestamp in seconds
            
        Returns:
            AudioFeatures with extracted motion data
        """
        # Convert to float and normalize
        audio_float = audio_data.astype(np.float32) / 32768.0
        
        # Calculate RMS amplitude
        rms = np.sqrt(np.mean(audio_float ** 2))
        amplitude = float(np.clip(rms * 3.0, 0.0, 1.0))  # Scale up for visibility
        
        # Simple energy-based beat detection
        energy = float(np.sum(audio_float ** 2))
        self._energy_history.append(energy)
        if len(self._energy_history) > self._max_history_size:
            self._energy_history.pop(0)
        
        # Beat when current energy significantly exceeds recent average
        if len(self._energy_history) > 10:
            avg_energy = np.mean(self._energy_history[:-1])
            beat_strength = float(np.clip((energy - avg_energy * 1.5) / (avg_energy + 1e-6), 0.0, 1.0))
        else:
            beat_strength = 0.0
        
        # Rough frequency content (high-pass energy ratio)
        if len(audio_float) > 10:
            high_freq_energy = float(np.sum(np.diff(audio_float) ** 2))
            total_energy = energy + 1e-6
            frequency_content = float(np.clip(high_freq_energy / total_energy * 2.0, 0.0, 1.0))
        else:
            frequency_content = 0.5
        
        return AudioFeatures(
            amplitude=amplitude,
            beat_strength=beat_strength,
            frequency_content=frequency_content,
            timestamp=timestamp
        )


class AudioReactiveMotion:
    """Generates real-time head movements synchronized to audio.
    
    This class analyzes audio in real-time and produces motion offsets
    that can be applied to the robot's head to create audio-reactive behavior.
    Uses a separate thread for audio processing to maintain timing precision.
    """
    
    def __init__(
        self,
        apply_motion_callback: Callable[[Tuple[float, float, float]], None],
        sample_rate: int = 24000,
        movement_latency: float = 0.08,  # seconds
    ):
        """Initialize audio-reactive motion system.
        
        Args:
            apply_motion_callback: Function to call with (roll, pitch, yaw) offsets in degrees
            sample_rate: Audio sample rate in Hz
            movement_latency: Time between audio and motion in seconds
        """
        self.sample_rate = sample_rate
        self.movement_latency = movement_latency
        self._apply_motion = apply_motion_callback
        
        # Audio processing pipeline
        self.analyzer = AudioAnalyzer(sample_rate=sample_rate)
        self.audio_queue: "queue.Queue[Tuple[int, NDArray[np.int16], float]]" = queue.Queue()
        
        # Motion parameters - matched to conversation app for smooth movement
        self.sway_magnitude = 3.5   # degrees (gentle side-to-side like conversation app)
        self.bob_magnitude = 4.5    # degrees (subtle nods on beats)
        self.tilt_magnitude = 6.0   # degrees (gentle head turns)
        
        # Thread control
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._generation = 0
        self._base_timestamp: Optional[float] = None
        self._lock = threading.Lock()
        
        logger.info(f"AudioReactiveMotion initialized with {movement_latency*1000:.0f}ms latency")
    
    def feed_audio(self, audio_data: NDArray[np.int16], timestamp: float) -> None:
        """Feed audio data for processing (thread-safe).
        
        Args:
            audio_data: Audio samples as int16 array
            timestamp: Current playback timestamp in seconds
        """
        with self._lock:
            generation = self._generation
        self.audio_queue.put((generation, audio_data, timestamp))
    
    def start(self) -> None:
        """Start the audio processing thread."""
        if self._thread is not None and self._thread.is_alive():
            logger.warning("AudioReactiveMotion already running")
            return
        
        self._stop_event.clear()
        with self._lock:
            self._generation += 1
            self._base_timestamp = None
        
        self._thread = threading.Thread(target=self._processing_loop, daemon=True)
        self._thread.start()
        logger.info("AudioReactiveMotion started")
    
    def stop(self) -> None:
        """Stop the audio processing thread."""
        if self._thread is None:
            return
        
        self._stop_event.set()
        self._thread.join(timeout=2.0)
        
        # Clear motion offsets
        try:
            self._apply_motion((0.0, 0.0, 0.0))
        except Exception as e:
            logger.warning(f"Failed to clear motion offsets: {e}")
        
        logger.info("AudioReactiveMotion stopped")
    
    def _processing_loop(self) -> None:
        """Main processing loop running in separate thread."""
        logger.debug("Audio processing thread started")
        
        while not self._stop_event.is_set():
            try:
                generation, audio_data, timestamp = self.audio_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            
            # Check if this audio is from current generation
            with self._lock:
                if generation != self._generation:
                    continue
                if self._base_timestamp is None:
                    self._base_timestamp = timestamp
            
            # Analyze audio
            try:
                features = self.analyzer.analyze_chunk(audio_data, timestamp)
                
                # Generate motion based on features
                motion = self._generate_motion(features)
                
                # Apply motion with latency compensation
                time_to_motion = timestamp + self.movement_latency - time.time()
                if time_to_motion > 0:
                    time.sleep(time_to_motion)
                
                self._apply_motion(motion)
                
            except Exception as e:
                logger.error(f"Error processing audio: {e}")
        
        logger.debug("Audio processing thread stopped")
    
    def _generate_motion(self, features: AudioFeatures) -> Tuple[float, float, float]:
        """Generate head motion offsets from audio features.
        
        Args:
            features: Extracted audio features
            
        Returns:
            (roll, pitch, yaw) offsets in degrees
        """
        # Sway (roll) based on amplitude - gentle side-to-side
        sway_freq = 1.5  # Hz
        sway = np.sin(features.timestamp * 2 * np.pi * sway_freq) * self.sway_magnitude * features.amplitude
        
        # Bob (pitch) on beats - nod forward/back
        bob = -features.beat_strength * self.bob_magnitude
        
        # Tilt (yaw) based on frequency content - turn head slightly
        tilt_freq = 0.8  # Hz
        tilt = np.sin(features.timestamp * 2 * np.pi * tilt_freq) * self.tilt_magnitude * features.frequency_content
        
        return (float(sway), float(bob), float(tilt))
    
    def reset(self) -> None:
        """Reset the motion system (new song/audio stream)."""
        with self._lock:
            self._generation += 1
            self._base_timestamp = None
        
        # Clear queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        
        logger.info("AudioReactiveMotion reset")


class SimpleAudioReactiveController:
    """Simplified controller that applies audio-reactive motion to robot.
    
    This class handles the integration between AudioReactiveMotion and
    ReachyWrapper, managing the motion offset application.
    """
    
    def __init__(self, robot: "ReachyWrapper"):  # type: ignore
        """Initialize controller with robot instance.
        
        Args:
            robot: ReachyWrapper instance to control
        """
        self.robot = robot
        self._base_pose = {"roll": 0.0, "pitch": 0.0, "yaw": 0.0}
        self._current_offsets = (0.0, 0.0, 0.0)
        self._lock = threading.Lock()
        
        # Create motion system
        self.motion = AudioReactiveMotion(
            apply_motion_callback=self._apply_offsets,
            sample_rate=24000,
            movement_latency=0.08
        )
        
        logger.info("SimpleAudioReactiveController initialized")
    
    def _apply_offsets(self, offsets: Tuple[float, float, float]) -> None:
        """Apply motion offsets to robot (called from audio thread).
        
        Args:
            offsets: (roll, pitch, yaw) offsets in degrees
        """
        with self._lock:
            self._current_offsets = offsets
            
            # Convert degrees to radians for set_target
            roll_rad = np.radians(offsets[0])
            pitch_rad = np.radians(offsets[1])
            yaw_rad = np.radians(offsets[2])
        
        try:
            # Use set_target with offset pose (like conversation app does)
            from reachy_mini.utils import create_head_pose
            offset_pose = create_head_pose(
                x=0, y=0, z=0,
                roll=roll_rad,
                pitch=pitch_rad,
                yaw=yaw_rad,
                degrees=False,
                mm=False
            )
            self.robot._robot.set_target(head=offset_pose)
        except Exception as e:
            logger.warning(f"Failed to apply motion offsets: {e}")
    
    def set_base_pose(self, roll: float = 0.0, pitch: float = 0.0, yaw: float = 0.0) -> None:
        """Set the base pose that offsets are applied relative to.
        
        Args:
            roll, pitch, yaw: Base angles in degrees
        """
        with self._lock:
            self._base_pose = {"roll": roll, "pitch": pitch, "yaw": yaw}
        logger.debug(f"Base pose set to: roll={roll}, pitch={pitch}, yaw={yaw}")
    
    def start(self) -> None:
        """Start audio-reactive motion."""
        self.motion.start()
    
    def stop(self) -> None:
        """Stop audio-reactive motion."""
        self.motion.stop()
    
    def reset(self) -> None:
        """Reset for new audio stream."""
        self.motion.reset()
