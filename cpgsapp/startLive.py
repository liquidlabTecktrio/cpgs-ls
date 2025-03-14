# Developed By Tecktrio At Liquidlab Infosystems
# Project: StartLive methods
# Version: 1.0
# Date: 2025-03-08
# Description: Runs to start the camera frames from when the server starts

# startup_watcher.py
import socket
import time
import requests

# from controllers.HardwareController import free_camera_device

"""Wait until the server is listening on the specified port."""
while True:
    try:


        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect(("0.0.0.0", 8000))
        print(f"Server is up on 0.0.0.0:8000")
        requests.get(f'http://0.0.0.0:8000/initiate')
        break
    except (ConnectionRefusedError, socket.timeout):
        print(f"Waiting for server on 0.0.0.0:8000...")
        time.sleep(1)  # Check every second



