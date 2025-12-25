"""
Test script to check for special assets in a screenshot.

This script captures the screen and runs the `check_if_image_exists` function
to determine if any of the predefined template assets are found in the
configured check region.
"""

import time
from scout.utils import capture_screen, check_if_image_exists, check_adb_connection
from scout.bot import TEMPLATES
from scout.config import CHECK_X1, CHECK_Y1, CHECK_X2, CHECK_Y2


def main():
    """Main function to run the test."""
    print("=" * 40)
    print("Star-Scout: Special Asset Test")
    print("=" * 40)

    if not check_adb_connection():
        return

    print("\n[1] Capturing screen...")
    screenshot_path = capture_screen()
    print(f"    -> Saved to {screenshot_path}")

    time.sleep(0.5)

    print("\n[2] Checking for special assets...")
    print(f"    -> Templates: {[name for name, _ in TEMPLATES]}")
    print(f"    -> Region: (x1={CHECK_X1}, y1={CHECK_Y1}, x2={CHECK_X2}, y2={CHECK_Y2})")

    found = check_if_image_exists(screenshot_path, TEMPLATES, debug=True)

    print("\n[3] Result:")
    if found:
        print("    -> SUCCESS: A special asset was found in the region!")
    else:
        print("    -> INFO: No special assets were found in the region.")

    print("\n" + "=" * 40)


if __name__ == "__main__":
    main()