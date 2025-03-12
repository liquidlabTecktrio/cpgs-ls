# Developed By Tecktrio At Liquidlab Infosystems
# Project: Network Contoller Methods
# Version: 1.0
# Date: 2025-03-08
# Description: A simple Network Controller to manage network related activities


# Importing functions
import socket
import subprocess
from cpgsapp.controllers.FileSystemContoller import get_space_info
from cpgsapp.models import NetworkSettings
from cpgsapp.serializers import NetworkSettingsSerializer
from storage import Variables

# Function to update space status to the server
def update_server():
    """Detects changes in space status and updates the main server."""
    current_spaces = get_space_info()
    if current_spaces != {}:
        NetworkSetting = NetworkSettings.objects.first()
        last_spaces = Variables.LAST_SPACES
        changed_space = None

        for space in range(Variables.TOTALSPACES):
            if space in current_spaces and space in last_spaces:
                if current_spaces[space]['spaceStatus'] != last_spaces[space]['spaceStatus']:
                    changed_space = space
                    break
        if changed_space is not None:
            sd = current_spaces[changed_space]
            print("Changes found in space index", changed_space)
            data_to_send = {
                "spaceID": sd['spaceID'],
                "spaceStatus": sd['spaceStatus'],
                # "licensePlate": sd['licensePlate']
            }
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_client:
                udp_client.sendto(str(data_to_send).encode(), (NetworkSetting.server_ip, NetworkSetting.server_port))
        print("Updating MS with IP ",NetworkSetting.server_ip," with ",NetworkSetting.server_port)



# Function to change the hostname
def change_hostname(new_hostname):
    """Updates the system hostname."""
    try:
        commands = [
            f'echo "{new_hostname}" | sudo tee /etc/hostname',
            f'sudo sed -i "s/127.0.1.1.*/127.0.1.1\t{new_hostname}/" /etc/hosts',
            f'sudo hostnamectl set-hostname {new_hostname}'
        ]
        for cmd in commands:
            subprocess.run(cmd, shell=True, check=True, text=True)
        print(f"Hostname successfully changed to {new_hostname}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error changing hostname: {e}")
        return False


# Function to set a static IP
def set_static_ip(data):
    """Configures a static IP address."""
    try:
        nmcli_commands = [
            f"nmcli con modify {data['connection_name']} ipv4.addresses {data['static_ip']}",
            f"nmcli con modify {data['connection_name']} ipv4.gateway {data['gateway_ip']}",
            f"nmcli con modify {data['connection_name']} ipv4.dns {data['dns_ip']}",
            f"nmcli con modify {data['connection_name']} ipv4.method manual",
            f"nmcli con down {data['connection_name']}",
            f"nmcli con up {data['connection_name']}"
        ]
        for cmd in nmcli_commands:
            subprocess.run(cmd, shell=True, check=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error setting static IP: {e}")
        return False


# Function to set a dynamic IP
def set_dynamic_ip(data):
    """Configures a dynamic IP address."""
    try:
        nmcli_commands = [
            f"nmcli con modify {data['connection_name']} ipv4.method auto",
            f"nmcli con down {data['connection_name']}",
            f"nmcli con up {data['connection_name']}"
        ]
        for cmd in nmcli_commands:
            subprocess.run(cmd, shell=True, check=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error setting dynamic IP: {e}")
        return False


# Function to get network settings
def get_network_settings():
    """Retrieves the current network settings."""
    settings = NetworkSettings.objects.first()
    return NetworkSettingsSerializer(settings).data if settings else {}


# Function to save network settings
def saveNetworkSetting(new_settings):
    """Saves new network settings and applies them."""
    try:
        command = f"""
        nmcli con modify $(nmcli -g UUID con show --active | head -n 1) \
        ipv4.method manual \
        ipv4.addresses {new_settings.ipv4_address}/24 \
        ipv4.gateway {new_settings.gateway_address} \
        ipv4.dns "8.8.8.8 8.8.4.4"
        """
        subprocess.run(["sudo", "bash", "-c", command], check=True, text=True)
        connection_name = "preconfigured"
        subprocess.run(["sudo", "nmcli", "connection", "down", connection_name], check=True, text=True)
        subprocess.run(["sudo", "nmcli", "connection", "up", connection_name], check=True, text=True)
        subprocess.run(["sudo", "reboot", "now"], check=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error saving network settings: {e}")


# Function to connect to a WiFi network
def connect_to_wifi(ssid, password):
    """Connects to a WiFi network and enables autoconnect."""
    try:
        nmcli_commands = [
            f'nmcli dev wifi connect "{ssid}" password "{password}"',
            f'nmcli connection modify "{ssid}" connection.autoconnect yes'
        ]
        for cmd in nmcli_commands:
            subprocess.run(cmd, shell=True, check=True, text=True)
        print(f"Connected to WiFi: {ssid}")
    except subprocess.CalledProcessError as e:
        print(f"Error connecting to WiFi: {e}")
