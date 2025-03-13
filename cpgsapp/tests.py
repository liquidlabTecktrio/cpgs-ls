# your_app/publish_monitor.py
import paho.mqtt.client as mqtt
import json
import time
from django.conf import settings

class MonitorPublisher:
    def __init__(self):
        self.broker = "localhost"  # Replace with your broker IP
        self.port = 1883
        self.topic = "monitor/stream"
        self.client = mqtt.Client()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT broker")
        else:
            print(f"Connection failed with code {rc}")

    def start(self):
        self.client.on_connect = self.on_connect
        self.client.connect(self.broker, self.port)
        self.client.loop_start()  # Start the network loop in a separate thread

    def publish(self, data):
        payload = json.dumps(data)
        self.client.publish(self.topic, payload, qos=1)
        print(f"Published to {self.topic}: {payload}")

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

# Example usage in a management command or view
publisher = MonitorPublisher()
publisher.start()

# Simulate continuous data (replace with your GET_MONITOR_VIEWS logic)
def simulate_stream():
    while True:
        data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "data": "Stream update"  # Replace with real monitor data
        }
        publisher.publish(data)
        time.sleep(1)  # Adjust frequency

# if __name__ == "__main__":
#     simulate_stream()