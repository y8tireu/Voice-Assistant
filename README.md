# Voice Assistant Installation for Ubuntu

This document provides instructions on how to set up your Ubuntu system with all the necessary dependencies to run the Voice Assistant application. The installation process includes:

1. Updating your system and installing system-level dependencies.
2. Creating and activating a Python virtual environment.
3. Installing the required Python packages.

## Prerequisites

- Ubuntu operating system
- A user account with `sudo` privileges
- An active internet connection

## Installation Steps

Follow these steps to install all required dependencies:

### 1. Update and Upgrade the System

First, update your package lists and upgrade any outdated packages:

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 2. Install System-Level Dependencies

The following commands install Python3, pip, Tkinter (for GUI support), audio libraries, and other multimedia tools:

```bash
sudo apt-get install -y python3 python3-pip python3-tk espeak portaudio19-dev python3-pyaudio ffmpeg
```

### 3. Set Up a Python Virtual Environment

Create and activate a virtual environment to keep your project dependencies isolated:

```bash
# Create a virtual environment named "venv" if it doesn't exist
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip inside the virtual environment
pip install --upgrade pip
```

### 4. Install Required Python Packages

With the virtual environment activated, install the Python packages required by the Voice Assistant application:

```bash
pip install customtkinter SpeechRecognition pyttsx3 pytz rate
```

### 5. Using the Installation Script

For convenience, you can use the provided shell script (`install.sh`) to automate the above steps. Below is the full content of the script.

---

## install.sh

```bash
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
```

---

## Usage Instructions

1. **Save the Script:**

   Save the above shell script code into a file named `install.sh`.

2. **Make It Executable:**

   Open your terminal, navigate to the directory where `install.sh` is saved, and run:

   ```bash
   chmod +x install.sh
   ```

3. **Run the Script:**

   Execute the script with:

   ```bash
   ./install.sh
   ```

This will update your system, install all necessary dependencies, set up a Python virtual environment, and install all required Python packages for the Voice Assistant application.

## Troubleshooting

- **Permission Errors:**  
  If you run into permission errors, ensure you are using a user with `sudo` privileges.

- **Virtual Environment Activation:**  
  If the virtual environment is not activated automatically, run:
  
  ```bash
  source venv/bin/activate
  ```

- **Dependency Issues:**  
  Ensure that your system's package lists are up-to-date by running `sudo apt-get update` before executing the script.
