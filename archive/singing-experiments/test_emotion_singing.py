"""Quick test of emotion-based singing.

Tests Twinkle Twinkle using Reachy's emotion sounds.
"""

import time
from common.reachy.robot_wrapper import ReachyWrapper
from common.reachy.safe_motions import SafeMotionController

# Import SingingPerformance class
import sys
import os
import importlib.util
spec = importlib.util.spec_from_file_location("reachy_sings_main", 
    os.path.join(os.path.dirname(__file__), '..', 'src', 'apps', 'reachy-sings', 'main.py'))
reachy_sings_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reachy_sings_main)
SingingPerformance = reachy_sings_main.SingingPerformance

def test_emotion_singing():
    """Test singing with emotion sounds."""
    
    print("🎤 Testing Emotion-Based Singing\n")
    print("="*60)
    
    # Connect to robot
    print("⏳ Connecting to Reachy Mini...")
    with ReachyWrapper() as robot:
        robot.wake_up()
        print("✅ Robot ready!\n")
        time.sleep(1)
        
        controller = SafeMotionController()
        
        # Create performance with EMOTION mode
        perf = SingingPerformance(robot, controller, song_key="twinkle", mode="emotion")
        
        print("\n⏳ Preparing performance...")
        perf.prepare()
        print("✅ Ready to perform!\n")
        
        input("Press ENTER to start singing with Reachy's sounds...")
        
        # Perform!
        perf.perform()
        
        print("\n✅ Test complete!\n")
        
        # Sleep before exit
        print("⏳ Putting robot to sleep...")
        robot.go_to_sleep()
        print("✅ Done!\n")

if __name__ == "__main__":
    try:
        test_emotion_singing()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
