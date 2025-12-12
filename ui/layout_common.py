"""
Common UI layout helpers for system feedback screens.

This module contains generic display functions used across various
flows where user feedback or temporary UI states are required.

Screens included:
1. Placeholder screen: for unimplemented features.
2. Sending screen: shown when publishing data to network.
3. Error screen: shown on network failure with retry option.

User interactions:
- Error screen supports encoder button press to retry early.
- All screens are rendered on OLED and block the current flow.
"""


from ui.oled import oled
import time
from core.utils import is_encoder_pressed

def show_placeholder(title):
    """
    Show a placeholder screen for unavailable features.

    Behaviour:
    - Displays a title (feature name).
    - Shows "COMING SOON" label.
    - Instructs user to press encoder to return.

    Args:
        title (str): Title to display at the top of the screen.
    """

    oled.fill(0)
    oled.text(title, 0, 10)
    oled.text("COMING SOON", 0, 30)
    oled.text("PRESS TO RETURN", 0, 50)
    oled.show()

def show_sending_screen():
    """
    Show a screen indicating data is being sent.

    Behaviour:
    - Clears OLED.
    - Displays "SENDING DATA..." at fixed position.
    - Used before Wi-Fi/MQTT transmission begins.
    """
     
    oled.fill(0)
    oled.text("SENDING DATA...", 0, 20)
    oled.show()

def show_error_screen():
    """
    Show a retry screen after data send failure.

    Behaviour:
    - Displays error text with countdown from 3 to 0 seconds.
    - During countdown, polls for encoder button press.
    - If user presses button, returns "retry".
    - If countdown ends without interaction, returns "exit".

    Returns:
        str: "retry" if user presses encoder, otherwise "exit"
    """

    for seconds in range(3, -1, -1):
        oled.fill(0)
        oled.text("ERROR SENDING DATA", 0, 0)
        oled.text("PRESS TO RETRY", 0, 20)
        oled.text("OR WAIT", 0, 35)
        oled.text(f"{seconds} sec", 0, 45)
        oled.show()

        for _ in range(10):
            if is_encoder_pressed():
                return "retry"
            time.sleep(0.1)
    return "exit"
