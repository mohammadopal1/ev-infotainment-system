# Installation Guide

## Prerequisites
- Windows 10/11 (64-bit)
- Python 3.7 or 3.8 (CARLA 0.9.15 compatibility)
- NVIDIA GPU with CUDA support (recommended)
- Minimum 8GB RAM

## Step 1: Download CARLA Simulator

1. Download CARLA 0.9.15 for Windows from the official release page:
   - https://github.com/carla-simulator/carla/releases/tag/0.9.15
   - Download: `CARLA_0.9.15.zip` (Windows version, ~6GB)

2. Extract the CARLA archive to a location of your choice (e.g., `C:\CARLA_0.9.15\`)

**Expected Directory Structure After Extraction:**
```
C:\CARLA_0.9.15\
└── WindowsNoEditor\              # Main CARLA directory
    ├── CarlaUE4.exe              # Run this to start simulator
    ├── CarlaUE4\                 # Game content folder
    ├── Engine\                   # Unreal Engine files
    ├── PythonAPI\                # Python API location
    │   └── carla\
    │       └── dist\             # Contains .whl files for installation
    ├── Co-Simulation\
    ├── HDMaps\
    └── Plugins\
```

**Important:** Keep CARLA in a separate directory, NOT inside your project repository.

## Step 2: Install Python Dependencies

1. Create a virtual environment (recommended):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. Install Python packages:
   ```powershell
   pip install -r requirements.txt
   ```

3. Install CARLA Python API (replace with your CARLA installation path):
   ```powershell
   # Example for Python 3.8
   pip install C:\CARLA_0.9.15\WindowsNoEditor\PythonAPI\carla\dist\carla-0.9.15-cp38-cp38-win_amd64.whl
   ```

   **Note**: Choose the correct `.whl` file matching your Python version:
   - Python 3.7: `carla-0.9.15-cp37-cp37m-win_amd64.whl`
   - Python 3.8: `carla-0.9.15-cp38-cp38-win_amd64.whl`

## Step 3: Verify Installation

Test the CARLA Python API:
```powershell
python -c "import carla; print(carla.__version__)"
```

## Step 4: Run the ADAS Dashboard

1. Start the CARLA simulator:
   ```powershell
   # Navigate to your CARLA installation directory
   cd C:\CARLA_0.9.15\WindowsNoEditor
   .\CarlaUE4.exe
   ```

2. Wait for CARLA to fully load (you should see the simulator window)

3. In a new terminal, run the ADAS dashboard:
   ```powershell
   # Navigate to the project directory
   cd path\to\ev-infotainment-system
   python src\adas_dashboard.py
   ```

## Controls

- **W**: Throttle (accelerate)
- **S**: Brake
- **A**: Steer left
- **D**: Steer right
- **SPACE**: Toggle reverse
- **ESC**: Exit application

## Troubleshooting

### "ModuleNotFoundError: No module named 'carla'"
- Ensure you've installed the CARLA Python API wheel file
- Verify your Python version matches the wheel file

### "Connection refused" or "Timeout" errors
- Make sure CarlaUE4.exe is running before starting the dashboard
- Check that CARLA is listening on port 2000 (default)

### Low FPS or performance issues
- Reduce the number of NPC vehicles (edit `num_vehicles` parameter in the script)
- Lower CARLA graphics settings
- Ensure you have a dedicated GPU

### "beep.wav not found" warning
- This is optional; the app will work without sound alerts
- You can add a beep.wav file to the assets/ directory for audio alerts

## Optional: Audio Alerts

To enable audio alerts, place a `beep.wav` file in the `assets/` directory.
