import sqlite3

# --- Config ---
DB_PATH = 'video_beach_fixself.db'      # path to your SQLite DB
TXT_PATH = 'ok.txt'         # path to your txt with video paths to remove
TABLE_NAME = 'videos'        # your table name
COLUMN_NAME = 'video_path'  # column to match

# --- Load paths from TXT ---
with open(TXT_PATH, 'r', encoding='utf-8') as f:
    paths_to_remove = [line.strip() for line in f if line.strip()]

print(f"Loaded {len(paths_to_remove)} paths to remove.")

# --- Connect to SQLite ---
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# --- Delete paths in batches (to avoid huge IN lists) ---
BATCH_SIZE = 1000
total_deleted = 0

for i in range(0, len(paths_to_remove), BATCH_SIZE):
    batch = paths_to_remove[i:i+BATCH_SIZE]
    placeholders = ','.join('?' for _ in batch)
    sql = f"DELETE FROM {TABLE_NAME} WHERE {COLUMN_NAME} IN ({placeholders})"
    cursor.execute(sql, batch)
    deleted = cursor.rowcount
    total_deleted += deleted

print(f"Deleted {total_deleted} rows from {TABLE_NAME}.")

# --- Commit changes and compact DB ---
conn.commit()
conn.execute('VACUUM;')  # optional, reclaims disk space
conn.close()

print("Done. Database cleaned and compacted.")
