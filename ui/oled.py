"""
OLED display initialization module.

This module sets up the I2C interface and creates a global `oled` object
to be used throughout the UI. It wraps the SSD1306 OLED driver and provides
a 128x64 pixel screen via I2C.

Configuration:
- Display resolution: 128x64 pixels
- I2C SCL pin: GPIO15
- I2C SDA pin: GPIO14
- I2C bus: 1

Exports:
    oled (SSD1306_I2C): Global display object for rendering UI
"""

from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

# --- Display resolution ---
WIDTH = 128
HEIGHT = 64

# --- Graph positioning ---
GRAPH_TOP = 14
GRAPH_HEIGHT = 50
GRAPH_BOTTOM = GRAPH_TOP + GRAPH_HEIGHT

# --- Signal ADC range ---
SIGNAL_MIN = 12000
SIGNAL_MAX = 40000

# --- Visual amplification ---
GAIN = 2.2

# --- I2C setup ---
I2C_SCL = 15
I2C_SDA = 14
i2c = I2C(1, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA))
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)
