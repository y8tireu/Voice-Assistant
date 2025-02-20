#!/bin/bash
#==============================================================================
# Voice Assistant Installation Script for Ubuntu
#------------------------------------------------------------------------------
# This script will:
# 1. Update and upgrade your system.
# 2. Install system-level dependencies (Python3, pip3, tkinter, audio libraries, etc.).
# 3. Create and activate a Python virtual environment.
# 4. Install required Python packages via pip.
# 5. Provide final instructions.
#==============================================================================

set -e  # Exit script if any command fails

#-----------------------------------
# Function: command_exists
# Checks if a command exists on the system.
#-----------------------------------
command_exists () {
    command -v "$1" >/dev/null 2>&1 ;
}

echo "=============================================="
echo "Starting installation of Voice Assistant dependencies on Ubuntu..."
echo "=============================================="

#-----------------------------------
# Step 1: Update and Upgrade the System
#-----------------------------------
echo "[1/5] Updating package lists..."
sudo apt-get update

echo "[1/5] Upgrading existing packages..."
sudo apt-get upgrade -y

#-----------------------------------
# Step 2: Install System-Level Dependencies
#-----------------------------------
echo "[2/5] Installing system dependencies..."

# Install Python3 if missing
if ! command_exists python3; then
    echo "Python3 not found. Installing Python3..."
    sudo apt-get install -y python3
else
    echo "Python3 is already installed."
fi

# Install pip3 if missing
if ! command_exists pip3; then
    echo "pip3 not found. Installing pip3..."
    sudo apt-get install -y python3-pip
else
    echo "pip3 is already installed."
fi

# Install Tkinter for Python3 (needed for GUI)
echo "Installing python3-tk (Tkinter)..."
sudo apt-get install -y python3-tk

# Install espeak (optional TTS engine dependency)
echo "Installing espeak..."
sudo apt-get install -y espeak

# Install PortAudio development files (for PyAudio)
echo "Installing PortAudio development files..."
sudo apt-get install -y portaudio19-dev

# Install PyAudio for Python3
echo "Installing PyAudio..."
sudo apt-get install -y python3-pyaudio

# Additional multimedia tools (optional but useful for audio processing)
echo "Installing additional multimedia libraries (ffmpeg)..."
sudo apt-get install -y ffmpeg

#-----------------------------------
# Step 3: Create and Activate a Python Virtual Environment
#-----------------------------------
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "[3/5] Creating a virtual environment in ./$VENV_DIR ..."
    python3 -m venv $VENV_DIR
else
    echo "[3/5] Virtual environment already exists in ./$VENV_DIR."
fi

echo "[3/5] Activating virtual environment..."
source $VENV_DIR/bin/activate

# Upgrade pip in the virtual environment
echo "Upgrading pip in the virtual environment..."
pip install --upgrade pip

#-----------------------------------
# Step 4: Install Required Python Packages
#-----------------------------------
echo "[4/5] Installing required Python packages..."

pip install customtkinter SpeechRecognition pyttsx3 pytz rate

# You can add any other Python packages needed for your project here
# For example:
# pip install numpy

#-----------------------------------
# Step 5: Cleanup and Final Instructions
#-----------------------------------
echo "[5/5] Cleaning up..."
sudo apt-get clean

echo "=============================================="
echo "Installation complete! Your environment is ready."
echo "To activate the virtual environment in future sessions, run:"
echo "   source $VENV_DIR/bin/activate"
echo "Then you can run your voice assistant application."
echo "=============================================="
