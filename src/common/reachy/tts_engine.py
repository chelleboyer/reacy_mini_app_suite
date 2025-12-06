"""Text-to-Speech engine with multiple backend support.

Provides a unified interface for generating speech audio with timing information
for synchronized choreography.
"""

import io
import time
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Literal
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from .note_player import MusicalSongPlayer, NoteResult

logger = logging.getLogger(__name__)


@dataclass
class TimingMarker:
    """Timing marker for word or phoneme boundaries."""
    text: str
    start_time: float  # seconds
    end_time: float    # seconds
    marker_type: Literal["word", "phoneme", "sentence", "beat"]


@dataclass
class TTSResult:
    """Result from TTS generation."""
    audio_data: NDArray[np.int16]  # Audio samples
    sample_rate: int               # Sample rate in Hz
    duration: float                # Total duration in seconds
    timing_markers: List[TimingMarker]  # Word/phoneme boundaries


class TTSEngine:
    """Abstract base class for TTS engines."""
    
    def generate(self, text: str, **kwargs: Any) -> TTSResult:
        """Generate speech from text.
        
        Args:
            text: Text to synthesize
            **kwargs: Engine-specific parameters
            
        Returns:
            TTSResult with audio and timing data
        """
        raise NotImplementedError


class MockTTSEngine(TTSEngine):
    """Mock TTS engine for testing without external dependencies.
    
    Generates simple sine wave audio with approximate timing markers.
    """
    
    def __init__(self, sample_rate: int = 24000):
        """Initialize mock TTS engine.
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        logger.info("MockTTSEngine initialized")
    
    def generate(self, text: str, voice_speed: float = 1.0, **kwargs: Any) -> TTSResult:
        """Generate mock speech audio.
        
        Args:
            text: Text to synthesize
            voice_speed: Speaking speed multiplier
            **kwargs: Ignored
            
        Returns:
            TTSResult with sine wave audio and word timing
        """
        logger.info(f"Generating mock TTS for: '{text}' (speed={voice_speed})")
        
        # Split into words
        words = text.split()
        
        # Estimate timing (rough approximation)
        chars_per_second = 15.0 * voice_speed  # typical speaking rate
        
        # Generate timing markers
        timing_markers = []
        current_time = 0.0
        
        for word in words:
            # Estimate word duration based on character count
            word_duration = len(word) / chars_per_second + 0.1  # +0.1 for pause
            
            timing_markers.append(TimingMarker(
                text=word,
                start_time=current_time,
                end_time=current_time + word_duration,
                marker_type="word"
            ))
            
            current_time += word_duration
        
        total_duration = current_time
        
        # Generate simple audio (sine wave with varying frequency)
        num_samples = int(total_duration * self.sample_rate)
        t = np.linspace(0, total_duration, num_samples)
        
        # Modulate frequency slightly to simulate speech intonation
        base_freq = 200  # Hz
        freq_modulation = 50 * np.sin(2 * np.pi * 2 * t)  # Vary ±50Hz
        frequency = base_freq + freq_modulation
        
        # Generate audio with amplitude envelope
        audio = np.sin(2 * np.pi * frequency * t)
        
        # Apply amplitude envelope (start/end fade, word emphasis)
        envelope = np.ones_like(audio)
        
        # Fade in/out
        fade_samples = int(0.05 * self.sample_rate)  # 50ms fade
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        
        # Add word emphasis
        for marker in timing_markers:
            start_idx = int(marker.start_time * self.sample_rate)
            end_idx = int(marker.end_time * self.sample_rate)
            if end_idx <= len(envelope):
                # Slight amplitude boost at word boundaries
                envelope[start_idx:min(start_idx + fade_samples, end_idx)] *= 1.2
        
        audio = audio * envelope * 0.5  # Scale to reasonable amplitude
        
        # Convert to int16
        audio_int16 = (audio * 32767).astype(np.int16)
        
        # Add beat markers (every ~0.5 seconds for rhythm)
        beat_interval = 0.5
        beat_time = beat_interval
        while beat_time < total_duration:
            timing_markers.append(TimingMarker(
                text="<beat>",
                start_time=beat_time,
                end_time=beat_time,
                marker_type="beat"
            ))
            beat_time += beat_interval
        
        # Sort markers by time
        timing_markers.sort(key=lambda m: m.start_time)
        
        logger.info(f"Generated {len(audio_int16)} samples ({total_duration:.2f}s) with {len([m for m in timing_markers if m.marker_type == 'word'])} words")
        
        return TTSResult(
            audio_data=audio_int16,
            sample_rate=self.sample_rate,
            duration=total_duration,
            timing_markers=timing_markers
        )


class OpenAITTSEngine(TTSEngine):
    """OpenAI TTS engine (requires API key).
    
    Note: This is a stub - requires openai package and API key setup.
    Will be implemented when API key is available.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "tts-1", voice: str = "alloy"):
        """Initialize OpenAI TTS engine.
        
        Args:
            api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            model: TTS model to use
            voice: Voice selection
        """
        self.api_key = api_key
        self.model = model
        self.voice = voice
        logger.warning("OpenAITTSEngine is a stub - not yet implemented")
    
    def generate(self, text: str, **kwargs: Any) -> TTSResult:
        """Generate speech using OpenAI TTS.
        
        Note: Currently raises NotImplementedError.
        """
        raise NotImplementedError("OpenAI TTS integration not yet implemented - use MockTTSEngine for testing")


