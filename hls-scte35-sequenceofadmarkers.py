import requests
import time
import re
from urllib.parse import urljoin

MASTER_URL = "https://d21gekbpgch6jl.cloudfront.net/v1/master/071c0467fcd02420cdf0d8a1ca3524b96c27a151/music_india/musicindia/master.m3u8"

MASTER_REFRESH = 300
child_manifests = []
target_duration = 6

latest_program_time = None


def fetch(url):
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.text.splitlines()
    except:
        return []


def parse_master():
    global child_manifests

    lines = fetch(MASTER_URL)
    new_children = []

    for line in lines:
        if line and not line.startswith("#"):
            full = urljoin(MASTER_URL, line.strip())
            new_children.append(full)

    if set(new_children) != set(child_manifests):
        child_manifests = new_children
        print(f"\n[MASTER] Updated {len(child_manifests)} child manifests\n")


def get_target_duration(lines):
    for line in lines:
        if "targetduration" in line.lower():
            return int(re.search(r'\d+', line).group())
    return 6


def check_manifest(url):
    global target_duration, latest_program_time

    lines = fetch(url)
    if not lines:
        return

    target_duration = get_target_duration(lines)

    cue_out = False
    cue_in = False
    duration = None
    ad_segments = False

    for line in lines:
        lower = line.lower()

        # -------- PROGRAM DATE TIME --------
        if "program-date-time" in lower:
            latest_program_time = line.split(":", 1)[1].strip()

        # -------- CUE-OUT --------
        if "cue-out" in lower:
            cue_out = True
            match = re.search(r'(\d+(\.\d+)?)', line)
            duration = match.group(1) if match else "NA"

        # -------- CUE-IN --------
        if "cue-in" in lower:
            cue_in = True

        # -------- AD SEGMENT DETECTION --------
        if "../../../../" in line:
            ad_segments = True

    # -------- OUTPUT --------
    print(f"\n[MANIFEST] {url}")
    print(f"Program-Date-Time: {latest_program_time if latest_program_time else 'NOT FOUND'}")

    if cue_out:
        print(f"CUE-OUT: YES | Duration: {duration}")
    else:
        print("CUE-OUT: NO")

    if cue_in:
        print("CUE-IN: YES")
    else:
        print("CUE-IN: NO")

    # -------- FINAL STATUS --------
    if cue_out:
        print("Status: AD START 🎬")
    elif ad_segments:
        print("Status: AD (IN PROGRESS) 🔄")
    elif cue_in:
        print("Status: AD END ✅")
    else:
        print("Status: NO AD ℹ️")


def main():
    last_master = 0

    while True:
        now = time.time()

        if now - last_master > MASTER_REFRESH:
            parse_master()
            last_master = now

        for child in child_manifests:
            check_manifest(child)

        time.sleep(target_duration)


if __name__ == "__main__":
    main()