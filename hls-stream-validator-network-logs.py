import requests
import time
from urllib.parse import urljoin
from datetime import datetime

# =========================================================
# CONFIGURATION
# =========================================================
POLL_INTERVAL = 5          # Seconds between monitoring cycles
SEGMENT_LIMIT = 3          # Number of latest segments to validate
REQUEST_TIMEOUT = 10       # HTTP timeout

# =========================================================
# MASTER MANIFEST URLS
# =========================================================
MASTER_URLS = [
    "https://swiftv.sofast.tv/sofastplayout/c36a36b6-d7aa-5004-64de-848ef811ce8c_0_HLS/manifest.m3u8",
    "https://streams2.sofast.tv/r/ptnr-swifttv/title-Comedy_Tadka/WiseM3U8_27/sofast/cleanhls/master.m3u8",
    "https://streams2.sofast.tv/r/ptnr-swifttv/title-DIY-ART/sofastplayout/61072256-466e-d788-1b52-db0936ae7e66_0_HLS/manifest.m3u8",
    "https://streams2.sofast.tv/r/ptnr-swifttv/title-THALAA-TV-TAM/sofastplayout/981f8f06-782a-4962-b5e0-7dcccd65279c_0_HLS/manifest.m3u8",
    "https://streams2.sofast.tv/r/ptnr-swifttv/title-TOLLY-TV-TEL/sofastplayout/2b9e9368-4803-4a2b-94c5-3c8c07e3a130_0_HLS/manifest.m3u8",
]

# =========================================================
# TIMESTAMP
# =========================================================
def current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

# =========================================================
# FETCH URL
# =========================================================
def fetch_url(url, label=""):

    try:
        start_time = time.time()

        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        latency_ms = (time.time() - start_time) * 1000

        size_kb = len(response.content) / 1024
        status = response.status_code

        ts = current_timestamp()

        headers = response.headers

        last_modified = headers.get("Last-Modified", "NA")
        cache_status = headers.get("Videograph-Cache-Status", "NA")
        cf_pop = headers.get("X-Amz-Cf-Pop", "NA")
        x_cache = headers.get("X-Cache", "NA")
        content_type = headers.get("Content-Type", "NA")

        if status == 200:

            print(f"[{ts}] {label}")
            print(f"URL              : {url}")
            print(f"HTTP Status      : {status}")
            print(f"Content-Type     : {content_type}")
            print(f"Object Size      : {size_kb:.2f} KB")
            print(f"Latency          : {latency_ms:.2f} ms")
            print(f"Last-Modified    : {last_modified}")
            print(f"Cache Status     : {cache_status}")
            print(f"CloudFront POP   : {cf_pop}")
            print(f"X-Cache          : {x_cache}")

            return response.text

        else:
            print(f"[{ts}] {label} FAILED")
            print(f"URL              : {url}")
            print(f"HTTP Status      : {status}")
            return None

    except Exception as e:

        print(f"[{current_timestamp()}] ERROR")
        print(f"URL              : {url}")
        print(f"Exception        : {str(e)}")

        return None

# =========================================================
# PARSE MASTER MANIFEST
# =========================================================
def parse_master_manifest(master_url, content):

    streams = []

    lines = content.splitlines()

    for i, line in enumerate(lines):

        if line.startswith("#EXT-X-STREAM-INF"):

            stream_info = {
                "bandwidth": "Unknown",
                "avg_bandwidth": "Unknown",
                "resolution": "Unknown",
                "frame_rate": "Unknown",
                "codecs": "Unknown",
                "audio": "Unknown",
                "manifest_url": "Unknown"
            }

            attributes = line.replace("#EXT-X-STREAM-INF:", "")

            parts = attributes.split(",")

            for part in parts:

                if "=" in part:

                    key, value = part.split("=", 1)

                    key = key.strip()
                    value = value.strip().replace('"', "")

                    if key == "BANDWIDTH":
                        stream_info["bandwidth"] = value

                    elif key == "AVERAGE-BANDWIDTH":
                        stream_info["avg_bandwidth"] = value

                    elif key == "RESOLUTION":
                        stream_info["resolution"] = value

                    elif key == "FRAME-RATE":
                        stream_info["frame_rate"] = value

                    elif key == "CODECS":
                        stream_info["codecs"] = value

                    elif key == "AUDIO":
                        stream_info["audio"] = value

            if i + 1 < len(lines):

                child_manifest = lines[i + 1].strip()

                child_url = urljoin(master_url, child_manifest)

                stream_info["manifest_url"] = child_url

            streams.append(stream_info)

    return streams

# =========================================================
# GET LATEST SEGMENTS
# =========================================================
def get_last_segments(base_url, content, limit=SEGMENT_LIMIT):

    segments = []

    for line in content.splitlines():

        line = line.strip()

        if line and not line.startswith("#"):

            if (
                ".ts" in line
                or ".m4s" in line
                or ".mp4" in line
            ):
                segments.append(
                    urljoin(base_url, line)
                )

    return segments[-limit:]

# =========================================================
# MONITOR HLS
# =========================================================
def monitor_hls():

    while True:

        print("\n")
        print("=" * 120)
        print("🎥 HLS STREAM MONITORING")
        print("=" * 120)

        for channel_number, master_url in enumerate(MASTER_URLS, start=1):

            print("\n")
            print("#" * 120)
            print(f"📡 CHANNEL {channel_number}")
            print("#" * 120)

            # =====================================================
            # MASTER MANIFEST
            # =====================================================

            print("\n📄 MASTER MANIFEST")
            print("-" * 120)

            master_content = fetch_url(
                master_url,
                label="[MASTER MANIFEST]"
            )

            if not master_content:
                continue

            # =====================================================
            # VIDEO LAYERS
            # =====================================================

            streams = parse_master_manifest(
                master_url,
                master_content
            )

            print("\n🎬 VIDEO LAYERS")
            print("-" * 120)

            if not streams:
                print("No video layers found!")
                continue

            for idx, stream in enumerate(streams, start=1):

                print(f"\nLayer #{idx}")
                print("-" * 80)

                print(f"Resolution        : {stream['resolution']}")
                print(f"Frame Rate        : {stream['frame_rate']}")
                print(f"Bandwidth         : {stream['bandwidth']}")
                print(f"Avg Bandwidth     : {stream['avg_bandwidth']}")
                print(f"Codecs            : {stream['codecs']}")
                print(f"Audio Group       : {stream['audio']}")
                print(f"Child Manifest    : {stream['manifest_url']}")

                # =================================================
                # CHILD MANIFEST
                # =================================================

                print("\n📄 CHILD MANIFEST")
                print("-" * 80)

                child_content = fetch_url(
                    stream['manifest_url'],
                    label=f"[CHILD-{idx}]"
                )

                if not child_content:
                    continue

                # =================================================
                # SEGMENTS
                # =================================================

                print("\n🧩 LATEST SEGMENTS")
                print("-" * 80)

                segments = get_last_segments(
                    stream['manifest_url'],
                    child_content
                )

                for seg_index, segment_url in enumerate(segments, start=1):

                    fetch_url(
                        segment_url,
                        label=f"[SEGMENT {idx}.{seg_index}]"
                    )

                    print("-" * 80)

                    time.sleep(0.2)

        print("\n")
        print("=" * 120)
        print(f"Sleeping for {POLL_INTERVAL} seconds...")
        print("=" * 120)

        time.sleep(POLL_INTERVAL)

# =========================================================
# MAIN
# =========================================================
if __name__ == "__main__":
    monitor_hls()