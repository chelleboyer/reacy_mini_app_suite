"""Reachy Mini robot control wrappers and utilities."""

from .robot_wrapper import ReachyWrapper
from .safe_motions import SafeMotionController
from .audio_reactive import (
    AudioReactiveMotion,
    SimpleAudioReactiveController,
    AudioAnalyzer,
    AudioFeatures,
)
from .tts_engine import (
    TTSEngine,
    TTSResult,
    TimingMarker,
    MockTTSEngine,
    OpenAITTSEngine,
    MusicalTTSEngine,
    create_tts_engine,
)
from .choreography import (
    ChoreographyEngine,
    ChoreographyEvent,
    GestureType,
)
from .audio_player import AudioPlayer
from .note_player import (
    MusicalNoteGenerator,
    MusicalSongPlayer,
    NoteResult,
    NOTE_FREQUENCIES,
)

__all__ = [
    "ReachyWrapper",
    "SafeMotionController",
    "AudioReactiveMotion",
    "SimpleAudioReactiveController",
    "AudioAnalyzer",
    "AudioFeatures",
    "TTSEngine",
    "TTSResult",
    "TimingMarker",
    "MockTTSEngine",
    "OpenAITTSEngine",
    "MusicalTTSEngine",
    "create_tts_engine",
    "ChoreographyEngine",
    "ChoreographyEvent",
    "GestureType",
    "AudioPlayer",
    "MusicalNoteGenerator",
    "MusicalSongPlayer",
    "NoteResult",
    "NOTE_FREQUENCIES",
]
