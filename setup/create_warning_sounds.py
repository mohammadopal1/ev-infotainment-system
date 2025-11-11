#!/usr/bin/env python
"""
Create different warning sound files for the ADAS system.
Each warning type gets a distinct sound pattern.
"""
import numpy as np
import wave
import struct
import os

# Get project root and assets directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

def create_wav(filename, frequency, duration, sample_rate=44100):
    """Create a simple sine wave WAV file"""
    samples = int(sample_rate * duration)
    data = []
    for i in range(samples):
        value = int(32767.0 * np.sin(2.0 * np.pi * frequency * i / sample_rate))
        data.append(struct.pack('<h', value))
    
    filepath = os.path.join(ASSETS_DIR, filename)
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)   # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(data))
    
    return filepath

def create_double_beep(filename, frequency, beep_duration=0.15, gap=0.05, sample_rate=44100):
    """Create a double beep pattern (beep-gap-beep)"""
    beep_samples = int(sample_rate * beep_duration)
    gap_samples = int(sample_rate * gap)
    
    data = []
    
    # First beep
    for i in range(beep_samples):
        value = int(32767.0 * np.sin(2.0 * np.pi * frequency * i / sample_rate))
        data.append(struct.pack('<h', value))
    
    # Gap (silence)
    for i in range(gap_samples):
        data.append(struct.pack('<h', 0))
    
    # Second beep
    for i in range(beep_samples):
        value = int(32767.0 * np.sin(2.0 * np.pi * frequency * i / sample_rate))
        data.append(struct.pack('<h', value))
    
    filepath = os.path.join(ASSETS_DIR, filename)
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(data))
    
    return filepath

if __name__ == "__main__":
    print("Creating warning sound files...")
    print("=" * 60)
    
    # Blind spot warning: High-pitched short beep (urgent)
    file1 = create_wav('blindspot_warning.wav', 1200, 0.2)
    print(f"✓ Created: blindspot_warning.wav")
    print(f"  Type: High-pitched short beep (1200Hz, 0.2s)")
    print(f"  Use: Blind spot vehicle detection")
    
    # Proximity warning: Double beep (attention needed)
    file2 = create_double_beep('proximity_warning.wav', 800, 0.15, 0.08)
    print(f"\n✓ Created: proximity_warning.wav")
    print(f"  Type: Double beep pattern (800Hz)")
    print(f"  Use: Forward collision warning")
    
    # Lane departure: Lower-pitched continuous tone (gentle warning)
    file3 = create_wav('lane_warning.wav', 600, 0.35)
    print(f"\n✓ Created: lane_warning.wav")
    print(f"  Type: Lower-pitched continuous tone (600Hz, 0.35s)")
    print(f"  Use: Lane departure warning")
    
    print("\n" + "=" * 60)
    print(f"All warning sounds created in: {ASSETS_DIR}")
    print("\nSound differentiation:")
    print("  • Blind Spot: High pitch, short = URGENT")
    print("  • Proximity:  Double beep = ATTENTION")  
    print("  • Lane:       Low pitch, longer = GENTLE WARNING")
