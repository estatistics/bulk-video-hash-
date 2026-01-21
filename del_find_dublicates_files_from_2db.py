import sqlite3
import csv
import os

# ---------------- CONFIG ----------------
DB_MAIN = "video_dhash.db";
DB_ORIG = "video_dhash_orig.db";

DELETE_DB_ROWS = False     # True to delete duplicate rows from main DB
DELETE_FILES = False      # True to delete video files from disk
CSV_LOG = "videos_marked_for_deletion.csv";
TXT_PATH_TO_DEL="paths_tobe_deleted.txt";


# ---------------- CONNECT DBs ----------------
conn_main = sqlite3.connect(DB_MAIN)
conn_main.row_factory = sqlite3.Row
cursor_main = conn_main.cursor()

conn_orig = sqlite3.connect(DB_ORIG)
conn_orig.row_factory = sqlite3.Row
cursor_orig = conn_orig.cursor()

# ---------------- DHASH COLUMNS ----------------
dhash_columns = [f"dhash_{i}" for i in range(1, 21)]

# ---------------- LOAD ORIGINAL DB ----------------
cursor_orig.execute(f"SELECT rowid, video_path, status, {', '.join(dhash_columns)} FROM videos")
orig_rows = cursor_orig.fetchall()

# Map dhash tuple -> list of original rows
orig_hash_map = {}
for row in orig_rows:
    dhash_tuple = tuple(row[col] for col in dhash_columns)
    orig_hash_map.setdefault(dhash_tuple, []).append(row)

# ---------------- FIND DUPLICATES ----------------
cursor_main.execute(f"SELECT rowid, video_path, status, {', '.join(dhash_columns)} FROM videos")
pairs = []

for row in cursor_main.fetchall():
    dhash_tuple = tuple(row[col] for col in dhash_columns)
    if dhash_tuple in orig_hash_map:
        for orig_row in orig_hash_map[dhash_tuple]:
            # Each pair: original -> duplicate
            pairs.append((
                orig_row["rowid"], orig_row["video_path"], orig_row["status"],
                row["rowid"], row["video_path"], row["status"]
            ))

print(f"Found {len(pairs)} duplicate pairs (original -> duplicate)")

# ---------------- LOG TO CSV ----------------
sep = ";;SEP;;"  # safe separator not in paths

with open(CSV_LOG, "w", encoding="utf-8") as f:
    # Write header
    header = ["original_rowid","original_path","original_status","duplicate_rowid","duplicate_path","duplicate_status"]
    f.write(sep.join(header) + "\n")

    # Write data rows
    for row in pairs:
        f.write(sep.join(map(str, row)) + "\n")

print(f"Logged duplicate pairs to CSV: {CSV_LOG}")



# ---------------- OPTIONAL FILE DELETION ----------------
if DELETE_FILES:
    paths_to_delete = []  # collect paths for logging
    for orig_rid, orig_path, orig_status, dup_rid, dup_path, dup_status in pairs:
        try:
            if os.path.isfile(dup_path):
                os.remove(dup_path)
                print(f"Deleted file: {dup_path}")
            else:
                print(f"File not found or not a file: {dup_path}")
            paths_to_delete.append(dup_path)  # save path regardless of existence
        except Exception as e:
            print(f"Error deleting file {dup_path}: {e}")
            paths_to_delete.append(dup_path)

    # Save paths to TXT file
    with open(TXT_PATH_TO_DEL, "w", encoding="utf-8") as f:
        for path in paths_to_delete:
            f.write(path + "\n")

    print(f"Saved paths to delete to: {TXT_PATH_TO_DEL}")


# ---------------- OPTIONAL DB ROW DELETION ----------------
if DELETE_DB_ROWS and pairs:
    # Only delete the duplicates (main DB)
    dup_rowids = list({dup_rid for _, _, _, dup_rid, _, _ in pairs})
    cursor_main.executemany("DELETE FROM videos WHERE rowid = ?", [(rid,) for rid in dup_rowids])
    conn_main.commit()
    print(f"Deleted {len(dup_rowids)} rows from DB: {DB_MAIN}")


# ---------------- CLOSE CONNECTIONS ----------------
conn_main.close()
conn_orig.close()
