"""Choreography engine for synchronized singing performances.

Coordinates gestures, audio-reactive motion, and timing markers
to create dynamic singing performances.
"""

import time
import logging
import threading
import os
from typing import List, Callable, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

import sounddevice as sd
import soundfile as sf

from .tts_engine import TTSResult, TimingMarker
from .safe_motions import SafeMotionController

try:
    from reachy_mini.motion.recorded_move import RecordedMoves
    RECORDED_MOVES_AVAILABLE = True
except ImportError:
    RECORDED_MOVES_AVAILABLE = False

logger = logging.getLogger(__name__)


class GestureType(Enum):
    """Types of gestures for choreography."""
    SWAY = "sway"
    LEAN_FORWARD = "lean_forward"
    DRAMATIC_PAUSE = "dramatic_pause"
    BIG_FINISH = "big_finish"
    BASHFUL_BOW = "bashful_bow"
    NOD = "nod"
    WAVE_ANTENNAS = "wave_antennas"
    EXPRESS_HAPPY = "express_happy"
    EXPRESS_EXCITED = "express_excited"


@dataclass
class ChoreographyEvent:
    """A timed choreography event."""
    timestamp: float  # seconds from start
    gesture_type: GestureType
    parameters: Dict[str, Any]  # gesture-specific parameters
    builtin_move: Optional[str] = None  # Name of built-in emotion library move to play


