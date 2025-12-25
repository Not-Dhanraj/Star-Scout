"""
ADB utilities for Scout Bot.
"""

import subprocess
import time
import cv2
import numpy as np
from .config import (
    CLICK_DELAY,
    ALERT_SOUND,
    CHECK_X1,
    CHECK_X2,
    CHECK_Y1,
    CHECK_Y2,
    MATCH_THRESHOLD,
)


def run_cmd(cmd: str, capture: bool = True) -> str:
    """Run shell command."""
    if capture:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    subprocess.run(cmd, shell=True)
    return ""


def capture_screen(path: str = "/tmp/screen.png") -> str:
    """Capture screen via ADB."""
    run_cmd(f"adb exec-out screencap -p > {path}", capture=False)
    time.sleep(0.2)
    return path


def tap(x: int, y: int) -> None:
    """Tap at coordinates via ADB (direct coordinates, no conversion)."""
    run_cmd(f"adb shell input tap {int(x)} {int(y)}", capture=False)
    time.sleep(CLICK_DELAY)


def play_alert() -> None:
    """Play alert sound."""
    if not ALERT_SOUND.exists():
        print(f"[WARN] Alert not found: {ALERT_SOUND}")
        return

    for player in ["paplay", "aplay", "mpv --no-video", "ffplay -nodisp -autoexit"]:
        try:
            run_cmd(f"{player} {ALERT_SOUND} &", capture=False)
            return
        except Exception:
            continue
    print("[WARN] Could not play alert!")


def check_adb_connection() -> bool:
    """Check ADB connection."""
    result = run_cmd("adb devices")
    lines = result.strip().split("\n")
    devices = [line for line in lines[1:] if line.strip() and "device" in line]

    if devices:
        print(f"[OK] ADB: {devices[0].split()[0]}")
        return True
    print("[ERROR] No ADB device!")
    return False