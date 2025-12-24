"""
Scout Bot - FC Mobile Star Scout Automation
User provides all coordinates directly - no conversion needed.
"""

from .config import ScreenState, TARGET_OVR_MIN, TARGET_OVR_MAX
from .ocr import detect_screen_state, extract_ovr, is_ovr_shown
from .utils import capture_screen, tap, check_adb_connection
from .bot import run, test

__all__ = [
    "ScreenState",
    "TARGET_OVR_MIN",
    "TARGET_OVR_MAX",
    "detect_screen_state",
    "extract_ovr",
    "is_ovr_shown",
    "capture_screen",
    "tap",
    "check_adb_connection",
    "run",
    "test",
]
