# macOS Setup Guide for RookieAI

## Required Permissions

RookieAI requires specific permissions on macOS to function properly. You must grant these permissions before running the application.

### 1. Screen Recording Permission

The application needs to capture your screen to detect targets.

**To grant permission:**
1. Open **System Preferences** → **Security & Privacy** → **Privacy**
2. Select **Screen Recording** from the left sidebar
3. Click the lock icon and enter your password
4. Check the box next to **Terminal** (if running from terminal) or **Python** (if running directly)
5. You may need to restart the application after granting permission

### 2. Accessibility Permission

The application needs to control mouse and keyboard input.

**To grant permission:**
1. Open **System Preferences** → **Security & Privacy** → **Privacy**
2. Select **Accessibility** from the left sidebar
3. Click the lock icon and enter your password
4. Check the box next to **Terminal** (if running from terminal) or **Python** (if running directly)
5. You may need to restart the application after granting permission

### 3. Input Monitoring Permission (macOS 10.15+)

Required for keyboard input detection.

**To grant permission:**
1. Open **System Preferences** → **Security & Privacy** → **Privacy**
2. Select **Input Monitoring** from the left sidebar
3. Click the lock icon and enter your password
4. Check the box next to **Terminal** (if running from terminal) or **Python** (if running directly)

## Installation Instructions

### Prerequisites

1. **Python 3.10 or higher**
   ```bash
   python3 --version
   ```

2. **Tkinter support** (required for GUI components)
   ```bash
   brew install python-tk@3.12
   ```

3. **Poetry** (recommended) or pip
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

### Installation Steps

1. **Clone or extract the project**
   ```bash
   cd RookieAI_yolov8_macos
   ```

2. **Install dependencies using Poetry**
   ```bash
   poetry install
   ```

   **Or using pip**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   poetry run python RookieAI.py
   ```

   **Or with pip**
   ```bash
   python3 RookieAI.py
   ```

## macOS-Specific Features

### Cross-Platform Mouse Control

The application automatically detects macOS and uses appropriate mouse control methods:

- **Primary**: Quartz framework (pyobjc-framework-Quartz) for precise control
- **Fallback**: pyautogui for basic mouse operations
- **Alternative**: mouse library for additional compatibility

### Movement Methods

On macOS, the following movement methods are available:

- **cross_platform**: Recommended for macOS (uses Quartz framework)
- **mouse**: Alternative cross-platform method
- **win32**: Windows-only (disabled on macOS)
- **飞易来**: Hardware-specific (disabled on macOS)
- **KmBoxNet**: Hardware-specific (disabled on macOS)
- **Logitech**: Hardware-specific (disabled on macOS)

## Troubleshooting

### Permission Issues

If you encounter permission errors:

1. **Check System Preferences**: Ensure all required permissions are granted
2. **Restart the application**: Some permissions require a restart to take effect
3. **Run from Terminal**: Sometimes running from Terminal helps with permission detection

### Performance Issues

1. **Close unnecessary applications**: Free up system resources
2. **Check Activity Monitor**: Ensure no other applications are using excessive CPU
3. **Adjust YOLO confidence**: Lower confidence values may improve performance

### Common Errors

**"Screen capture failed"**
- Grant Screen Recording permission in System Preferences

**"Mouse control not working"**
- Grant Accessibility permission in System Preferences

**"Keyboard detection failed"**
- Grant Input Monitoring permission in System Preferences

**"Module not found" errors**
- Ensure all dependencies are installed: `poetry install` or `pip3 install -r requirements.txt`

## Hardware Limitations

The following hardware-specific features are not available on macOS:

- 飞易来 USB mouse control
- KmBoxNet hardware control
- Logitech driver integration
- Windows-specific DLL functions

These limitations do not affect core functionality, as the application uses cross-platform alternatives.

## Performance Optimization

### Recommended Settings for macOS

1. **Movement Method**: Set to "cross_platform" for best performance
2. **Process Mode**: "多进程模式" (Multi-process) recommended for better performance
3. **YOLO Confidence**: Start with 0.5-0.7 and adjust based on performance

### System Requirements

- **macOS**: 10.15 (Catalina) or later
- **RAM**: 8GB minimum, 16GB recommended
- **CPU**: Intel i5 or Apple M1/M2 or better
- **GPU**: Dedicated GPU recommended for YOLO inference

## Support

If you encounter issues specific to macOS:

1. Check this documentation first
2. Verify all permissions are granted
3. Ensure you're using the latest version of the application
4. Check the console output for specific error messages

The application maintains full compatibility with Windows while adding macOS support through cross-platform libraries and conditional platform detection.
