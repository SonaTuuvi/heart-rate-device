from core.utils import is_encoder_pressed, encoder_button
from core.hrm import calibrate_threshold, pulse_sensor
from ui.layout_hr import show_start_instruction, show_hr_screen
from ui.layout_common import show_error_screen, show_sending_screen
from ui.layout_menu import show_menu
from ui.layout_animations import show_countdown_animation_kubios
from core.config import MAC_ADDRESS

from core.wifi_mqtt import connect_wifi, wait_for_kubios_result, publish_json
from history.history_utils import save_to_history
from core.menu import get_menu_items, get_current_selection
from core.config import (
    WIFI_SSID,
    WIFI_PASSWORD,
    MQTT_TOPIC_PUB,
    MQTT_TOPIC_SUB
)

import time
import network
import ujson
import core.wifi_mqtt as wifi
from cloud.kubios_utils import format_kubios_payload, handle_kubios_response


def collect_ppi_data(duration=30):
    """
    Collect P-P (peak-to-peak) intervals using the ECG animation.
    This function shows the animated ECG graph while collecting data.

    Args:
        duration (int): Duration in seconds for data collection.

    Returns:
        list: Collected RR intervals (in milliseconds).
    """
    intervals = show_countdown_animation_kubios(duration=duration)
    return intervals


def wait_for_encoder_press():
    """
    Show start instructions and wait for the user to press the encoder button.

    Debounces the button to avoid multiple triggers.
    """
    show_start_instruction()
    while not is_encoder_pressed():
        time.sleep(0.05)
    while encoder_button.value() == 0:
        time.sleep(0.05)


def setup_wifi_and_mqtt():
    """
    Connect to Wi-Fi and initialize the MQTT client.

    Raises:
        Exception: If Wi-Fi connection fails.
    """
    if not wifi.connect_wifi(WIFI_SSID, WIFI_PASSWORD):
        raise Exception("WiFi not connected")
    wifi.connect_mqtt()


def kubios_analysis():
    """
    Main flow for Kubios HRV analysis:

    1. Wait for the user to press the encoder button.
    2. Collect RR intervals using ECG display animation.
    3. Validate collected data (must have at least 5 valid intervals).
    4. Format the data into a Kubios-compatible JSON payload.
    5. Connect to Wi-Fi and send the payload via MQTT.
    6. Wait for Kubios results and handle the response.
    7. If any step fails, show an error screen with retry/exit options.
    """
    try:
        wait_for_encoder_press()

        intervals = collect_ppi_data(duration=30)

        if len(intervals) < 5:
            # Not enough data for analysis – show error and exit
            show_error_screen()
            return

        # Format collected data into Kubios-compatible format
        payload = format_kubios_payload(intervals)

        # Show "sending" animation and pause briefly
        show_sending_screen()
        time.sleep(1)

        # Establish Wi-Fi and MQTT connection
        setup_wifi_and_mqtt()

        # Publish the request to the Kubios server
        publish_json("kubios/request", intervals)

        # Wait for Kubios to send back analysis results
        result = wait_for_kubios_result()

        if result:
            # If response received, handle and display it
            handle_kubios_response(result)
        else:
            # Timeout or no response – ask user to retry or exit
            user_choice = show_error_screen()
            if user_choice == "retry":
                kubios_analysis()
            elif user_choice == "exit":
                show_menu(get_menu_items(), get_current_selection())

    except Exception:
        # Any unexpected exception – allow user to retry or exit
        user_choice = show_error_screen()
        if user_choice == "retry":
            kubios_analysis()
        elif user_choice == "exit":
            show_menu(get_menu_items(), get_current_selection())
