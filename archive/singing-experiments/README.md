# Singing Experiments Archive

This directory contains experimental code for making Reachy Mini "sing" using emotion library sounds.

## Files

- `emotion_song_player.py` - Module for creating melodies from emotion sounds with pitch shifting
- `test_emotion_singing.py` - Test script for emotion-based singing performance
- `test_emotion_sounds.py` - Simple test of emotion sounds with movements
- `test_sound_library.py` - Interactive sound browser for the emotion library

## What Was Tried

1. **Synthesized Musical Notes** - Generated proper musical notes with harmonics and ADSR envelopes ✅
2. **Different Emotion Sounds as Notes** - Used various emotion sounds (calming, cheerful, etc.) as musical notes
3. **Pitch-Shifted "Hoo Hoo"** - Took cheerful1 sound and pitch-shifted it to create melody
4. **Pitch-Shifted dance2** - Used the Bee Gees sound (dance2) with pitch shifting for longer melodic segments

## Issues Encountered

- Pitch-shifting emotion sounds degraded audio quality
- Short emotion sounds didn't create flowing melodies
- dance2 (Bee Gees "Stayin' Alive") is great but doesn't match Twinkle Twinkle
- Need better approach for natural-sounding robot singing

## Status

Archived on November 30, 2025 - experiments paused for regrouping.
