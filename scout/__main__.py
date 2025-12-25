#!/usr/bin/env python3
"""
Scout Bot - Entry point.

Usage:
    python -m scout           # Run bot
    python -m scout test      # Test detection
    python -m scout --help    # Help
"""

import sys

from .utils import check_adb_connection
from .bot import run, test
from .config import TARGET_OVR_MIN, TARGET_OVR_MAX


def main():
    print("Scout Bot for FC Mobile")
    print("=" * 40)

    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()

        if arg in ("--help", "-h", "help"):
            print(
                """
Usage:
    python -m scout           Run automation
    python -m scout test      Test screen detection
    python -m scout --help    Show help

Config:
    Edit scout/config.py to change coordinates and target OVR.
"""
            )
            return

        if arg == "test":
            if check_adb_connection():
                test()
            return

        print(f"Unknown: {arg}")
        return

    if not check_adb_connection():
        sys.exit(1)

    print(f"\nTarget OVR: {TARGET_OVR_MIN}-{TARGET_OVR_MAX}")
    print("\nCommands:")
    print("  python -m scout       - Run")
    print("  python -m scout test  - Test")

    if input("\nStart? (y/n): ").lower() == "y":
        print("\nStarting in 3s...")
        import time

        time.sleep(3)
        run()


if __name__ == "__main__":
    main()
