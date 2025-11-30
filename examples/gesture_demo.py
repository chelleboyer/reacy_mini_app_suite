#!/usr/bin/env python3
"""Interactive gesture demo showcasing SafeMotionController capabilities.

A friendly demonstration of expressions and gestures.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from common.reachy.robot_wrapper import ReachyWrapper
from common.reachy.safe_motions import SafeMotionController


def main():
    """Run interactive gesture demo."""
    print("=" * 60)
    print("Reachy Mini - Gesture Demo")
    print("=" * 60)
    print()
    
    with ReachyWrapper(media_backend="no_media") as robot:
        controller = SafeMotionController()
        
        print("✓ Connected to robot")
        print()
        print("Starting demo sequence...")
        print()
        
        # Wake up
        print("▶ Waking up...")
        robot.wake_up()
        time.sleep(2)
        
        # Greeting sequence
        print("▶ Saying hello...")
        controller.wave_antennas(robot, count=2, synchronized=True)
        controller.nod_yes(robot, count=1)
        time.sleep(1)
        
        # Show curiosity
        print("▶ Looking around curiously...")
        controller.express_curious(robot)
        controller.look_around(robot)
        time.sleep(1)
        
        # Show excitement
        print("▶ Getting excited!")
        controller.express_excited(robot)
        time.sleep(1)
        
        # Think about something
        print("▶ Thinking...")
        controller.express_thinking(robot)
        time.sleep(1)
        
        # Show happiness
        print("▶ Feeling happy!")
        controller.express_happy(robot)
        time.sleep(1)
        
        # Show confusion
        print("▶ Wait, what?")
        controller.express_confused(robot)
        time.sleep(1)
        
        # Shake no
        print("▶ No, no, no...")
        controller.shake_no(robot, count=2)
        time.sleep(1)
        
        # Show sadness
        print("▶ Feeling a bit sad...")
        controller.express_sad(robot)
        time.sleep(1)
        
        # Cheer up
        print("▶ But then feeling better!")
        controller.express_happy(robot)
        time.sleep(1)
        
        # Wave goodbye
        print("▶ Saying goodbye...")
        controller.wave_antennas(robot, count=3, synchronized=True)
        controller.nod_yes(robot, count=1)
        time.sleep(1)
        
        # Return to neutral
        print("▶ Returning to neutral...")
        controller.return_to_neutral(robot, duration=2.0)
        time.sleep(2)
        
        print()
        print("=" * 60)
        print("Demo complete!")
        print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
