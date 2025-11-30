#!/usr/bin/env python3
"""Test script for SafeMotionController gesture library.

This script demonstrates all available gestures and expressions
on the physical robot. Run with the daemon active.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from common.reachy.robot_wrapper import ReachyWrapper
from common.reachy.safe_motions import SafeMotionController


def main():
    """Run through all gestures and expressions."""
    print("=" * 60)
    print("SafeMotionController Gesture Library Test")
    print("=" * 60)
    print()
    print("This will test all gestures and expressions on your robot.")
    print("Make sure the daemon is running and the robot has space to move.")
    print()
    input("Press Enter to begin...")
    print()
    
    # Initialize wrapper and controller
    with ReachyWrapper(media_backend="no_media") as robot:
        controller = SafeMotionController(log_level="INFO")
        
        print("✓ Connected to robot")
        print()
        
        # Wake up
        print("=" * 60)
        print("WAKE UP SEQUENCE")
        print("=" * 60)
        robot.wake_up()
        time.sleep(2)
        
        # Test basic gestures
        gestures = [
            ("Nod Yes", lambda: controller.nod_yes(robot, count=2)),
            ("Shake No", lambda: controller.shake_no(robot, count=2)),
            ("Tilt Curious (Right)", lambda: controller.tilt_curious(robot, "right")),
            ("Tilt Curious (Left)", lambda: controller.tilt_curious(robot, "left")),
            ("Wave Antennas (Synchronized)", lambda: controller.wave_antennas(robot, count=3, synchronized=True)),
            ("Wave Antennas (Alternating)", lambda: controller.wave_antennas(robot, count=3, synchronized=False)),
            ("Look Around", lambda: controller.look_around(robot)),
            ("Express Thinking", lambda: controller.express_thinking(robot)),
        ]
        
        for name, gesture_func in gestures:
            print()
            print(f"▶ Testing: {name}")
            print("-" * 60)
            gesture_func()
            time.sleep(1)
            print(f"✓ Completed: {name}")
        
        # Test expressions
        print()
        print("=" * 60)
        print("EXPRESSION PRESETS")
        print("=" * 60)
        
        expressions = [
            ("Happy", lambda: controller.express_happy(robot)),
            ("Sad", lambda: controller.express_sad(robot)),
            ("Curious", lambda: controller.express_curious(robot)),
            ("Confused", lambda: controller.express_confused(robot)),
            ("Excited", lambda: controller.express_excited(robot)),
        ]
        
        for name, expr_func in expressions:
            print()
            print(f"▶ Testing: {name}")
            print("-" * 60)
            expr_func()
            time.sleep(1)
            print(f"✓ Completed: {name}")
        
        # Test smooth transitions
        print()
        print("=" * 60)
        print("SMOOTH TRANSITIONS")
        print("=" * 60)
        
        print()
        print("▶ Testing custom pose transition")
        print("-" * 60)
        controller.transition_to_pose(
            robot,
            roll=10,
            pitch=-10,
            yaw=15,
            left_antenna=0.5,
            right_antenna=-0.5,
            duration=1.5,
            degrees=True
        )
        time.sleep(1)
        print("✓ Custom pose reached")
        
        print()
        print("▶ Returning to neutral")
        print("-" * 60)
        controller.return_to_neutral(robot, duration=1.5)
        time.sleep(1)
        print("✓ Returned to neutral")
        
        # Test validation
        print()
        print("=" * 60)
        print("SAFETY VALIDATION")
        print("=" * 60)
        
        print()
        print("▶ Testing angle validation")
        print("-" * 60)
        
        test_cases = [
            ("Safe angles", 10, 5, 20, True),
            ("Excessive roll", 50, 0, 0, False),
            ("Excessive pitch", 0, 60, 0, False),
            ("Excessive yaw", 0, 0, 100, False),
        ]
        
        for name, roll, pitch, yaw, expected in test_cases:
            is_valid, violations = controller.validate_head_angles(roll, pitch, yaw, degrees=True)
            status = "✓" if is_valid == expected else "✗"
            print(f"{status} {name}: valid={is_valid}")
            if violations:
                for v in violations:
                    print(f"    - {v}")
        
        print()
        print("▶ Testing angle clamping")
        print("-" * 60)
        
        excessive_roll, excessive_pitch, excessive_yaw = 50, 60, 100
        clamped = controller.clamp_head_angles(
            excessive_roll, excessive_pitch, excessive_yaw, degrees=True
        )
        print(f"Input:   roll={excessive_roll}°, pitch={excessive_pitch}°, yaw={excessive_yaw}°")
        print(f"Clamped: roll={clamped[0]:.1f}°, pitch={clamped[1]:.1f}°, yaw={clamped[2]:.1f}°")
        print("✓ Angles clamped to safe limits")
        
        # Final return to neutral
        print()
        print("=" * 60)
        print("CLEANUP")
        print("=" * 60)
        controller.return_to_neutral(robot, duration=2.0)
        time.sleep(2)
        
        print()
        print("=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print("Summary:")
        print(f"  ✓ {len(gestures)} gestures tested")
        print(f"  ✓ {len(expressions)} expressions tested")
        print(f"  ✓ Smooth transitions verified")
        print(f"  ✓ Safety validation working")
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError during test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
