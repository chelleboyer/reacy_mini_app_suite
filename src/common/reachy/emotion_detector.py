"""
Emotion detection from audio features for Reachy Mini.

Analyzes music in real-time to detect emotional content and map to
appropriate gestures and sounds.
"""

import numpy as np
import logging
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class Emotion(Enum):
    """Supported emotions for music reaction."""
    HAPPY = "happy"
    SAD = "sad"
    ENERGETIC = "energetic"
    NEUTRAL = "neutral"


@dataclass
class EmotionResult:
    """Result of emotion detection."""
    emotion: Emotion
    confidence: float
    tempo: float
    energy: float
    valence: float  # Positive (happy) vs negative (sad)


class EmotionDetector:
    """
    Detects emotion from audio features.
    
    Uses simple heuristics based on tempo, energy, and spectral features
    to classify music into emotional categories.
    """
    
    def __init__(self):
        """Initialize emotion detector with thresholds."""
        # Tempo thresholds (BPM)
        self.tempo_slow = 90
        self.tempo_fast = 130
        
        # Energy thresholds (0-1)
        self.energy_low = 0.3
        self.energy_high = 0.7
        
        # Valence thresholds (positive/negative feeling)
        self.valence_threshold = 0.5
        
        logger.info("EmotionDetector initialized")
    
    def detect_from_features(
        self, 
        tempo: float, 
        energy: float, 
        spectral_centroid: float,
        sample_rate: int = 22050
    ) -> EmotionResult:
        """
        Detect emotion from audio features.
        
        Args:
            tempo: Beats per minute
            energy: RMS energy (0-1 normalized)
            spectral_centroid: Average frequency (Hz)
            sample_rate: Audio sample rate
            
        Returns:
            EmotionResult with detected emotion and confidence
        """
        # Calculate valence (brightness) from spectral centroid
        # Higher frequencies = more positive/bright
        valence = min(1.0, spectral_centroid / (sample_rate / 4))
        
        # Decision tree for emotion classification
        emotion, confidence = self._classify_emotion(tempo, energy, valence)
        
        return EmotionResult(
            emotion=emotion,
            confidence=confidence,
            tempo=tempo,
            energy=energy,
            valence=valence
        )
    
    def _classify_emotion(
        self, 
        tempo: float, 
        energy: float, 
        valence: float
    ) -> Tuple[Emotion, float]:
        """
        Classify emotion using heuristic rules.
        
        Returns:
            (emotion, confidence) tuple
        """
        # High energy + fast tempo = ENERGETIC
        if energy > self.energy_high and tempo > self.tempo_fast:
            confidence = min(energy, tempo / 180.0)
            return Emotion.ENERGETIC, confidence
        
        # High valence + moderate energy = HAPPY
        if valence > self.valence_threshold and energy > self.energy_low:
            confidence = (valence + energy) / 2.0
            return Emotion.HAPPY, confidence
        
        # Low valence + low energy = SAD
        if valence < self.valence_threshold and energy < self.energy_high:
            confidence = (1.0 - valence + (1.0 - energy)) / 2.0
            return Emotion.SAD, confidence
        
        # Default to neutral with low confidence
        return Emotion.NEUTRAL, 0.5
    
    def detect_from_audio(
        self, 
        audio_data: np.ndarray, 
        sample_rate: int
    ) -> EmotionResult:
        """
        Detect emotion from raw audio data.
        
        Requires librosa for feature extraction.
        
        Args:
            audio_data: Audio samples as numpy array
            sample_rate: Sample rate in Hz
            
        Returns:
            EmotionResult with detected emotion
        """
        try:
            import librosa
        except ImportError:
            logger.warning("librosa not available, using default emotion")
            return EmotionResult(
                emotion=Emotion.NEUTRAL,
                confidence=0.0,
                tempo=120.0,
                energy=0.5,
                valence=0.5
            )
        
        # Extract features using librosa
        tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sample_rate)
        
        # Calculate RMS energy
        rms = librosa.feature.rms(y=audio_data)[0]
        energy = float(np.mean(rms))
        
        # Calculate spectral centroid (brightness)
        centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
        spectral_centroid = float(np.mean(centroid))
        
        return self.detect_from_features(
            tempo=float(tempo),
            energy=energy,
            spectral_centroid=spectral_centroid,
            sample_rate=sample_rate
        )


class EmotionGestureMapper:
    """
    Maps detected emotions to Reachy gestures and sounds.
    """
    
    def __init__(self):
        """Initialize gesture mapper with emotion profiles."""
        self.emotion_profiles = {
            Emotion.HAPPY: {
                'gesture': 'express_happy',
                'dance_gestures': ['singing_sway', 'wave_antennas', 'express_excited'],
                'note_range': (523.25, 783.99),  # C5-G5 (high, bright)
                'motion_intensity': 1.2,
                'speed_multiplier': 1.3
            },
            Emotion.SAD: {
                'gesture': 'express_sad',
                'dance_gestures': ['nod_yes', 'tilt_curious'],
                'note_range': (261.63, 392.00),  # C4-G4 (low, mellow)
                'motion_intensity': 0.6,
                'speed_multiplier': 0.7
            },
            Emotion.ENERGETIC: {
                'gesture': 'express_excited',
                'dance_gestures': ['singing_sway', 'singing_lean_forward', 'look_around'],
                'note_range': (392.00, 587.33),  # G4-D5 (mid, punchy)
                'motion_intensity': 1.5,
                'speed_multiplier': 1.5
            },
            Emotion.NEUTRAL: {
                'gesture': 'nod_yes',
                'dance_gestures': ['singing_sway', 'tilt_curious'],
                'note_range': (349.23, 523.25),  # F4-C5 (neutral)
                'motion_intensity': 1.0,
                'speed_multiplier': 1.0
            }
        }
    
    def get_gesture_for_emotion(self, emotion: Emotion) -> str:
        """Get primary gesture for an emotion."""
        return self.emotion_profiles[emotion]['gesture']
    
    def get_dance_gestures(self, emotion: Emotion) -> list:
        """Get list of gestures for dancing to this emotion."""
        return self.emotion_profiles[emotion]['dance_gestures']
    
    def get_note_range(self, emotion: Emotion) -> Tuple[float, float]:
        """Get frequency range for sounds matching this emotion."""
        return self.emotion_profiles[emotion]['note_range']
    
    def get_motion_params(self, emotion: Emotion) -> Dict[str, float]:
        """Get motion parameters for this emotion."""
        return {
            'intensity': self.emotion_profiles[emotion]['motion_intensity'],
            'speed': self.emotion_profiles[emotion]['speed_multiplier']
        }
    
    def select_random_gesture(self, emotion: Emotion) -> str:
        """Randomly select a gesture from the emotion's dance set."""
        gestures = self.get_dance_gestures(emotion)
        return np.random.choice(gestures)
