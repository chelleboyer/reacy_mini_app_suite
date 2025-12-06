"""Main entry point for Reachy Sings app - Audio-Reactive Singing Robot!"""

import sys
import time
from pathlib import Path
from typing import Literal

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from common.core import AppConfig, setup_logger
from common.reachy import (
    ReachyWrapper,
    SafeMotionController,
    AudioReactiveMotion,
    SimpleAudioReactiveController,
)
from common.reachy.tts_engine import create_tts_engine, TTSResult
from common.reachy.choreography import ChoreographyEngine
from common.reachy.audio_player import AudioPlayer


# Demo songs - now with REAL MUSICAL NOTES!
DEMO_SONGS = {
    "twinkle": {
        "title": "Twinkle Twinkle Little Star",
        "lyrics": "Twinkle twinkle little star, how I wonder what you are. Up above the world so high, like a diamond in the sky.",
        "style": "default",
        "song_key": "twinkle",
        "tempo": 100,  # Slower, gentle pace
    },
    "happy": {
        "title": "Happy Birthday",
        "lyrics": "Happy birthday to you, happy birthday to you, happy birthday dear friend, happy birthday to you!",
        "style": "energetic",
        "song_key": "happy_birthday",
        "tempo": 110,  # Upbeat
    },
    "opera": {
        "title": "Mini Opera (Twinkle Variation)",
        "lyrics": "O sole mio, stands in radiant splendor! My sunshine bright, forever I surrender!",
        "style": "dramatic",
        "song_key": "twinkle",
        "tempo": 80,  # Slower, more dramatic
    },
}


class SingingPerformance:
    """Orchestrates a complete singing performance."""
    
    def __init__(
        self,
        robot: ReachyWrapper,
        controller: SafeMotionController,
        song_key: str = "twinkle",
        mode: str = "emotion"
    ):
        """Initialize singing performance.
        
        Args:
            robot: ReachyWrapper instance
            controller: SafeMotionController instance
            song_key: Key for song from DEMO_SONGS
            mode: Singing mode - "emotion" (Reachy sounds) or "musical" (notes)
        """
        self.robot = robot
        self.controller = controller
        self.song = DEMO_SONGS.get(song_key, DEMO_SONGS["twinkle"])
        self.mode = mode
        
        self.logger = setup_logger(f"{__name__}.Performance")
        
        # Components
        self.audio_reactive = SimpleAudioReactiveController(robot)
        self.choreography = ChoreographyEngine(robot, controller)
        self.audio_player: AudioPlayer | None = None
        self.tts_result: TTSResult | None = None
        self.tts_engine = None
        
        self.logger.info(f"Performance initialized: {self.song['title']} (mode: {mode})")
    
    def prepare(self) -> None:
        """Generate TTS and choreography."""
        self.logger.info("Preparing performance...")
        
        # Generate audio based on mode
        if self.mode == "emotion":
            self.logger.info(f"Generating emotion sounds: '{self.song['title']}'")
            self.tts_engine = create_tts_engine("emotion")
        else:
            self.logger.info(f"Generating musical notes: '{self.song['title']}'")
            self.tts_engine = create_tts_engine("musical", sample_rate=24000)
        
        self.tts_result = self.tts_engine.generate(
            self.song["lyrics"],
            song=self.song.get("song_key", "twinkle"),
            tempo=self.song.get("tempo", 120)
        )
        
        mode_str = "emotion sounds" if self.mode == "emotion" else "notes"
        self.logger.info(f"{mode_str.capitalize()} generated: {self.tts_result.duration:.2f}s, {len(self.tts_result.timing_markers)} {mode_str}")
        
        # Generate choreography (only for musical mode - emotion mode has built-in movements)
        if self.mode == "musical":
            self.choreography.generate_from_tts(self.tts_result, style=self.song["style"])
        
        # Setup audio player (only for musical mode)
        if self.mode == "musical":
            def audio_callback(audio_chunk, timestamp):
                """Feed audio to reactive motion system."""
                self.audio_reactive.motion.feed_audio(audio_chunk, timestamp)
            
            self.audio_player = AudioPlayer(
                sample_rate=self.tts_result.sample_rate,
                audio_callback=audio_callback
            )
            self.audio_player.load_audio(
                self.tts_result.audio_data,
                self.tts_result.sample_rate
            )
        
        self.logger.info("Performance prepared!")
    
    def perform(self) -> None:
        """Execute the full performance."""
        if self.tts_result is None:
            self.logger.error("Performance not prepared - call prepare() first")
            return
        
        mode_display = "🔊 Reachy's Sounds" if self.mode == "emotion" else "🎹 Musical Notes"
        self.logger.info(f"🎤 Performing: {self.song['title']} 🎤")
        print(f"\n{'='*60}")
        print(f"♪♪♪  {self.song['title'].upper()}  ♪♪♪")
        print(f"{'='*60}")
        print(f"\nLyrics: {self.song['lyrics']}")
        print(f"Mode: {mode_display}")
        print(f"Style: {self.song['style']}")
        print(f"Duration: {self.tts_result.duration:.1f}s")
        print(f"{'='*60}\n")
        
        try:
            # Start choreography (only for musical mode)
            sync_time = time.time()
            if self.mode == "musical":
                self.logger.info("Starting choreography with built-in emotion moves...")
                self.choreography.start(start_time=sync_time)
                time.sleep(0.1)
            
            # Start audio playback
            self.logger.info("🎵 Starting playback...")
            print("\n🎵 SINGING NOW! 🎵\n")
            
            if self.mode == "emotion":
                # Play emotion song using the TTS engine's stored notes
                self.logger.info(f"Playing emotion-based melody with {len(self.tts_engine._current_notes)} notes")
                self.tts_engine.play_song(sync_time)
                time.sleep(self.tts_result.duration + 2.0)
            else:
                # Play musical notes via audio player
                self.audio_player.play(blocking=True)
                time.sleep(2.0)
            
            print("\n✨ Performance complete! ✨\n")
            
        except Exception as e:
            self.logger.error(f"Performance error: {e}")
            raise
        
        finally:
            # Stop all systems
            # self.logger.info("Stopping audio-reactive motion...")
            # self.audio_reactive.stop()
            
            self.logger.info("Stopping choreography...")
            self.choreography.stop()
            
            if self.audio_player:
                self.audio_player.stop()


