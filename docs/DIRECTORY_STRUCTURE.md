# Directory Structure Guide

This document explains how CARLA and your application should be organized.

## ⚠️ Important: Keep Directories Separate

Your workspace should have **TWO separate directories**:

```
📁 Your Computer
├── 📁 C:\CARLA_0.9.15\                          ← CARLA Installation (Download separately)
│   └── 📁 WindowsNoEditor\
│       ├── 🎮 CarlaUE4.exe                      ← Start simulator with this
│       ├── 📁 CarlaUE4\
│       ├── 📁 Engine\
│       ├── 📁 PythonAPI\                        ← Python API here
│       │   └── 📁 carla\
│       │       └── 📁 dist\
│       │           ├── carla-0.9.15-cp37-cp37m-win_amd64.whl
│       │           └── carla-0.9.15-cp38-cp38-win_amd64.whl
│       ├── 📁 Co-Simulation\
│       ├── 📁 HDMaps\
│       └── 📁 Plugins\
│
└── 📁 C:\Users\YourName\Documents\
    └── 📁 ev-infotainment-system\               ← This Repository (Your code)
        ├── 📁 src\
        │   └── 🐍 adas_dashboard.py
        ├── 📁 assets\
        │   ├── yolov5n.pt
        │   └── beep.wav (optional)
        ├── 📁 logs\
        │   └── detections_*.csv (generated)
        ├── 📁 docs\
        ├── 📄 requirements.txt
        ├── 📄 setup.ps1
        ├── 📄 run.ps1
        └── 📄 README.md
```

## ✅ DO: Correct Setup

```
Git Repository: ev-infotainment-system/
├── src/
├── assets/
├── logs/
├── docs/
├── requirements.txt
└── README.md

CARLA Installation: C:\CARLA_0.9.15\WindowsNoEditor\
├── CarlaUE4.exe
├── CarlaUE4/
├── Engine/
├── PythonAPI/
└── ...
```

## ❌ DON'T: Mixing Directories

**DO NOT** commit CARLA files to your repository:
```
❌ WRONG - Don't do this:
ev-infotainment-system/
├── src/
├── CarlaUE4/          ← ❌ Don't include CARLA files
├── Engine/            ← ❌ Don't include CARLA files
├── PythonAPI/         ← ❌ Don't include CARLA files
└── CarlaUE4.exe       ← ❌ Don't include CARLA executable
```

## 🔧 How to Use

### Starting CARLA
```powershell
# Navigate to CARLA installation
cd C:\CARLA_0.9.15\WindowsNoEditor
.\CarlaUE4.exe
```

### Running Your Application
```powershell
# Navigate to your project
cd C:\Users\YourName\Documents\ev-infotainment-system
.\run.ps1
```

## 📦 What Gets Committed to Git

### ✅ Include in Repository
- `src/` - Your Python scripts
- `assets/` - Model weights, media files
- `logs/README.md` - Documentation
- `docs/` - Installation guides
- `requirements.txt` - Dependencies list
- `setup.ps1`, `run.ps1` - Helper scripts
- `.gitignore` - Ignore rules

### ❌ Exclude from Repository (in .gitignore)
- `CarlaUE4/` - CARLA game files
- `Engine/` - Unreal Engine
- `PythonAPI/` - CARLA Python API
- `Co-Simulation/` - Co-sim tools
- `HDMaps/` - Map data
- `Plugins/` - CARLA plugins
- `*.exe` - Executables
- `venv/` - Virtual environment
- `logs/*.csv` - Generated logs

## 🌐 For Git Clone Users

When someone clones your repository:

1. They clone: `git clone https://github.com/mohammadopal1/ev-infotainment-system.git`
2. They get: Only your application files (small, ~10MB)
3. They download CARLA separately: From https://github.com/carla-simulator/carla/releases
4. They install CARLA API: `pip install path/to/carla.whl`
5. They run: Your application connects to their local CARLA installation

## 📊 Size Comparison

| Component | Size | Location |
|-----------|------|----------|
| Your Repository | ~10 MB | Git (tracked) |
| CARLA 0.9.15 | ~6 GB | User downloads separately |
| Python venv | ~500 MB | Generated locally (ignored) |
| Generated logs | Varies | Generated locally (ignored) |

## 🔄 Workflow Summary

```
┌─────────────────────────────────────────────────────────────┐
│ Developer Machine                                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📦 Git Repo (ev-infotainment-system)                       │
│  ├── Push/Pull your code changes                           │
│  └── Small, version controlled                              │
│                                                              │
│  🎮 CARLA (C:\CARLA_0.9.15\)                                │
│  ├── Downloaded once from official source                   │
│  ├── Not in version control                                 │
│  └── Same for all users                                     │
│                                                              │
│  🔗 Connection                                              │
│  └── Your app connects to CARLA via Python API (localhost)  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 💡 Benefits of This Structure

1. **Small Repository**: Only ~10MB instead of ~6GB
2. **Clean Separation**: Your code separate from CARLA
3. **Easy Updates**: Update CARLA without affecting your code
4. **Standard Practice**: Matches how external dependencies are handled
5. **Clear Ownership**: Your code vs. third-party simulator
