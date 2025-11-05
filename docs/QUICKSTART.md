# Quick Start Guide

Get up and running with the ADAS Dashboard in minutes!

## TL;DR - For Experienced Users

```powershell
# 1. Download CARLA 0.9.15 from GitHub releases
# 2. Extract to C:\CARLA_0.9.15\

# 3. Setup
git clone https://github.com/mohammadopal1/ev-infotainment-system.git
cd ev-infotainment-system
.\setup.ps1

# 4. Install CARLA API
pip install C:\CARLA_0.9.15\WindowsNoEditor\PythonAPI\carla\dist\carla-0.9.15-cp38-cp38-win_amd64.whl

# 5. Run (in two terminals)
# Terminal 1:
C:\CARLA_0.9.15\WindowsNoEditor\CarlaUE4.exe

# Terminal 2:
.\run.ps1
```

## Step-by-Step Guide

### Step 1: Download CARLA (5 minutes)

1. Go to: https://github.com/carla-simulator/carla/releases/tag/0.9.15
2. Download: **CARLA_0.9.15.zip** (Windows, ~6GB)
3. Extract to: `C:\CARLA_0.9.15\`

### Step 2: Setup Project (2 minutes)

```powershell
# Clone repository
git clone https://github.com/mohammadopal1/ev-infotainment-system.git
cd ev-infotainment-system

# Run automated setup
.\setup.ps1
```

The setup script will:
- ✅ Check Python version
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Check CARLA API

### Step 3: Install CARLA Python API (1 minute)

```powershell
# For Python 3.8 (most common)
pip install C:\CARLA_0.9.15\WindowsNoEditor\PythonAPI\carla\dist\carla-0.9.15-cp38-cp38-win_amd64.whl

# For Python 3.7
pip install C:\CARLA_0.9.15\WindowsNoEditor\PythonAPI\carla\dist\carla-0.9.15-cp37-cp37m-win_amd64.whl
```

### Step 4: Launch! (30 seconds)

**Terminal 1** - Start CARLA:
```powershell
cd C:\CARLA_0.9.15\WindowsNoEditor
.\CarlaUE4.exe
```
Wait for the simulator window to appear (~10 seconds)

**Terminal 2** - Run Dashboard:
```powershell
cd path\to\ev-infotainment-system
.\run.ps1
```

### Step 5: Drive!

Use keyboard controls:
- **W** - Gas
- **S** - Brake
- **A/D** - Steer
- **SPACE** - Reverse
- **ESC** - Quit

## Troubleshooting

### "Python not found"
```powershell
# Install Python 3.8 from python.org
# Make sure to check "Add Python to PATH" during installation
```

### "CARLA module not found"
```powershell
# Verify CARLA API installation
pip list | Select-String carla

# Reinstall if needed
pip install C:\CARLA_0.9.15\WindowsNoEditor\PythonAPI\carla\dist\carla-0.9.15-cp38-cp38-win_amd64.whl --force-reinstall
```

### "Connection refused"
- CARLA must be running FIRST
- Wait until you see the CARLA simulator window
- Then start the dashboard

### "Low FPS / Lag"
Edit `src\adas_dashboard.py`:
```python
# Line ~477: Reduce NPC vehicles
npcs = spawn_npc_traffic(world, client, num_vehicles=10)  # Changed from 20
```

## Next Steps

- 📖 Read [INSTALLATION.md](INSTALLATION.md) for detailed configuration
- 📊 Check `logs/` directory for detection data
- 🎨 Customize detection thresholds in `src/adas_dashboard.py`
- 🔊 Add `beep.wav` to `assets/` for audio alerts

## Need Help?

- 📚 Full documentation: [README.md](../README.md)
- 🐛 Issues: https://github.com/mohammadopal1/ev-infotainment-system/issues
- 📧 Contact: See README for contact information
