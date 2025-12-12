#!/bin/bash

# Automatically detect Raspberry Pi Pico serial port
PORT=$(ls /dev/cu.usbmodem* 2>/dev/null | head -n 1)

if [ -z "$PORT" ]; then
  echo "ERROR: Raspberry Pi Pico not detected. Please connect the device via USB."
  exit 1
fi

echo "Using device: $PORT"
echo "Starting installation..."

# Check if mpremote is installed
if ! command -v mpremote &> /dev/null; then
    echo "ERROR: mpremote not found. Please install it using: pip install mpremote"
    exit 1
fi

# Step 1: Upload main.py
echo "Uploading main.py"
mpremote connect $PORT fs cp main.py :

# Step 2: Upload lib and nested folders
LIB_FOLDERS=("lib" "lib/umqtt")
for folder in "${LIB_FOLDERS[@]}"; do
    echo "Installing folder: $folder"
    mpremote connect $PORT fs mkdir ":/$folder" 2>/dev/null

    for file in $folder/*; do
        if [ -f "$file" ]; then
            echo "Uploading $file"
            mpremote connect $PORT fs cp "$file" ":/$folder/"
        fi
    done
done

# Step 3: Upload source code folders
FOLDERS=("app" "core" "cloud" "history" "ui")

for folder in "${FOLDERS[@]}"; do
    echo "Installing folder: $folder"
    mpremote connect $PORT fs mkdir ":/$folder" 2>/dev/null

    for file in $folder/*.{py,json}; do
        [ -e "$file" ] || continue
        echo "Uploading $file"
        mpremote connect $PORT fs cp "$file" ":/$folder/"
    done
done

echo "Installation complete."
echo "Running main.py..."

# Step 4: Run main.py
mpremote connect $PORT run main.py
