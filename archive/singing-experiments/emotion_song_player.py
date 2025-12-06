"""Emotion-based song player using Reachy's own sounds.

Uses Reachy Mini's emotion library sounds (WAV files) to create
melodies by playing different emotion sounds at specific timings.
"""

import logging
import os
from dataclasses import dataclass
from typing import List, Tuple

import numpy.typing as npt
import sounddevice as sd
import soundfile as sf
from reachy_mini.motion.recorded_move import RecordedMoves

from ..core import setup_logger


logger = setup_logger(__name__)


@dataclass
class EmotionNote:
    """A note in an emotion-based song."""
    emotion_sound: str  # Name of emotion sound (e.g., "dance2", "cheerful1")
    start_time: float   # When to start playing (seconds)
    duration: float     # How long to play (seconds)


class EmotionSongPlayer:
    """Play songs using Reachy's emotion library sounds."""
    
    def __init__(self):
        """Initialize emotion song player."""
        logger.info("Loading emotion library for singing...")
        self._emotion_moves = RecordedMoves('pollen-robotics/reachy-mini-emotions-library')
        logger.info("Emotion library loaded")
    
    def create_twinkle_twinkle(self) -> Tuple[List[EmotionNote], float]:
        """Create Twinkle Twinkle Little Star using dance2 sound at different pitches.
        
        Uses the melodic dance2 sound (Bee Gees) and pitch-shifts it
        to create different musical notes with longer, flowing segments.
        
        Returns:
            Tuple of (note_sequence, total_duration)
        """
        # Use dance2 as the base - it has nice melodic qualities
        base_sound = "dance2"
        
        # Map musical notes to pitch shifts relative to C4 (base pitch = 1.0)
        # Using equal temperament intervals
        pitch_map = {
            "C4": 1.0,      # Base (261.63 Hz)
            "D4": 1.122,    # Major second (293.66 Hz)
            "E4": 1.260,    # Major third (329.63 Hz)
            "F4": 1.335,    # Perfect fourth (349.23 Hz)
            "G4": 1.498,    # Perfect fifth (392.00 Hz)
            "A4": 1.682,    # Major sixth (440.00 Hz)
        }
        
        # Twinkle Twinkle note sequence with longer durations for melodic flow
        # "Twinkle twinkle little star"
        melody = [
            ("C4", 0.0, 0.8),   # Twin-
            ("C4", 0.9, 0.8),   # kle
            ("G4", 1.8, 0.8),   # twin-
            ("G4", 2.7, 0.8),   # kle
            ("A4", 3.6, 0.8),   # lit-
            ("A4", 4.5, 0.8),   # tle
            ("G4", 5.4, 1.5),   # star
            
            # "How I wonder what you are"
            ("F4", 7.2, 0.8),   # How
            ("F4", 8.1, 0.8),   # I
            ("E4", 9.0, 0.8),   # won-
            ("E4", 9.9, 0.8),   # der
            ("D4", 10.8, 0.8),  # what
            ("D4", 11.7, 0.8),  # you
            ("C4", 12.6, 1.5),  # are
            
            # "Up above the world so high"
            ("G4", 14.4, 0.8),  # Up
            ("G4", 15.3, 0.8),  # a-
            ("F4", 16.2, 0.8),  # bove
            ("F4", 17.1, 0.8),  # the
            ("E4", 18.0, 0.8),  # world
            ("E4", 18.9, 0.8),  # so
            ("D4", 19.8, 1.5),  # high
            
            # "Like a diamond in the sky"
            ("G4", 21.6, 0.8),  # Like
            ("G4", 22.5, 0.8),  # a
            ("F4", 23.4, 0.8),  # dia-
            ("F4", 24.3, 0.8),  # mond
            ("E4", 25.2, 0.8),  # in
            ("E4", 26.1, 0.8),  # the
            ("D4", 27.0, 1.5),  # sky
        ]
        
        # Convert to EmotionNotes with pitch information stored in emotion_sound field
        notes = []
        for note_name, start_time, duration in melody:
            pitch_shift = pitch_map[note_name]
            # Store pitch shift info by encoding it: "base_sound:pitch"
            emotion_with_pitch = f"{base_sound}:{pitch_shift:.3f}"
            notes.append(EmotionNote(emotion_with_pitch, start_time, duration))
        
        total_duration = melody[-1][1] + melody[-1][2] + 0.5
        
        return notes, total_duration
    
    def create_happy_birthday(self) -> Tuple[List[EmotionNote], float]:
        """Create Happy Birthday using emotion sounds.
        
        Returns:
            Tuple of (note_sequence, total_duration)
        """
        notes = [
            # "Happy birthday to you" (first)
            EmotionNote("cheerful1", 0.0, 0.5),
            EmotionNote("cheerful1", 0.6, 0.5),
            EmotionNote("enthusiastic1", 1.2, 0.7),
            EmotionNote("happy1", 2.0, 1.0),
            
            # "Happy birthday to you" (second)
            EmotionNote("cheerful1", 3.2, 0.5),
            EmotionNote("cheerful1", 3.8, 0.5),
            EmotionNote("enthusiastic2", 4.4, 0.7),
            EmotionNote("happy2", 5.2, 1.0),
            
            # "Happy birthday dear friend"
            EmotionNote("cheerful1", 6.4, 0.5),
            EmotionNote("cheerful1", 7.0, 0.5),
            EmotionNote("enthusiastic1", 7.6, 0.5),
            EmotionNote("grateful1", 8.2, 0.5),
            EmotionNote("happy1", 8.8, 1.0),
            
            # "Happy birthday to you" (final)
            EmotionNote("cheerful2", 10.0, 0.5),
            EmotionNote("cheerful2", 10.6, 0.5),
            EmotionNote("enthusiastic1", 11.2, 0.7),
            EmotionNote("happy1", 12.0, 1.5),
        ]
        
        total_duration = notes[-1].start_time + notes[-1].duration + 0.5
        
        return notes, total_duration
    
    def get_audio_data(self, emotion_sound: str) -> Tuple[npt.NDArray, int]:
        """Load audio data for an emotion sound.
        
        Args:
            emotion_sound: Name of emotion sound (e.g., "dance2")
            
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        audio_file = os.path.join(self._emotion_moves.local_path, f"{emotion_sound}.wav")
        if not os.path.exists(audio_file):
            logger.warning(f"Audio file not found: {audio_file}")
            return None, None
        
        audio_data, sample_rate = sf.read(audio_file)
        return audio_data, sample_rate
    
    def play_emotion_note(self, emotion_sound: str, duration: float = None, pitch_shift: float = 1.0):
        """Play an emotion sound for a specific duration at a specific pitch.
        
        Args:
            emotion_sound: Name of emotion sound
            duration: How long to play (None = full sound)
            pitch_shift: Pitch multiplier (1.0 = original, 2.0 = octave up, 0.5 = octave down)
        """
        audio_data, sample_rate = self.get_audio_data(emotion_sound)
        
        if audio_data is None:
            return
        
        # Truncate to duration if specified
        if duration is not None:
            max_samples = int(duration * sample_rate)
            if len(audio_data) > max_samples:
                audio_data = audio_data[:max_samples]
        
        # Play with pitch shift by adjusting sample rate
        # Higher sample rate = higher pitch
        playback_rate = int(sample_rate * pitch_shift)
        sd.play(audio_data, samplerate=playback_rate, blocking=False)
        logger.debug(f"Playing emotion sound: {emotion_sound} (duration={duration}s, pitch={pitch_shift:.2f}x)")
