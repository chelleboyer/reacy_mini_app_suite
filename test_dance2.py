#!/usr/bin/env python3
"""Quick test of dance2 move with audio."""

import sys
import time
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from common.reachy.robot_wrapper import ReachyWrapper

def main():
    """Play dance2 move with sound."""
    print("🎵 Testing dance2 move with audio\n")
    print("="*60)
    
    # Load emotion library
    print("⏳ Loading emotion library...")
    try:
        from reachy_mini.motion.recorded_move import RecordedMoves
        moves = RecordedMoves('pollen-robotics/reachy-mini-emotions-library')
        print(f"✅ Emotion library loaded")
    except Exception as e:
        print(f"❌ Error loading library: {e}")
        return
    
    # Connect to robot
    print("\n⏳ Connecting to Reachy Mini...")
    with ReachyWrapper(localhost_only=True) as robot:
        print("✅ Connected!")
        
        print("\n⏳ Waking up robot...")
        robot.wake_up()
        time.sleep(1)
        print("✅ Robot ready!")
        
        # Load dance2 move
        print("\n" + "="*60)
        print("🎭 Loading dance2 move...")
        print("="*60)
        
        try:
            move = moves.get("dance2")
            print(f"Move duration: {move.duration:.1f}s")
            
            # Check for audio file
            audio_file = os.path.join(moves.local_path, "dance2.wav")
            
            if os.path.exists(audio_file):
                print(f"🔊 Found audio file: {audio_file}")
                
                # Load and play audio
                import sounddevice as sd
                import soundfile as sf
                
                print("\n🎵 Playing dance2 with movement...")
                audio_data, sample_rate = sf.read(audio_file)
                sd.play(audio_data, samplerate=sample_rate, blocking=False)
                
                # Play move
                robot._robot.play_move(move, initial_goto_duration=0.5)
                
                print("✅ Dance completed!")
                
            else:
                print(f"⚠️  No audio file found at {audio_file}")
                print("Playing move without audio...")
                robot._robot.play_move(move, initial_goto_duration=0.5)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*60)
        print("🎉 Test complete!")
        print("="*60)
        
        # Sleep before exit
        print("\n⏳ Putting robot to sleep...")
        robot.go_to_sleep()
        print("✅ Done!\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
