import sqlite3
import csv

# ========== CONFIG ==========
db_a = "im_fix.db"
db_b = "im_rec.db"

commons_a_csv = "commonsA.csv"
commons_b_csv = "commonsB.csv"
unique_a_csv = "uniquefiles_a.csv"
unique_b_csv = "uniquefiles_b.csv"

csv_sep = ">"  # or ">", whatever you prefer

# ---------- helper functions ----------
def load_dhashes(db_path):
    """Load dhashes -> list of paths"""
    conn = sqlite3.connect(db_path)
    cur = conn.execute("SELECT image_path, dhash FROM image_hashes")
    dhash_map = {}
    for path, dhash in cur:
        dhash_map.setdefault(dhash, []).append(path)
    conn.close()
    return dhash_map

def write_csv(filename, rows, sep="\t"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=sep)
        writer.writerow(["image_path", "dhash"])
        writer.writerows(rows)

# ---------- load databases ----------
print("[INFO] Loading databases...")
dhash_a = load_dhashes(db_a)
dhash_b = load_dhashes(db_b)

set_a = set(dhash_a.keys())
set_b = set(dhash_b.keys())

# ---------- COMMON DHASHES ----------
common_dhashes = set_a & set_b

# Paths from DB-A only
common_a_rows = [(p, dh) for dh in common_dhashes for p in dhash_a[dh]]
write_csv(commons_a_csv, common_a_rows, sep=csv_sep)
print(f"[INFO] Common files from DB-A: {len(common_a_rows)} rows written to {commons_a_csv}")

# Paths from DB-B only
common_b_rows = [(p, dh) for dh in common_dhashes for p in dhash_b[dh]]
write_csv(commons_b_csv, common_b_rows, sep=csv_sep)
print(f"[INFO] Common files from DB-B: {len(common_b_rows)} rows written to {commons_b_csv}")

# ---------- UNIQUE TO DB-A ----------
unique_a = set_a - set_b
unique_a_rows = [(p, dh) for dh in unique_a for p in dhash_a[dh]]
write_csv(unique_a_csv, unique_a_rows, sep=csv_sep)
print(f"[INFO] Unique to DB-A: {len(unique_a_rows)} rows written to {unique_a_csv}")

# ---------- UNIQUE TO DB-B ----------
unique_b = set_b - set_a
unique_b_rows = [(p, dh) for dh in unique_b for p in dhash_b[dh]]
write_csv(unique_b_csv, unique_b_rows, sep=csv_sep)
print(f"[INFO] Unique to DB-B: {len(unique_b_rows)} rows written to {unique_b_csv}")

print("[DONE] All comparisons finished.")
