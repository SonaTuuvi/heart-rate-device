from core.config import MAC_ADDRESS
from ui.layout_hrv import show_kubios_results

from ui.layout_menu import show_menu
from core.menu import get_menu_items, get_current_selection
from ui.layout_common import show_error_screen


from core.utils import is_encoder_pressed, encoder_button
from ui.layout_hrv import show_kubios_results
from history.history_utils import save_to_history
import time


def format_kubios_payload(ppi_list):
    mac_no_colons = MAC_ADDRESS.replace(":", "")
    return {
        "type": "RRI",
        "mac": mac_no_colons,
        "data": ppi_list,
        "analysis": {
            "type": "readiness"
        }
    } 

def handle_kubios_response(result):
    try:
        print("[DEBUG] handle_kubios_response() called with:", result)

        display_data = {
            "mean_hr": result["mean_hr"],
            "mean_ppi": result["mean_ppi"],
            "rmssd": result["rmssd"],
            "sdnn": result["sdnn"],
            "sns": result.get("sns", 0),
            "pns": result.get("pns", 0)
        }

        save_to_history(display_data)

        show_kubios_results(
            display_data["mean_hr"],
            display_data["mean_ppi"],
            display_data["rmssd"],
            display_data["sdnn"],
            display_data["sns"],
            display_data["pns"]
        )

        # Ожидание кнопки
        while not is_encoder_pressed():
            time.sleep(0.05)
        while encoder_button.value() == 0:
            time.sleep(0.05)

        show_menu(get_menu_items(), get_current_selection())

    except Exception as e:
        print("❌ Error in handle_kubios_response:", e)
        show_error_screen()
