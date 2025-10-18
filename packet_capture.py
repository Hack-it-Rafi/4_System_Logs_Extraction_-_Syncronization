from datetime import datetime
import subprocess
import os
import time
import sys
import re

def get_network_interfaces():
    """List available network interfaces using tshark."""
    try:
        result = subprocess.run(['tshark', '-D'], capture_output=True, text=True, check=True)
        interfaces = result.stdout.splitlines()
        return interfaces
    except subprocess.CalledProcessError as e:
        print(f"Error listing interfaces: {e}")
        sys.exit(1)

def get_wifi_interface():
    """Automatically find the Wi-Fi interface by name."""
    try:
        result = subprocess.run(['tshark', '-D'], capture_output=True, text=True, check=True)
        interfaces = result.stdout.splitlines()
        
        wifi_keywords = ['Wi-Fi', 'WiFi', 'Wireless', 'WLAN']
        
        for interface_line in interfaces:
            interface_name = parse_interface_name(interface_line)
            for keyword in wifi_keywords:
                if keyword.lower() in interface_name.lower():
                    print(f"Found Wi-Fi interface: {interface_name}")
                    return interface_name
        
        print("No Wi-Fi interface found automatically. Available interfaces:")
        for interface_line in interfaces:
            print(f"  {interface_line}")
        
        if interfaces:
            default_interface = parse_interface_name(interfaces[0])
            print(f"Using default interface: {default_interface}")
            return default_interface
            
        raise Exception("No network interfaces found")
        
    except subprocess.CalledProcessError as e:
        print(f"Error listing interfaces: {e}")
        sys.exit(1)

def capture_packets(interface, output_folder, timestamp, duration=20*60):
    """Capture packets using tshark for the specified duration and save with provided timestamp."""
    os.makedirs(output_folder, exist_ok=True)
    output_file = os.path.join(output_folder, f"packet_capture_{timestamp}.pcap")
    
    tshark_cmd = [
        'tshark',
        '-i', interface,
        '-a', f'duration:{duration}',
        '-w', output_file
    ]
    
    print(f"Starting capture for {duration//60} minutes on interface {interface}, saving to {output_file}")
    try:
        subprocess.run(tshark_cmd, check=True)
        print(f"Saved packet capture: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during packet capture: {e}")
        print("Please ensure you have administrator privileges to capture packets.")
    except KeyboardInterrupt:
        print("Packet capture stopped by user")

def parse_interface_name(full_line):
    """Extract just the interface name from tshark -D output"""
    match = re.search(r'\((.*?)\)', full_line)
    if match:
        return match.group(1)
    return full_line.split()[-1]

if __name__ == "__main__":
    if len(sys.argv) > 2:
        output_folder = sys.argv[1]
        timestamp = sys.argv[2]
        # Use automatic Wi-Fi detection instead of interface number
        selected_interface = get_wifi_interface()
        capture_packets(selected_interface, output_folder, timestamp)
    else:
        # Interactive mode - automatically detect Wi-Fi
        selected_interface = get_wifi_interface()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        capture_packets(selected_interface, "packet_captures", timestamp)