class ChoreographyEngine:
    """Manages timed gestures synchronized with audio.
    
    This engine runs gestures at specific timestamps, coordinating with
    audio playback to create choreographed performances.
    """
    
    def __init__(self, robot: "ReachyWrapper", controller: SafeMotionController):  # type: ignore
        """Initialize choreography engine.
        
        Args:
            robot: ReachyWrapper instance to control
            controller: SafeMotionController for gesture execution
        """
        self.robot = robot
        self.controller = controller
        
        self._events: List[ChoreographyEvent] = []
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._start_time: Optional[float] = None
        
        # Load emotion library for built-in moves
        self._emotion_moves: Optional["RecordedMoves"] = None
        if RECORDED_MOVES_AVAILABLE:
            try:
                self._emotion_moves = RecordedMoves("pollen-robotics/reachy-mini-emotions-library")
                logger.info(f"Loaded {len(self._emotion_moves.list_moves())} built-in emotion moves")
            except Exception as e:
                logger.warning(f"Could not load emotion moves: {e}")
        
        logger.info("ChoreographyEngine initialized")
    
    def add_event(
        self,
        timestamp: float,
        gesture_type: GestureType,
        builtin_move: Optional[str] = None,
        **parameters: Any
    ) -> None:
        """Add a choreography event.
        
        Args:
            timestamp: Time in seconds when gesture should start
            gesture_type: Type of gesture to perform
            builtin_move: Optional name of built-in emotion library move
            **parameters: Gesture-specific parameters
        """
        event = ChoreographyEvent(
            timestamp=timestamp,
            gesture_type=gesture_type,
            parameters=parameters,
            builtin_move=builtin_move
        )
        self._events.append(event)
        logger.debug(f"Added event: {gesture_type.value} at {timestamp:.2f}s")
    
    def clear_events(self) -> None:
        """Clear all choreography events."""
        self._events.clear()
        logger.debug("Cleared all choreography events")
    
    def generate_from_tts(
        self,
        tts_result: TTSResult,
        style: str = "default"
    ) -> None:
        """Generate choreography automatically from TTS timing markers.
        
        Args:
            tts_result: TTS result with timing markers
            style: Choreography style ("default", "energetic", "dramatic")
        """
        logger.info(f"Generating choreography in '{style}' style")
        self.clear_events()
        
        duration = tts_result.duration
        word_markers = [m for m in tts_result.timing_markers if m.marker_type == "word"]
        beat_markers = [m for m in tts_result.timing_markers if m.marker_type == "beat"]
        
        if style == "energetic":
            # High energy - lots of movement
            # Nod on beats
            for beat in beat_markers:
                self.add_event(beat.start_time, GestureType.NOD, count=1, speed=1.5)
            
            # Wave antennas periodically
            for i in range(int(duration / 3)):
                timestamp = i * 3.0 + 1.0
                if timestamp < duration - 1.0:
                    self.add_event(
                        timestamp,
                        GestureType.WAVE_ANTENNAS,
                        count=2,
                        speed=1.5,
                        synchronized=True
                    )
            
            # Big finish at end
            if duration > 2.0:
                self.add_event(duration - 0.5, GestureType.BIG_FINISH)
        
        elif style == "dramatic":
            # Dramatic style - emphasis on key moments
            # Dramatic pauses between phrases
            phrase_breaks = [m for m in word_markers if m.start_time > 0 and m.start_time % 3.0 < 0.5]
            for marker in phrase_breaks[:3]:  # Limit to 3 dramatic pauses
                if marker.start_time > 1.0:
                    self.add_event(marker.start_time - 0.3, GestureType.DRAMATIC_PAUSE, duration=0.8)
            
            # Lean forward at midpoint (climax)
            if duration > 4.0:
                self.add_event(duration / 2, GestureType.LEAN_FORWARD, duration=1.2, intensity=0.9)
            
            # Big finish
            if duration > 2.0:
                self.add_event(duration - 0.5, GestureType.BIG_FINISH)
        
        else:  # default style - USE BUILT-IN MOVES!
            # Use Reachy's built-in emotion library for smooth, professional movements
            # These are pre-recorded moves that play beautifully
            
            # Start with cheerful/welcoming moves
            if duration > 2.0:
                self.add_event(0.5, GestureType.EXPRESS_HAPPY)  # Start happy
            
            # Gentle dance moves throughout
            dance_moves = ["dance1", "dance2", "dance3"]
            num_dances = min(3, int(duration / 10))  # One dance every ~10 seconds
            for i in range(num_dances):
                timestamp = i * 10.0 + 2.0
                if timestamp < duration - 3.0:
                    move_name = dance_moves[i % len(dance_moves)]
                    self.add_event(
                        timestamp,
                        GestureType.SWAY,  # We'll intercept this to play built-in move
                        duration=2.5,
                        magnitude=0.0,  # Signal to use built-in move
                        builtin_move=move_name
                    )
            
            # End with shy bow
            if duration > 2.0:
                self.add_event(duration - 1.0, GestureType.BASHFUL_BOW)
        
        # Sort events by timestamp
        self._events.sort(key=lambda e: e.timestamp)
        logger.info(f"Generated {len(self._events)} choreography events")
    
    def start(self, start_time: Optional[float] = None) -> None:
        """Start executing choreography.
        
        Args:
            start_time: Reference time (default: current time)
        """
        if self._thread is not None and self._thread.is_alive():
            logger.warning("Choreography already running")
            return
        
        self._stop_event.clear()
        self._start_time = start_time or time.time()
        
        self._thread = threading.Thread(target=self._execution_loop, daemon=True)
        self._thread.start()
        logger.info("Choreography started")
    
    def stop(self) -> None:
        """Stop choreography execution."""
        if self._thread is None:
            return
        
        self._stop_event.set()
        self._thread.join(timeout=2.0)
        logger.info("Choreography stopped")
    
    def _execution_loop(self) -> None:
        """Main execution loop (runs in separate thread)."""
        if self._start_time is None:
            logger.error("Start time not set")
            return
        
        event_index = 0
        logger.debug(f"Choreography loop started with {len(self._events)} events")
        
        while not self._stop_event.is_set() and event_index < len(self._events):
            event = self._events[event_index]
            
            # Calculate time until event
            current_time = time.time() - self._start_time
            time_until_event = event.timestamp - current_time
            
            if time_until_event > 0:
                # Wait until event time (with early exit check)
                if self._stop_event.wait(timeout=min(time_until_event, 0.1)):
                    break
                continue
            
            # Execute gesture (non-blocking - gestures run in separate thread/direct control)
            try:
                self._execute_gesture(event)
            except Exception as e:
                logger.error(f"Error executing gesture {event.gesture_type}: {e}")
            
            event_index += 1
        
        logger.debug("Choreography loop finished")
    
    def _execute_gesture(self, event: ChoreographyEvent) -> None:
        """Execute a choreography event.
        
        Args:
            event: Event to execute
        """
        gesture_type = event.gesture_type
        params = event.parameters
        builtin_move = event.builtin_move
        
        logger.debug(f"Executing: {gesture_type.value} with params {params}")
        
        # If this event specifies a built-in move, play it!
        if builtin_move and params.get("magnitude", 1.0) == 0.0:
            logger.info(f"Playing built-in move: {builtin_move}")
            threading.Thread(
                target=self._play_builtin_move,
                args=(builtin_move,),
                daemon=True
            ).start()
            return
        
        # Map gesture types to controller methods (non-blocking execution)
        # Note: These gestures block internally with time.sleep - in production,
        # we'd need fully async gesture system for true parallelism
        
        if gesture_type == GestureType.SWAY:
            threading.Thread(
                target=self.controller.singing_sway,
                args=(self.robot,),
                kwargs=params,
                daemon=True
            ).start()
        
        elif gesture_type == GestureType.LEAN_FORWARD:
            threading.Thread(
                target=self.controller.singing_lean_forward,
                args=(self.robot,),
                kwargs=params,
                daemon=True
            ).start()
        
        elif gesture_type == GestureType.DRAMATIC_PAUSE:
            threading.Thread(
                target=self.controller.singing_dramatic_pause,
                args=(self.robot,),
                kwargs=params,
                daemon=True
            ).start()
        
        elif gesture_type == GestureType.BIG_FINISH:
            threading.Thread(
                target=self.controller.singing_big_finish,
                args=(self.robot,),
                daemon=True
            ).start()
        
        elif gesture_type == GestureType.BASHFUL_BOW:
            threading.Thread(
                target=self.controller.singing_bashful_bow,
                args=(self.robot,),
                daemon=True
            ).start()
        
        elif gesture_type == GestureType.NOD:
            threading.Thread(
                target=self.controller.nod_yes,
                args=(self.robot,),
                kwargs=params,
                daemon=True
            ).start()
        
        elif gesture_type == GestureType.WAVE_ANTENNAS:
            threading.Thread(
                target=self.controller.wave_antennas,
                args=(self.robot,),
                kwargs=params,
                daemon=True
            ).start()
        
        elif gesture_type == GestureType.EXPRESS_HAPPY:
            threading.Thread(
                target=self.controller.express_happy,
                args=(self.robot,),
                daemon=True
            ).start()
        
        elif gesture_type == GestureType.EXPRESS_EXCITED:
            threading.Thread(
                target=self.controller.express_excited,
                args=(self.robot,),
                daemon=True
            ).start()
        
        else:
            logger.warning(f"Unknown gesture type: {gesture_type}")
    
    def _play_builtin_move(self, move_name: str) -> None:
        """Play a built-in emotion library move with its audio.
        
        Args:
            move_name: Name of the move from emotion library
        """
        if not self._emotion_moves:
            logger.warning("Emotion moves not loaded")
            return
        
        try:
            move = self._emotion_moves.get(move_name)
            logger.info(f"Playing built-in move '{move_name}' (duration: {move.duration:.1f}s)")
            
            # Play the corresponding audio file if it exists
            audio_file = os.path.join(self._emotion_moves.local_path, f"{move_name}.wav")
            if os.path.exists(audio_file):
                try:
                    logger.info(f"Playing emotion sound: {move_name}.wav")
                    # Load and play audio using sounddevice (non-blocking)
                    audio_data, sample_rate = sf.read(audio_file)
                    sd.play(audio_data, samplerate=sample_rate, blocking=False)
                except Exception as e:
                    logger.warning(f"Could not play sound for '{move_name}': {e}")
            
            # Play the move using robot's play_move() method
            self.robot._robot.play_move(move, initial_goto_duration=0.5)
            
        except Exception as e:
            logger.error(f"Failed to play built-in move '{move_name}': {e}")
