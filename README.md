# Mp3Splitter

Splits a single MP3 file into individual tracks using track data from MusicBrainz. Generates a CUE sheet from the release's track listing, then uses `mp3splt` to split the file.

## Requirements

- Python 3
- `requests` (`pip install requests`)
- `mp3splt` (install via your package manager, e.g. `sudo apt install mp3splt`)

## Usage

```bash
python split_album.py <musicbrainz_release_id> <mp3_file>
```

### Finding the MusicBrainz Release ID

1. Go to [musicbrainz.org](https://musicbrainz.org) and search for the album.
2. Open the release page. The release ID is the UUID in the URL, e.g.:
   ```
   https://musicbrainz.org/release/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
                                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                               This is the release ID
   ```

### Single CD Album

```bash
python split_album.py a1b2c3d4-e5f6-7890-abcd-ef1234567890 album.mp3
```

The script fetches track data, generates `album.cue`, and prompts to split. Output files go into a folder named after the album.

### Multi-CD Album

```bash
python split_album.py a1b2c3d4-e5f6-7890-abcd-ef1234567890 cd1.mp3
```

When the release has multiple discs, the script lists them and asks which CD this MP3 corresponds to:

```
This release has 2 discs:
  CD 1 (CD, 22 tracks)
  CD 2 (CD, 13 tracks)
Which CD is this? (1-2): 1
```

Output files go into a folder named `<Album Title> - CD <n>`.

## How It Works

1. Fetches release data from the MusicBrainz API (track titles and durations).
2. Generates a CUE sheet with timestamps calculated from cumulative track lengths.
3. If single CD, uses all tracks directly. If multi-CD, prompts for disc selection.
4. Runs `mp3splt -c album.cue -d <output_dir> <mp3_file>` to split into individual tracks.

## Output

Split tracks are placed in a folder named after the album (or `Album - CD n` for multi-disc releases). The CUE sheet is written as `album.cue` in the current directory.