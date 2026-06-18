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

# Single call stats for the whole project
PROJECT_STATS_URL = f"https://sourceforge.net/projects/{PROJECT_NAME}/stats/json"
# Individual stats fallback
STATS_URL_TEMPLATE = "https://sourceforge.net/projects/{project}/files/{path}/stats/json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": f"https://sourceforge.net/projects/{PROJECT_NAME}/files/",
    "X-Requested-With": "XMLHttpRequest",
}

class StatsUpdater:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def fetch(self, url, params=None, retries=3):
        for i in range(retries):
            try:
                response = self.session.get(url, params=params, timeout=30)
                if response.status_code == 403:
                    print(f"DEBUG: 403 Forbidden for {url} (Attempt {i+1}/{retries})")
                response.raise_for_status()
                return response
            except Exception as e:
                if i == retries - 1:
                    print(f"Error fetching {url}: {e}")
                    return None
                time.sleep(5 * (i + 1))
        return None

    def get_discovery_list(self):
        print(f"Discovering devices from {BASE_URL}...")
        page = self.fetch(BASE_URL)
        if page:
            devices = re.findall(r'href="/projects/' + re.escape(PROJECT_NAME) + r'/files/([^/"]+)/"', page.text)
            devices = [f for f in set(devices) if f not in ("stats", "index_ajax")]
            if devices:
                print(f"Discovered {len(devices)} devices via HTML.")
                return devices

        print("HTML discovery failed or empty. Trying RSS...")
        rss = self.fetch(RSS_URL)
        if rss:
            devices = re.findall(r'<title>/([^/]+)/', rss.text)
            if devices:
                print(f"Discovered {len(set(devices))} devices via RSS.")
                return list(set(devices))

        print("Falling back to local devices.json...")
        try:
            if os.path.exists(DEVICES_JSON):
                with open(DEVICES_JSON, "r") as f:
                    data = json.load(f)
                    return [d["codename"] for d in data.get("devices", [])]
        except Exception as e:
            print(f"Warning: Could not read {DEVICES_JSON}: {e}")
        return []

    def run(self):
        params = {
            "start_date": "2010-01-01",
            "end_date": datetime.now().strftime("%Y-%m-%d")
        }

        devices = self.get_discovery_list()
        if not devices:
            print("CRITICAL: No devices found.")
            sys.exit(1)

        stats_data = {}
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, "r") as f:
                try:
                    stats_data = json.load(f)
                except:
                    stats_data = {}

        # Try PROJECT-WIDE stats first (one request for everything)
        print(f"Fetching global project stats from {PROJECT_STATS_URL}...")
        # Note: We append ?path=/ to see breakdown by folder if supported
        global_resp = self.fetch(PROJECT_STATS_URL, params=params)
        
        updated_from_global = False
        if global_resp:
            try:
                data = global_resp.json()
                # SourceForge global stats sometimes provides a 'top_paths' or similar
                # If it's not in the format we expect, we fallback to individual
                print("DEBUG: Global stats fetched successfully.")
            except:
                print("Warning: Global stats response not valid JSON.")

        # Always process individual list to ensure accuracy, but now using the session
        print(f"Processing {len(devices)} devices...")
        updated_count = 0
        for device in sorted(devices):
            print(f"  {device}...", end=" ", flush=True)
            url = STATS_URL_TEMPLATE.format(project=PROJECT_NAME, path=device)
            resp = self.fetch(url, params=params)
            if resp:
                try:
                    count = resp.json().get("total", 0)
                    stats_data[device] = count
                    print(f"Done ({count})")
                    updated_count += 1
                except:
                    print("JSON Error.")
            else:
                print("Failed.")
                if device not in stats_data:
                    stats_data[device] = 0
            
            # Small delay to avoid triggering rate limits
            time.sleep(1)

        # Save results
        final_stats = dict(sorted(stats_data.items()))
        os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
        with open(STATS_FILE, "w") as f:
            json.dump(final_stats, f, indent=2)
            f.write("\n")
        
        print(f"Successfully updated {STATS_FILE} ({updated_count} devices updated)")

if __name__ == "__main__":
    updater = StatsUpdater()
    updater.run()