class MusicalTTSEngine(TTSEngine):
    """Musical note TTS engine for singing.
    
    Generates musical notes instead of speech, perfect for making Reachy sing!
    """
    
    def __init__(self, sample_rate: int = 24000):
        """Initialize musical TTS engine.
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.song_player = MusicalSongPlayer(sample_rate)
        logger.info("MusicalTTSEngine initialized - ready to sing!")
    
    def generate(
        self,
        text: str,
        song: str = "twinkle",
        tempo: float = 120.0,
        **kwargs: Any
    ) -> TTSResult:
        """Generate musical notes for a song.
        
        Args:
            text: Song text (for display/logging only)
            song: Song to play ("twinkle", "happy_birthday")
            tempo: Tempo in BPM
            **kwargs: Ignored
            
        Returns:
            TTSResult with musical note audio and timing
        """
        logger.info(f"Generating musical notes for '{song}' at {tempo} BPM")
        
        # Generate note sequence based on song
        if song == "twinkle":
            note_result = self.song_player.play_twinkle_twinkle(tempo)
        elif song == "happy_birthday":
            note_result = self.song_player.play_happy_birthday(tempo)
        else:
            logger.warning(f"Unknown song '{song}', defaulting to Twinkle Twinkle")
            note_result = self.song_player.play_twinkle_twinkle(tempo)
        
        # Convert note timings to timing markers
        timing_markers = []
        for note_name, start_time, end_time in note_result.note_timings:
            timing_markers.append(TimingMarker(
                text=note_name,
                start_time=start_time,
                end_time=end_time,
                marker_type="beat"
            ))
        
        logger.info(f"Generated {len(timing_markers)} notes, duration: {note_result.duration:.2f}s")
        
        return TTSResult(
            audio_data=note_result.audio_data,
            sample_rate=note_result.sample_rate,
            duration=note_result.duration,
            timing_markers=timing_markers
        )


class EmotionTTSEngine(TTSEngine):
    """Emotion-based TTS engine using Reachy's own sounds.
    
    Uses Reachy Mini's emotion library sounds to "sing" songs
    with the robot's natural vocalizations.
    """
    
    def __init__(self):
        """Initialize emotion TTS engine."""
        from .emotion_song_player import EmotionSongPlayer
        self.song_player = EmotionSongPlayer()
        logger.info("EmotionTTSEngine initialized - ready to sing with emotion sounds!")
    
    def generate(
        self,
        text: str,
        song: str = "twinkle",
        **kwargs: Any
    ) -> TTSResult:
        """Generate emotion-based singing audio.
        
        Args:
            text: Song text (ignored, just for display)
            song: Song to sing ("twinkle" or "birthday")
            **kwargs: Additional parameters
            
        Returns:
            TTSResult with emotion sound sequence
        """
        from .emotion_song_player import EmotionNote
        import time
        
        # Get song notes
        if song == "twinkle":
            notes, total_duration = self.song_player.create_twinkle_twinkle()
        elif song == "birthday":
            notes, total_duration = self.song_player.create_happy_birthday()
        else:
            raise ValueError(f"Unknown song: {song}")
        
        logger.info(f"Generating emotion song '{song}': {len(notes)} emotion sounds, {total_duration:.1f}s")
        
        # Create timing markers for choreography synchronization
        timing_markers = []
        for i, note in enumerate(notes):
            duration = note.duration if note.duration is not None else total_duration
            timing_markers.append(TimingMarker(
                text=f"note_{i}",
                start_time=note.start_time,
                end_time=note.start_time + duration,
                marker_type="beat"
            ))
        
        # Store notes for playback
        self._current_notes = notes
        self._total_duration = total_duration
        
        # Return empty audio (we'll play sounds live during performance)
        sample_rate = 24000
        silent_audio = np.zeros(int(total_duration * sample_rate), dtype=np.float32)
        
        logger.info(f"Emotion song ready: {len(notes)} sounds over {total_duration:.1f}s")
        
        return TTSResult(
            audio_data=silent_audio,
            sample_rate=sample_rate,
            duration=total_duration,
            timing_markers=timing_markers
        )
    
    def play_song(self, start_time: float):
        """Play the emotion sounds in a background thread.
        
        Args:
            start_time: Performance start time from time.time()
        """
        import threading
        import time
        
        def play_notes():
            for note in self._current_notes:
                # Wait until it's time for this note
                target_time = start_time + note.start_time
                wait_time = target_time - time.time()
                if wait_time > 0:
                    time.sleep(wait_time)
                
                # Parse emotion sound and pitch
                if ':' in note.emotion_sound:
                    # Format: "emotion:pitch_shift"
                    emotion, pitch_str = note.emotion_sound.split(':')
                    pitch_shift = float(pitch_str)
                else:
                    emotion = note.emotion_sound
                    pitch_shift = 1.0
                
                # Play the emotion sound with pitch shift
                self.song_player.play_emotion_note(emotion, note.duration, pitch_shift)
        
        thread = threading.Thread(target=play_notes, daemon=True)
        thread.start()
        logger.info("Started emotion sound playback thread")


def create_tts_engine(
    engine_type: Literal["mock", "openai", "musical", "emotion"] = "mock",
    **kwargs: Any
) -> TTSEngine:
    """Factory function to create TTS engine.
    
    Args:
        engine_type: Type of engine to create
        **kwargs: Engine-specific parameters
        
    Returns:
        TTSEngine instance
    """
    if engine_type == "mock":
        return MockTTSEngine(**kwargs)
    elif engine_type == "openai":
        return OpenAITTSEngine(**kwargs)
    elif engine_type == "musical":
        return MusicalTTSEngine(**kwargs)
    elif engine_type == "emotion":
        return EmotionTTSEngine(**kwargs)
    else:
        raise ValueError(f"Unknown engine type: {engine_type}")
