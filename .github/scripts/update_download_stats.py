import os
import json
import time
import re
import requests
import sys
from datetime import datetime

PROJECT_NAME = "project-ascp"
STATS_FILE = "API/download_stats.json"
DEVICES_JSON = "API/devices.json"
BASE_URL = f"https://sourceforge.net/projects/{PROJECT_NAME}/files/"
RSS_URL = f"https://sourceforge.net/projects/{PROJECT_NAME}/rss?path=/"
STATS_URL_TEMPLATE = "https://sourceforge.net/projects/{project}/files/{path}/stats/json"

# A more realistic User-Agent to avoid 403 blocks
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def fetch_content(url, params=None, retries=5, backoff=5):
    for i in range(retries):
        try:
            response = requests.get(url, params=params, headers=HEADERS, timeout=30)
            if response.status_code == 403:
                print(f"DEBUG: 403 Forbidden for {url} (Attempt {i+1}/{retries})")
            response.raise_for_status()
            return response
        except Exception as e:
            if i == retries - 1:
                print(f"Error fetching {url}: {e}")
                return None
            time.sleep(backoff * (i + 1))
    return None

def get_devices_from_json():
    print(f"Loading fallback devices from {DEVICES_JSON}...")
    try:
        if os.path.exists(DEVICES_JSON):
            with open(DEVICES_JSON, "r") as f:
                data = json.load(f)
                return [d["codename"] for d in data.get("devices", [])]
    except Exception as e:
        print(f"Warning: Could not read {DEVICES_JSON}: {e}")
    return []

def main():
    params = {
        "start_date": "2010-01-01",
        "end_date": datetime.now().strftime("%Y-%m-%d")
    }

    print(f"Discovering devices from {BASE_URL}...")
    page = fetch_content(BASE_URL)
    discovered_devices = []

    if page:
        # Method 1: HTML Scraping
        discovered_devices = re.findall(r'href="/projects/' + re.escape(PROJECT_NAME) + r'/files/([^/"]+)/"', page.text)
        discovered_devices = [f for f in discovered_devices if f not in ("stats", "index_ajax")]
        print(f"Method 1 (HTML) found {len(set(discovered_devices))} devices.")
    else:
        print("Method 1 (HTML) failed. Trying Method 2 (RSS)...")
        rss = fetch_content(RSS_URL)
        if rss:
            # Method 2: RSS Feed
            discovered_devices = re.findall(r'<title>/([^/]+)/', rss.text)
            print(f"Method 2 (RSS) found {len(set(discovered_devices))} devices.")
        else:
            print("Method 2 (RSS) failed.")

    # Combine with local JSON to ensure we don't miss anything known
    json_devices = get_devices_from_json()
    all_devices = sorted(list(set(discovered_devices + json_devices)))
    
    if not all_devices:
        print("CRITICAL: No devices found through any method.")
        sys.exit(1)

    print(f"Total devices to process: {len(all_devices)}")
    
    stats_data = {}
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r") as f:
            try:
                stats_data = json.load(f)
            except json.JSONDecodeError:
                stats_data = {}

    updated_count = 0
    for device in all_devices:
        print(f"Fetching stats for {device}...", end=" ", flush=True)
        url = STATS_URL_TEMPLATE.format(project=PROJECT_NAME, path=device)
        response = fetch_content(url, params=params)
        
        if response:
            try:
                data = response.json()
                if "total" in data:
                    stats_data[device] = data["total"]
                    print(f"Done ({data['total']})")
                    updated_count += 1
                else:
                    print("No 'total' key.")
            except ValueError:
                print("Invalid JSON.")
        else:
            print("Failed.")
            if device not in stats_data:
                stats_data[device] = 0
            
    # Final sort and save
    final_stats = dict(sorted(stats_data.items()))

    # Ensure target directory exists
    os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)

    with open(STATS_FILE, "w") as f:
        json.dump(final_stats, f, indent=2)
        f.write("\n")
    
    print(f"Successfully updated {STATS_FILE} ({updated_count}/{len(all_devices)} devices updated)")

if __name__ == "__main__":
    main()
