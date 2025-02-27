
# Networking
import socket
import subprocess

import requests

from cpgsapp.controllers.FileSystemContoller import get_space_info
from cpgsapp.models import NetworkSettings
from cpgsapp.serializers import NetworkSettingsSerializer
from cpgsserver.settings import MAIN_SERVER_IP, MAIN_SERVER_PORT




def update_server():


 
    timestamp = ""
    device_id = 20001
    mac_addr = "SDF34:34DFS:L#43:DF"
    ip_address = "192.168.1.25"
    ssid = "CPGSWIFI"
    device_mode = "LIVE"
    licenseNumber = "kl23f345"
    space_id = 1003
    '''
    Sends the slotData to the server in UDP protocol
    '''
    # slotData = f'{timestamp}:{device_id}:{mac_addr}:{space_id}:{ip_address}:{ssid}:{licenseNumber}:{device_mode}'
    slotData = {
    "data":f'{timestamp}-{device_id}-{mac_addr}-{space_id}-{ip_address}:{ssid}:{licenseNumber}:{device_mode}'
    }
        
    # try:
    # url = MAIN_SERVER_IP
    # requests.post(url, json=slotData)
    # message = spaceInfo
    with open('storage/spaceInfo.txt','r') as spaces:
        spaceData = spaces.read()
        bytesToSend = str(spaceData).encode()
        print("byes array - ",spaceData)
        UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDPClientSocket.sendto(bytesToSend, (MAIN_SERVER_IP, MAIN_SERVER_PORT))
        print('Updated to MS')

    # except Exception as e:
    #     print(e)
    
    
def change_hostname(data):
        new_hostname = data['new_hostname']
        with open('/etc/hostname', 'w') as f:
            f.write(new_hostname + '\n')
        with open('/etc/hosts', 'r') as f:
            hosts_content = f.readlines()
        with open('/etc/hosts', 'w') as f:
            for line in hosts_content:
                if '127.0.1.1' in line:
                    line = f'127.0.1.1\t{new_hostname}\n'
                f.write(line)
        subprocess.run(['hostnamectl', 'set-hostname', new_hostname])
        return True
        
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
    print(currentNetworkSettings)
    serialized_settings = NetworkSettingsSerializer(currentNetworkSettings)
    return serialized_settings.data

# def network_handler():
#     spaceInfo = get_space_info()
#     timestamp = ""
#     device_id = 20001
#     mac_addr = "SDF34:34DFS:L#43:DF"
#     ip_address = "192.168.1.25"
#     ssid = "CPGSWIFI"
#     device_mode = "LIVE"
#     licenseNumber = "kl23f345"
#     space_id = 1003
#     '''
#     Sends the slotData to the server in UDP protocol
#     '''
#     # slotData = f'{timestamp}:{device_id}:{mac_addr}:{space_id}:{ip_address}:{ssid}:{licenseNumber}:{device_mode}'
#     slotData = {
#     "data":f'{timestamp}-{device_id}-{mac_addr}-{space_id}-{ip_address}:{ssid}:{licenseNumber}:{device_mode}'
#     }
        
#     # try:
#     #     url = MAIN_SERVER_IP
#     #     requests.post(url, json=slotData)
#     #     # UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
#     #     # UDPClientSocket.sendto(bytesToSend, serverSocketAddress)
#     print('Updated to MS')

def saveNetworkSetting():
    newnetworksettings = req.get('data')
    print(newnetworksettings)

    command = f"""
    nmcli con modify $(nmcli -g UUID con show --active | head -n 1) \
    ipv4.method manual \
    ipv4.addresses {newnetworksettings['ipv4_address']}/24 \
    ipv4.gateway {newnetworksettings['gateway_address']} \
    ipv4.dns "8.8.8.8 8.8.4.4"
    """

    NetworkSettings.objects.update(ipv4_address=newnetworksettings['ipv4_address'], gateway_address=newnetworksettings['gateway_address'])

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
