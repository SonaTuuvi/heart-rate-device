from ui.layout_hr import show_start_instruction
from ui.layout_animations import draw_ecg_frame
from ui.layout_hrv import show_hrv_screen, show_start_instruction_hrv
from ui.layout_common import show_error_screen
from ui.oled import oled

from core.utils import is_encoder_pressed, encoder_button
from core.hrv import calculate_hrv
from core.hrm import calibrate_threshold, read_live_signal, calculate_bpm
from core.wifi_mqtt import connect_wifi, connect_mqtt, publish_json
from core.config import WIFI_SSID, WIFI_PASSWORD, MQTT_BROKER
from core.adc_sampler import start_sampling
from history.history_utils import append_to_hrv_history

import time
import network



def handle_basic_hrv():
    print("[HRV] handle_basic_hrv() ENTER")

    show_start_instruction_hrv()
    print("[HRV] start instruction shown")

    while not is_encoder_pressed():
        time.sleep(0.05)
    print("[HRV] encoder pressed (logical)")

    while encoder_button.value() == 0:
        time.sleep(0.05)
    print("[HRV] encoder released (physical)")

    start_sampling()
    print("[HRV] ADC sampling started")

    oled.fill(0)
    oled.text("COLLECTING DATA...", 0, 20)
    oled.show()
    time.sleep(1)

    threshold = calibrate_threshold()
    print("[HRV] threshold calibrated:", threshold)

    buffer = []
    intervals = []
    beats = []

    start_time = time.ticks_ms()
    print("[HRV] measurement start_time:", start_time)

    while time.ticks_diff(time.ticks_ms(), start_time) < 30_000:
        value, beat = read_live_signal(threshold)

        buffer.append(value)
        if len(buffer) > 128:
            buffer.pop(0)

        if beat:
            now = time.ticks_ms()
            beats.append(now)
            print("[HRV] beat detected at", now)

            if len(beats) > 1:
                interval = time.ticks_diff(beats[-1], beats[-2])
                print("[HRV] interval:", interval)

                if 250 < interval < 2000:
                    intervals.append(interval)
                    print("[HRV] interval accepted, total:", len(intervals))
                else:
                    print("[HRV] interval rejected")

        bpm = calculate_bpm(intervals[-5:])
        time_left = 30 - time.ticks_diff(time.ticks_ms(), start_time) // 1000

        draw_ecg_frame(buffer, time_left, bpm)
        time.sleep(0.01)

    print("[HRV] collection finished")
    print("[HRV] intervals count:", len(intervals))

    if len(intervals) < 2:
        print("[HRV] ERROR: not enough intervals")
        show_error_screen()
        return

    mean_hr, mean_ppi, rmssd, sdnn = calculate_hrv(intervals)
    print("[HRV] HRV calculated:",
          mean_hr, mean_ppi, rmssd, sdnn)

    data = {
        "timestamp": str(time.ticks_ms()),
        "mean_hr": mean_hr,
        "mean_ppi": mean_ppi,
        "rmssd": rmssd,
        "sdnn": sdnn
    }

    print("[HRV] data prepared:", data)

    print("[HRV] saving to hrv_analysis.json")
    append_to_hrv_history(data)
    print("[HRV] save function returned")

    oled.fill(0)
    oled.text("SENDING DATA...", 0, 20)
    oled.show()

    while True:
        try:
            print("[HRV] connecting WiFi...")
            connect_wifi(WIFI_SSID, WIFI_PASSWORD)

            if network.WLAN(network.STA_IF).isconnected():
                print("[HRV] WiFi connected")
                connect_mqtt()
                print("[HRV] MQTT connected")
                publish_json("hrv/data", data)
                print("[HRV] MQTT data published")
                break
            else:
                print("[HRV] WiFi NOT connected")
                if show_error_screen() == "exit":
                    return

        except Exception as e:
            print("[HRV] EXCEPTION during MQTT:", e)
            if show_error_screen() == "exit":
                return

    print("[HRV] showing HRV screen")
    show_hrv_screen(mean_hr, mean_ppi, rmssd, sdnn)
    print("[HRV] handle_basic_hrv() EXIT")
