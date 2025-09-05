import sys
import os
import requests
from datetime import datetime, timedelta
import json
import pytz

API_BASE = "http://localhost:5600/api/0"

def get_available_buckets():
    """Fetch list of available buckets from ActivityWatch."""
    try:
        response = requests.get(f"{API_BASE}/buckets")
        response.raise_for_status()
        return list(response.json().keys())
    except requests.exceptions.RequestException as e:
        print(f"Error fetching buckets: {e}")
        return []

def fetch_browser_logs(bucket_id, start_time, end_time, output_folder, timestamp):
    api_url = f"{API_BASE}/buckets/{bucket_id}/events"
    
    print(f"start_time: {start_time}, end_time: {end_time}")
    
    try:
        if isinstance(start_time, str):
            start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.UTC)
        else:
            start_dt = start_time.astimezone(pytz.UTC) 
        
        if isinstance(end_time, str):
            end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.UTC)
        else:
            end_dt = end_time.astimezone(pytz.UTC)  
            
        print(f"Fetching logs from {start_dt} to {end_dt}")
        
        response = requests.get(api_url)
        response.raise_for_status()
        events = response.json()
        
        filtered_events = [
            event for event in events
            if start_dt <= datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00")) <= end_dt
        ]
        
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, f"{bucket_id}_logs_{timestamp}.json")
        with open(output_file, "w") as f:
            json.dump(filtered_events, f, indent=4)
        print(f"Browser logs saved to {output_file}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching browser logs: {e}")
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, f"{bucket_id}_logs_{timestamp}_error.json")
        with open(output_file, "w") as f:
            json.dump({"error": str(e)}, f)
    except ValueError as e:
        print(f"Error parsing timestamps: {e}")
        os.makedirs(output_folder, exist_ok=True)
        output_file = os.path.join(output_folder, f"{bucket_id}_logs_{timestamp}_error.json")
        with open(output_file, "w") as f:
            json.dump({"error": f"Timestamp parsing error: {str(e)}"}, f)
            
                  
def main():
    if len(sys.argv) == 4:
        output_folder = sys.argv[1]
        timestamp = sys.argv[2]
        interval_minutes = int(sys.argv[3])
    else:
        print("No arguments provided, running with default values...")
        output_folder = "logs"
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        interval_minutes = 50
    
    try:
        end_time = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
        start_time = end_time - timedelta(minutes=interval_minutes)
    except ValueError as e:
        print(f"Error parsing timestamp: {e}")
        sys.exit(1)

    buckets = get_available_buckets()
    if not buckets:
        print("No buckets found. Is ActivityWatch running?")
        sys.exit(1)

    print("Available buckets:", buckets)

    # Find any Chrome or Firefox browser log bucket
    bucket_id = None
    for b in buckets:
        if b.startswith("aw-watcher-web-chrome") or b.startswith("aw-watcher-web-firefox"):
            bucket_id = b
            break

    if not bucket_id:
        print("No supported browser watcher found (expected -firefox or -chrome).")
        sys.exit(1)

    fetch_browser_logs(bucket_id, start_time, end_time, output_folder, timestamp)

if __name__ == "__main__":
    main()
