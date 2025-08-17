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

# Global variables to track subprocesses
processes = []
stop_event = threading.Event()

def run_script(script_name, *args):
    """Run a Python script in a separate process."""
    cmd = ["python", script_name]
    cmd.extend(args)
    process = subprocess.Popen(cmd)
    processes.append(process)
    return process

def stop_all_processes():
    """Stop all running subprocesses."""
    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()
    processes.clear()

def signal_handler(sig, frame):
    """Handle Ctrl+C signal to gracefully shutdown."""
    print("\nShutting down monitoring system...")
    stop_event.set()
    stop_all_processes()
    sys.exit(0)

def synchronize_start():
    """Wait until the next 20-minute interval starts."""
    now = datetime.now()
    next_interval = now + timedelta(minutes=INTERVAL_MINUTES)
    next_interval = next_interval.replace(second=0, microsecond=0)
    sleep_seconds = (next_interval - now).total_seconds()
    
    if sleep_seconds > 0:
        print(f"Waiting {sleep_seconds:.1f} seconds until next interval at {next_interval}")
        time.sleep(sleep_seconds)

def main():
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Make sure output directories exist
    os.makedirs("screen_recordings", exist_ok=True)
    os.makedirs("packet_captures", exist_ok=True)
    os.makedirs("system_logs", exist_ok=True)
    
    print("Starting synchronized monitoring system...")
    print(f"Will capture data in {INTERVAL_MINUTES}-minute intervals")
    
    # Initial synchronization
    synchronize_start()
    
    # Start packet capture (runs continuously)
    print("Starting packet capture...")
    run_script(PACKET_CAPTURE_SCRIPT, "5")  # Assuming interface 1 is selected
    
    while not stop_event.is_set():
        current_interval_start = datetime.now().replace(second=0, microsecond=0)
        timestamp = current_interval_start.strftime("%Y%m%d_%H%M%S")
        print(f"\nStarting new capture interval at {current_interval_start}")
        
        # Start screen recording (will auto-stop after INTERVAL_MINUTES)
        print("Starting screen recording...")
        run_script(SCREEN_RECORDING_SCRIPT)
        
        # Start log extraction (will auto-stop after INTERVAL_MINUTES)
        print("Starting log extraction...")
        run_script(LOG_EXTRACTION_SCRIPT)
        
        # Wait for the interval to complete
        time.sleep(INTERVAL_MINUTES * 60)
        
        # Stop and restart processes for the next interval
        print("Preparing for next interval...")
        stop_all_processes()

if __name__ == "__main__":
    main()