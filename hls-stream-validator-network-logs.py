import requests
import time
from urllib.parse import urljoin
from datetime import datetime

POLL_INTERVAL = 2
SEGMENT_LIMIT = 5


def current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def fetch_url(url, label=""):
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        latency_ms = (time.time() - start_time) * 1000

        size_kb = len(response.content) / 1024
        status = response.status_code
        ts = current_timestamp()

        prefix = f"{label} " if label else ""

        # -------- HEADER EXTRACTION (CASE-INSENSITIVE) --------
        headers = response.headers

        last_modified = headers.get("last-modified", "NA")
        videograph_cache = headers.get("videograph-cache-status", "NA")
        cf_pop = headers.get("x-amz-cf-pop", "NA")
        x_cache = headers.get("x-cache", "NA")

        if status == 200:
            print(f"[{ts}] {prefix}[OK] {url}")
            print(f"           Status: {status} | Size: {size_kb:.2f} KB | Latency: {latency_ms:.2f} ms")

            # -------- PRINT HEADERS --------
            print(f"           Last-Modified: {last_modified}")
            print(f"           Videograph-Cache-Status: {videograph_cache}")
            print(f"           X-Amz-Cf-Pop: {cf_pop}")
            print(f"           X-Cache: {x_cache}")

        else:
            print(f"[{ts}] {prefix}[FAIL] {url} | Status: {status} | Latency: {latency_ms:.2f} ms")

        return response.text if status == 200 else None

    except Exception as e:
        ts = current_timestamp()
        print(f"[{ts}] {prefix}[ERROR] {url} | Exception: {str(e)}")
        return None


def parse_manifest(base_url, content):
    urls = []
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            urls.append(urljoin(base_url, line))
    return urls


def get_last_segments(base_url, content, limit=SEGMENT_LIMIT):
    segments = []
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            segments.append(urljoin(base_url, line))
    return segments[-limit:]


def monitor_hls(master_url):
    while True:
        print("\n================ HLS MONITORING =================")

        # Master Manifest
        print("\n--- Master Manifest ---")
        master_content = fetch_url(master_url, label="[MASTER]")

        if not master_content:
            time.sleep(POLL_INTERVAL)
            continue

        # Child Manifests
        print("\n--- Child Manifests ---")
        child_manifests = parse_manifest(master_url, master_content)

        for idx, child_url in enumerate(child_manifests, start=1):
            print(f"\n>>> Rendition [{idx}]")

            child_content = fetch_url(child_url, label=f"[CHILD-{idx}]")

            if not child_content:
                continue

            # Segments
            print(f"----- Segments (Sequential) [Rendition {idx}] -----")
            segments = get_last_segments(child_url, child_content)

            for seg_idx, segment_url in enumerate(segments, start=1):
                fetch_url(segment_url, label=f"[SEG-{idx}.{seg_idx}]")
                time.sleep(0.2)

        print(f"\nSleeping for {POLL_INTERVAL} seconds...\n")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    master_url = "https://d21gekbpgch6jl.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/music_india/musicindia/master.m3u8"
    monitor_hls(master_url)