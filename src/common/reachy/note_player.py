"""Musical note generation and playback for Reachy Mini.

This module generates simple musical notes as audio waveforms and provides
a way to play sequences of notes for songs like Twinkle Twinkle Little Star.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import numpy as np
import numpy.typing as npt

from ..core import setup_logger


# Musical note frequencies (Hz) in equal temperament tuning
# Using octave 4 (middle octave)
NOTE_FREQUENCIES = {
    "C4": 261.63,
    "D4": 293.66,
    "E4": 329.63,
    "F4": 349.23,
    "G4": 392.00,
    "A4": 440.00,
    "B4": 493.88,
    
    # Higher octave for extended range
    "C5": 523.25,
    "D5": 587.33,
    "E5": 659.25,
}

# Twinkle Twinkle Little Star note sequence
# Each tuple is (note, duration_beats)
# Quarter note = 1 beat, half note = 2 beats
TWINKLE_TWINKLE_NOTES = [
    # "Twinkle twinkle little star"
    ("C4", 1), ("C4", 1), ("G4", 1), ("G4", 1),
    ("A4", 1), ("A4", 1), ("G4", 2),
    
    # "How I wonder what you are"
    ("F4", 1), ("F4", 1), ("E4", 1), ("E4", 1),
    ("D4", 1), ("D4", 1), ("C4", 2),
    
    # "Up above the world so high"
    ("G4", 1), ("G4", 1), ("F4", 1), ("F4", 1),
    ("E4", 1), ("E4", 1), ("D4", 2),
    
    # "Like a diamond in the sky"
    ("G4", 1), ("G4", 1), ("F4", 1), ("F4", 1),
    ("E4", 1), ("E4", 1), ("D4", 2),
    
    # "Twinkle twinkle little star"
    ("C4", 1), ("C4", 1), ("G4", 1), ("G4", 1),
    ("A4", 1), ("A4", 1), ("G4", 2),
    
    # "How I wonder what you are"
    ("F4", 1), ("F4", 1), ("E4", 1), ("E4", 1),
    ("D4", 1), ("D4", 1), ("C4", 2),
]


@dataclass
class NoteResult:
    """Result from note sequence generation."""
    audio_data: npt.NDArray[np.int16]
    sample_rate: int
    duration: float
    note_timings: List[Tuple[str, float, float]]  # (note_name, start_time, end_time)


class MusicalNoteGenerator:
    """Generate musical notes as audio waveforms."""
    
    def __init__(self, sample_rate: int = 24000):
        """Initialize note generator.
        
        Args:
            sample_rate: Sample rate for generated audio (Hz)
        """
        self.sample_rate = sample_rate
        self.logger = setup_logger(__name__)
    
    def generate_note(
        self,
        note_name: str,
        duration: float,
        volume: float = 0.3,
        envelope: bool = True
    ) -> npt.NDArray[np.float32]:
        """Generate a single musical note.
        
        Args:
            note_name: Name of note (e.g., "C4", "G4")
            duration: Duration in seconds
            volume: Volume level (0.0 to 1.0)
            envelope: Apply ADSR envelope for smoother sound
        
        Returns:
            Audio waveform as float32 array
        """
        if note_name not in NOTE_FREQUENCIES:
            self.logger.warning(f"Unknown note '{note_name}', using C4")
            note_name = "C4"
        
        frequency = NOTE_FREQUENCIES[note_name]
        
        # Generate time array
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        
        # Generate sine wave with harmonics for richer sound
        # Fundamental + 2nd harmonic (octave) + 3rd harmonic (fifth)
        waveform = (
            np.sin(2 * np.pi * frequency * t) * 1.0 +          # Fundamental
            np.sin(2 * np.pi * frequency * 2 * t) * 0.3 +      # Octave
            np.sin(2 * np.pi * frequency * 3 * t) * 0.15       # Fifth
        )
        
        # Normalize
        waveform = waveform / np.max(np.abs(waveform))
        
        # Apply ADSR envelope for more natural sound
        if envelope:
            n_samples = len(waveform)
            
            # Attack (10% of note)
            attack_samples = int(n_samples * 0.1)
            attack = np.linspace(0, 1, attack_samples)
            
            # Decay (10% of note)
            decay_samples = int(n_samples * 0.1)
            decay = np.linspace(1, 0.8, decay_samples)
            
            # Sustain (60% of note at 80% volume)
            sustain_samples = int(n_samples * 0.6)
            sustain = np.ones(sustain_samples) * 0.8
            
            # Release (20% of note)
            release_samples = n_samples - attack_samples - decay_samples - sustain_samples
            release = np.linspace(0.8, 0, release_samples)
            
            # Combine envelope
            envelope_curve = np.concatenate([attack, decay, sustain, release])
            
            # Ensure envelope matches waveform length exactly
            if len(envelope_curve) != n_samples:
                envelope_curve = np.interp(
                    np.linspace(0, len(envelope_curve), n_samples),
                    np.arange(len(envelope_curve)),
                    envelope_curve
                )
            
            waveform = waveform * envelope_curve
        
        # Apply volume
        waveform = waveform * volume
        
        return waveform.astype(np.float32)
    
    def generate_sequence(
        self,
        note_sequence: List[Tuple[str, float]],
        tempo: float = 120.0,
        gap_between_notes: float = 0.05
    ) -> NoteResult:
        """Generate a sequence of musical notes.
        
        Args:
            note_sequence: List of (note_name, duration_beats) tuples
            tempo: Tempo in beats per minute
            gap_between_notes: Silence between notes (seconds)
        
        Returns:
            NoteResult with audio data and timing information
        """
        # Calculate beat duration in seconds
        beat_duration = 60.0 / tempo
        
        # Generate each note
        audio_segments = []
        note_timings = []
        current_time = 0.0
        
        for note_name, beats in note_sequence:
            note_duration = beats * beat_duration
            
            # Record timing (before note starts)
            start_time = current_time
            
            # Generate note
            note_audio = self.generate_note(note_name, note_duration)
            audio_segments.append(note_audio)
            
            # Add gap
            if gap_between_notes > 0:
                gap_samples = int(self.sample_rate * gap_between_notes)
                gap_audio = np.zeros(gap_samples, dtype=np.float32)
                audio_segments.append(gap_audio)
            
            # Calculate timing
            end_time = current_time + note_duration
            note_timings.append((note_name, start_time, end_time))
            
            # Update time (including gap)
            current_time = end_time + gap_between_notes
        
        # Concatenate all segments
        full_audio = np.concatenate(audio_segments)
        
        # Convert to int16 for playback
        audio_int16 = (full_audio * 32767).astype(np.int16)
        
        self.logger.info(
            f"Generated {len(note_sequence)} notes, "
            f"total duration: {len(full_audio) / self.sample_rate:.2f}s"
        )
        
        return NoteResult(
            audio_data=audio_int16,
            sample_rate=self.sample_rate,
            duration=len(full_audio) / self.sample_rate,
            note_timings=note_timings
        )


class MusicalSongPlayer:
    """High-level interface for playing musical songs."""
    
    def __init__(self, sample_rate: int = 24000):
        """Initialize song player.
        
        Args:
            sample_rate: Sample rate for audio generation
        """
        self.generator = MusicalNoteGenerator(sample_rate)
        self.logger = setup_logger(__name__)
    
    def play_twinkle_twinkle(self, tempo: float = 120.0) -> NoteResult:
        """Generate Twinkle Twinkle Little Star.
        
        Args:
            tempo: Playback tempo in BPM
        
        Returns:
            NoteResult ready for playback
        """
        self.logger.info("Generating 'Twinkle Twinkle Little Star'")
        return self.generator.generate_sequence(
            TWINKLE_TWINKLE_NOTES,
            tempo=tempo,
            gap_between_notes=0.05
        )
    
    def play_happy_birthday(self, tempo: float = 100.0) -> NoteResult:
        """Generate Happy Birthday melody.
        
        Args:
            tempo: Playback tempo in BPM
        
        Returns:
            NoteResult ready for playback
        """
        happy_birthday_notes = [
            # "Happy birthday to you"
            ("C4", 0.75), ("C4", 0.25), ("D4", 1), ("C4", 1),
            ("F4", 1), ("E4", 2),
            
            # "Happy birthday to you"
            ("C4", 0.75), ("C4", 0.25), ("D4", 1), ("C4", 1),
            ("G4", 1), ("F4", 2),
            
            # "Happy birthday dear..."
            ("C4", 0.75), ("C4", 0.25), ("C5", 1), ("A4", 1),
            ("F4", 1), ("E4", 1), ("D4", 2),
            
            # "Happy birthday to you"
            ("A4", 0.75), ("A4", 0.25), ("G4", 1), ("F4", 1),
            ("G4", 1), ("F4", 2),
        ]
        
        self.logger.info("Generating 'Happy Birthday'")
        return self.generator.generate_sequence(
            happy_birthday_notes,
            tempo=tempo,
            gap_between_notes=0.05
        )
