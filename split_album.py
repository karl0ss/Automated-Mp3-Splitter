import requests
from datetime import timedelta
import subprocess
import sys
import os
import re

RELEASE_ID = sys.argv[1]
MP3_FILE = sys.argv[2]

def ms_to_mmssff(ms):
    seconds = ms / 1000
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    frames = int((ms % 1000) / 1000 * 75)
    return f"{minutes:02}:{seconds:02}:{frames:02}"

def sanitize_dirname(name):
    return re.sub(r'[<>:"/\\|?*]', '', name).strip()

def get_release_data(release_id):
    url = f"https://musicbrainz.org/ws/2/release/{release_id}?inc=recordings&fmt=json"
    r = requests.get(url, headers={"User-Agent": "KarlSplitter/1.0"})
    r.raise_for_status()
    return r.json()

def select_medium(media):
    if len(media) == 1:
        return media[0]

    print(f"\nThis release has {len(media)} discs:")
    for i, m in enumerate(media, 1):
        fmt = m.get('format', 'Unknown')
        track_count = len(m.get('tracks', []))
        print(f"  CD {i} ({fmt}, {track_count} tracks)")

    while True:
        choice = input(f"Which CD is this? (1-{len(media)}): ")
        if choice.isdigit() and 1 <= int(choice) <= len(media):
            return media[int(choice) - 1]
        print("Invalid choice, try again.")

def build_cue(medium, mp3_file, cd_num=None):
    tracks = []
    for track in medium['tracks']:
        title = track['recording']['title']
        length = track.get('length', 0)
        tracks.append((title, length))

    cue_lines = []
    cue_lines.append(f'FILE "{mp3_file}" MP3')

    if cd_num is not None:
        cue_lines.append(f'REM CD {cd_num}')

    current_time = 0

    for i, (title, length) in enumerate(tracks, start=1):
        timestamp = ms_to_mmssff(current_time)

        cue_lines.append(f'  TRACK {i:02} AUDIO')
        cue_lines.append(f'    TITLE "{title}"')
        cue_lines.append(f'    INDEX 01 {timestamp}')

        current_time += length

    return "\n".join(cue_lines)

def write_cue(cue_text, filename="album.cue"):
    with open(filename, "w") as f:
        f.write(cue_text)
    return filename

def split_mp3(cue_file, mp3_file, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    subprocess.run(["mp3splt", "-c", cue_file, "-d", output_dir, mp3_file])

if __name__ == "__main__":
    print("Fetching release data...")
    data = get_release_data(RELEASE_ID)

    album_title = data.get('title', 'Unknown Album')
    media = data.get('media', [])
    multi_cd = len(media) > 1

    medium = select_medium(media)
    cd_num = medium.get('position') if multi_cd else None

    print("Generating CUE...")
    cue = build_cue(medium, MP3_FILE, cd_num)
    cue_file = write_cue(cue)

    print(f"CUE file written: {cue_file}")

    if multi_cd:
        output_dir = sanitize_dirname(f"{album_title} - CD {cd_num}")
    else:
        output_dir = sanitize_dirname(album_title)

    print(f"Output folder: {output_dir}")

    choice = input("Split MP3 now? (y/n): ")
    if choice.lower() == "y":
        split_mp3(cue_file, MP3_FILE, output_dir)