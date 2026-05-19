import requests
from urllib.parse import urljoin
import re

# ==========================================
# Add Multiple Master Manifest URLs Here
# ==========================================
MASTER_MANIFEST_URLS = [
    "https://d3ptspza8nzxps.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/itv_india_daily_news/indiadailylive/index.m3u8",
    "https://d2sqrjitisvn17.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/tara_tv/taratv/index.m3u8"
]

# ==========================================
# Fetch Manifest
# ==========================================
def fetch_manifest(url):

    response = requests.get(url, timeout=15)

    response.raise_for_status()

    return response.text

# ==========================================
# Extract Attribute Helper
# ==========================================
def extract_attribute(line, attribute):

    match = re.search(
        rf'{attribute}=("[^"]+"|[^,]+)',
        line
    )

    if match:
        return match.group(1).replace('"', '')

    return "N/A"

# ==========================================
# Convert Bandwidth to Mbps
# ==========================================
def bandwidth_to_mbps(value):

    try:
        return f"{round(int(value) / 1000000, 2)} Mbps"

    except:
        return value

# ==========================================
# Parse Master Manifest
# ==========================================
def parse_master_manifest(master_content, master_url):

    streams = []

    lines = master_content.splitlines()

    for i, line in enumerate(lines):

        if line.startswith("#EXT-X-STREAM-INF"):

            stream_info = {

                "resolution": extract_attribute(
                    line,
                    "RESOLUTION"
                ),

                "bandwidth": extract_attribute(
                    line,
                    "BANDWIDTH"
                ),

                "average_bandwidth": extract_attribute(
                    line,
                    "AVERAGE-BANDWIDTH"
                ),

                "frame_rate": extract_attribute(
                    line,
                    "FRAME-RATE"
                ),

                "codecs": extract_attribute(
                    line,
                    "CODECS"
                ),

                "audio": extract_attribute(
                    line,
                    "AUDIO"
                ),

                "subtitles": extract_attribute(
                    line,
                    "SUBTITLES"
                ),

                "closed_captions": extract_attribute(
                    line,
                    "CLOSED-CAPTIONS"
                )
            }

            # Child Manifest URL
            if i + 1 < len(lines):

                child_manifest = lines[i + 1].strip()

                child_manifest_url = urljoin(
                    master_url,
                    child_manifest
                )

                stream_info["manifest_url"] = child_manifest_url

                streams.append(stream_info)

    return streams

# ==========================================
# Parse Child Manifest
# ==========================================
def parse_child_manifest(child_url):

    child_content = fetch_manifest(child_url)

    lines = child_content.splitlines()

    data = {

        "segment_duration": "N/A",
        "target_duration": "N/A",
        "media_sequence": "N/A",
        "playlist_type": "LIVE",
        "version": "N/A",
        "total_segments": 0
    }

    # Manifest Level Info
    for line in lines:

        if line.startswith("#EXT-X-TARGETDURATION"):
            data["target_duration"] = line.split(":")[1]

        elif line.startswith("#EXT-X-MEDIA-SEQUENCE"):
            data["media_sequence"] = line.split(":")[1]

        elif line.startswith("#EXT-X-PLAYLIST-TYPE"):
            data["playlist_type"] = line.split(":")[1]

        elif line.startswith("#EXT-X-VERSION"):
            data["version"] = line.split(":")[1]

        elif line.startswith("#EXTINF"):
            data["total_segments"] += 1

    # Segment Duration
    for line in lines:

        if line.startswith("#EXTINF"):

            try:

                duration_part = line.split(":")[1]

                match = re.search(
                    r'(\d+(\.\d+)?)',
                    duration_part
                )

                if match:
                    data["segment_duration"] = match.group(1)

                break

            except:
                pass

    return data

# ==========================================
# Pretty Print Header
# ==========================================
def print_header(title):

    print("\n" + "═" * 120)
    print(f"{title.center(120)}")
    print("═" * 120)

