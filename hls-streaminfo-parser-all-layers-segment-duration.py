import requests
from urllib.parse import urljoin
import re

# ==========================================
# Add Multiple Master Manifest URLs Here
# ==========================================
MASTER_MANIFEST_URLS = [
    "https://d13lu7nbt4by7g.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/sangeet_bangla/sangeetbangla/master.m3u8",
"https://d2pc7kx157en8h.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/sangeet_bhojpuri/sangeetbhojhpuri/master.m3u8",
"https://dw5w6ea1sg8un.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/sangeet_marathi/sangeetmarathi/master.m3u8",
"https://d2fr1pr3k53e7j.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/bollywood_tv/manifest.m3u8"
]

# ==========================================
# Fetch Manifest
# ==========================================
def fetch_manifest(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text

# ==========================================
# Parse Master Manifest
# ==========================================
def parse_master_manifest(master_content, master_url):

    streams = []

    lines = master_content.splitlines()

    for i, line in enumerate(lines):

        if "#EXT-X-STREAM-INF" in line:

            # Resolution
            resolution_match = re.search(
                r'RESOLUTION=(\d+x\d+)',
                line
            )

            resolution = (
                resolution_match.group(1)
                if resolution_match
                else "Unknown"
            )

            # Bandwidth
            bandwidth_match = re.search(
                r'BANDWIDTH=(\d+)',
                line
            )

            bandwidth = (
                bandwidth_match.group(1)
                if bandwidth_match
                else "Unknown"
            )

            # Child Manifest
            if i + 1 < len(lines):

                child_manifest = lines[i + 1].strip()

                child_manifest_url = urljoin(
                    master_url,
                    child_manifest
                )

                streams.append({
                    "resolution": resolution,
                    "bandwidth": bandwidth,
                    "manifest_url": child_manifest_url
                })

    return streams

# ==========================================
# Parse Child Manifest
# ==========================================
def parse_child_manifest(child_url):

    child_content = fetch_manifest(child_url)

    lines = child_content.splitlines()

    segment_duration = "Not Found"
    first_segment = "Not Found"

    for i, line in enumerate(lines):

        if line.startswith("#EXTINF"):

            try:
                duration_part = line.split(":")[1]

                # Extract only number
                match = re.search(
                    r'(\d+(\.\d+)?)',
                    duration_part
                )

                if match:
                    segment_duration = match.group(1)

                # Get first segment
                for j in range(i + 1, len(lines)):

                    next_line = lines[j].strip()

                    if next_line and not next_line.startswith("#"):
                        first_segment = next_line
                        break

                break

            except:
                pass

    return segment_duration, first_segment

# ==========================================
# Main Logic
# ==========================================
def main():

    print("\n===== HLS VIDEO LAYER ANALYSIS =====\n")

    for master_url in MASTER_MANIFEST_URLS:

        print("=" * 100)
        print(f"\nMASTER MANIFEST : {master_url}\n")

        try:

            master_content = fetch_manifest(master_url)

            streams = parse_master_manifest(
                master_content,
                master_url
            )

            if not streams:
                print("No video layers found!\n")
                continue

            total_layers = len(streams)

            all_durations = []

            for idx, stream in enumerate(streams, start=1):

                try:

                    duration, segment = parse_child_manifest(
                        stream['manifest_url']
                    )

                    all_durations.append(duration)

                    print(f"Layer {idx}")
                    print(f"Resolution       : {stream['resolution']}")
                    print(f"Bandwidth        : {stream['bandwidth']}")
                    print(f"Child Manifest   : {stream['manifest_url']}")
                    print(f"1st Segment      : {segment}")
                    print(f"Segment Duration : {duration} sec")
                    print("-" * 100)

                except Exception as e:

                    print(f"Error parsing child manifest:")
                    print(stream['manifest_url'])
                    print(f"Error : {e}")
                    print("-" * 100)

            # ==========================================
            # Final Summary
            # ==========================================

            print("\nFINAL SUMMARY")
            print("-" * 100)

            print(f"Total Video Layers : {total_layers}")

            print("Segment Durations  : "
                  f"{', '.join([str(x) + ' sec' for x in all_durations])}")

            print("=" * 100)

        except Exception as e:

            print(f"Error fetching master manifest:")
            print(master_url)
            print(f"Error : {e}")

# ==========================================
# Execute Script
# ==========================================
if __name__ == "__main__":
    main()