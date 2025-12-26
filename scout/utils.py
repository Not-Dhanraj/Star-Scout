"""
ADB utilities for Scout Bot.
"""

from pathlib import Path
import subprocess
import time
import cv2
import numpy as np
import platform
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


def capture_screen(path: str = "screen.png") -> str:
    """Capture screen via ADB."""
    # Use current directory or temp directory if path is just a filename
    if not Path(path).is_absolute():
        path = str(Path(path).resolve())
        
    run_cmd(f"adb exec-out screencap -p > \"{path}\"", capture=False)
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

    if platform.system() == "Windows":
        try:
            import winsound
            winsound.PlaySound(str(ALERT_SOUND), winsound.SND_FILENAME | winsound.SND_ASYNC)
            return
        except Exception:
            pass

    for player in ["paplay", "aplay", "mpv --no-video", "ffplay -nodisp -autoexit", "afplay"]:
        try:
            run_cmd(f"{player} \"{ALERT_SOUND}\" &", capture=False)
            return
        except Exception:
            continue
    print("[WARN] Could not play alert!")


def load_templates(directory: Path) -> list[tuple[str, np.ndarray]]:
    """
    Load all image templates from the specified directory.
    Returns a list of tuples: (template_name, template_image).
    """
    templates = []
    if not directory.is_dir():
        print(f"[WARN] Asset directory not found: {directory}")
        return templates

    valid_extensions = {".png", ".jpg", ".jpeg", ".bmp"}
    for file_path in directory.iterdir():
        if file_path.suffix.lower() in valid_extensions:
            img = cv2.imread(str(file_path), cv2.IMREAD_COLOR)
            if img is not None:
                templates.append((file_path.stem, img))
            else:
                print(f"[WARN] Could not load template: {file_path}")
    
    print(f"[INFO] Loaded {len(templates)} templates from {directory}")
    return templates


def check_if_image_exists(
    screenshot: str | np.ndarray, templates: list[tuple[str, np.ndarray]], debug: bool = False
) -> tuple[bool, float]:
    """
    Check if any of the template images exist in the specified region of the screenshot.
    This function performs template matching that is resilient to size variations.
    Args:
        screenshot: Path to the screenshot file or loaded OpenCV image.
        templates: A list of (name, image_data) tuples.
        debug: If True, save debug images and print confidence scores.
    Returns:
        (found, max_confidence):
            found: True if a match is found, False otherwise.
            max_confidence: The highest confidence score found (0.0 to 1.0).
    """
    if isinstance(screenshot, str):
        main_image = cv2.imread(screenshot, cv2.IMREAD_COLOR)
        img_name = screenshot
    else:
        main_image = screenshot
        img_name = "memory_image"

    if main_image is None:
        print(f"[ERROR] Could not load screenshot: {img_name}")
        return False, 0.0

    h, w = main_image.shape[:2]
    if debug:
        print(f"  [DEBUG] Screenshot size: {w}x{h}")

    if CHECK_X2 > w or CHECK_Y2 > h:
        print(f"[WARN] Check region ({CHECK_X1},{CHECK_Y1},{CHECK_X2},{CHECK_Y2}) is out of bounds for image size {w}x{h}")
        return False, 0.0

    if debug:
        from .config import DEBUG_SAVE_DIR

        DEBUG_SAVE_DIR.mkdir(parents=True, exist_ok=True)
        print(f"  [DEBUG] Saving debug images to: {DEBUG_SAVE_DIR}")

    # Crop the main image to the specified check region
    region_color = main_image[CHECK_Y1:CHECK_Y2, CHECK_X1:CHECK_X2]
    region_gray = cv2.cvtColor(region_color, cv2.COLOR_BGR2GRAY)

    if debug:
        cv2.imwrite(str(DEBUG_SAVE_DIR / "region.png"), region_gray)

    global_max_val = 0.0

    for t_name, template_color in templates:
        template_gray = cv2.cvtColor(template_color, cv2.COLOR_BGR2GRAY)

        best_match_val = -1

        # Resize template to match the height of the region for a baseline
        scale = region_gray.shape[0] / template_gray.shape[0]
        base_w = int(template_gray.shape[1] * scale)
        base_h = int(template_gray.shape[0] * scale)

        # Test scales from 60% to 140% of the baseline height
        for i, scale_percent in enumerate(np.linspace(0.6, 1.4, 40)):
            w = int(base_w * scale_percent)
            h = int(base_h * scale_percent)

            if w > region_gray.shape[1] or h > region_gray.shape[0] or w < 5 or h < 5:
                continue

            resized_template = cv2.resize(
                template_gray, (w, h), interpolation=cv2.INTER_AREA
            )
            result = cv2.matchTemplate(
                region_gray, resized_template, cv2.TM_CCOEFF_NORMED
            )
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val > best_match_val:
                best_match_val = max_val

            if max_val >= MATCH_THRESHOLD:
                print(
                    f"  [FOUND] Template '{t_name}' "
                    f"with confidence: {max_val:.2f}"
                )
                if debug:
                    # Draw rectangle and save match
                    dbg_region = region_color.copy()
                    cv2.rectangle(
                        dbg_region, max_loc, (max_loc[0] + w, max_loc[1] + h), (0, 0, 255), 2
                    )
                    cv2.putText(
                        dbg_region,
                        f"{max_val:.2f}",
                        (max_loc[0], max_loc[1] - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 0, 255),
                        1,
                    )
                    cv2.imwrite(str(DEBUG_SAVE_DIR / f"match_{t_name}.png"), dbg_region)
                return True, max_val
        
        if best_match_val > global_max_val:
            global_max_val = best_match_val

        if debug:
            print(f"  [DEBUG] Best match for '{t_name}': {best_match_val:.2f}")

    return False, global_max_val


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