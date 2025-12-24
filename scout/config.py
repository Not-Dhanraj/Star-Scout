"""
Configuration for Scout Bot.
All coordinates are direct ADB tap coordinates - no conversion needed.
"""

from pathlib import Path
from enum import Enum, auto


class ScreenState(Enum):
    """Screen states in the Star Scout workflow."""
    P1_MAIN = auto()            # Main screen with FREE REVEAL
    P2_CONFIRM = auto()         # "Reveal clue?" confirmation
    P3_TILES = auto()           # Pick any clue box
    P4_SKIP = auto()            # Skip/swipe screen
    P5_RESULT = auto()          # Result card
    P6_REFRESH_CONFIRM = auto() # "Refresh this player?" confirmation
    UNKNOWN = auto()


# ==================== USER CONFIG ====================

# Target OVR range
TARGET_OVR_MIN = 114
TARGET_OVR_MAX = 115

# Timing (seconds)
CLICK_DELAY = 0.3
ACTION_DELAY = 0.8
OCR_DELAY = 0.5

# Alert sound file
ALERT_SOUND = Path(__file__).parent / "alert.wav"


# ==================== COORDINATES ====================
# All coordinates are direct ADB tap coordinates
# Get them using: adb shell getevent -l (then tap and see coordinates)

# P1: FREE REVEAL button
FREE_REVEAL_POS = (1182, 926)

# P2/P6: YES button on confirmation dialogs
YES_BUTTON_POS = (1411, 817)

# P2/P6: NO button on confirmation dialogs  
NO_BUTTON_POS = (989, 817)

# P3: Tile positions (clue box grid)
TILE_POSITIONS = [
    (854, 567),    # Row 1, Col 1
    (1183, 567),   # Row 1, Col 2
    (1487, 567),   # Row 1, Col 3
    (892, 772),    # Row 2, Col 1
    (1183, 772),   # Row 2, Col 2
    (1487, 772),   # Row 2, Col 3
]

# P4: SKIP button
SKIP_BUTTON_POS = (425, 1008)

# P5: FREE REFRESH button
FREE_REFRESH_POS = (1940, 1035)

# P5: Click to dismiss card (outside card area)
DISMISS_CLICK_POS = (200, 540)


# ==================== DEBUG ====================
DEBUG_MODE = True
DEBUG_SAVE_DIR = Path("/tmp/scout_debug")
