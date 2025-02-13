import os
import subprocess

def set_static_ip(interface, ip_address, gateway, dns):
    try:
        # Bring the interface down before configuring
        subprocess.run(["nmcli", "device", "down", interface], check=True)

        # Modify connection settings to use manual IP configuration
        subprocess.run(["nmcli", "con", "modify", interface, "ipv4.addresses", ip_address], check=True)
        subprocess.run(["nmcli", "con", "modify", interface, "ipv4.gateway", gateway], check=True)
        subprocess.run(["nmcli", "con", "modify", interface, "ipv4.dns", dns], check=True)
        subprocess.run(["nmcli", "con", "modify", interface, "ipv4.method", "manual"], check=True)

        # Bring the interface up after configuration
        subprocess.run(["nmcli", "device", "up", interface], check=True)

        print("Static IP configured successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to set static IP: {e}")

if __name__ == "__main__":
    interface = "wlan0"  # Change to 'wlan0' if needed
    ip_address = "192.168.1.100/24"  # Static IP with CIDR notation
    gateway = "192.168.1.1"  # Default gateway
    dns = "8.8.8.8"  # DNS server

    set_static_ip(interface, ip_address, gateway, dns)
