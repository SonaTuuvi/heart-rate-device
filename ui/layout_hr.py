"""
UI layouts for heart rate (HR) measurement screens.

This module provides display helpers for:
1. Start instruction screen prompting the user to begin HR measurement.
2. HR result screen showing current BPM and wait-for-input instruction.

These screens are used at the beginning and end of HR-related flows,
and are displayed on the OLED screen.

User interaction:
- Encoder button is expected to be pressed to proceed from each screen.
"""

from .oled import oled

def show_start_instruction():
    """
    Display instructions for starting the HR measurement.

    Behaviour:
    - Clears the OLED screen.
    - Displays "START MEASUREMENT" and prompt to press the button.
    - Typically shown before countdown or HRV capture begins.
    """

    oled.fill(0)
    oled.text("START MEASUREMENT", 0, 20)
    oled.text("BY PRESSING", 0, 30)
    oled.text("THE BUTTON", 0, 40)
    oled.show()

def show_hr_screen(bpm):
    """
    Display the user's heart rate after measurement.

    Behaviour:
    - Shows the measured BPM value.
    - Prompts user to press encoder to return.
    - This function only renders the screen and does not wait for input.

    Args:
        bpm (int): Measured heart rate in beats per minute.
    """
    
    oled.fill(0)
    oled.text(f"{bpm} BPM", 0, 10)
    oled.text("PRESS ENCODER", 0, 30)
    oled.text("TO RETURN", 0, 40)
    oled.show()
    
   