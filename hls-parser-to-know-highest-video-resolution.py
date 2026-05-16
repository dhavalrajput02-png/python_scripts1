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

            # Extract Resolution
            resolution_match = re.search(
                r'RESOLUTION=(\d+x\d+)',
                line
            )

            resolution = (
                resolution_match.group(1)
                if resolution_match
                else "Unknown"
            )

            # Child manifest usually next line
            if i + 1 < len(lines):

                child_manifest = lines[i + 1].strip()

                child_manifest_url = urljoin(
                    master_url,
                    child_manifest
                )

                streams.append({
                    "resolution": resolution,
                    "manifest_url": child_manifest_url
                })

    return streams

# ==========================================
# Parse Child Manifest
# ==========================================
def parse_child_manifest(child_url):

    child_content = fetch_manifest(child_url)

    extinf_values = []

    lines = child_content.splitlines()

    for line in lines:

        if line.startswith("#EXTINF"):

            try:
                duration_part = line.split(":")[1]

                # Extract only numeric value
                match = re.search(
                    r'(\d+(\.\d+)?)',
                    duration_part
                )

                if match:
                    duration = float(match.group(1))
                    extinf_values.append(duration)

            except:
                pass

    return extinf_values

# ==========================================
# Resolution Sorting Logic
# ==========================================
def get_resolution_value(resolution):

    try:
        width, height = resolution.split("x")
        return int(width) * int(height)

    except:
        return 0

# ==========================================
# Main Logic
# ==========================================
def main():

    print("\n===== HLS STREAM ANALYSIS =====\n")

    for master_url in MASTER_MANIFEST_URLS:

        try:

            # Fetch Master Manifest
            master_content = fetch_manifest(master_url)

            # Parse Streams
            streams = parse_master_manifest(
                master_content,
                master_url
            )

            if not streams:

                print(f"URL : {master_url}")
                print("No streams found!\n")

                continue

            # Select Highest Resolution
            highest_stream = max(
                streams,
                key=lambda x: get_resolution_value(
                    x['resolution']
                )
            )

            # Parse Child Manifest
            extinf_values = parse_child_manifest(
                highest_stream['manifest_url']
            )

            if extinf_values:

                avg_duration = (
                    sum(extinf_values) /
                    len(extinf_values)
                )

                print(f"URL : {master_url}")

                print(
                    f"Selected Resolution : "
                    f"{highest_stream['resolution']} "
                    f"& Average Segment Duration : "
                    f"{avg_duration:.2f} sec\n"
                )

            else:

                print(f"URL : {master_url}")
                print("No EXTINF values found!\n")

        except Exception as e:

            print(f"URL : {master_url}")
            print(f"Error : {e}\n")

# ==========================================
# Execute Script
# ==========================================
if __name__ == "__main__":
    main()