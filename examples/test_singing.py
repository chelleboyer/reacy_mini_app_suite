#!/usr/bin/env python3
"""Quick test of audio-reactive singing system."""

import sys
import time
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from common.core import setup_logger
from common.reachy import (
    ReachyWrapper,
    SafeMotionController,
    SimpleAudioReactiveController,
    create_tts_engine,
    ChoreographyEngine,
    AudioPlayer,
)


def test_audio_reactive():
    """Test audio-reactive motion with simple audio."""
    print("\n" + "="*60)
    print("🎵 Testing Audio-Reactive Motion")
    print("="*60 + "\n")
    
    logger = setup_logger(__name__)
    
    with ReachyWrapper(media_backend="no_media") as robot:
        print("✅ Connected to robot\n")
        
        # Wake up
        robot.wake_up()
        time.sleep(1)
        
        # Generate test audio
        print("⏳ Generating test TTS...")
        tts = create_tts_engine("mock")
        result = tts.generate("Hello! I am Reachy Mini and I love to sing!")
        print(f"✅ Generated {result.duration:.1f}s of audio\n")
        
        # Setup audio-reactive controller
        print("⏳ Setting up audio-reactive motion...")
        reactive_controller = SimpleAudioReactiveController(robot)
        
        # Configure motion parameters
        reactive_controller.motion.sway_magnitude = 10.0  # degrees
        reactive_controller.motion.bob_magnitude = 8.0
        reactive_controller.motion.tilt_magnitude = 5.0
        
        # Setup audio player with callback
        def audio_callback(chunk, timestamp):
            reactive_controller.motion.feed_audio(chunk, timestamp)
        
        player = AudioPlayer(sample_rate=result.sample_rate, audio_callback=audio_callback)
        player.load_audio(result.audio_data, result.sample_rate)
        
        print("✅ Audio-reactive system ready\n")
        
        # Start motion
        print("🎵 Starting audio-reactive motion...")
        reactive_controller.start()
        time.sleep(0.1)
        
        # Play audio
        print("▶️  Playing audio...\n")
        player.play(blocking=True)
        
        # Wait a bit
        time.sleep(1.0)
        
        # Stop motion
        print("\n⏹️  Stopping motion...")
        reactive_controller.stop()
        
        print("\n✅ Test complete!\n")
        
        # Return to neutral
        time.sleep(0.5)


def test_full_performance():
    """Test full singing performance with choreography."""
    print("\n" + "="*60)
    print("🎤 Testing Full Singing Performance")
    print("="*60 + "\n")
    
    logger = setup_logger(__name__)
    
    with ReachyWrapper(media_backend="no_media") as robot:
        controller = SafeMotionController()
        
        print("✅ Connected to robot\n")
        
        # Wake up
        robot.wake_up()
        time.sleep(1)
        
        # Generate song
        print("⏳ Generating song...")
        tts = create_tts_engine("mock")
        lyrics = "Twinkle twinkle little star, how I wonder what you are!"
        result = tts.generate(lyrics, voice_speed=0.9)
        print(f"✅ Generated song: {result.duration:.1f}s\n")
        
        # Setup choreography
        print("⏳ Generating choreography...")
        choreography = ChoreographyEngine(robot, controller)
        choreography.generate_from_tts(result, style="default")
        print(f"✅ Generated {len(choreography._events)} choreography events\n")
        
        # Setup audio-reactive
        print("⏳ Setting up audio-reactive motion...")
        reactive = SimpleAudioReactiveController(robot)
        
        def audio_callback(chunk, timestamp):
            reactive.motion.feed_audio(chunk, timestamp)
        
        player = AudioPlayer(sample_rate=result.sample_rate, audio_callback=audio_callback)
        player.load_audio(result.audio_data, result.sample_rate)
        
        print("✅ Performance ready\n")
        
        # Perform!
        print("🎵 STARTING PERFORMANCE! 🎵\n")
        
        # Start systems
        reactive.start()
        sync_time = time.time()
        choreography.start(start_time=sync_time)
        time.sleep(0.1)
        
        # Play
        player.play(blocking=True)
        
        # Wait for choreography to finish
        time.sleep(2.0)
        
        # Stop systems
        print("\n⏹️  Stopping systems...")
        reactive.stop()
        choreography.stop()
        
        print("\n✨ Performance complete! ✨\n")
        
        # Return to neutral
        controller.return_to_neutral(robot)


def main():
    """Run tests."""
    print("\n" + "="*60)
    print("🧪 Reachy Sings - Audio-Reactive System Tests")
    print("="*60)
    print("\nTests:")
    print("  1. Audio-reactive motion only")
    print("  2. Full performance (choreography + audio-reactive)")
    print("  q. Quit")
    print("="*60 + "\n")
    
    choice = input("Select test (1-2) or 'q' to quit: ").strip()
    
    if choice == '1':
        test_audio_reactive()
    elif choice == '2':
        test_full_performance()
    elif choice == 'q':
        print("\n👋 Goodbye!\n")
        return 0
    else:
        print("❌ Invalid choice")
        return 1
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)
