
# Networking
import socket
import subprocess

import requests

from cpgsapp.controllers.FileSystemContoller import get_space_info
from cpgsapp.models import NetworkSettings
from cpgsapp.serializers import NetworkSettingsSerializer
from cpgsserver.settings import MAIN_SERVER_IP, MAIN_SERVER_PORT
from storage import Variables




def update_server():

    currentSpacesInfo = get_space_info()
    lastSpacesInfo = Variables.LAST_SPACES

    indexThatchanged = 0
    isChange = False
    # status = 'unknown'

    for space in range(Variables.TOTALSPACES):
        if currentSpacesInfo[space]['spaceStatus'] != lastSpacesInfo[space]['spaceStatus']:
            indexThatchanged = space
            isChange=True


    if isChange:
        sd = currentSpacesInfo[indexThatchanged]

        print(" changes found in space index", indexThatchanged)

        dataToSend = {
        "spaceID" : sd['spaceID'], 
        "spaceStatus" : sd['spaceStatus'], 
        "licensePlate" : sd['licensePlate']
        }


        bytesToSend = str(dataToSend).encode()
        UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPClientSocket.sendto(bytesToSend, (MAIN_SERVER_IP, MAIN_SERVER_PORT))
        print('Updated to MS')
import subprocess

def change_hostname(new_hostname):
    try:
        # Update /etc/hostname
        subprocess.run(['sudo', 'bash', '-c', f'echo "{new_hostname}" > /etc/hostname'], check=True)

        # Update /etc/hosts
        subprocess.run(['sudo', 'sed', '-i', f's/127.0.1.1.*/127.0.1.1\t{new_hostname}/', '/etc/hosts'], check=True)

        # Change system hostname
        subprocess.run(['sudo', 'hostnamectl', 'set-hostname', new_hostname], check=True)

        print(f"Hostname successfully changed to {new_hostname}")
        return True

    except Exception as e:
        print(f"Error changing hostname: {e}")
        return False

        
def set_static_ip(data):
    connection_name = data['connection_name']
    static_ip = data['static_ip']
    gateway_ip = data['gateway_ip']
    dns_ip = data['dns_ip']
    subprocess.run(['nmcli', 'con', 'modify', connection_name, 'ipv4.addresses', static_ip])
    subprocess.run(['nmcli', 'con', 'modify', connection_name, 'ipv4.gateway', gateway_ip])
    subprocess.run(['nmcli', 'con', 'modify', connection_name, 'ipv4.dns', dns_ip])
    subprocess.run(['nmcli', 'con', 'modify', connection_name, 'ipv4.method', 'manual'])
    subprocess.run(['nmcli', 'con', 'down', connection_name])
    subprocess.run(['nmcli', 'con', 'up', connection_name])
    return True

def set_dynamic_ip(data):
    connection_name = data['connection_name']
    subprocess.run(['nmcli', 'con', 'modify', connection_name, 'ipv4.method', 'auto'])
    subprocess.run(['nmcli', 'con', 'down', connection_name])
    subprocess.run(['nmcli', 'con', 'up', connection_name])
    return True

# @sync_to_async
def get_network_settings():
    currentNetworkSettings = NetworkSettings.objects.first()
    serialized_settings = NetworkSettingsSerializer(currentNetworkSettings)
    return serialized_settings.data

def saveNetworkSetting(newnetworksettings):
    command = f"""
    nmcli con modify $(nmcli -g UUID con show --active | head -n 1) \
    ipv4.method manual \
    ipv4.addresses {newnetworksettings.ipv4_address}/24 \
    ipv4.gateway {newnetworksettings.gateway_address} \
    ipv4.dns "8.8.8.8 8.8.4.4"
    """

    # Run the command with sudo
    subprocess.run(["sudo", "bash", "-c", command], capture_output=True, text=True)
    connection_name = "preconfigured"


    # Bring the connection down
    subprocess.run(
        ["sudo", "nmcli", "connection", "down", connection_name],
        check=True,
        capture_output=True,
        text=True
    )

    # Bring the connection up
    subprocess.run(
        ["sudo", "nmcli", "connection", "up", connection_name],
        check=True,
        capture_output=True,
        text=True
    )

        # Bring the connection up
    subprocess.run(
        ["sudo", "reboot", "now"],
        check=True,
        capture_output=True,
        text=True
    )


def connect_to_wifi(ssid, password):
    try:
        # Scan for new networks
        subprocess.run('sudo nmcli device wifi rescan', shell=True, check=True, text=True, capture_output=True)
        
        # Connect to the WiFi
        connect_command = f'sudo nmcli dev wifi connect "{ssid}" password "{password}"'
        subprocess.run(connect_command, shell=True, check=True, text=True, capture_output=True)
        print(f"Connected to WiFi: {ssid}")

        # Set autoconnect to ensure it connects after reboot
        autoconnect_command = f'sudo nmcli connection modify "{ssid}" connection.autoconnect yes'
        subprocess.run(autoconnect_command, shell=True, check=True, text=True, capture_output=True)
        print(f"Enabled autoconnect for: {ssid}")

    except subprocess.CalledProcessError as e:
        print("Error:", e.stderr)

# Example usage:
