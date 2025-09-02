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
    if len(sys.argv) > 3:
        output_folder = sys.argv[1]
        timestamp = sys.argv[2]
        interface_num = sys.argv[3]
        interfaces = get_network_interfaces()
        selected_interface = parse_interface_name(interfaces[int(interface_num)-1])
        capture_packets(selected_interface, output_folder, timestamp)
    else:
        interfaces = get_network_interfaces()
        print("Available network interfaces:")
        for i, iface in enumerate(interfaces, 1):
            print(f"{i}. {iface}")
        try:
            choice = int(input("Select interface number (e.g., 1): ")) - 1
            if 0 <= choice < len(interfaces):
                selected_interface = parse_interface_name(interfaces[choice])
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                capture_packets(selected_interface, "packet_captures", timestamp)
            else:
                print("Invalid interface number")
                sys.exit(1)
        except ValueError:
            print("Invalid input. Please enter a number.")
            sys.exit(1)