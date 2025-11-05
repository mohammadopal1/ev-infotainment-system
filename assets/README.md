# Assets Directory

This directory contains model weights and optional audio files for the ADAS system.

## Files

### Required
- **yolov5n.pt**: YOLOv5 nano model weights for vehicle detection
  - This file is automatically downloaded by the application on first run
  - You can also manually download it from: https://github.com/ultralytics/yolov5/releases

### Optional
- **beep.wav**: Alert sound for warning notifications
  - Not included by default
  - Add your own beep.wav file to enable audio alerts
  - Any short WAV format audio file will work

## Usage

The ADAS dashboard will automatically:
1. Load the YOLOv5 model from this directory (or download if missing)
2. Check for beep.wav and enable audio alerts if present
3. Continue without audio if beep.wav is not found
