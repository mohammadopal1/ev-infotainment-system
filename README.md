# EV Infotainment System

Electric Vehicle In-Vehicle Cameras and Onboard Display for Driving Safety System - An Advanced Driver Assistance System (ADAS) dashboard built with CARLA Simulator.

![ADAS Dashboard](https://img.shields.io/badge/CARLA-0.9.15-blue)
![Python](https://img.shields.io/badge/Python-3.7%20%7C%203.8-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🚗 Features

- **Real-time Blind Spot Detection**: Uses YOLOv5 for vehicle detection in left and right mirrors
- **Lane Departure Warning**: Visual alerts when crossing lane markings
- **Forward Collision Warning**: Proximity detection for vehicles ahead
- **Multi-Sound Audio Alerts**: Distinct warning sounds for each scenario (blind spot, proximity, lane)
- **Intelligent Warning System**: Auto-clearing warnings 0.5s after danger passes
- **4-Camera Display**: Front, rear, and side mirror views
- **Live Vehicle Telemetry**: Speed, throttle, brake, and steering indicators
- **Manual Vehicle Control**: Keyboard-based driving interface
- **CSV Data Logging**: Records all detections for analysis
- **Fixed Tesla Model 3**: Consistent vehicle for testing and demonstration

## 📁 Project Structure

This repository contains only the custom application files. CARLA Simulator must be downloaded separately.

### Your Application Files (This Repository)
```
ev-infotainment-system/
├── src/
│   └── adas_dashboard.py          # Main ADAS dashboard application
├── assets/
│   ├── yolov5n.pt                 # YOLOv5 model weights
│   ├── blindspot_warning.wav      # Blind spot alert sound
│   ├── proximity_warning.wav      # Forward collision alert sound
│   ├── lane_warning.wav           # Lane departure alert sound
│   └── README.md                  # Assets documentation
├── logs/
│   ├── detections_*.csv           # Generated detection logs (auto-created)
│   └── README.md                  # Logs documentation
├── docs/
│   ├── INSTALLATION.md            # Detailed installation guide
│   ├── QUICKSTART.md              # Quick start guide
│   ├── AUDIO_SYSTEM.md            # Audio alert system documentation
│   └── DIRECTORY_STRUCTURE.md     # Project structure reference
├── setup/
│   ├── setup.ps1                  # Automated setup script
│   ├── run.ps1                    # Quick launch script
│   ├── check_carla_files.ps1      # CARLA verification script
│   └── create_warning_sounds.py   # Generate audio alert files
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore rules
├── CHANGELOG.md                   # Version history
├── LICENSE                        # MIT License
└── README.md                      # This file
```

### CARLA Simulator Location

CARLA 0.9.15 files are located in the `CARLA_0.9.15\WindowsNoEditor\` subdirectory of this repository.

**Current Directory Structure:**
```
ev-infotainment-system/
├── src/                          # Your application code
├── assets/                       # Application assets
├── logs/                         # Generated logs
├── docs/                         # Documentation
├── setup/                        # Setup and launch scripts
│   ├── setup.ps1                 # Automated setup script
│   ├── run.ps1                   # Quick launch script
│   └── check_carla_files.ps1     # CARLA verification script
├── CARLA_0.9.15/                # CARLA Simulator (ignored by git)
│   └── WindowsNoEditor/         # Main CARLA directory
│       ├── CarlaUE4.exe         # CARLA Simulator executable ⭐
│       ├── CarlaUE4/            # Game content
│       │   ├── Binaries/
│       │   ├── Config/
│       │   ├── Content/
│       │   └── Plugins/
│       ├── Engine/              # Unreal Engine files
│       │   ├── Binaries/
│       │   ├── Config/
│       │   ├── Content/
│       │   └── Plugins/
│       ├── PythonAPI/           # Python API ⭐
│       │   ├── carla/
│       │   │   └── dist/        # Python wheel files
│       │   │       ├── carla-0.9.15-cp37-cp37m-win_amd64.whl
│       │   │       └── carla-0.9.15-cp38-cp38-win_amd64.whl
│       │   ├── examples/
│       │   └── util/
│       ├── Co-Simulation/       # Co-simulation tools
│       ├── HDMaps/              # HD map data
│       └── Plugins/             # Additional plugins
└── requirements.txt
```

**Important Notes:**
- ✅ CARLA files are in `CARLA_0.9.15\WindowsNoEditor\` subdirectory
- ✅ The entire `CARLA_0.9.15\` directory is ignored by git (see `.gitignore`)
- ✅ Users cloning this repo need to download CARLA 0.9.15 separately
- ❌ CARLA files (~18GB) are NOT committed to the repository

## 🔧 Prerequisites

- **Operating System**: Windows 10/11 (64-bit)
- **Python**: 3.7 or 3.8 (for CARLA 0.9.15 compatibility)
- **GPU**: NVIDIA GPU with CUDA support (recommended)
- **RAM**: Minimum 8GB
- **CARLA Simulator**: 0.9.15

## 🚀 Quick Start

### 1. Download CARLA Simulator

Download CARLA 0.9.15 from the official repository:
- **Release Page**: https://github.com/carla-simulator/carla/releases/tag/0.9.15
- **Download**: `CARLA_0.9.15.zip` (Windows)

Extract to the `CARLA_0.9.15\WindowsNoEditor\` directory in this repository.

**Important Notes:**
- Extract CARLA to: `ev-infotainment-system\CARLA_0.9.15\WindowsNoEditor\`
- The `CARLA_0.9.15\` directory is already in `.gitignore` (won't be committed)
- Total size: ~18GB (excluded from git repository)
- If you cloned this repo, you need to download and extract CARLA separately

### 2. Clone This Repository

```powershell
git clone https://github.com/mohammadopal1/ev-infotainment-system.git
cd ev-infotainment-system
```

### 3. Set Up Python Environment

```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Install CARLA Python API from the local CARLA installation
pip install .\CARLA_0.9.15\WindowsNoEditor\PythonAPI\carla\dist\carla-0.9.15-cp38-cp38-win_amd64.whl
```

**Note**: Choose the correct `.whl` file matching your Python version:
- Python 3.7: `carla-0.9.15-cp37-cp37m-win_amd64.whl`
- Python 3.8: `carla-0.9.15-cp38-cp38-win_amd64.whl`

### 4. Run the Application

**Terminal 1** - Start CARLA Simulator:
```powershell
cd CARLA_0.9.15\WindowsNoEditor
.\CarlaUE4.exe
```

**Terminal 2** - Run ADAS Dashboard:
```powershell
python src\adas_dashboard.py
```

Or use the convenient launcher script:
```powershell
.\setup\run.ps1
```

## 🎮 Controls

| Key | Action |
|-----|--------|
| **W** | Throttle (Accelerate) |
| **S** | Brake |
| **A** | Steer Left |
| **D** | Steer Right |
| **SPACE** | Toggle Reverse |
| **ESC** | Exit Application |

## 📊 Dashboard Elements

### Main Display Components

1. **Vehicle Schematic**: Central visualization showing blind-spot zones
   - **Left/Right Bars**: Color-coded blind spot alerts
     - 🟢 Green: Clear
     - 🟡 Yellow: Vehicle nearby
     - 🔴 Red: Warning - vehicle too close
   
2. **Camera Feeds**: Real-time views from 4 cameras
   - Left Mirror
   - Right Mirror
   - Front Camera
   - Rear Camera

3. **Alert Status Panel**: Shows current alert levels
   - Left blind spot status
   - Right blind spot status
   - Proximity alert
   - Lane departure status

4. **Vehicle Controls Display**: Real-time telemetry
   - Speed (km/h)
   - Throttle bar
   - Brake bar
   - Steering bar
   - Reverse indicator

## 🔊 Audio Alert System

The system features intelligent audio warnings with distinct sounds for each scenario:

### Warning Sound Types

| Scenario | Sound Pattern | Urgency | Description |
|----------|--------------|---------|-------------|
| **Blind Spot** | High-pitched short beep (1200Hz) | 🔴 HIGH | Single sharp beep when vehicle in blind spot |
| **Proximity** | Double beep pattern (800Hz) | 🔴 CRITICAL | Beep-pause-beep when too close to vehicle ahead |
| **Lane Departure** | Lower continuous tone (600Hz) | 🟡 MEDIUM | Smooth tone when crossing lane markings |

### Smart Alert Management
- ✅ **Time-based persistence**: Warnings auto-clear 0.5s after danger passes
- ✅ **No alert fatigue**: Sounds play once when danger detected, not continuously
- ✅ **Instant re-trigger**: Alert plays immediately if danger returns
- ✅ **Distinct frequencies**: Quick identification without looking at screen

### Setup Audio Files

Audio files are automatically created during setup. To regenerate:
```powershell
python setup\create_warning_sounds.py
```

For custom sounds, see: [Audio System Documentation](docs/AUDIO_SYSTEM.md)

## 🧠 Technology Stack

- **Simulator**: CARLA 0.9.15
- **Object Detection**: YOLOv5 (PyTorch)
- **Computer Vision**: OpenCV
- **GUI**: Pygame + OpenCV
- **Language**: Python 3.7/3.8

## 📝 Data Logging

Detection logs are automatically saved to `logs/detections_YYYYMMDD_HHMMSS.csv` with the following fields:

- `time`: Timestamp of detection
- `vehicle_detected`: Vehicle type (car, truck, bus)
- `confidence`: Detection confidence score
- `side`: left/right/front/rear
- `alert_level`: clear/near/warn
- `lane_departure`: Lane invasion event
- `distance_m`: Distance to detected vehicle
- `rel_speed_mps`: Relative speed

## 🔍 Configuration

### Adjust NPC Traffic

Edit `src/adas_dashboard.py` - line ~460:
```python
npcs = spawn_npc_traffic(world, client, num_vehicles=20)  # Change this number
```

### Detection Thresholds

Edit detection sensitivity in `src/adas_dashboard.py`:
```python
# Line ~24-26
model.conf = 0.25  # Confidence threshold (0-1)
model.iou = 0.45   # IoU threshold for NMS
```

### Camera Settings

Modify camera parameters around line ~440:
```python
cam_bp.set_attribute('image_size_x', '320')
cam_bp.set_attribute('image_size_y', '240')
cam_bp.set_attribute('fov', '100')
```

## ⚠️ Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'carla'"**
- Install the CARLA Python API wheel matching your Python version
- Check: `pip list | Select-String carla`

**"Connection refused" errors**
- Ensure CarlaUE4.exe is running before starting the dashboard
- Verify CARLA is on port 2000 (default)

**Low FPS / Performance Issues**
- Reduce NPC vehicle count
- Lower CARLA graphics settings
- Use dedicated NVIDIA GPU

**Missing beep.wav warning**
- Optional feature - app works without it
- Add `beep.wav` to `assets/` for audio alerts

See [docs/INSTALLATION.md](docs/INSTALLATION.md) for detailed troubleshooting.

## 📚 Documentation

- [Directory Structure Guide](docs/DIRECTORY_STRUCTURE.md) - **Read this first!** Explains how to organize CARLA and your project
- [Installation Guide](docs/INSTALLATION.md) - Detailed setup instructions
- [Quick Start Guide](docs/QUICKSTART.md) - Get running in minutes
- [CARLA Documentation](https://carla.readthedocs.io/)
- [YOLOv5 Documentation](https://docs.ultralytics.com/)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CARLA Team**: For the excellent autonomous driving simulator
- **Ultralytics**: For YOLOv5 object detection
- **OpenCV Community**: For computer vision tools

## 📧 Contact

**Project Link**: https://github.com/mohammadopal1/ev-infotainment-system

---

**Note**: This project is for educational and research purposes. It demonstrates ADAS concepts using simulation and should not be used for real-world autonomous driving applications without proper safety validation.