# ==========================================
# Pretty Print Key/Value
# ==========================================
def print_kv(key, value):

    print(f"{key:<28}: {value}")

# ==========================================
# Main Logic
# ==========================================
def main():

    print_header("HLS MASTER MANIFEST ANALYZER")

    for master_url in MASTER_MANIFEST_URLS:

        print("\n")
        print("▓" * 120)

        print("\nMASTER MANIFEST URL")
        print("-" * 120)

        print(master_url)

        try:

            master_content = fetch_manifest(master_url)

            streams = parse_master_manifest(
                master_content,
                master_url
            )

            if not streams:

                print("\n❌ No video layers found.\n")

                continue

            print(f"\n✅ Total Video Layers Found : {len(streams)}")

            print("\n")

            all_durations = []

            # ==========================================
            # Per Layer Analysis
            # ==========================================
            for idx, stream in enumerate(streams, start=1):

                print("┌" + "─" * 118 + "┐")

                print(
                    f"│ VIDEO LAYER {idx}".ljust(119)
                    + "│"
                )

                print("├" + "─" * 118 + "┤")

                try:

                    child_data = parse_child_manifest(
                        stream['manifest_url']
                    )

                    all_durations.append(
                        child_data['segment_duration']
                    )

                    # ==========================================
                    # Video Information
                    # ==========================================
                    print("\n🎥 VIDEO INFORMATION")
                    print("-" * 40)

                    print_kv(
                        "Resolution",
                        stream['resolution']
                    )

                    print_kv(
                        "Frame Rate",
                        f"{stream['frame_rate']} fps"
                    )

                    print_kv(
                        "CODECS",
                        stream['codecs']
                    )

                    print_kv(
                        "Bandwidth",
                        f"{stream['bandwidth']} "
                        f"({bandwidth_to_mbps(stream['bandwidth'])})"
                    )

                    print_kv(
                        "Average Bandwidth",
                        f"{stream['average_bandwidth']} "
                        f"({bandwidth_to_mbps(stream['average_bandwidth'])})"
                    )

                    # ==========================================
                    # Audio/Subtitles
                    # ==========================================
                    print("\n🔊 AUDIO / SUBTITLE INFORMATION")
                    print("-" * 40)

                    print_kv(
                        "Audio Group",
                        stream['audio']
                    )

                    print_kv(
                        "Subtitles",
                        stream['subtitles']
                    )

                    print_kv(
                        "Closed Captions",
                        stream['closed_captions']
                    )

                    # ==========================================
                    # Child Manifest
                    # ==========================================
                    print("\n📄 CHILD MANIFEST")
                    print("-" * 40)

                    print_kv(
                        "Manifest URL",
                        stream['manifest_url']
                    )

                    print_kv(
                        "Playlist Type",
                        child_data['playlist_type']
                    )

                    print_kv(
                        "HLS Version",
                        child_data['version']
                    )

                    print_kv(
                        "Target Duration",
                        f"{child_data['target_duration']} sec"
                    )

                    print_kv(
                        "Segment Duration",
                        f"{child_data['segment_duration']} sec"
                    )

                    print_kv(
                        "Media Sequence",
                        child_data['media_sequence']
                    )

                    print_kv(
                        "Total Segments",
                        child_data['total_segments']
                    )

                except Exception as e:

                    print(f"\n❌ Error parsing child manifest")
                    print(f"Error : {e}")

                print("\n└" + "─" * 118 + "┘\n")

            # ==========================================
            # Final Summary
            # ==========================================
            print("\n")
            print("█" * 120)

            print("\n📊 FINAL SUMMARY")
            print("-" * 120)

            print_kv(
                "Total Video Layers",
                len(streams)
            )

            print_kv(
                "Segment Durations",
                ", ".join(
                    [str(x) + " sec" for x in all_durations]
                )
            )

            print("█" * 120)

        except Exception as e:

            print(f"\n❌ Error fetching master manifest")
            print(f"Error : {e}")

# ==========================================
# Execute Script
# ==========================================
if __name__ == "__main__":

    main()