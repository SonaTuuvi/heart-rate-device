"""
UI layouts for displaying HRV measurement history.

This module provides user interface screens for navigating and viewing
previously stored HRV results. It supports:
1. History list navigation with encoder selection.
2. Detailed view of a specific measurement with scrollable stats.
3. Contextual back menu to return to history or main screen.

User input:
- The encoder is used to scroll/select menu options.
- Pressing the encoder confirms the selection.

Data fields displayed:
- Timestamp, HR, PPI, RMSSD, SDNN, SNS, PNS
"""

from .oled import oled
import time
from core.utils import is_encoder_pressed, encoder_button

def show_history_list(history, selected_index):
    """
    Display a vertical list of the 5 most recent measurements.

    Behaviour:
    - Shows up to 5 items from the end of the `history` list.
    - Highlights the currently selected index with a ">" prefix.
    - Each row is labeled as "MEASUREMENT {n}".

    Args:
        history (list): Full list of saved HRV data entries.
        selected_index (int): Index of the currently selected row (0–4).
    """

    oled.fill(0)
    for i, _ in enumerate(history[-5:]):
        prefix = "> " if i == selected_index else "  "
        oled.text(prefix + f"MEASUREMENT {i+1}", 0, i * 10)
    oled.show()

def show_measurement_detail(data, encoder):
    """
    Display detailed HRV statistics for a selected measurement.

    Behaviour:
    - Renders timestamp and all six HRV metrics:
      mean_hr, mean_ppi, rmssd, sdnn, sns, pns.
    - Waits for user to press encoder to proceed.
    - Then shows a back menu (via `show_back_menu`) and returns the result.

    Args:
        data (dict): HRV result with keys:
            timestamp, mean_hr, mean_ppi, rmssd, sdnn, sns, pns.
        encoder (Encoder): Encoder instance for reading turn input.

    Returns:
        str: Result from `show_back_menu`, either:
              "BACK TO HISTORY" or "BACK TO MAIN"
    """

    oled.fill(0)
    oled.text(f"{data['timestamp']}", 0, 0)
    oled.text(f"HR: {int(data['mean_hr'])}", 0, 10)
    oled.text(f"PPI: {int(data['mean_ppi'])}", 0, 20)
    oled.text(f"RMSSD: {int(data['rmssd'])}", 0, 30)
    oled.text(f"SDNN: {int(data['sdnn'])}", 0, 40)
    oled.text(f"SNS: {round(data['sns'], 2)}", 0, 50)
    oled.text(f"PNS: {round(data['pns'], 2)}", 0, 60)
    oled.show()

    while not is_encoder_pressed():
        time.sleep(0.05)


    return show_back_menu(encoder)

def show_back_menu(encoder):
    """
    Display a two-option menu for returning from the detail view.

    Behaviour:
    - Shows two options:
        - "BACK TO HISTORY"
        - "BACK TO MAIN"
    - User navigates using encoder rotation.
    - Selection is confirmed by pressing encoder.

    Args:
        encoder (Encoder): Encoder instance for navigation.
 
    Returns:
        str: Selected option text.
    """
    
    options = ["BACK TO HISTORY", "BACK TO MAIN"]
    selected = 0

    while True:
        oled.fill(0)
        for i, option in enumerate(options):
            prefix = "> " if i == selected else "  "
            oled.text(prefix + option, 0, i * 10 + 10)
        oled.show()

        turn = encoder.get_turn()
        if turn:
            selected = (selected + turn) % len(options)

        if is_encoder_pressed():
            return options[selected]

        time.sleep(0.05)
