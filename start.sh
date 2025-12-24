#!/bin/bash

# Star Scout Bot - Startup Script
# This script starts the Scout bot with proper error handling

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_msg() {
    echo -e "${2}${1}${NC}"
}

# Print header
print_header() {
    echo ""
    echo "=========================================="
    echo "     Star Scout Bot - Starting Up"
    echo "=========================================="
    echo ""
}

# Check if Python is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_msg "ERROR: Python 3 is not installed!" "$RED"
        print_msg "Please install Python 3.7 or higher." "$YELLOW"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_msg "✓ Python $PYTHON_VERSION found" "$GREEN"
}

# Check if ADB is installed
check_adb() {
    if ! command -v adb &> /dev/null; then
        print_msg "ERROR: ADB is not installed!" "$RED"
        print_msg "Please install Android Debug Bridge (ADB):" "$YELLOW"
        print_msg "  Ubuntu/Debian: sudo apt-get install android-tools-adb" "$YELLOW"
        print_msg "  Fedora/RHEL: sudo dnf install android-tools" "$YELLOW"
        print_msg "  Arch Linux: sudo pacman -S android-tools" "$YELLOW"
        print_msg "  macOS: brew install android-platform-tools" "$YELLOW"
        exit 1
    fi
    
    ADB_VERSION=$(adb --version | head -n 1)
    print_msg "✓ $ADB_VERSION found" "$GREEN"
}

# Check if Tesseract is installed
check_tesseract() {
    if ! command -v tesseract &> /dev/null; then
        print_msg "ERROR: Tesseract OCR is not installed!" "$RED"
        print_msg "Please install Tesseract OCR:" "$YELLOW"
        print_msg "  Ubuntu/Debian: sudo apt-get install tesseract-ocr" "$YELLOW"
        print_msg "  Fedora/RHEL: sudo dnf install tesseract" "$YELLOW"
        print_msg "  Arch Linux: sudo pacman -S tesseract" "$YELLOW"
        print_msg "  macOS: brew install tesseract" "$YELLOW"
        exit 1
    fi
    
    TESSERACT_VERSION=$(tesseract --version 2>&1 | head -n 1)
    print_msg "✓ $TESSERACT_VERSION found" "$GREEN"
}

# Setup virtual environment
setup_venv() {
    if [ ! -d "venv" ]; then
        print_msg "Creating virtual environment..." "$YELLOW"
        python3 -m venv .venv
    fi
    
    print_msg "✓ Virtual environment ready" "$GREEN"
}

# Activate virtual environment
activate_venv() {
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        print_msg "✓ Virtual environment activated" "$GREEN"
    else
        print_msg "ERROR: Virtual environment not found!" "$RED"
        exit 1
    fi
}

# Check if Python dependencies are installed
check_dependencies() {
    print_msg "Checking Python dependencies..." "$BLUE"
    
    if ! python -c "import cv2" &> /dev/null; then
        print_msg "Installing missing dependencies..." "$YELLOW"
        pip install -r requirements.txt
    else
        print_msg "✓ Python dependencies installed" "$GREEN"
    fi
}

# Check ADB connection
check_adb_device() {
    print_msg "Checking ADB device connection..." "$BLUE"
    
    DEVICES=$(adb devices | tail -n +2 | grep -v "^$" | wc -l)
    
    if [ "$DEVICES" -eq 0 ]; then
        print_msg "ERROR: No ADB device connected!" "$RED"
        print_msg "" "$NC"
        print_msg "Please connect your Android device and enable USB debugging:" "$YELLOW"
        print_msg "  1. Go to Settings → About Phone" "$YELLOW"
        print_msg "  2. Tap 'Build Number' 7 times" "$YELLOW"
        print_msg "  3. Go to Settings → Developer Options" "$YELLOW"
        print_msg "  4. Enable 'USB Debugging'" "$YELLOW"
        print_msg "  5. Connect device via USB and allow debugging" "$YELLOW"
        print_msg "" "$NC"
        print_msg "Or connect wirelessly:" "$YELLOW"
        print_msg "  adb tcpip 5555" "$YELLOW"
        print_msg "  adb connect <device-ip>:5555" "$YELLOW"
        exit 1
    fi
    
    DEVICE_NAME=$(adb devices | tail -n +2 | head -n 1 | awk '{print $1}')
    print_msg "✓ Device connected: $DEVICE_NAME" "$GREEN"
}

# Main script
main() {
    print_header
    
    # Run checks
    check_python
    check_adb
    check_tesseract
    setup_venv
    activate_venv
    check_dependencies
    check_adb_device
    
    echo ""
    print_msg "All checks passed! Starting bot..." "$GREEN"
    echo ""
    echo "=========================================="
    echo ""
    
    # Start the bot
    python -m scout
}

# Run main function
main
