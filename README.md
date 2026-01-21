### Video Segment dHash/vhash Processor 
## Introduction
This Python script scans a directory of videos and generates per-segment perceptual hashes (dHashes) for each video. These hashes allow you to efficiently compare videos, detect duplicates, or analyze video similarity. The script handles large videos by splitting them into segments and hashing representative frames, while also ensuring that small videos with very few frames are still processed and assigned at least one hash. This is done per 1000 frames, ideal for video indexing and finding if smaller clips are from bigger videos. Also,  smaller files with less frames are indexed with 1 frame at least. 
- It stores the results in a SQLite database (vhash_files.db), making it easy to query and integrate with other systems.

# Features
- Processes common video formats: .mp4, .avi, .mkv, .flv, .mpg, .webm, .mov, .wmv, .qt, .m4v, .ts, .mpeg, .divx.
  - swf or ogv files can create problems. 
- Generates perceptual hashes per segment for similarity detection.
- Handles small videos (<1000 frames) gracefully with at least 1 hash.
- Stores hashes in a SQLite database for easy querying.
- Supports parallel processing using multithreading for faster execution.
- Skips videos already processed to avoid redundant work.
- Can continue if stopt from where it remained
- Configurable segment size, maximum number of segments, and resize dimensions for hash computation.

# Dependencies
The script uses the following Python libraries:
- opencv-python: for video reading and frame processing.
- Pillow: for image handling.
- ImageHash: for perceptual hashing (dHash).
- Standard Python libraries: os, sqlite3, concurrent.futures.

# Install dependencies:
`pip install opencv-python Pillow ImageHash`

# Usage
- Clone or download this repository.
- Place your videos in a folder (default: ./).
- Configure options at the top of the script:

VIDEO_ROOT = "./"           # Folder to scan for videos
FRAMES_PER_SEGMENT = 1000   # Frames per segment
MAX_SEGMENTS = 400          # Max segments per video
RESIZE_DIM = (64, 64)       # Resize frames for hashing
MAX_WORKERS = 8             # Parallel threads
DB_PATH = "vhash_files.db"  # SQLite database file

Run the script:
- `python video_vhash.py`

# The script will create/update vhash_files.db with columns:
- video_path – full path to the video
- segment_count – number of segments actually hashed
- zero_count – number of failed frames
- hash1, hash2, ..., hash400 – per-segment hashes (padded with "0" if fewer segments)

# How It Works
- Video scanning: Walks through the specified directory recursively and finds video files with allowed extensions.
- Per-segment hashing: Each video is divided into segments of FRAMES_PER_SEGMENT.
- The middle frame of each segment is extracted.
- Frame is resized and converted to grayscale.
- dHash is computed using ImageHash.
- Each video’s hashes, segment count, and failure info are row-wise stored in a SQLite table.
- Existing entries are skipped to avoid re-processing.
- Parallel processing: Multiple videos are processed concurrently using threads (MAX_WORKERS).
- Small videos: If a video is smaller than one segment, at least one frame is hashed.
- Ensures even short videos are indexed.

Example Query
- Find videos with at least one zero-hash segment
SELECT video_path, zero_count FROM videos WHERE zero_count > 0;

- Compare hashes between two videos
SELECT hash1, hash2, hash3 FROM videos WHERE video_path = 'video1.mp4';


