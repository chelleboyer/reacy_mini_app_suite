"""Audio playback with precise timestamp tracking for synchronization.

Provides audio playback with real-time timestamp feedback for coordinating
choreography and audio-reactive motion.
"""

import time
import wave
import logging
import threading
from typing import Optional, Callable
from pathlib import Path
import io

import numpy as np
from numpy.typing import NDArray

logger = logging.getLogger(__name__)


# Try to import sounddevice (optional dependency)
try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False
    logger.warning("sounddevice not available - audio playback disabled")


class AudioPlayer:
    """Synchronized audio player with timestamp tracking.
    
    Plays audio while providing precise timestamp information for
    coordinating choreography and audio-reactive motion.
    """
    
    def __init__(
        self,
        sample_rate: int = 24000,
        audio_callback: Optional[Callable[[NDArray[np.int16], float], None]] = None
    ):
        """Initialize audio player.
        
        Args:
            sample_rate: Audio sample rate in Hz
            audio_callback: Optional callback for audio chunks: callback(audio_data, timestamp)
        """
        self.sample_rate = sample_rate
        self.audio_callback = audio_callback
        
        self._audio_data: Optional[NDArray[np.int16]] = None
        self._duration: float = 0.0
        self._playing = False
        self._start_time: Optional[float] = None
        self._playback_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        if not SOUNDDEVICE_AVAILABLE:
            logger.warning("Audio playback unavailable - sounddevice not installed")
        
        logger.info(f"AudioPlayer initialized ({sample_rate}Hz)")
    
    def load_audio(self, audio_data: NDArray[np.int16], sample_rate: int) -> None:
        """Load audio data for playback.
        
        Args:
            audio_data: Audio samples as int16 array
            sample_rate: Sample rate of the audio
        """
        if sample_rate != self.sample_rate:
            logger.warning(f"Sample rate mismatch: {sample_rate} != {self.sample_rate}")
            # In production, we'd resample here
        
        self._audio_data = audio_data
        self._duration = len(audio_data) / sample_rate
        logger.info(f"Loaded audio: {len(audio_data)} samples ({self._duration:.2f}s)")
    
    def load_from_wav(self, wav_path: Path) -> None:
        """Load audio from WAV file.
        
        Args:
            wav_path: Path to WAV file
        """
        logger.info(f"Loading WAV file: {wav_path}")
        
        with wave.open(str(wav_path), 'rb') as wav_file:
            sample_rate = wav_file.getframerate()
            num_frames = wav_file.getnframes()
            audio_bytes = wav_file.readframes(num_frames)
            
            # Convert to numpy array
            audio_data = np.frombuffer(audio_bytes, dtype=np.int16)
            
            # Handle stereo -> mono
            if wav_file.getnchannels() == 2:
                audio_data = audio_data.reshape(-1, 2).mean(axis=1).astype(np.int16)
                logger.debug("Converted stereo to mono")
            
            self.load_audio(audio_data, sample_rate)
    
    def play(self, blocking: bool = False) -> None:
        """Start audio playback.
        
        Args:
            blocking: If True, block until playback completes
        """
        if self._audio_data is None:
            logger.error("No audio loaded")
            return
        
        if not SOUNDDEVICE_AVAILABLE:
            logger.warning("Simulating playback (sounddevice not available)")
            self._simulate_playback()
            return
        
        if self._playing:
            logger.warning("Already playing")
            return
        
        self._playing = True
        self._stop_event.clear()
        
        if blocking:
            self._playback_loop()
        else:
            self._playback_thread = threading.Thread(target=self._playback_loop, daemon=True)
            self._playback_thread.start()
    
    def stop(self) -> None:
        """Stop audio playback."""
        if not self._playing:
            return
        
        self._stop_event.set()
        self._playing = False
        
        if self._playback_thread is not None:
            self._playback_thread.join(timeout=1.0)
        
        logger.info("Playback stopped")
    
    def get_current_time(self) -> float:
        """Get current playback time in seconds.
        
        Returns:
            Current timestamp (0.0 if not playing)
        """
        if not self._playing or self._start_time is None:
            return 0.0
        return time.time() - self._start_time
    
    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        return self._playing
    
    def _playback_loop(self) -> None:
        """Main playback loop."""
        if self._audio_data is None:
            return
        
        logger.info("Starting playback")
        self._start_time = time.time()
        
        # Chunk size for callbacks (update every ~50ms)
        chunk_size = int(self.sample_rate * 0.05)  # 50ms chunks
        
        try:
            # Play using sounddevice
            with sd.OutputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype='int16',
                blocksize=chunk_size
            ) as stream:
                
                offset = 0
                while offset < len(self._audio_data) and not self._stop_event.is_set():
                    # Get chunk
                    chunk_end = min(offset + chunk_size, len(self._audio_data))
                    chunk = self._audio_data[offset:chunk_end]
                    
                    # Pad if needed
                    if len(chunk) < chunk_size:
                        chunk = np.pad(chunk, (0, chunk_size - len(chunk)))
                    
                    # Send to audio callback if provided
                    if self.audio_callback is not None:
                        try:
                            current_time = self.get_current_time()
                            self.audio_callback(chunk, current_time)
                        except Exception as e:
                            logger.error(f"Audio callback error: {e}")
                    
                    # Write to audio stream
                    stream.write(chunk.reshape(-1, 1))
                    
                    offset += chunk_size
        
        except Exception as e:
            logger.error(f"Playback error: {e}")
        
        finally:
            self._playing = False
            logger.info("Playback finished")
    
    def _simulate_playback(self) -> None:
        """Simulate playback when sounddevice is not available."""
        if self._audio_data is None:
            return
        
        logger.info("Simulating playback (no audio output)")
        self._start_time = time.time()
        self._playing = True
        
        chunk_size = int(self.sample_rate * 0.05)  # 50ms chunks
        offset = 0
        
        while offset < len(self._audio_data) and not self._stop_event.is_set():
            chunk_end = min(offset + chunk_size, len(self._audio_data))
            chunk = self._audio_data[offset:chunk_end]
            
            # Send to audio callback if provided
            if self.audio_callback is not None:
                try:
                    current_time = self.get_current_time()
                    self.audio_callback(chunk, current_time)
                except Exception as e:
                    logger.error(f"Audio callback error: {e}")
            
            # Simulate playback timing
            time.sleep(len(chunk) / self.sample_rate)
            offset += chunk_size
        
        self._playing = False
        logger.info("Simulated playback finished")
