import os
import time
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
import json

def get_elasticsearch_client(host="localhost", port=9200, username="elastic", password="Faizalove13"):
    es = Elasticsearch(
        [{'host': host, 'port': port, 'scheme': 'http'}],
        basic_auth=(username, password)
    )
    if not es.ping():
        raise ConnectionError("Failed to connect to Elasticsearch")
    return es

def query_and_save_logs(es, index_pattern, start_time, end_time, output_file):
    """Fetch all logs in the given time range and write directly to file."""
    query = {
        "query": {
            "bool": {
                "filter": [
                    {
                        "range": {
                            "@timestamp": {
                                "gte": start_time.isoformat(),
                                "lte": end_time.isoformat()
                            }
                        }
                    }
                ]
            }
        }
    }

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    try:
        with open(output_file, 'w') as f:
            # Initial search with scroll
            page = es.search(
                index=index_pattern,
                body=query,
                scroll="2m",    # Keep search context alive for 2 minutes
                size=5000       # Fetch 5k logs at a time
            )

            sid = page["_scroll_id"]
            hits = page["hits"]["hits"]

            total_logs = 0

            while hits:
                for hit in hits:
                    json.dump(hit["_source"], f)
                    f.write("\n")
                    total_logs += 1

                # Get next batch
                page = es.scroll(scroll_id=sid, scroll="2m")
                sid = page["_scroll_id"]
                hits = page["hits"]["hits"]

            # Clear scroll context
            es.clear_scroll(scroll_id=sid)

        print(f"Saved {total_logs} logs to: {output_file}")

    except Exception as e:
        print(f"Error fetching logs: {e}")

def main():
    # Config
    es_host = "localhost"
    es_port = 9200
    index_pattern = "winlogbeat-*"
    output_dir = "system_logs"
    interval_minutes = 20

    es = get_elasticsearch_client(es_host, es_port, username="elastic", password="Faizalove13")

    while True:
        # Calculate 20-minute interval
        current_time = datetime.utcnow()
        interval_start = current_time - timedelta(seconds=current_time.second, microseconds=current_time.microsecond)
        interval_start -= timedelta(minutes=interval_start.minute % interval_minutes)
        interval_end = interval_start + timedelta(minutes=interval_minutes)

        timestamp = interval_start.strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"syslogs_{timestamp}.json")

        query_and_save_logs(es, index_pattern, interval_start, interval_end, output_file)

        # Sleep until next interval
        sleep_seconds = (interval_end - datetime.utcnow()).total_seconds()
        if sleep_seconds > 0:
            time.sleep(sleep_seconds)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Log extraction stopped by user")
