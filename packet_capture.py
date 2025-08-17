import subprocess
import os
import time
from datetime import datetime
import psutil
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

def capture_packets(interface, output_dir="packet_captures", duration=20*60):
    """Capture packets using tshark for the specified duration and save with timestamped filenames."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"Starting packet capture on interface: {interface}")
    
    while True:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"packet_capture_{timestamp}.pcap")
        
        tshark_cmd = [
            'tshark',
            '-i', interface,
            '-a', f'duration:{duration}',
            '-w', output_file
        ]
        
        try:
            print(f"Starting capture for {duration//60} minutes, saving to {output_file}")
            subprocess.run(tshark_cmd, check=True)
            print(f"Saved packet capture: {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error during packet capture: {e}")
            print("Please ensure you have administrator privileges to capture packets.")
            break
        except KeyboardInterrupt:
            print("Packet capture stopped by user")
            break
        
        time.sleep(1)

def parse_interface_name(full_line):
    """Extract just the interface name from tshark -D output"""
    # Example line: "1. \Device\NPF_{3AAD2F16-7ECD-492F-B5FD-2C1E14CCCED5} (Local Area Connection* 9)"
    match = re.search(r'\((.*?)\)', full_line)
    if match:
        return match.group(1)
    return full_line.split()[-1]

if __name__ == "__main__":
        if len(sys.argv) > 1:
            # Use the provided interface number
            interfaces = get_network_interfaces()
            selected_interface = parse_interface_name(interfaces[int(sys.argv[1])-1])
            capture_packets(selected_interface)
        else:
            # Original interactive selection code
            interfaces = get_network_interfaces()
            print("Available network interfaces:")
            for i, iface in enumerate(interfaces, 1):
                print(f"{i}. {iface}")

            try:
                choice = int(input("Select interface number (e.g., 1): ")) - 1
                if 0 <= choice < len(interfaces):
                    # Extract just the interface name (the part in parentheses)
                    selected_interface = parse_interface_name(interfaces[choice])
                else:
                    print("Invalid interface number")
                    sys.exit(1)
            except ValueError:
                print("Invalid input. Please enter a number.")
                sys.exit(1)

            capture_packets(selected_interface)