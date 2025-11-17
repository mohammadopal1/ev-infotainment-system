#!/usr/bin/env python
"""
ADAS Configuration and Initialization
Contains all configuration constants, model loading, and audio setup.
"""

import os
import csv
import datetime
import torch
import pygame

# Get project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")

# Create directories if they don't exist
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# Performance settings
DETECTION_SKIP_FRAMES = 3
TARGET_FPS = 30
WARNING_CLEAR_TIME = 0.5
VEHICLE_KEYWORDS = ("car", "truck", "bus")

# YOLOv5 Model
print("Loading YOLOv5 model...")
model = torch.hub.load('ultralytics/yolov5:v7.0', 'yolov5n',
                       pretrained=True, trust_repo=True)
model.conf = 0.30
model.iou = 0.45
print("Model loaded!")

# CSV logging
log_filename = os.path.join(LOGS_DIR, f"detections_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
log_file = open(log_filename, "w", newline="")
writer = csv.writer(log_file)
writer.writerow(["time", "vehicle_detected", "confidence", "side",
                 "alert_level", "lane_departure", "distance_m", "rel_speed_mps"])
print(f"Logging to: {log_filename}")

# Audio System
pygame.init()
audio_alerts = {
    "blindspot": None,
    "proximity": None,
    "lane": None,
}

try:
    pygame.mixer.init()
    sound_files = {
        "blindspot": "blindspot_warning.wav",
        "proximity": "proximity_warning.wav",
        "lane": "lane_warning.wav",
    }
    sounds_loaded = 0
    for alert_type, filename in sound_files.items():
        sound_path = os.path.join(ASSETS_DIR, filename)
        if os.path.exists(sound_path):
            audio_alerts[alert_type] = pygame.mixer.Sound(sound_path)
            sounds_loaded += 1
    if sounds_loaded > 0:
        print(f"Audio alerts enabled: {sounds_loaded}/3 warning sounds loaded")
    else:
        print("Audio alerts disabled (no warning sound files found in assets/)")
        print("  Expected files: blindspot_warning.wav, proximity_warning.wav, lane_warning.wav")
except Exception as e:
    print(f"Audio initialization failed: {e}")
