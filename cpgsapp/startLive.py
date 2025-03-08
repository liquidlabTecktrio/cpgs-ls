# startup_watcher.py
import socket
import threading
import time
import json
from pathlib import Path

import requests

# Function to start live after server is started
def wait_for_server(host='0.0.0.0', port=8000):
    """Wait until the server is listening on the specified port."""
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((host, port))
            print(f"Server is up on {host}:{port}")
            requests.get(f'http://{host}:{port}/initiate')
            break
        except (ConnectionRefusedError, socket.timeout):
            print(f"Waiting for server on {host}:{port}...")
            time.sleep(1)  # Check every second

if __name__ == "__main__":
    wait_for_server()  # Wait for port 8000
   

