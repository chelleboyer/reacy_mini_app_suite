#!/usr/bin/env python3
"""
Music-Reactive Dance App for Reachy Mini.

Reachy listens to music via microphone and responds with:
- Dance movements synchronized to the beat
- Emotional expressions matching the music's mood
- Sounds that complement the detected emotion

Usage:
    python -m src.apps.music-reactive.main [--host HOST] [--mock]
"""

import sys
import time
import argparse
import logging
import numpy as np
import sounddevice as sd
from collections import deque
from typing import Optional

from src.common.core.logger import setup_logger
from src.common.reachy.robot_wrapper import ReachyWrapper
from src.common.reachy.safe_motions import SafeMotionController
# Removed AudioReactiveMotion - using choreographed routines instead
from src.common.reachy.emotion_detector import EmotionDetector, EmotionGestureMapper, Emotion
from src.common.reachy.note_player import MusicalNoteGenerator

logger = logging.getLogger(__name__)


class MusicReactiveDance:
    """
    Main application for music-reactive dancing.
    
    Combines real-time audio analysis, emotion detection, and
    synchronized gesture execution.
    """
    
    def __init__(
        self, 
        mock: bool = False,
        sample_rate: Optional[int] = None,
        chunk_size: int = 2048,
        audio_device: Optional[int] = None
    ):
        """
        Initialize the music-reactive dance app.
        
        Args:
            mock: Use mock robot for testing
            sample_rate: Audio sample rate in Hz (None for device default)
            chunk_size: Audio buffer size in samples
            audio_device: Specific audio device index (None for default)
        """
        self.mock = mock
        self.audio_device = audio_device
        
        # Detect sample rate from device if not specified
        if sample_rate is None:
            import sounddevice as sd
            if audio_device is not None:
                device_info = sd.query_devices(audio_device)
                self.sample_rate = int(device_info['default_samplerate'])
                logger.info(f"Using device sample rate: {self.sample_rate} Hz")
            else:
                self.sample_rate = 16000  # Safe default for Reachy
                logger.info(f"Using default sample rate: {self.sample_rate} Hz")
        else:
            self.sample_rate = sample_rate
        
        self.chunk_size = chunk_size
        self.running = False
        
        # Audio buffer for analysis (store ~3 seconds)
        buffer_seconds = 3
        buffer_size = int(self.sample_rate * buffer_seconds / chunk_size)
        self.audio_buffer = deque(maxlen=buffer_size)
        
        # Components
        self.robot: Optional[ReachyWrapper] = None
        self.motion_controller: Optional[SafeMotionController] = None
        self.audio_reactive: Optional[AudioReactiveMotion] = None
        self.emotion_detector = EmotionDetector()
        self.gesture_mapper = EmotionGestureMapper()
        self.note_generator = MusicalNoteGenerator(sample_rate=self.sample_rate)
        
        logger.info(f"MusicReactiveDance initialized (mock={mock}, device={audio_device}, rate={self.sample_rate}Hz)")
        
        # State
        self.current_emotion = Emotion.NEUTRAL
        self.emotion_confidence = 0.0
        self.last_emotion_check = 0
        self.emotion_check_interval = 3.0  # Check emotion every 3 seconds
        self.performing_routine = False  # Flag for when performing a routine
        self.routine_count = 0  # Track number of routines performed
        self.current_tempo = 120.0  # BPM for rhythm timing
        
        logger.info(f"MusicReactiveDance initialized (mock={mock}, device={audio_device})")
    
    def setup(self):
        """Initialize robot and audio components."""
        logger.info("Setting up robot connection...")
        
        if self.mock:
            logger.info("Running in MOCK mode - no physical robot")
            self.robot = None
            self.motion_controller = None
        else:
            # Connect to robot
            self.robot = ReachyWrapper(localhost_only=True)
            try:
                self.robot.connect()
                logger.info("✅ Connected to Reachy Mini!")
            except Exception as e:
                logger.error(f"Failed to connect to robot: {e}")
                return False
            
            # Initialize motion controllers
            self.motion_controller = SafeMotionController(self.robot)
            
            # Wake up robot
            logger.info("Waking up Reachy...")
            self.robot.wake_up()
            time.sleep(1)
            
            # Initial greeting
            self.motion_controller.look_around(self.robot)
            self.motion_controller.express_curious(self.robot)
        
        logger.info("Setup complete!")
        return True
    
    def audio_callback(self, indata, frames, time_info, status):
        """
        Callback for audio stream processing.
        
        Called by sounddevice for each audio chunk.
        """
        if status:
            logger.warning(f"Audio status: {status}")
        
        # Convert to mono if stereo
        audio_chunk = indata[:, 0] if len(indata.shape) > 1 else indata
        
        # Convert float32 to int16 for processing
        audio_int16 = (audio_chunk * 32767).astype(np.int16)
        
        # Store in buffer for emotion analysis
        self.audio_buffer.append(audio_chunk.copy())
        
        # Feed audio to reactive motion system if robot connected
        if self.audio_reactive:
            try:
                timestamp = time.time()
                self.audio_reactive.feed_audio(audio_int16, timestamp)
            except Exception as e:
                logger.error(f"Error feeding audio: {e}")
    
    def analyze_emotion(self):
        """Analyze buffered audio to detect emotion."""
        if len(self.audio_buffer) == 0:
            return
        
        try:
            # Concatenate buffer into single array
            audio_data = np.concatenate(list(self.audio_buffer))
            
            # Detect emotion
            result = self.emotion_detector.detect_from_audio(audio_data, self.sample_rate)
            
            # Update current emotion and tempo
            self.current_tempo = result.tempo
            if result.emotion != self.current_emotion:
                logger.info(
                    f"Emotion: {result.emotion.value.upper()} "
                    f"(tempo: {result.tempo:.1f} BPM, energy: {result.energy:.1%})"
                )
                self.current_emotion = result.emotion
                self.emotion_confidence = result.confidence
            
            # Perform routine for current emotion (even if unchanged)
            if self.motion_controller and self.robot and not self.performing_routine:
                self._perform_mood_routine(result.emotion, result.tempo)
                
            # Display emotion info
            self._display_emotion_status(result)
            
        except Exception as e:
            logger.error(f"Error analyzing emotion: {e}")
    def _perform_mood_routine(self, emotion: Emotion, tempo: float):
        """Perform a choreographed routine matching the music's tempo and mood."""
        if not self.motion_controller or not self.robot:
            return
        
        self.performing_routine = True
        self.routine_count += 1
        
        # Calculate beat duration from BPM (60 seconds / BPM = seconds per beat)
        beat_duration = 60.0 / tempo
        # One sway cycle = 2 beats (sway right, sway left)
        sway_duration = beat_duration * 2
        
        logger.info(f"🎭 Routine #{self.routine_count}: {emotion.value.upper()} @ {tempo:.0f} BPM")
        logger.info(f"  → Swaying to the beat (every {beat_duration:.2f}s)")
        
        try:
            if emotion == Emotion.HAPPY:
                # Happy: energetic swaying with bigger magnitude
                magnitude = 12.0
                self.motion_controller.singing_sway(self.robot, duration=sway_duration, magnitude=magnitude)
                self.motion_controller.singing_sway(self.robot, duration=sway_duration, magnitude=magnitude)
                
            elif emotion == Emotion.SAD:
                # Sad: slower, smaller swaying
                magnitude = 8.0
                self.motion_controller.singing_sway(self.robot, duration=sway_duration, magnitude=magnitude)
                self.motion_controller.singing_sway(self.robot, duration=sway_duration, magnitude=magnitude)
                
            elif emotion == Emotion.ENERGETIC:
                # Energetic: fast, big swaying movements
                magnitude = 15.0
                self.motion_controller.singing_sway(self.robot, duration=sway_duration, magnitude=magnitude)
                self.motion_controller.singing_sway(self.robot, duration=sway_duration, magnitude=magnitude)
                
            else:  # NEUTRAL
                # Neutral: moderate swaying to the beat
                magnitude = 10.0
                self.motion_controller.singing_sway(self.robot, duration=sway_duration, magnitude=magnitude)
                self.motion_controller.singing_sway(self.robot, duration=sway_duration, magnitude=magnitude)
                self.motion_controller.singing_sway(self.robot, duration=2.0)
                
        except Exception as e:
            logger.error(f"Error in mood routine: {e}")
        finally:
            self.performing_routine = False
    
    def _display_emotion_status(self, result):
        """Display current emotion status."""
        print(f"\r🎵 Emotion: {result.emotion.value.upper():12} | "
              f"Confidence: {result.confidence:.2%} | "
              f"Tempo: {result.tempo:6.1f} BPM | "
              f"Energy: {result.energy:.2%} | "
              f"Valence: {result.valence:.2%}", 
              end='', flush=True)
    
    def run_gesture_cycle(self):
        """Periodically check emotion and perform routines."""
        current_time = time.time()
        
        # Check if it's time for emotion analysis
        if current_time - self.last_emotion_check >= self.emotion_check_interval:
            if not self.performing_routine:
                self.analyze_emotion()
                self.last_emotion_check = current_time
    
    def run(self):
        """Main run loop."""
        logger.info("Starting music-reactive dance...")
        logger.info("Play some music and watch Reachy react!")
        logger.info("Press Ctrl+C to stop")
        
        self.running = True
        
        try:
            # Start audio stream
            stream_kwargs = {
                'callback': self.audio_callback,
                'channels': 1,
                'samplerate': self.sample_rate,
                'device': self.audio_device,
                'blocksize': self.chunk_size
            }
            
            with sd.InputStream(**stream_kwargs):
                logger.info("🎤 Listening for music...")
                logger.info(f"   Using audio device: {sd.query_devices(self.audio_device)['name']}")
                
                # Initial curious expression
                if self.motion_controller and self.robot:
                    self.motion_controller.express_curious(self.robot)
                
                # Main loop - check for emotion periodically
                while self.running:
                    self.run_gesture_cycle()
                    time.sleep(0.1)  # Small sleep to prevent CPU spinning
                    
        except KeyboardInterrupt:
            logger.info("\n⏹️  Stopping...")
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up...")
        
        if self.motion_controller and self.robot:
            # Final bow
            try:
                self.motion_controller.singing_bashful_bow(self.robot)
                time.sleep(1)
            except:
                pass
        
        if self.robot:
            self.robot.disconnect()
        
        logger.info("Goodbye! 👋")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Music-Reactive Dance for Reachy Mini"
    )
    parser.add_argument(
        '--mock',
        action='store_true',
        help='Run in mock mode without physical robot'
    )
    parser.add_argument(
        '--device',
        type=int,
        default=None,
        help='Audio input device index (use --list-devices to see options)'
    )
    parser.add_argument(
        '--list-devices',
        action='store_true',
        help='List available audio devices and exit'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Handle --list-devices
    if args.list_devices:
        import sounddevice as sd
        print("\n🎤 Available Audio Devices:\n")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            input_mark = "✅" if device['max_input_channels'] > 0 else "  "
            print(f"{input_mark} {i}: {device['name']}")
            print(f"      Input channels: {device['max_input_channels']}, "
                  f"Output channels: {device['max_output_channels']}")
        print("\nUse --device <number> to select a specific device\n")
        return 0
    
    # Setup logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logger(__name__, level=log_level)
    
    # Create and run app
    app = MusicReactiveDance(mock=args.mock, audio_device=args.device)
    
    if not app.setup():
        logger.error("Setup failed!")
        return 1
    
    try:
        app.run()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
