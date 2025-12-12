"""
Wi-Fi and MQTT communication utilities for Kubios cloud integration.

This module provides helper functions to:
1. Connect to Wi-Fi with retry logic and timeout handling.
2. Establish MQTT connection, configure callbacks, and subscribe to topic.
3. Publish JSON payloads to a remote endpoint.
4. Wait asynchronously for a Kubios result within a timeout.
5. Parse inbound MQTT messages, validate content, and extract HRV metrics.

Global variables:
- `client` holds the active MQTTClient instance after connection.
- `kubios_result` stores parsed results from Kubios reply.

The module acts as a networking layer for HRV analysis publishing and
result retrieval. Error handling is intentionally lightweight to avoid
device crash, printing status messages to console instead.
"""


import network
import time
import ujson
from umqtt.simple import MQTTClient

from core.config import (
    WIFI_SSID,
    WIFI_PASSWORD,
    MAX_WIFI_RETRIES,
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_CLIENT_ID,
    MAX_MQTT_RETRIES,
    MQTT_TOPIC_SUB,
    MQTT_TOPIC_PUB,
    MAC_ADDRESS
)

from cloud.kubios_utils import handle_kubios_response, format_kubios_payload

client = None
kubios_result = None

def connect_wifi(ssid, password):
    """
    Connect to a Wi-Fi access point with retry attempts.

    Behaviour:
    - Activates STA interface.
    - Attempts connection MAX_WIFI_RETRIES times.
    - Each attempt waits up to 10 seconds for association.
    - Prints diagnostic output to console during connection wait.

    Args:
        ssid (str): Wi-Fi SSID name.
        password (str): Wi-Fi password.

    Returns:
        bool: True on successful connection,
              False if all retries are exhausted.
    """

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    for attempt in range(MAX_WIFI_RETRIES):
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        timeout = 10
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1

        if wlan.isconnected():
            return True

    return False

def connect_mqtt():
    """
    Initialize and connect the MQTT client with retry logic.

    Behaviour:
    - Creates an MQTTClient with broker, port, and client ID.
    - Sets up message callback handler.
    - Attempts MAX_MQTT_RETRIES connections.
    - On success:
        - Prints confirmation.
        - Subscribes to `MQTT_TOPIC_SUB`.

    Returns:
        bool: True when connected and subscribed,
              False on persistent failure.
    """

    global client

    client = MQTTClient(
        client_id=MQTT_CLIENT_ID,
        server=MQTT_BROKER,
        port=MQTT_PORT
    )

    client.set_callback(on_message)

    for attempt in range(MAX_MQTT_RETRIES):
        try:
            client.connect(clean_session=True)

            client.subscribe(MQTT_TOPIC_SUB)
            return True

        except Exception as e:
            time.sleep(1)

    return False


def publish_json(topic, rr_intervals):
    """
    Publish a formatted JSON payload to the MQTT broker.

    Behaviour:
    - Builds payload using `format_kubios_payload(rr_intervals)`.
    - Serializes to JSON string via `ujson.dumps`.
    - Publishes to `topic` via active MQTT client.

    Args:
        topic (str): MQTT topic to publish to.
        rr_intervals (list): Sequence of R-R interval values.

    Notes:
    - If no active `client`, logs an error message.
    - Runtime errors during publish are caught and printed.
    """

    global client
    if client:
        payload_dict = format_kubios_payload(rr_intervals)
        payload = ujson.dumps(payload_dict)
        client.publish(topic, payload)
    else:
        print("MQTT not connected!")



def wait_for_kubios_result(timeout=10):
    """
    Wait asynchronously for Kubios analysis result to arrive via MQTT.

    Behaviour:
    - Polls client.check_msg() in a loop.
    - Returns global `kubios_result` when available.
    - Terminates after `timeout` seconds if no message arrived.

    Args:
        timeout (int): Seconds to wait before giving up.

    Returns:
        dict | None:
            HRV result if received within timeout,
            None otherwise.
    """

    global kubios_result
    start = time.time()

    while time.time() - start < timeout:
        client.check_msg()

        if kubios_result is not None:
            return kubios_result

        time.sleep(0.1)

    return None

def on_message(topic, msg):
    """
    MQTT message callback handler for Kubios response parsing.

    Behaviour:
    - Decodes inbound MQTT payload.
    - Validates presence of 'data' field.
    - Extracts nested 'analysis' dictionary.
    - Normalizes HRV metrics into a flat result:
        mean_hr, mean_ppi, rmssd, sdnn, sns, pns.
    - Performs sanity check for required keys.
    - Assigns normalized dict to global `kubios_result`.

    Args:
        topic (bytes): Incoming MQTT topic.
        msg (bytes): Raw JSON message.

    Notes:
    - Errors during decoding or validation are printed.
    - Does not raise exceptions to avoid IRQ crash.
    """
    
    global kubios_result

    try:
        parsed = ujson.loads(msg.decode())

        if "data" not in parsed:
            return

        raw_data = parsed["data"]

        if not isinstance(raw_data, dict):
            return

        analysis = raw_data.get("analysis", {})
        normalized = {
            "mean_hr": analysis.get("mean_hr_bpm"),
            "mean_ppi": analysis.get("mean_rr_ms"),
            "rmssd": analysis.get("rmssd_ms"),
            "sdnn": analysis.get("sdnn_ms"),
            "sns": analysis.get("sns_index", 0),
            "pns": analysis.get("pns_index", 0)
        }

        for key in ["mean_hr", "mean_ppi", "rmssd", "sdnn"]:
            if normalized[key] is None:
                return

        kubios_result = normalized

    except Exception as e:
        kubios_result = None
