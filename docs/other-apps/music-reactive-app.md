# Music-Reactive Dance App

**Make Reachy dance and respond emotionally to music!**

## Overview

The Music-Reactive Dance app transforms Reachy into an expressive performer that listens to music via microphone and responds with:

- **Real-time dance movements** synchronized to the beat (80ms latency)
- **Emotional expressions** matching the music's mood
- **Sounds** that complement the detected emotion

## Quick Start

### Run the App

```bash
# With physical robot
python -m src.apps.music-reactive.main --host <robot-ip>

# Mock mode (testing without robot)
python -m src.apps.music-reactive.main --mock

# Debug mode
python -m src.apps.music-reactive.main --debug
```

### Usage

1. Start the app
2. Play music from your device or nearby speakers
3. Watch Reachy react with dance moves and emotional expressions
4. Press `Ctrl+C` to stop

## How It Works

### Emotion Detection

The app analyzes music in real-time using three key features:

- **Tempo** (BPM) - How fast the music is
- **Energy** (RMS) - How loud/intense the music is  
- **Valence** (Spectral Centroid) - How bright/dark the music sounds

These features are classified into emotions:

| Emotion | Characteristics | Example Music |
|---------|----------------|---------------|
| **Happy** | Bright tones + moderate energy | Pop, upbeat indie |
| **Sad** | Dark tones + low energy | Ballads, slow jazz |
| **Energetic** | Fast tempo + high energy | EDM, rock, workout music |
| **Neutral** | Moderate everything | Ambient, background |

### Emotion-to-Gesture Mapping

Each emotion triggers specific gestures and sounds:

#### Happy 😊
- **Primary gesture:** `express_happy()`
- **Dance moves:** `singing_sway`, `wave_antennas`, `express_excited`
- **Sound range:** C5-G5 (high, bright notes)
- **Motion:** 1.2x intensity, 1.3x speed

#### Sad 😢
- **Primary gesture:** `express_sad()`
- **Dance moves:** `nod_yes`, `tilt_curious`
- **Sound range:** C4-G4 (low, mellow notes)
- **Motion:** 0.6x intensity, 0.7x speed

#### Energetic ⚡
- **Primary gesture:** `express_excited()`
- **Dance moves:** `singing_sway`, `singing_lean_forward`, `look_around`
- **Sound range:** G4-D5 (mid, punchy notes)
- **Motion:** 1.5x intensity, 1.5x speed

#### Neutral 😐
- **Primary gesture:** `nod_yes()`
- **Dance moves:** `singing_sway`, `tilt_curious`
- **Sound range:** F4-C5 (neutral range)
- **Motion:** 1.0x intensity, 1.0x speed

### Real-Time Processing

```
Audio Input (Microphone)
    ↓
Audio Analysis (every 2048 samples)
    ↓
Motion Generation ← Current Emotion Intensity
    ↓
Apply to Robot (80ms latency)
    ↓
Periodic Emotion Check (every 3 seconds)
    ↓
Gesture Execution (every 2 seconds)
    ↓
Emotion Sound Playback
```

## Configuration

### Adjustable Parameters

Edit `src/apps/music-reactive/main.py` to customize:

```python
# Audio settings
sample_rate = 22050        # Hz
chunk_size = 2048          # samples

# Timing
emotion_check_interval = 3.0   # seconds between emotion analysis
gesture_interval = 2.0         # seconds between gestures

# Buffer
buffer_seconds = 3         # audio history for emotion detection
```

### Emotion Thresholds

Edit `src/common/reachy/emotion_detector.py`:

```python
# Tempo thresholds (BPM)
self.tempo_slow = 90
self.tempo_fast = 130

# Energy thresholds (0-1)
self.energy_low = 0.3
self.energy_high = 0.7

# Valence threshold
self.valence_threshold = 0.5
```

## Testing

### Validate Emotion Detection

```bash
# Run unit tests
python examples/test_emotion_detection.py
```

This tests:
- ✅ Emotion detection from audio features
- ✅ Gesture mapping correctness
- ✅ Feature-based classification

