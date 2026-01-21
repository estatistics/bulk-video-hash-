import sqlite3
import os

DB_PATH = "./video_dhash.db"
TABLE = "videos"  # your table name
PATH_COLUMN = "video_path"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 1️⃣ Fetch all paths
cur.execute(f"SELECT rowid, {PATH_COLUMN} FROM {TABLE}")
rows = cur.fetchall()

deleted_count = 0

for rowid, path in rows:
    if not os.path.exists(path):
        cur.execute(f"DELETE FROM {TABLE} WHERE rowid = ?", (rowid,))
        deleted_count += 1
        print(f"Deleted row for missing file: {path}")

# 2️⃣ Commit changes
conn.commit()
conn.close()

print(f"Done. Removed {deleted_count} rows for missing files.")
