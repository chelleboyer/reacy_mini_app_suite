"""Test emotion library sounds with movements.

Simple test to verify emotion sounds play correctly with their moves.
"""

import time
import sounddevice as sd
import soundfile as sf
from reachy_mini.motion.recorded_move import RecordedMoves
from common.reachy.robot_wrapper import ReachyWrapper

def test_emotion_sounds():
    """Test a few emotion moves with their sounds."""
    
    print("🔊 Testing Reachy Emotion Sounds\n")
    print("="*60)
    
    # Load emotion library
    print("⏳ Loading emotion library...")
    moves = RecordedMoves('pollen-robotics/reachy-mini-emotions-library')
    print(f"✅ Emotion library loaded\n")
    
    # Connect to robot
    print("⏳ Connecting to Reachy Mini...")
    with ReachyWrapper() as robot:
        robot.wake_up()
        print("✅ Robot ready!\n")
        time.sleep(1)
        
        # Test moves with sounds
        test_moves = [
            ("dance1", "Dance Move 1"),
            ("dance2", "Dance Move 2"),
            ("cheerful1", "Cheerful Expression"),
            ("enthusiastic1", "Enthusiastic Expression"),
        ]
        
        for move_name, description in test_moves:
            print(f"\n{'='*60}")
            print(f"🎭 Testing: {description} ({move_name})")
            print('='*60)
            
            try:
                # Load move
                move = moves.get(move_name)
                print(f"Move duration: {move.duration:.1f}s")
                
                # Check for audio file
                import os
                audio_file = os.path.join(moves.local_path, f"{move_name}.wav")
                
                if os.path.exists(audio_file):
                    print(f"🔊 Playing sound: {move_name}.wav")
                    # Load and play audio
                    audio_data, sample_rate = sf.read(audio_file)
                    sd.play(audio_data, samplerate=sample_rate, blocking=False)
                else:
                    print(f"⚠️  No audio file found for {move_name}")
                
                # Play move
                print(f"🤖 Playing movement...")
                robot._robot.play_move(move, initial_goto_duration=0.5)
                
                print(f"✅ Completed!")
                
            except Exception as e:
                print(f"❌ Error: {e}")
            
            # Wait between moves
            print("\n⏳ Waiting 2 seconds before next move...")
            time.sleep(2)
        
        print("\n" + "="*60)
        print("🎉 Testing complete!")
        print("="*60)
        
        # Sleep before exit
        print("\n⏳ Putting robot to sleep...")
        robot.go_to_sleep()
        print("✅ Done!\n")

if __name__ == "__main__":
    try:
        test_emotion_sounds()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
