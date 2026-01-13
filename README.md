# Star Scout Bot

An automated bot for FC Mobile's Star Scout feature that helps you find players within a specific OVR (Overall Rating) range.
### PS: "I haven't personally gotten a 114-115 OVR, so idk if the script stops as intended.....

## Features

- 🤖 Automated player scouting workflow
- 🎯 Target specific OVR ranges
- 🔍 OCR-based screen state detection
- 📱 ADB integration for Android device control
- 🔊 Alert notifications when target players are found
- 🐛 Debug mode for troubleshooting

## Prerequisites

- Python 3.7+
- Android device or emulator with ADB debugging enabled
- ADB (Android Debug Bridge) installed on your system
- Tesseract OCR installed on your system

### Installing Prerequisites

#### ADB Installation

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install android-tools-adb android-tools-fastboot
```

**Fedora/RHEL:**
```bash
sudo dnf install android-tools
```

**Arch Linux:**
```bash
sudo pacman -S android-tools
```

**macOS:**
```bash
brew install android-platform-tools
```

**Windows:**
Download the SDK Platform-Tools for Windows from [developer.android.com](https://developer.android.com/tools/releases/platform-tools) and extract it to a folder. Add that folder to your system PATH environment variable.

#### Tesseract OCR Installation

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**Fedora/RHEL:**
```bash
sudo dnf install tesseract
```

**Arch Linux:**
```bash
sudo pacman -S tesseract
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download the installer from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki). Run the installer and ensure the installation directory is added to your system PATH environment variable.

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Not-Dhanraj/Star-Scout.git
cd Star-Scout
```

2. **Create and activate a virtual environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Linux/macOS
# Or on Windows: .venv\Scripts\activate
```

3. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

**Note:** Always activate the virtual environment before running the bot:
```bash
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

## Setup

### 1. Enable USB Debugging on Your Android Device

### 2. Connect Your Device via ADB

#### USB Connection (Recommended)

1. Connect your device to your computer via USB cable
2. When prompted on your device, allow USB debugging
3. Verify the connection:
```bash
adb devices
```
You should see your device listed with "device" status.

### 3. Determine Screen Coordinates

The bot needs precise tap coordinates for various buttons and areas. Here's how to find them:

#### Method 1: Using `adb shell getevent` (Most Accurate)

1. Enable pointer location on your device:
```bash
adb shell settings put system pointer_location 1
```

2. Monitor touch events:
```bash
adb shell getevent -l
```

3. Tap on the screen element you want to capture
4. Look for lines containing `ABS_MT_POSITION_X` and `ABS_MT_POSITION_Y`
5. The hexadecimal values need to be converted to decimal coordinates

Example output:
```
/dev/input/event2: EV_ABS       ABS_MT_POSITION_X    000004a0
/dev/input/event2: EV_ABS       ABS_MT_POSITION_Y    0000039e
```

Convert hex to decimal: `0x4a0` = 1184, `0x39e` = 926

6. Disable pointer location when done:
```bash
adb shell settings put system pointer_location 0
```

#### Method 2: Using Developer Options (Easier)

1. Enable **Settings** → **Developer Options** → **Show Taps**
2. Take a screenshot:
```bash
adb exec-out screencap -p > screen.png
```
3. Tap the element you want coordinates for
4. The tap location will be visible on screen
5. Use an image viewer to check pixel coordinates

#### Method 3: Using `adb shell input` (Quick Test)

Test if coordinates work:
```bash
adb shell input tap X Y
```
Replace X and Y with your coordinates. Adjust until the tap hits the right spot.

### 4. Configure the Bot

Edit `scout/config.py` to customize:

```python
# Target OVR range
TARGET_OVR_MIN = 114
TARGET_OVR_MAX = 115

# Timing (seconds) - adjust based on your device speed
CLICK_DELAY = 0.3      # Delay after each tap
ACTION_DELAY = 0.8     # Delay between actions
OCR_DELAY = 0.5        # Delay before OCR processing

# Coordinates - Update these based on your screen resolution
FREE_REVEAL_POS = (1182, 926)      # P1: FREE REVEAL button
YES_BUTTON_POS = (1411, 817)       # P2/P6: YES button
NO_BUTTON_POS = (989, 817)         # P2/P6: NO button
SKIP_BUTTON_POS = (425, 1008)      # P4: SKIP button
FREE_REFRESH_POS = (1940, 1035)    # P5: FREE REFRESH button
DISMISS_CLICK_POS = (200, 540)     # P5: Click to dismiss card

