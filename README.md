# pi-display

pi-display is a system server to display the Raspberry Pi's IP address (and other stats)

If you find an issue, please [let us know](../..//issues)!

## Setup

Follow the steps below to download pi-display directly or create it from scratch.

On the Raspberry Pi, run the pi-display installation script:

### Option 1: Using Virtual Environment (Recommended)

    git clone https://github.com/helloadhavan/pi-display
    cd pi-display
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e .

### Option 2: System-wide Installation (Legacy)

    git clone https://github.com/helloadhavan/pi-display
    cd pi-display
    ./install.sh <password>

**Note:** The legacy installation script may encounter setuptools compatibility issues with newer Python versions. The virtual environment approach is recommended for modern systems.

### Requirements

- Python 3.7+
- I2C enabled on Raspberry Pi
- SSD1306 OLED display connected via I2C
