

import network
import time
import ujson
from umqtt.simple import MQTTClient
from core.config import (
    WIFI_SSID,
    WIFI_PASSWORD,
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_CLIENT_ID
)

client = None

def connect_wifi(ssid=WIFI_SSID, password=WIFI_PASSWORD):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    timeout = 10
    while not wlan.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1
    return wlan.isconnected()

def connect_mqtt():
    global client
    client = MQTTClient(
        client_id=MQTT_CLIENT_ID,
        server=MQTT_BROKER,
        port=MQTT_PORT
    )
    client.connect(clean_session=True)

def publish_json(topic, data_dict):
    global client
    if client:
        payload = ujson.dumps(data_dict)
        client.publish(topic, payload)
    else:
        print("MQTT client not connected.")
