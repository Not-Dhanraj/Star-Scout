"""
Bot logic for Scout.
"""

import time
import random
import shutil
from datetime import datetime

from .config import (
    ScreenState,
    TARGET_OVR_MIN, TARGET_OVR_MAX,
    ACTION_DELAY, OCR_DELAY,
    FREE_REVEAL_POS, YES_BUTTON_POS, TILE_POSITIONS,
    SKIP_BUTTON_POS, FREE_REFRESH_POS, DISMISS_CLICK_POS,
    DEBUG_MODE, DEBUG_SAVE_DIR,
)
from .utils import capture_screen, tap, play_alert
from .ocr import detect_screen_state, extract_ovr, is_ovr_shown


def detect_with_retry(retries: int = 3) -> tuple[ScreenState, str]:
    """Capture and detect state with retries."""
    img_path = capture_screen()
    
    for i in range(retries):
        state = detect_screen_state(img_path)
        if state != ScreenState.UNKNOWN:
            return state, img_path
        
        if i < retries - 1:
            print(f"  [RETRY {i+1}/{retries}]")
            time.sleep(0.5)
            img_path = capture_screen()
    
    # Save unknown for debug
    if DEBUG_MODE:
        DEBUG_SAVE_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy(img_path, DEBUG_SAVE_DIR / f"unknown_{ts}.png")
        print(f"  [DEBUG] Saved: {DEBUG_SAVE_DIR}/unknown_{ts}.png")
        detect_screen_state(img_path, debug=True)
    
    return ScreenState.UNKNOWN, img_path


def handle_p5(img_path: str) -> bool:
    """Handle P5 result screen. Returns True if target found."""
    time.sleep(OCR_DELAY)
    img_path = capture_screen()
    
    if not is_ovr_shown(img_path):
        print("  -> OVR not shown")
        dismiss_and_refresh()
        return False
    
    ovr = extract_ovr(img_path)
    if ovr is None:
        print("  -> Could not read OVR")
        dismiss_and_refresh()
        return False
    
    print(f"  -> OVR: {ovr}")
    
    if TARGET_OVR_MIN <= ovr <= TARGET_OVR_MAX:
        print(f"\n{'='*40}")
        print(f"  *** TARGET FOUND: {ovr} ***")
        print(f"{'='*40}\n")
        play_alert()
        return True
    
    print(f"  -> Not in range [{TARGET_OVR_MIN}-{TARGET_OVR_MAX}]")
    dismiss_and_refresh()
    return False


def dismiss_and_refresh():
    """Dismiss card and click refresh."""
    print("  -> Dismiss & refresh")
    tap(*DISMISS_CLICK_POS)
    time.sleep(ACTION_DELAY)
    
    tap(*FREE_REFRESH_POS)
    time.sleep(ACTION_DELAY)
    
    # Check for confirmation dialog
    img = capture_screen()
    if detect_screen_state(img) == ScreenState.P6_REFRESH_CONFIRM:
        print("  -> Confirm refresh")
        tap(*YES_BUTTON_POS)
        time.sleep(ACTION_DELAY)


def run():
    """Main automation loop."""
    iteration = 0
    unknown_count = 0
    
    print(f"\n{'='*40}")
    print("Scout Bot - Starting")
    print(f"{'='*40}")
    print(f"Target OVR: {TARGET_OVR_MIN}-{TARGET_OVR_MAX}")
    print("Ctrl+C to stop\n")
    
    while True:
        iteration += 1
        print(f"\n[{iteration}] Checking...")
        
        try:
            state, img_path = detect_with_retry()
            print(f"  State: {state.name}")
            
            if state == ScreenState.UNKNOWN:
                unknown_count += 1
                if unknown_count >= 5:
                    print("  [WARN] Too many unknowns, waiting...")
                    time.sleep(2.0)
                    unknown_count = 0
                continue
            
            unknown_count = 0
            
            if state == ScreenState.P1_MAIN:
                print("  -> FREE REVEAL")
                tap(*FREE_REVEAL_POS)
                time.sleep(ACTION_DELAY)
            
            elif state == ScreenState.P2_CONFIRM:
                print("  -> YES")
                tap(*YES_BUTTON_POS)
                time.sleep(ACTION_DELAY)
            
            elif state == ScreenState.P3_TILES:
                tile = random.choice(TILE_POSITIONS)
                print(f"  -> Tile {tile}")
                tap(*tile)
                time.sleep(ACTION_DELAY)
            
            elif state == ScreenState.P4_SKIP:
                print("  -> SKIP")
                tap(*SKIP_BUTTON_POS)
                time.sleep(ACTION_DELAY)
            
            elif state == ScreenState.P5_RESULT:
                if handle_p5(img_path):
                    print("\n*** Target player found! Bot stopped. ***")
                    print("You can manually accept or refresh the player.")
                    break
            
            elif state == ScreenState.P6_REFRESH_CONFIRM:
                print("  -> Confirm refresh")
                tap(*YES_BUTTON_POS)
                time.sleep(ACTION_DELAY)
        
        except KeyboardInterrupt:
            print("\n\nStopped.")
            break
        except Exception as e:
            print(f"  [ERROR] {e}")
            time.sleep(ACTION_DELAY)


def test():
    """Test current screen detection."""
    print("\n[TEST] Capturing...")
    img = capture_screen()
    
    print("[TEST] Detecting...")
    state = detect_screen_state(img, debug=True)
    print(f"\n[TEST] State: {state.name}")
    
    if state == ScreenState.P5_RESULT:
        ovr = extract_ovr(img)
        print(f"[TEST] OVR: {ovr}")
