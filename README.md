### Video Segment dHash/vhash Processor 
## Introduction of main script "vhash_db.py"
This Python script scans a directory of videos and generates per-segment perceptual hashes (dHashes) for each video. These hashes allow you to efficiently compare videos, detect duplicates, or analyze video similarity. The script handles large videos by splitting them into segments and hashing representative frames, while also ensuring that small videos with very few frames are still processed and assigned at least one hash. This is done per 1000 frames, ideal for video indexing and finding if smaller clips are from bigger videos. Also,  smaller files with less frames are indexed with 1 frame at least. 
- It stores the results in a SQLite database (vhash_files.db), making it easy to query and integrate with other systems.

### Features
- Processes common video formats: .mp4, .avi, .mkv, .flv, .mpg, .webm, .mov, .wmv, .qt, .m4v, .ts, .mpeg, .divx.
  - swf or ogv files can create problems. 
- Generates perceptual hashes per segment for similarity detection.
- Handles small videos (<1000 frames) gracefully with at least 1 hash.
- Stores hashes in a SQLite database for easy querying.
- Supports parallel processing using multithreading for faster execution.
- Skips videos already processed to avoid redundant work.
- Can continue if stopt from where it remained
- Configurable segment size, maximum number of segments, and resize dimensions for hash computation.

### Dependencies
The script uses the following Python libraries:
- opencv-python: for video reading and frame processing.
- Pillow: for image handling.
- ImageHash: for perceptual hashing (dHash).
- Standard Python libraries: os, sqlite3, concurrent.futures.

### Install dependencies
`pip install opencv-python Pillow ImageHash`

### Usage
- Clone or download this repository.
- Place your videos in a folder (default: ./).
- Configure options at the top of the script:

```
VIDEO_ROOT = "./"           # Folder to scan for videos
FRAMES_PER_SEGMENT = 1000   # Frames per segment
MAX_SEGMENTS = 400          # Max segments per video
RESIZE_DIM = (64, 64)       # Resize frames for hashing
MAX_WORKERS = 8             # Parallel threads
DB_PATH = "vhash_files.db"  # SQLite database file
```
Run the script:
`python video_vhash.py`

### The script will create/update vhash_files.db with columns:
- video_path – full path to the video
- segment_count – number of segments actually hashed
- zero_count – number of failed frames
- hash1, hash2, ..., hash400 – per-segment hashes (padded with "0" if fewer segments)

### How It Works
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

### Example Query
- Find videos with at least one zero-hash segment
SELECT video_path, zero_count FROM videos WHERE zero_count > 0;

- Compare hashes between two videos
SELECT hash1, hash2, hash3 FROM videos WHERE video_path = 'video1.mp4';

---
---
---


### Useful tools
### 1) clean_nonexistpaths_from_db.py – Remove DB entries for missing video files
- Scans a SQLite database table containing video paths.
- Checks if each file still exists on disk.
- Deletes any rows where the file is missing.
- Prints a log of deleted entries and the total removed count.

---
---

### 2) del_find_dublicates_files_from_2db.py – Find and optionally delete duplicate videos across two databases
- Compares videos between a main DB and an original DB using their dHash values (dhash_1 … dhash_20).
- Detects duplicate videos (same hash across databases).
- Logs duplicate pairs (original -> duplicate) to a CSV file (videos_marked_for_deletion.csv).
- Optionally deletes duplicate files from disk (DELETE_FILES = True).
- Optionally removes duplicate rows from the main DB (DELETE_DB_ROWS = True).
- Saves paths of deleted files to a text file (paths_tobe_deleted.txt) for record-keeping.

---
---

### 3) compare_dhash_image_in2db.py – Compare image hashes between two databases
- Loads image paths and their dHashes from two SQLite databases.
- Compares the dHashes to find:
  - Common images (same hash in both databases).
  - Unique images (present in only one database).
- Exports results to CSV files:
```
commonsA.csv – common files from DB-A
commonsB.csv – common files from DB-B
uniquefiles_a.csv – unique to DB-A
uniquefiles_b.csv – unique to DB-B
```
---
---
### 4) video_dhash_partial_matches_betw_db.py – Find partial video hash matches between two databases
- Compares dHash segments of videos stored in two SQLite databases.
- Counts matching dHash segments between videos to detect partial duplicates or similar videos.
- You must ensure the dHASH columns in the SQL SELECT statements MATCH your database schema.
- Logs results to a CSV file (video_match_filtered.csv) with columns:
```
video_path_db – path in first database
video_path_orig – path in second database
match_count – number of matching dHash segments
```

Filters results using thresholds:
- low_dhash_match – minimum matching segments to log (default: 3)
- max_dhash_match – maximum matching segments to log (default: 5)


---
---
### 5) video_dhash_remove_pathsTXT.py – Remove video entries from database using a TXT list
- Reads a list of video paths from a text file (ok.txt).
- Deletes all matching rows from a specified SQLite table (videos) and column (video_path).
- Processes deletions in batches to avoid SQL query limits for very large lists.
- Optionally compacts the database (VACUUM) after deletions to reclaim disk space.
- Prints the number of deleted rows for confirmation.

- Make sure DB_PATH, TXT_PATH, TABLE_NAME, and COLUMN_NAME match your setup.
- TXT file should contain one video path per line.


---
---
### 6) count_ext_in_db.py – Count file extensions in a video hash database
- Reads all video_path entries from a SQLite database (vhash_files.db).
- Extracts the file extension from each path.
- Counts how many videos exist per extension (e.g., mp4, mkv, avi).
- Prints a sorted list of extensions from most to least common.

---
---

### 7) sumcount_exts_files.sh – Count file extensions in a directory (Bash)
- Recursively scans the current directory (.) for all files.
- Extracts file extensions from filenames.
- Counts how many files exist for each extension.
- Prints a sorted list from most common to least common.
- Labels files without an extension as [no_ext].

---
---

### 8) simfiles_mvSEQfolders.py: video files with >90% similarity moved into grouped folders
- This script reads a SQLite database of videos with hash values
- identifies videos that share the same hash (or meet a similarity threshold)
- automatically moves each group of similar videos into numbered folders.
- Videos without matches remain in their original location.
- Useful for organizing large video collections based on content similarity.

---
---
# Helpful Tools summary 

## 1️⃣ Database Cleaners
Tools for cleaning or deduplicating your SQLite video/image databases.

- **`clean_nonexistpaths_from_db.py`** – Removes DB rows for missing files.
- **`video_dhash_remove_pathsTXT.py`** – Remove DB entries using a TXT list.
- **`del_find_dublicates_files_from_2db.py`** – Detect and optionally remove duplicate files across two DBs.

## 2️⃣ Duplicate & Similarity Analysis
Tools for finding duplicates or partial matches.

- **`compare_dhash_image_in2db.py`** – Compare image hashes across two DBs.
- **`video_dhash_partial_matches_betw_db.py`** – Find videos with partially matching dHashes.
- **`simfiles_mvSEQfolders.py`** – Video files with >90% similarity moved into grouped folders
  
## 3️⃣ File & Extension Analysis
Tools for analyzing file types or counting extensions.

- **`count_ext_in_db.py`** – Count file extensions stored in a database.
- **`sumcount_exts_files.sh`** – Count file extensions in a directory (Bash).
