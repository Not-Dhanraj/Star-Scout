"""
OCR functions for Scout Bot using pytesseract.
"""

import re
from collections import Counter

import cv2
from PIL import Image
import pytesseract

from .config import ScreenState


def get_text(image_path: str) -> str:
    """Extract text from screenshot using grayscale + pytesseract."""
    img = cv2.imread(image_path)
    if img is None:
        return ""
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    pil_gray = Image.fromarray(gray)
    
    # PSM 6 (block) and PSM 11 (sparse) work best for game UI
    texts = []
    for psm in [6, 11]:
        text = pytesseract.image_to_string(pil_gray, config=f'--psm {psm}').upper()
        texts.append(text)
    
    return " ".join(texts)


def detect_screen_state(image_path: str, debug: bool = False) -> ScreenState:
    """Detect current screen state from OCR text."""
    text = get_text(image_path)
    
    if debug:
        print(f"[OCR] {text[:600]}...")
    
    # P6: Refresh confirmation popup
    if "REFRESH THIS PLAYER" in text or "REFRESH THIS" in text:
        return ScreenState.P6_REFRESH_CONFIRM
    
    # P2: Reveal clue confirmation popup
    if "REVEAL CLUE" in text or ("YES" in text and "NO" in text and "REVEAL CLUE" in text):
        return ScreenState.P2_CONFIRM
    
    # P4: Swipe to reveal screen (has "SWIPE TO REVEAL" text)
    if "SWIPE TO REVEAL" in text or "SWIPE" in text:
        return ScreenState.P4_SKIP
    
    # P3: Tile selection
    if "PICK ANY CLUE BOX" in text or "PICK ANY CLUE" in text:
        return ScreenState.P3_TILES
    
    # P5: Result card - unique attributes only appear here
    p5_unique = ["TRADABILITY", "UNTRADABLE", "TRADABLE", "ANNIVERSARY", "PROGRAM",]
    if any(attr in text for attr in p5_unique):
        # Make sure it's not P1 (which shows card preview)
        if "STAR SCOUT" not in text and "POSSIBLE REWARDS" not in text:
            return ScreenState.P5_RESULT
    
    # P5: Other attributes + no P1 indicators
    p5_other = ["POSITION", "ATTACK", "MIDFIELD", "DEFEND", "GOALKEEPER", 
                "TEAM", "NATION", "OVR", "OOVR", "0VR"]
    has_attr = any(attr in text for attr in p5_other)
    if has_attr and "FREE REVEAL" not in text and "STAR SCOUT" not in text:
        return ScreenState.P5_RESULT
    
    # P1: Main screen
    if "STAR SCOUT" in text and "FREE REVEAL" in text:
        return ScreenState.P1_MAIN
    if "POSSIBLE REWARDS" in text and "FREE REVEAL" in text:
        return ScreenState.P1_MAIN
    
    return ScreenState.UNKNOWN


def extract_ovr(image_path: str) -> int | None:
    """Extract OVR number from result screen."""
    img = cv2.imread(image_path)
    if img is None:
        return None
    
    h, w = img.shape[:2]
    numbers = []
    
    # Card center area
    card = img[int(h * 0.22):int(h * 0.9), int(w * 0.25):int(w * 0.72)]
    scaled = cv2.resize(card, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(scaled, cv2.COLOR_BGR2GRAY)
    
    for thresh_val in [100, 120, 140]:
        _, thresh = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY)
        text = pytesseract.image_to_string(Image.fromarray(thresh), config='--psm 6')
        nums = re.findall(r'\d{2,3}', text)
        numbers.extend([int(n) for n in nums])
    
    # Full image fallback
    full_text = pytesseract.image_to_string(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)))
    nums = re.findall(r'\d{2,3}', full_text)
    numbers.extend([int(n) for n in nums])
    
    # Filter valid OVR range (80-150)
    valid = [n for n in numbers if 80 <= n <= 150]
    if valid:
        return Counter(valid).most_common(1)[0][0]
    return None


def is_ovr_shown(image_path: str) -> bool:
    """Check if OVR attribute is shown."""
    text = get_text(image_path)
    return any(p in text for p in ["OVR", "OOVR", "0VR", "OVVR"])
