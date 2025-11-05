# Detection Logs

This directory contains CSV files with detection logs from the ADAS system.

## Log File Format

Each run generates a timestamped CSV file: `detections_YYYYMMDD_HHMMSS.csv`

### Columns:
- **time**: Timestamp of detection
- **vehicle_detected**: Type of vehicle detected (car, truck, bus)
- **confidence**: YOLOv5 detection confidence (0-1)
- **side**: Camera location (left, right, front, rear)
- **alert_level**: Alert severity (clear, near, warn)
- **lane_departure**: Lane departure event indicator
- **distance_m**: Distance to detected vehicle in meters
- **rel_speed_mps**: Relative speed in meters per second

## Usage

Logs are automatically generated when running the ADAS dashboard. You can analyze these files for:
- Detection performance analysis
- Alert frequency statistics
- Driving behavior patterns
- System validation and testing
