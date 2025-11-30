#!/usr/bin/env python3
"""Simple demo showing Reachy Mini basic movements.

This is a minimal example of using the ReachyWrapper for basic robot control.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from common.reachy.robot_wrapper import ReachyWrapper


def main():
    """Run a simple demo sequence."""
    print("\n🤖 Starting Reachy Mini Demo\n")
    
    with ReachyWrapper(media_backend="no_media") as robot:
        print("✓ Connected to Reachy Mini\n")
        
        # Wake up
        print("Waking up...")
        robot.wake_up()
        time.sleep(2)
        
        # Look around
        print("Looking left...")
        robot.move_head(yaw=-30, duration=1.5)
        time.sleep(1.5)
        
        print("Looking right...")
        robot.move_head(yaw=30, duration=1.5)
        time.sleep(1.5)
        
        print("Looking forward...")
        robot.move_head(yaw=0, duration=1.0)
        time.sleep(1.0)
        
        # Nod
        print("Nodding...")
        for _ in range(2):
            robot.move_head(pitch=-10, duration=0.5)
            time.sleep(0.5)
            robot.move_head(pitch=10, duration=0.5)
            time.sleep(0.5)
        robot.move_head(pitch=0, duration=0.5)
        time.sleep(0.5)
        
        # Wave antennas
        print("Waving antennas...")
        for _ in range(3):
            robot.move_antennas(left=0.8, right=-0.8, duration=0.4)
            time.sleep(0.4)
            robot.move_antennas(left=-0.8, right=0.8, duration=0.4)
            time.sleep(0.4)
        robot.move_antennas(left=0, right=0, duration=0.5)
        time.sleep(0.5)
        
        print("\n✓ Demo complete!\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo stopped by user\n")
    except Exception as e:
        print(f"\n✗ Error: {e}\n")
        sys.exit(1)