# Tile positions (clue box grid)
TILE_POSITIONS = [
    (854, 567),    # Row 1, Col 1
    (1183, 567),   # Row 1, Col 2
    (1487, 567),   # Row 1, Col 3
    (892, 772),    # Row 2, Col 1
    (1183, 772),   # Row 2, Col 2
    (1487, 772),   # Row 2, Col 3
]
```

**Important:** Coordinates are device-specific and depend on your screen resolution. Make sure to determine coordinates for YOUR device!

### 5. Special Asset Detection (Card Backgrounds)

The bot can detect specific card types (e.g., Icons, special events) based on their visual appearance. It specifically checks the "Result" screen (P5) to see if a special card background appears on the right side.

**How it works:**
1. The bot loads all images found in the `scout/assets/` folder.
2. It searches for these images *only* within the region defined by the `CHECK_` coordinates in `config.py` (default: right side of the screen where the card appears).
3. If a match is found with a confidence score higher than `MATCH_THRESHOLD`, the bot stops and plays an alert, assuming a special player has been found.

**Tuning the Threshold:**
If the bot is missing your special cards (false negatives) or stopping for wrong cards (false positives), you need to adjust `MATCH_THRESHOLD` in `scout/config.py`.

1. **Run the test script:**
   Connect your device, open the game to the screen showing the card you want to test, and run:
   ```bash
   python test_thresh.py
   ```
2. **Analyze the output:**
   The script will capture the screen and check against your assets, printing the confidence score:
   ```
   [FOUND] Template 'MyNewAsset' with confidence: 0.72
   ```
3. **Update Config:**
   - **Target Value:** Set `MATCH_THRESHOLD` to be slightly lower than the confidence score you see for a correct match.
     - *Example:* If your asset matches with `0.72`, set the threshold to `0.65`.
   - **Too Strict:** If the bot doesn't stop for the card, **decrease** the threshold.
   - **Too Loose:** If the bot stops for normal cards, **increase** the threshold.

## Usage

### Quick Start

**Linux/macOS:**
```bash
./start.sh
```

**Windows:**
Double-click `start.bat` or run in terminal:
```cmd
start.bat
```

### Manual Commands

**Activate virtual environment first:**
```bash
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

**Run the bot:**
```bash
python -m scout
```

**Test screen detection:**
```bash
python -m scout test
```

**Show help:**
```bash
python -m scout --help
```

### Understanding the Workflow

The bot automates this workflow:

1. **P1_MAIN**: Taps "FREE REVEAL" button
2. **P2_CONFIRM**: Confirms "Reveal clue?" with YES
3. **P3_TILES**: Randomly selects a clue box tile
4. **P4_SKIP**: Skips the swipe/animation
5. **P5_RESULT**: Extracts OVR from result card
   - If OVR matches target: Plays alert and pauses
   - If OVR doesn't match: Taps "FREE REFRESH"
6. **P6_REFRESH_CONFIRM**: Confirms "Refresh this player?" with YES
7. Repeats from step 1

## Troubleshooting

### ADB Connection Issues

**Device not detected:**
```bash
# Restart ADB server
adb kill-server
adb start-server
adb devices
```

**Multiple devices:**
```bash
# List devices
adb devices

# Specify device
adb -s <device-id> shell
```

## Development

### Project Structure

```
Star-Scout/
├── scout/
│   ├── __init__.py      # Package initialization
│   ├── __main__.py      # Entry point
│   ├── bot.py           # Main bot logic
│   ├── config.py        # Configuration settings
│   ├── ocr.py           # OCR and screen detection
│   └── utils.py         # ADB utilities
├── start.sh             # Startup script
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Debug Mode

Enable debug mode in `config.py`:
```python
DEBUG_MODE = True
DEBUG_SAVE_DIR = Path("/tmp/scout_debug")
```

This will save screenshots of unknown screen states to help troubleshooting.

## Safety & Disclaimer

⚠️ **Use at your own risk!** This bot automates gameplay and may violate the game's Terms of Service. Use responsibly and be aware that using automation tools could result in account penalties.

## License

See [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Happy Scouting! ⚽🌟**
