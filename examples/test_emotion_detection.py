#!/usr/bin/env python3
"""
Test script for emotion detection and music reactive features.

Tests emotion detection with synthetic audio and validates gesture mapping.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import logging
from src.common.core.logger import setup_logger
from src.common.reachy.emotion_detector import (
    EmotionDetector, 
    EmotionGestureMapper, 
    Emotion
)

logger = logging.getLogger(__name__)


def generate_test_audio(emotion_type: str, duration: float = 3.0, sample_rate: int = 22050):
    """
    Generate synthetic audio with characteristics matching an emotion.
    
    Args:
        emotion_type: 'happy', 'sad', or 'energetic'
        duration: Audio duration in seconds
        sample_rate: Sample rate in Hz
        
    Returns:
        numpy array of audio samples
    """
    t = np.linspace(0, duration, int(duration * sample_rate))
    
    if emotion_type == 'happy':
        # High frequency, moderate energy
        frequency = 800  # Hz (bright)
        tempo = 0.5  # Fast oscillation
        amplitude = 0.6
        audio = amplitude * np.sin(2 * np.pi * frequency * t)
        # Add some rhythm
        audio *= (1 + 0.3 * np.sin(2 * np.pi * tempo * t))
        
    elif emotion_type == 'sad':
        # Low frequency, low energy
        frequency = 200  # Hz (dark)
        tempo = 0.3  # Slow oscillation
        amplitude = 0.3
        audio = amplitude * np.sin(2 * np.pi * frequency * t)
        # Gentle modulation
        audio *= (1 + 0.1 * np.sin(2 * np.pi * tempo * t))
        
    elif emotion_type == 'energetic':
        # Mid frequency, high energy, fast tempo
        frequency = 500  # Hz
        tempo = 1.0  # Very fast
        amplitude = 0.9
        audio = amplitude * np.sin(2 * np.pi * frequency * t)
        # Strong rhythmic variation
        audio *= (1 + 0.5 * np.sin(2 * np.pi * tempo * t))
        # Add noise for energy
        audio += 0.1 * np.random.randn(len(t))
        
    else:
        # Neutral - mid everything
        frequency = 440  # A4
        amplitude = 0.5
        audio = amplitude * np.sin(2 * np.pi * frequency * t)
    
    return audio.astype(np.float32)


def test_emotion_detection():
    """Test emotion detector with synthetic audio."""
    logger.info("=" * 60)
    logger.info("Testing Emotion Detection")
    logger.info("=" * 60)
    
    detector = EmotionDetector()
    sample_rate = 22050
    
    test_cases = ['happy', 'sad', 'energetic', 'neutral']
    
    for emotion_type in test_cases:
        logger.info(f"\n📊 Testing {emotion_type.upper()} audio...")
        
        # Generate test audio
        audio = generate_test_audio(emotion_type, duration=3.0, sample_rate=sample_rate)
        
        # Detect emotion
        result = detector.detect_from_audio(audio, sample_rate)
        
        logger.info(f"  Detected: {result.emotion.value}")
        logger.info(f"  Confidence: {result.confidence:.2%}")
        logger.info(f"  Tempo: {result.tempo:.1f} BPM")
        logger.info(f"  Energy: {result.energy:.2%}")
        logger.info(f"  Valence: {result.valence:.2%}")
        
        # Check if detection matches expected
        expected_emotion = Emotion[emotion_type.upper()]
        if result.emotion == expected_emotion:
            logger.info(f"  ✅ Correct detection!")
        else:
            logger.warning(f"  ⚠️  Expected {expected_emotion.value}, got {result.emotion.value}")


def test_gesture_mapping():
    """Test emotion-to-gesture mapping."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Gesture Mapping")
    logger.info("=" * 60)
    
    mapper = EmotionGestureMapper()
    
    for emotion in Emotion:
        logger.info(f"\n🎭 Emotion: {emotion.value.upper()}")
        
        gesture = mapper.get_gesture_for_emotion(emotion)
        logger.info(f"  Primary gesture: {gesture}")
        
        dance_gestures = mapper.get_dance_gestures(emotion)
        logger.info(f"  Dance gestures: {', '.join(dance_gestures)}")
        
        note_range = mapper.get_note_range(emotion)
        logger.info(f"  Note range: {note_range[0]:.2f} Hz - {note_range[1]:.2f} Hz")
        
        params = mapper.get_motion_params(emotion)
        logger.info(f"  Motion intensity: {params['intensity']:.1f}x")
        logger.info(f"  Speed multiplier: {params['speed']:.1f}x")
        
        # Test random selection
        random_gesture = mapper.select_random_gesture(emotion)
        logger.info(f"  Random selection: {random_gesture}")


def test_feature_extraction():
    """Test manual feature extraction and classification."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Feature-Based Classification")
    logger.info("=" * 60)
    
    detector = EmotionDetector()
    
    # Test cases with known features
    test_features = [
        {
            'name': 'Fast + Bright + High Energy',
            'tempo': 150,
            'energy': 0.8,
            'centroid': 4000,
            'expected': Emotion.ENERGETIC
        },
        {
            'name': 'Slow + Dark + Low Energy',
            'tempo': 70,
            'energy': 0.2,
            'centroid': 1000,
            'expected': Emotion.SAD
        },
        {
            'name': 'Moderate + Bright + Medium Energy',
            'tempo': 110,
            'energy': 0.6,
            'centroid': 3500,
            'expected': Emotion.HAPPY
        },
    ]
    
    for test in test_features:
        logger.info(f"\n🔬 {test['name']}")
        logger.info(f"  Input: tempo={test['tempo']} BPM, energy={test['energy']:.1%}, "
                   f"centroid={test['centroid']} Hz")
        
        result = detector.detect_from_features(
            tempo=test['tempo'],
            energy=test['energy'],
            spectral_centroid=test['centroid']
        )
        
        logger.info(f"  Detected: {result.emotion.value} (confidence: {result.confidence:.2%})")
        
        if result.emotion == test['expected']:
            logger.info(f"  ✅ Matches expected: {test['expected'].value}")
        else:
            logger.warning(f"  ⚠️  Expected {test['expected'].value}")


def main():
    """Run all tests."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    logger.info("🎵 Music-Reactive Dance - Emotion Detection Tests")
    logger.info("=" * 60)
    
    try:
        # Test 1: Emotion detection with synthetic audio
        test_emotion_detection()
        
        # Test 2: Gesture mapping
        test_gesture_mapping()
        
        # Test 3: Feature-based classification
        test_feature_extraction()
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ All tests complete!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
