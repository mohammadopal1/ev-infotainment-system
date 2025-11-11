# ADAS Audio Alert System

The EV Infotainment System features distinct warning sounds for different driving scenarios to help drivers quickly identify the type of danger without looking at the dashboard.

## Warning Sound Types

### 1. Blind Spot Warning 🔊
- **Sound**: High-pitched short beep (1200Hz, 0.2s)
- **Pattern**: Single sharp beep
- **Urgency**: HIGH
- **Trigger**: Vehicle detected in left or right blind spot zone
- **File**: `assets/blindspot_warning.wav`

**When you hear this:** A vehicle is in your blind spot. Do not change lanes!

---

### 2. Proximity Warning 🔊🔊
- **Sound**: Double beep pattern (800Hz)
- **Pattern**: Beep-pause-beep
- **Urgency**: CRITICAL
- **Trigger**: Vehicle ahead is too close (< 8 meters)
- **File**: `assets/proximity_warning.wav`

**When you hear this:** You're too close to the vehicle ahead. Increase following distance or brake!

---

### 3. Lane Departure Warning 🔊~~~
- **Sound**: Lower-pitched continuous tone (600Hz, 0.35s)
- **Pattern**: Smooth continuous beep
- **Urgency**: MEDIUM
- **Trigger**: Vehicle crossing lane markings
- **File**: `assets/lane_warning.wav`

**When you hear this:** You're drifting out of your lane. Correct your steering!

---

## Audio System Features

### Intelligent Alert Management
- **Time-based persistence**: Warnings automatically clear 0.5 seconds after danger passes
- **No alert fatigue**: Sounds only play when danger is first detected, not continuously
- **Instant re-trigger**: If danger returns, alert plays immediately

### Sound Design Philosophy
1. **Frequency differentiation**: Each warning uses a distinct pitch
   - High pitch = Immediate action needed (blind spot)
   - Medium pitch = Critical attention (proximity)
   - Low pitch = Gentle correction (lane departure)

2. **Duration signaling**: Urgency level reflected in sound length
   - Shortest (0.2s) = Quick reaction needed
   - Medium (0.3s) = Sustained attention
   - Longer (0.35s) = Gradual correction

3. **Pattern recognition**: Unique patterns for quick identification
   - Single beep = Side danger
   - Double beep = Forward danger
   - Continuous tone = Position correction

### Fallback Behavior
If audio files are missing, the system will:
- Continue operating with visual warnings only
- Display message: "Audio alerts disabled"
- Not impact driving functionality

## Creating Custom Warning Sounds

You can replace the default warning sounds with your own:

1. Create WAV files with these names:
   - `blindspot_warning.wav`
   - `proximity_warning.wav`
   - `lane_warning.wav`

2. Place them in the `assets/` directory

3. Recommended specifications:
   - Format: WAV (PCM)
   - Sample Rate: 44100 Hz
   - Channels: Mono
   - Duration: 0.2 - 0.5 seconds
   - Volume: Normalized to prevent distortion

### Regenerating Default Sounds

To recreate the default warning sounds:
```bash
python setup/create_warning_sounds.py
```

This will generate all three warning sound files in the `assets/` directory.

## Technical Implementation

The audio system uses pygame.mixer for low-latency sound playback:

```python
audio_alerts = {
    "blindspot": pygame.mixer.Sound("assets/blindspot_warning.wav"),
    "proximity": pygame.mixer.Sound("assets/proximity_warning.wav"),
    "lane": pygame.mixer.Sound("assets/lane_warning.wav"),
}
```

Sounds are triggered at key detection points:
- **Blind spot**: In `detect_blindspot_frame()` when alert_level = "warn"
- **Proximity**: In `check_proximity()` when distance < 8m
- **Lane**: In `on_lane_invasion()` callback when lane marking crossed

## Troubleshooting

### No sound playing
1. Check that WAV files exist in `assets/` directory
2. Verify pygame.mixer initialized successfully
3. Check system volume and audio output device
4. Look for error messages in console output

### Wrong sound for warning type
- Verify file names match exactly (case-sensitive on Linux)
- Ensure files are valid WAV format
- Check console for "Audio alerts enabled: X/3 sounds loaded"

### Sounds too loud/quiet
- Adjust system volume
- Edit WAV files with audio editor to normalize volume
- Or modify the amplitude in `create_warning_sounds.py` and regenerate

## Future Enhancements

Potential improvements for the audio system:
- [ ] Voice alerts with spoken warnings
- [ ] Configurable sound themes (professional, minimal, futuristic)
- [ ] Volume adjustment settings
- [ ] Spatial audio (left speaker for left warnings, etc.)
- [ ] Adaptive volume based on vehicle speed
- [ ] Custom alert preferences per warning type
