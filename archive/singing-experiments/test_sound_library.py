"""Test different emotion sounds to find good singing voices."""

import os
import time
import sounddevice as sd
import soundfile as sf
from reachy_mini.motion.recorded_move import RecordedMoves

def play_sound(moves, sound_name):
    """Play an emotion sound."""
    audio_file = os.path.join(moves.local_path, f"{sound_name}.wav")
    if os.path.exists(audio_file):
        print(f"\n🔊 Playing: {sound_name}")
        audio_data, sample_rate = sf.read(audio_file)
        print(f"   Duration: {len(audio_data)/sample_rate:.2f}s")
        sd.play(audio_data, samplerate=sample_rate, blocking=True)
        time.sleep(0.5)
    else:
        print(f"❌ {sound_name} not found")

def main():
    print("🎵 Testing Emotion Sounds for Singing\n")
    print("="*60)
    
    moves = RecordedMoves('pollen-robotics/reachy-mini-emotions-library')
    
    # Test candidates for singing
    candidates = [
        ("DANCE SOUNDS", ["dance1", "dance2", "dance3"]),
        ("CHEERFUL/UPBEAT", ["cheerful1", "enthusiastic1", "enthusiastic2", "laughing1"]),
        ("VOCAL EXPRESSIONS", ["amazed1", "curious1", "surprised1", "oops1"]),
        ("CALM/MELODIC", ["calming1", "serenity1", "loving1", "welcoming1"]),
        ("PROUD/SUCCESS", ["proud1", "proud2", "success1", "grateful1"]),
    ]
    
    for category, sounds in candidates:
        print(f"\n{'='*60}")
        print(f"📂 {category}")
        print('='*60)
        
        for sound in sounds:
            try:
                play_sound(moves, sound)
            except Exception as e:
                print(f"   Error: {e}")
        
        choice = input("\n⏸️  Press ENTER to continue, 's' to skip category, 'q' to quit: ").strip().lower()
        if choice == 'q':
            break
        elif choice == 's':
            continue
    
    print("\n✅ Sound test complete!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user\n")