### Test with Real Music

Best test tracks:

- **Happy:** "Happy" by Pharrell Williams, "Walking on Sunshine"
- **Sad:** "Someone Like You" by Adele, "Mad World"  
- **Energetic:** "Eye of the Tiger", EDM/house music

## Requirements

### Python Packages

```bash
pip install librosa sounddevice numpy scipy
```

### Hardware

- **Microphone:** Built-in or USB microphone for audio input
- **Reachy Mini:** Physical robot or mock mode for testing
- **Speakers:** To play music (optional if using device audio)

### System Requirements

- Python 3.10+
- Reachy Mini SDK v1.1.2+
- CM4/Raspberry Pi or Linux system

## Troubleshooting

### No Audio Input

```bash
# List available audio devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# Test microphone
python -c "import sounddevice as sd; import time; sd.rec(44100, samplerate=44100, channels=1); time.sleep(1)"
```

### Incorrect Emotion Detection

- Ensure music is loud enough (check Energy% in output)
- Music should have clear beat/melody (ambient noise confuses detector)
- Try adjusting thresholds in `emotion_detector.py`

### Robot Not Moving

- Verify daemon is running: `reachy-daemon status`
- Check connection: `ping <robot-ip>`
- Enable debug mode: `--debug` flag
- Test with mock mode first: `--mock` flag

### Latency Issues

- Reduce `chunk_size` for lower latency (increases CPU usage)
- Increase `chunk_size` for smoother motion (increases latency)
- Check CPU usage—emotion analysis is compute-intensive

## Architecture

### Components

```
MusicReactiveDance (main.py)
├── EmotionDetector (emotion_detector.py)
│   └── Classifies audio → emotion
├── EmotionGestureMapper (emotion_detector.py)
│   └── Maps emotion → gestures + sounds
├── AudioReactiveMotion (audio_reactive.py)
│   └── Generates real-time head motion
├── SafeMotionController (safe_motions.py)
│   └── Executes gestures safely
└── MusicalNoteGenerator (note_player.py)
    └── Synthesizes emotion-matching sounds
```

### Data Flow

1. **Audio Callback:** Receives audio chunks from microphone
2. **Buffer:** Stores 3 seconds for emotion analysis
3. **Real-Time Motion:** Generates head motion from current chunk
4. **Emotion Check:** Every 3 seconds, analyze buffer → detect emotion
5. **Gesture Cycle:** Every 2 seconds, execute random gesture for current emotion
6. **Sound Output:** Play emotion-matching note when emotion changes

## API Reference

### EmotionDetector

```python
detector = EmotionDetector()

# From audio data
result = detector.detect_from_audio(audio_array, sample_rate)

# From extracted features
result = detector.detect_from_features(tempo, energy, spectral_centroid)

# Result contains
result.emotion      # Emotion enum
result.confidence   # 0-1
result.tempo        # BPM
result.energy       # 0-1
result.valence      # 0-1
```

### EmotionGestureMapper

```python
mapper = EmotionGestureMapper()

gesture = mapper.get_gesture_for_emotion(Emotion.HAPPY)
gestures = mapper.get_dance_gestures(Emotion.ENERGETIC)
note_range = mapper.get_note_range(Emotion.SAD)
params = mapper.get_motion_params(Emotion.HAPPY)
random = mapper.select_random_gesture(Emotion.ENERGETIC)
```

## Future Enhancements

- **ML-based emotion detection** - More accurate classification
- **Genre detection** - Adapt to music style (jazz, rock, classical)
- **Multi-robot sync** - Coordinated dance with multiple Reachys
- **User preferences** - Learn which emotions user prefers
- **Custom choreography** - User-defined gesture sequences per emotion
- **Beat detection** - Sync gestures precisely to beat drops

## Credits

Built on:
- **AudioReactiveMotion** - 80ms latency motion system
- **SafeMotionController** - 13+ gestures and expressions
- **MusicalNoteGenerator** - ADSR envelope synthesis
- **Librosa** - Audio feature extraction

---

**Now go play some music and watch Reachy groove!** 🎵🤖
