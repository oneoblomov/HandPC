# HCI (Hand Control Interface) - GNOME Shell Extension

[![CI](https://github.com/oneoblomov/HandPC/workflows/HCI%20Extension%20CI/CD%20Pipeline/badge.svg)](https://github.com/oneoblomov/HandPC/actions)
[![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![GNOME Shell 45](https://img.shields.io/badge/GNOME%20Shell-45-orange.svg)](https://wiki.gnome.org/)
[![GNOME Shell 46](https://img.shields.io/badge/GNOME%20Shell-46-orange.svg)](https://wiki.gnome.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A GNOME Shell extension for computer control with hand gestures. It allows you to perform mouse and keyboard operations with hand gestures using MediaPipe-based gesture recognition.

## Features

### Main Features

- Hand Gesture Control: Advanced hand detection with MediaPipe
- Modular Structure: Clean and maintainable code
- GNOME Integration: Full integration in the top bar
- Safe Mode: Prevents unwanted actions
- Tutorial Mode: Safe learning environment

### Supported Gestures

- Pinch: Cursor movement (thumb + index finger)
- Single Pinch: Left click
- Double Pinch: Right click
- Three Fingers: Drag and drop
- Fist to Open Hand: Win key/Application menu

### Security Features

- Screen edge protection
- Action frequency limitation
- Minimum confidence level control
- Safe testing with tutorial mode

## Installation

### Requirements

```bash
# Python dependencies
pip install opencv-python mediapipe pyautogui

# System requirements
sudo apt install python3-opencv python3-pip glib-2.0-dev
```

### Extension Installation

1. Copy extension files to the correct location
2. Compile schemas:

```bash
cd ~/.local/share/gnome-shell/extensions/hci@oneOblomov.dev/schemas
glib-compile-schemas .
```

3. Restart GNOME Shell: `Alt+F2` → `r` → `Enter`
4. Enable the extension from the Extensions app

## Usage

### First Startup

1. Click the HCI icon in the top bar
2. Turn on the "Gesture Control" switch
3. Wait for automatic calibration to complete
4. Test safely with tutorial mode

### Panel Menu

- Gesture Control: Main on/off
- Tutorial Mode: Safe test mode
- Safe Mode: Protection system
- Hand Calibration: Manual calibration
- Statistics: Usage data
- Log: Real-time status information

### Gesture Usage

1. Cursor Movement: Pinch with thumb and index finger, move
2. Left Click: Pinch and release
3. Right Click: Pinch twice quickly
4. Drag: Join three fingers, move
5. Win Menu: Change from fist to open hand

## Settings

### Main Settings

- Tutorial Mode: Safe test environment
- Safe Mode: Protection against unwanted actions
- Automatic Calibration: Initial calibration

### Sensitivity

- Cursor Smoothness: Movement smoothness (0.1-0.9)
- Pinch Sensitivity: Detection threshold (0.01-0.2)
- Minimum Confidence: Gesture confidence level (0.5-0.95)

### Security

- Click Delay: Time between clicks (0.1-2.0s)
- Max Actions/Second: Speed limit (1-10)
- Screen Edge Distance: Safe area (10-200px)

### Camera

- Camera Device: Camera to use (0-10)
- FPS: Frame rate (15-60)

## Troubleshooting

### Camera Not Opening

```bash
# Check camera access
ls /dev/video*

# Python test
python3 -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
```

### MediaPipe Error

```bash
# Reinstall MediaPipe
pip uninstall mediapipe
pip install mediapipe
```

### PyAutoGUI Issue

```bash
# For X11
export DISPLAY=:0

# For Wayland (limited support)
sudo apt install python3-xlib
```

### Extension Logs

```bash
# GNOME Shell logs
journalctl -f -o cat /usr/bin/gnome-shell

# HCI logs
tail -f ~/.local/share/gnome-shell/extensions/hci@oneOblomov.dev/logs/hci.log
```

## File Structure

```
hci@oneOblomov.dev/
├── metadata.json          # Extension metadata
├── extension.js          # Main GNOME JS code
├── prefs.js             # Settings page
├── gesture_service.py   # Python gesture service
├── gesture_core.py      # Modular gesture detection
├── schemas/             # GSettings schema
│   ├── *.gschema.xml
│   └── gschemas.compiled
├── logs/               # Log files
└── commands/          # Command files
```

## Development

### Debug Mode

```bash
# Extension logs
journalctl -f -o cat /usr/bin/gnome-shell | grep HCI

# Python service debug
python3 gesture_service.py /path/to/extension
```

### Adding New Gesture

1. Edit the `detect_gesture()` function in `gesture_core.py`
2. Add new action to the `ActionHandler` class
3. Update the settings schema

### Test

```bash
# Extension test
busctl --user call org.gnome.Shell /org/gnome/Shell org.gnome.Shell Eval s 'Extension.reloadExtension("hci@oneOblomov.dev")'

# Python test
python3 -c "from gesture_core import GestureDetector; print('OK')"
```

## Future Features

- [ ] Multi-hand support
- [ ] Custom gesture definition
- [ ] Voice command integration
- [ ] Full Wayland support
- [ ] Application-based gesture profiles

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Send a pull request

## License

MIT License - You can use and develop it freely.

## Support

- Issues: GitHub repository
- Wiki: Detailed documentation
- Discussions: Community support

---

Warning: This extension is still in development. Test safely with tutorial mode.
