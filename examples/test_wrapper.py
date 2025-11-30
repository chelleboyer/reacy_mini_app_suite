#!/usr/bin/env python3
"""Test the ReachyWrapper with real hardware."""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from common.reachy.robot_wrapper import ReachyWrapper


def main():
    """Test basic wrapper functionality with real hardware."""
    print("=" * 60)
    print("  REACHY WRAPPER TEST - Real Hardware")
    print("=" * 60)
    
    print("\n[1/6] Creating wrapper instance...")
    wrapper = ReachyWrapper(media_backend="no_media")
    print("✓ Wrapper created\n")
    
    print("[2/6] Connecting to daemon...")
    try:
        wrapper.connect()
        print("✓ Connected successfully!\n")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return 1
    
    try:
        print("[3/6] Getting current position...")
        head_joints, antenna_joints = wrapper.get_joint_positions()
        print(f"✓ Head joints: {[f'{j:.3f}' for j in head_joints]}")
        print(f"✓ Antenna joints: {[f'{j:.3f}' for j in antenna_joints]}\n")
        
        print("[4/6] Testing head movement (roll)...")
        wrapper.move_head(roll=15, duration=1.0)
        time.sleep(1.2)
        print("✓ Roll right complete!")
        
        wrapper.move_head(roll=-15, duration=1.0)
        time.sleep(1.2)
        print("✓ Roll left complete!")
        
        wrapper.move_head(roll=0, duration=1.0)
        time.sleep(1.2)
        print("✓ Return to neutral complete!\n")
        
        print("[5/6] Testing antenna movement...")
        wrapper.move_antennas(left=0.5, right=-0.5, duration=1.0)
        time.sleep(1.2)
        print("✓ Antennas moved!")
        
        wrapper.move_antennas(left=0.0, right=0.0, duration=1.0)
        time.sleep(1.2)
        print("✓ Antennas returned to neutral!\n")
        
        print("[6/6] Testing wake_up animation...")
        wrapper.wake_up()
        time.sleep(2.5)
        print("✓ Wake up complete!\n")
        
    except KeyboardInterrupt:
        print("\n⚠ Test interrupted by user")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        print("\nDisconnecting...")
        wrapper.disconnect()
        print("✓ Disconnected")
    
    print("\n" + "=" * 60)
    print("  🎉 WRAPPER TEST: SUCCESS!")
    print("=" * 60)
    print("\n✓ ReachyWrapper implementation working")
    print("✓ All basic movements tested")
    print("✓ Ready for application development\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
