import sqlite3
from collections import Counter
import os

DB_PATH = "vhash_files.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT video_path FROM videos")
extensions = []

for (path,) in cursor.fetchall():
    # os.path.splitext handles multiple dots correctly
    base, ext = os.path.splitext(path)
    ext = ext.lower().strip(". ")  # remove dot and extra spaces
    if not ext:
        ext = "<no_extension>"
    extensions.append(ext)

conn.close()

# Count occurrences
counts = Counter(extensions)

# Print sorted by most common
for ext, cnt in counts.most_common():
    print(f"{ext}: {cnt}")
