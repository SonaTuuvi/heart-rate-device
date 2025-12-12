"""
UI layouts for displaying HRV analysis results.

This module provides visual feedback screens after HRV measurement,
either from local calculations or remote Kubios analysis.

Screens:
1. `show_hrv_screen`: displays basic HRV stats (local calculation).
2. `show_kubios_results`: shows extended metrics (including SNS/PNS)
   after receiving results from Kubios cloud.

All values are rounded for readability and shown in stacked format.
User is prompted to press the encoder to return after viewing.
"""

from .oled import oled

def show_start_instruction_hrv():
    """
    Display instructions for starting the HR measurement.

    Behaviour:
    - Clears the OLED screen.
    - Displays "START MEASUREMENT" and prompt to press the button.
    - Typically shown before countdown or HRV capture begins.
    """
    oled.fill(0)
    oled.text("START MEASUREMENT", 0, 0)
    oled.text("BY PLACING FINGER", 0, 10)
    oled.text("ON THE SENSOR AND", 0, 20)
    oled.text("PRESS THE BUTTON TO", 0, 30)
    oled.text("START", 0, 40)
    oled.show()
 
def show_hrv_screen(mean_hr, mean_ppi, rmssd, sdnn):
    """
    Display locally computed HRV results.

    Behaviour:
    - Shows four key metrics: HR, PPI, RMSSD, SDNN.
    - Rounds each value for clarity.
    - Displays a "PRESS TO RETURN" prompt.

    Args:
        mean_hr (float): Mean heart rate in BPM.
        mean_ppi (float): Mean P-P interval in ms.
        rmssd (float): Root mean square of successive differences.
        sdnn (float): Standard deviation of NN intervals.
    """
    oled.fill(0)
    oled.text(f"HR: {round(mean_hr)}", 0, 0)
    oled.text(f"PPI: {round(mean_ppi)}", 0, 10)
    oled.text(f"RMSSD: {round(rmssd)}", 0, 20)
    oled.text(f"SDNN: {round(sdnn)}", 0, 30)
    oled.text("PRESS TO RETURN", 0, 50)
    oled.show()

def show_kubios_results(hr, ppi, rmssd, sdnn, sns, pns):
    """
    Display full HRV analysis from Kubios cloud.

    Behaviour:
    - Shows six metrics:
        HR, PPI, RMSSD, SDNN, SNS index, PNS index.
    - Values are rounded for display.
    - Does not prompt for input (render-only screen).

    Args:
        hr (float): Mean heart rate (BPM)
        ppi (float): Mean R-R interval (ms)
        rmssd (float): RMSSD value
        sdnn (float): SDNN value
        sns (float): Sympathetic Nervous System index
        pns (float): Parasympathetic Nervous System index
    """
    oled.fill(0)
    oled.text(f"HR: {round(hr)}", 0, 0)
    oled.text(f"PPI: {round(ppi)}", 0, 10)
    oled.text(f"RMSSD: {round(rmssd)}", 0, 20)
    oled.text(f"SDNN: {round(sdnn)}", 0, 30)
    oled.text(f"SNS: {round(sns)}", 0, 40)
    oled.text(f"PNS: {round(pns)}", 0, 50)
    oled.show()
