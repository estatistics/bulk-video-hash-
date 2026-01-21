import sqlite3
import os
import shutil
from collections import defaultdict

# Config
DB_PATH = "vhash_rec.db"
HASH_COLUMN = "hash1"           # we compare only hash1
SIMILARITY_THRESHOLD = 0.9      # 90% similarity (for hash1 equality, use 1.0)
DEST_FOLDER_PREFIX = "folder_"

# Base folder for moving files
BASE_DEST = "grouped_videos"

os.makedirs(BASE_DEST, exist_ok=True)

# Connect to DB
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Fetch video_path and hash1
cur.execute(f"SELECT video_path, {HASH_COLUMN} FROM videos")
rows = cur.fetchall()
conn.close()

# Build a map: hash -> list of videos
hash_map = defaultdict(list)
for video_path, h1 in rows:
    if h1 is None or h1 == 0:   # skip zero/empty hash
        continue
    hash_map[h1].append(video_path)

# Group counter
folder_counter = 1

for h, videos in hash_map.items():
    if len(videos) < 2:
        continue  # skip unpaired files

    # Create folder for this group
    folder_name = f"{DEST_FOLDER_PREFIX}{folder_counter:03d}"
    folder_path = os.path.join(BASE_DEST, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # Move videos into folder
    for video in videos:
        if os.path.exists(video):
            shutil.move(video, folder_path)
        else:
            print(f"Warning: {video} not found!")

    print(f"Moved {len(videos)} videos with hash {h} to {folder_path}")
    folder_counter += 1

print("Process complete.")
