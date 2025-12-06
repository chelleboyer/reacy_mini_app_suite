# Musical Notes Feature - Reachy Sings Real Songs! 🎵

## Overview

Reachy Mini can now sing with **real musical notes** instead of simple beeps! The system generates proper melodies using synthesized musical notes with harmonics and ADSR envelopes.

## What Changed

### Before
- MockTTS generated simple sine wave beeps at 440Hz
- No melodic structure
- Sounded like telephone tones

### After
- Musical note generator creates proper notes (C4, D4, E4, F4, G4, A4, B4, C5, D5, E5)
- Each note uses fundamental frequency + harmonics (octave + fifth) for richer sound
- ADSR envelope (Attack, Decay, Sustain, Release) for natural note transitions
- Pre-programmed songs: **Twinkle Twinkle Little Star** and **Happy Birthday**

## Technical Details

### Note Generation

**File**: `src/common/reachy/note_player.py`

```python
NOTE_FREQUENCIES = {
    "C4": 261.63,  # Middle C
    "D4": 293.66,
    "E4": 329.63,
    "F4": 349.23,
    "G4": 392.00,
    "A4": 440.00,
    "B4": 493.88,
    "C5": 523.25,
    # ... more octaves
}
```

Each note is synthesized with:
1. **Fundamental** - Base frequency (100% amplitude)
2. **2nd Harmonic** - Octave above (30% amplitude)
3. **3rd Harmonic** - Fifth above (15% amplitude)

### ADSR Envelope

Notes sound natural with smooth attack and release:
- **Attack** (10%): 0 → 100% volume
- **Decay** (10%): 100% → 80% volume
- **Sustain** (60%): Hold at 80% volume
- **Release** (20%): 80% → 0% volume

### Song Encoding

Twinkle Twinkle Little Star note sequence:
```python
TWINKLE_TWINKLE_NOTES = [
    # "Twinkle twinkle little star"
    ("C4", 1), ("C4", 1), ("G4", 1), ("G4", 1),
    ("A4", 1), ("A4", 1), ("G4", 2),
    
    # "How I wonder what you are"
    ("F4", 1), ("F4", 1), ("E4", 1), ("E4", 1),
    ("D4", 1), ("D4", 1), ("C4", 2),
    
    # ... continues for full song
]
```

Each tuple is `(note_name, duration_in_beats)`.

## Musical TTS Engine

**File**: `src/common/reachy/tts_engine.py`

New `MusicalTTSEngine` class:
- Generates musical notes instead of speech
- Compatible with existing `TTSResult` format
- Provides timing markers for choreography synchronization
- Supports tempo adjustment (BPM)

```python
# Usage
tts_engine = create_tts_engine("musical", sample_rate=24000)
result = tts_engine.generate(
    "Song title",
    song="twinkle",
    tempo=100
)
```

## Integration with Reachy Sings App

**Updated**: `src/apps/reachy-sings/main.py`

Song definitions now include:
```python
DEMO_SONGS = {
    "twinkle": {
        "title": "Twinkle Twinkle Little Star",
        "lyrics": "...",
        "style": "default",
        "song_key": "twinkle",
        "tempo": 100,  # BPM
    },
}
```

The app automatically:
1. Generates musical notes at specified tempo
2. Creates timing markers for each note
3. Synchronizes choreography with note boundaries
4. Applies audio-reactive motion during playback

## Performance Characteristics

### Twinkle Twinkle Little Star
- **42 notes** in sequence
- **30.9 seconds** duration at 100 BPM
- **6 repetitions** of main melodic patterns
- Gentle, calming tempo

### Happy Birthday
- **32 notes** in sequence
- ~26 seconds duration at 110 BPM
- Upbeat, energetic tempo
- Classic birthday melody

## Audio Quality

The synthesized notes provide:
- ✅ Clear melodic structure
- ✅ Rich harmonic content (not just sine waves)
- ✅ Smooth note transitions (no clicks)
- ✅ Adjustable volume and tempo
- ✅ Proper musical intervals

## System Architecture

```
User selects song
     ↓
MusicalTTSEngine
     ↓
MusicalNoteGenerator
     ↓
Generate note sequence with ADSR envelopes
     ↓
Convert to int16 audio data
     ↓
AudioPlayer plays with callbacks
     ↓
Audio-reactive motion + Choreography
     ↓
Robot performs synchronized dance & song!
```

## Testing

Successfully tested on hardware:
- ✅ Daemon running on /dev/ttyACM0
- ✅ Musical notes play clearly through speakers
- ✅ Choreography synchronized with note timing
- ✅ Audio-reactive motion responds to musical frequencies
- ✅ All gestures execute smoothly (sway, happy, antenna waves, bow)

## Future Enhancements

Potential improvements:
- [ ] Add more songs (Mary Had a Little Lamb, Jingle Bells, etc.)
- [ ] Support for sharps/flats (C#, Eb, etc.)
- [ ] Variable note volumes for dynamics
- [ ] Vibrato effect for expressive singing
- [ ] Load songs from MIDI files
- [ ] Use actual flute samples from HuggingFace dataset (if available)
- [ ] Polyphonic notes (chords)

## Files Created/Modified

### New Files
- `src/common/reachy/note_player.py` - Musical note generation

### Modified Files
- `src/common/reachy/tts_engine.py` - Added MusicalTTSEngine
- `src/common/reachy/__init__.py` - Export musical components
- `src/apps/reachy-sings/main.py` - Use musical engine instead of MockTTS

## Comparison: Before vs After

| Aspect | Before (MockTTS) | After (Musical) |
|--------|------------------|-----------------|
| Sound | Simple 440Hz beep | Proper musical notes |
| Melody | None | Twinkle Twinkle, Happy Birthday |
| Harmonics | None | Fundamental + octave + fifth |
| Envelope | Abrupt on/off | Smooth ADSR |
| Tempo | Fixed | Adjustable BPM |
| Notes | 1 frequency | 10+ notes (C4-E5) |
| Expressiveness | Low | High |

## Credits

**Sheet Music Source**: Twinkle Twinkle Little Star traditional melody
**Note Frequencies**: Equal temperament tuning, A4 = 440Hz
**Synthesis Method**: Additive synthesis with harmonics
**Envelope Design**: Standard ADSR (10/10/60/20 split)

---

🎵 **Reachy can now sing real songs with proper melodies!** 🎵