def interactive_menu(robot: ReachyWrapper, controller: SafeMotionController) -> None:
    """Interactive song selection menu."""
    logger = setup_logger(f"{__name__}.menu")
    
    while True:
        print("\n" + "="*60)
        print("🎤 REACHY SINGS - SONG MENU 🎤")
        print("="*60)
        print("\nAvailable Songs:")
        print("  1. Twinkle Twinkle Little Star (gentle, calm)")
        print("  2. Happy Birthday (energetic, cheerful)")
        print("  3. Mini Opera (dramatic, powerful)")
        print("  q. Quit")
        print("\n" + "="*60)
        
        choice = input("\nSelect a song (1-3) or 'q' to quit: ").strip().lower()
        
        if choice == 'q':
            print("\n👋 Thanks for listening! Goodbye!\n")
            break
        
        song_map = {"1": "twinkle", "2": "happy", "3": "opera"}
        song_key = song_map.get(choice)
        
        if song_key is None:
            print("❌ Invalid choice. Please try again.")
            continue
        
        try:
            # Create and execute performance
            performance = SingingPerformance(robot, controller, song_key)
            
            print("\n⏳ Preparing performance...")
            performance.prepare()
            
            print("✅ Ready to perform!")
            input("\nPress ENTER to start the performance...")
            
            performance.perform()
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Performance interrupted by user")
            logger.info("Performance interrupted")
        except Exception as e:
            print(f"\n❌ Error during performance: {e}")
            logger.error(f"Performance error: {e}", exc_info=True)


def main():
    """Run the Reachy Sings application."""
    logger = setup_logger(__name__)
    logger.info("Starting Reachy Sings...")
    
    print("\n" + "="*60)
    print("🤖 REACHY SINGS - Audio-Reactive Singing Robot 🤖")
    print("="*60)
    print("\nFeatures:")
    print("  ✓ Real-time audio-reactive head motion")
    print("  ✓ Synchronized choreography")
    print("  ✓ Multiple singing styles")
    print("  ✓ Dynamic gesture generation")
    print("="*60 + "\n")
    
    # Load configuration
    config = AppConfig(
        app_name="reachy-sings",
        app_version="0.2.0",  # Audio-reactive version!
        media_backend="no_media",  # We handle all audio via sounddevice
    )
    
    logger.info(f"App: {config.app_name} v{config.app_version}")
    
    try:
        # Connect to robot
        print("⏳ Connecting to Reachy Mini...")
        with ReachyWrapper(
            localhost_only=config.localhost_only,
            use_sim=config.use_sim,
            media_backend=config.media_backend,
            log_level=config.log_level,
        ) as robot:
            logger.info("Connected to Reachy Mini")
            print("✅ Connected to Reachy Mini!\n")
            
            # Wake up
            print("⏳ Waking up robot...")
            robot.wake_up()
            print("✅ Robot ready!\n")
            time.sleep(1)
            
            # Create controller
            controller = SafeMotionController()
            
            # Run interactive menu
            interactive_menu(robot, controller)
            
            # Sleep before exit
            print("\n⏳ Putting robot to sleep...")
            robot.go_to_sleep()
            print("✅ Goodnight! 😴\n")
            
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Exiting...\n")
        logger.info("Application interrupted by user")
        return 130
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}\n")
        return 1
    
    logger.info("Application finished successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
