import os
import subprocess
import time
from datetime import datetime, timedelta
import threading
import signal
import sys

# Configuration
INTERVAL_MINUTES = 20
SCREEN_RECORDING_SCRIPT = "screen_recorder.py"
PACKET_CAPTURE_SCRIPT = "packet_capture.py"
LOG_EXTRACTION_SCRIPT = "extract_syslogs.py"

# Global variables
processes = []
stop_event = threading.Event()

def run_script(script_name, output_folder, timestamp, *args):
    """Run a Python script as a subprocess."""
    cmd = ["python", script_name, output_folder, timestamp]
    cmd.extend(args)
    process = subprocess.Popen(cmd)
    processes.append(process)
    return process

def stop_all_processes():
    """Stop and clear all running subprocesses."""
    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()
    processes.clear()

def signal_handler(sig, frame):
    """Graceful shutdown on Ctrl+C."""
    print("\nShutting down monitoring system...")
    stop_event.set()
    stop_all_processes()
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)

    base_output_dir = "monitoring_outputs"
    os.makedirs(base_output_dir, exist_ok=True)

    print("Starting continuous monitoring system...")
    print(f"Interval: {INTERVAL_MINUTES} minutes\n")

    while not stop_event.is_set():
        # Mark the start of the interval
        interval_start = datetime.now().replace(second=0, microsecond=0)
        print(f"Monitor Interval starting at {interval_start}")
        timestamp = interval_start.strftime("%Y%m%d_%H%M%S")
        print(f"Timestamp for this interval: {timestamp}")
        output_folder = os.path.join(base_output_dir, timestamp)
        os.makedirs(output_folder, exist_ok=True)

        print(f"New interval started at {interval_start}, saving to {output_folder}")

        # Start screen recording + packet capture immediately
        print(" -> Starting screen recording...")
        run_script(SCREEN_RECORDING_SCRIPT, output_folder, timestamp)

        print(" -> Starting packet capture...")
        run_script(PACKET_CAPTURE_SCRIPT, output_folder, timestamp, "5")

        # Sleep for the interval duration
        time.sleep(INTERVAL_MINUTES * 60)

        # End of interval: stop recording + capture
        print(f"\nInterval ended ({INTERVAL_MINUTES} mins). Stopping processes...")
        stop_all_processes()

        # Extract system logs for the past interval
        print(" -> Extracting system logs for this interval...")
        run_script(LOG_EXTRACTION_SCRIPT, output_folder, timestamp)

        # Wait for logs extraction to finish before next interval
        for process in processes:
            process.wait()
        processes.clear()

        print("Ready for next interval...\n")

if __name__ == "__main__":
    main()
