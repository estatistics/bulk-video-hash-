import os
import sqlite3
import concurrent.futures
import cv2
from PIL import Image
import imagehash

# -------------------------
# CONFIG
VIDEO_ROOT = "./"
# , ".ogv"
VIDEO_EXTS = (".mp4", ".avi", ".mkv", ".flv", ".mpg", ".webm", ".mov", ".wmv", ".qt", ".m4v", ".ts", ".mpeg", ".divx")

FRAMES_PER_SEGMENT = 1000
MAX_SEGMENTS = 400          # <-- IMPORTANT
RESIZE_DIM = (64, 64)

DB_PATH = "vhash_files.db"
MAX_WORKERS = 8

# -------------------------
# DATABASE SETUP (MAIN THREAD ONLY)

# --- DB setup (once, main thread) ---
conn = sqlite3.connect(DB_PATH, timeout=30)
conn.execute("PRAGMA journal_mode=WAL;")  # enable WAL for concurrency
cursor = conn.cursor()

hash_cols = ",\n".join([f"hash{i} TEXT" for i in range(1, MAX_SEGMENTS + 1)])
cursor.execute(f"""
CREATE TABLE IF NOT EXISTS videos (
    video_path TEXT PRIMARY KEY,
    segment_count INTEGER,
    zero_count INTEGER,
    {hash_cols}
)
""")
conn.commit()
conn.close()



# Check what files processed already
def is_already_processed(video_path):
    conn_check = sqlite3.connect(DB_PATH)
    cursor_check = conn_check.cursor()
    cursor_check.execute("SELECT 1 FROM videos WHERE video_path = ?", (video_path,))
    result = cursor_check.fetchone()
    conn_check.close()
    return result is not None


# -------------------------
# VIDEO HASH FUNCTION
def segment_vhash(video_path):
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise RuntimeError("Cannot open video")

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if frame_count <= 0:
            raise RuntimeError("Video has 0 frames")

        # ensure at least 1 segment
        total_segments = max(1, min(
            MAX_SEGMENTS,
            (frame_count + FRAMES_PER_SEGMENT - 1) // FRAMES_PER_SEGMENT
        ))

        hashes = []

        for i in range(total_segments):
            start = i * FRAMES_PER_SEGMENT
            end = min(start + FRAMES_PER_SEGMENT - 1, frame_count - 1)
            idx = start + (end - start) // 2

            # For very small videos, cap idx to the last frame
            idx = min(idx, frame_count - 1)

            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret:
                hashes.append("0")
                continue

            frame_small = cv2.resize(frame, RESIZE_DIM)
            frame_gray = cv2.cvtColor(frame_small, cv2.COLOR_BGR2GRAY)
            frame_pil = Image.fromarray(frame_gray)

            h = str(imagehash.dhash(frame_pil))
            hashes.append(h)

        cap.release()
        return hashes

    except Exception as e:
        print(f"[ERROR] {video_path}: {e}")
        return []


# -------------------------
# PROCESS ONE FILE (THREAD SAFE)
def process_file(video_path):
    try:
        hashes = segment_vhash(video_path)

        segment_count = len(hashes)
        zero_count = hashes.count("0")

        # pad to MAX_SEGMENTS
        hashes += ["0"] * (MAX_SEGMENTS - segment_count)

        values = [video_path, segment_count, zero_count] + hashes
        placeholders = ",".join(["?"] * (3 + MAX_SEGMENTS))

        # thread-safe connection with timeout
        conn_thread = sqlite3.connect(DB_PATH, timeout=30)
        cursor_thread = conn_thread.cursor()

        cursor_thread.execute(
            f"INSERT OR REPLACE INTO videos VALUES ({placeholders})",
            values
        )

        conn_thread.commit()
        conn_thread.close()

        print(f"Processed: {video_path} | segments: {segment_count}")
        return video_path

    except Exception as e:
        print(f"[ERROR processing {video_path}]: {e}")
        return None


# -------------------------
# WALK FOLDER

def get_video_files(root):
    for root_dir, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d != "__snapshots"]
        for f in files:
            if f.lower().endswith(VIDEO_EXTS):
                yield os.path.abspath(os.path.join(root_dir, f))

# -------------------------
# PARALLEL PROCESSING

def main():
    video_files = [f for f in get_video_files(VIDEO_ROOT) if not is_already_processed(f)]
    print(f"Found {len(video_files)} videos.")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        list(executor.map(process_file, video_files))

    print("All videos processed.")

if __name__ == "__main__":
    main()
