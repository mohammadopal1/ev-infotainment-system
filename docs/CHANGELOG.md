# Changelog

All notable changes to the EV Infotainment System project will be documented in this file.

## [1.0.0] - 2025-11-05

### Added
- Initial release of ADAS Dashboard
- Real-time blind-spot detection using YOLOv5
- Lane departure warning system
- Forward collision warning with proximity detection
- 4-camera display (front, rear, left mirror, right mirror)
- Live vehicle telemetry (speed, throttle, brake, steering)
- Manual vehicle control with keyboard
- CSV data logging for all detections
- Comprehensive documentation and installation guide
- PowerShell setup and run scripts for Windows

### Features
- YOLOv5 object detection for vehicle identification
- Color-coded alert system (green/yellow/red)
- Real-time HUD with vehicle schematic
- Automatic NPC traffic generation
- Synchronous mode for stable simulation
- Optional audio alerts

### Technical Details
- CARLA Simulator 0.9.15 integration
- Python 3.7/3.8 compatibility
- PyTorch-based deep learning inference
- OpenCV for image processing
- Pygame for UI and controls

### Documentation
- README.md with quick start guide
- INSTALLATION.md with detailed setup instructions
- Project structure reorganization
- Separate CARLA installation from project files

## Development Notes

### Version History (Legacy Scripts)
- `carla_adas_project.py` - Current production version
- `carla_adas_project-v3.py` - Third iteration
- `carla_adas_project-v2.py` - Second iteration
- `carla_adas_project-v1.py` - Initial prototype

### Migration Notes
- Reorganized project structure to separate application from CARLA installation
- Moved main script to `src/adas_dashboard.py`
- Created `assets/` directory for models and media
- Created `logs/` directory for detection data
- Added proper path handling for cross-platform compatibility
