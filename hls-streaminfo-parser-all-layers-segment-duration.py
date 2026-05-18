import requests
from urllib.parse import urljoin
import re

# ==========================================
# Add Multiple Master Manifest URLs Here
# ==========================================
MASTER_MANIFEST_URLS = [
    "https://d3ptspza8nzxps.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/itv_india_daily_news/indiadailylive/index.m3u8",
"https://d2sqrjitisvn17.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/tara_tv/taratv/index.m3u8",
"https://d88z77jazwrot.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/anand_tv/anandtv/index.m3u8",
"https://d2qjmm8pp6modv.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/haryana_beats/haryanabeat/index.m3u8",
"https://d28aw9z1v9dl52.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/news_malayalam_swiftv/newsmalayalamlive/index.m3u8",
"https://dhschn7phghlj.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/punjabi_hits/punjabihits/index.m3u8",
"https://d2c64wlzqq0ngq.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/rongeen_tv/rongeentv/index.m3u8",
"https://d27p16vtqgequl.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/rplus/hls5/index.m3u8",
"https://dd1587ggje2rn.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/lakshya_tv/distrolakshya/index.m3u8",
"https://dat3ebe9q09hb.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/kalyan_tv/distrotvkalyantv/index.m3u8",
"https://d3foatmq523jy6.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/kartvya_tv/distrotvkartavyatv/index.m3u8",
"https://d1rjy43nstmb82.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/living_india/livingindia/index.m3u8",
"https://d34ty5mrc8bxua.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/tabbar_hits/tabbarhits/index.m3u8",
"https://d3i4nfibrjst21.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/news_tamil_swifttv/newstamil/index.m3u8",
"https://d22euq38lyxy6x.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/pratidin_times/pratidin/index.m3u8",
"https://d1vlbhvyvl59gv.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/munsif_tv/munsiftv/index.m3u8",
"https://ddfiowhw29pcs.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/global_punjab/distroglobalpunjab/index.m3u8",
"https://ds37poyi3xm8n.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/mahuaa_play/mahuaplayjio/index.m3u8",
"https://d1yak0wyh733r.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/mahuaa_khabar/mahuakhabarjio/index.m3u8",
"https://d1lxslxfgt5l3u.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/mahaa_news/mahaanews/index.m3u8",
"https://d23babkhkiy0fk.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/mahaa_maxx/mahaamaxx/index.m3u8",
"https://dk6cuki64nihv.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/sandesh_news/sandeshnews/index.m3u8",
"https://d13f1k5bcoch3z.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/abn_andhrajyoti/abnandhrajyothycdn/index.m3u8",
"https://d1rzdclb147bs.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/kolkata_tv/kolkatatv/index.m3u8",
"https://d3esntc4thfeda.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/sakshi_tv/sakshitv/index.m3u8",
"https://d2uk2hcw7n1tv9.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/big_tv/bigtv/index.m3u8",
"https://d19jglf6lo77w6.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/gujarat_first/gujaratfirst/index.m3u8"
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