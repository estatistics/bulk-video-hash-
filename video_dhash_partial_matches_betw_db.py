import sqlite3
import csv

# Thresholds
low_dhash_match = 3
max_dhash_match = 5

conn1 = sqlite3.connect("vd_btrs_piercings.db")
conn2 = sqlite3.connect("vd_temp_parent.db")

cur1 = conn1.cursor()
cur2 = conn2.cursor()

# Fetching paths and dhash columns
# dhash_1, dhash_2, dhash_3, dhash_4, dhash_5, dhash_6, dhash_7, dhash_8, dhash_9, dhash_10, dhash_11,  dhash_12, dhash_13, dhash_14, dhash_15, dhash_16, dhash_17, dhash_18, dhash_19, dhash_20
cur1.execute("SELECT video_path, dhash_2, dhash_3, dhash_4, dhash_5, dhash_6, dhash_7 FROM videos")
videos1 = cur1.fetchall()

cur2.execute("SELECT video_path, dhash_2, dhash_3, dhash_4, dhash_5, dhash_6, dhash_7 FROM videos")
videos2 = cur2.fetchall()


with open("video_match_filtered.csv", "w", encoding="utf-8") as f:
    # Write the header
    f.write("video_path_db||video_path_orig||match_count\n")

    for video1 in videos1:
        path1, dhash_es1 = video1[0], video1[1:]
        for video2 in videos2:
            path2, dhash_es2 = video2[0], video2[1:]

            match_count = 0
            for h1, h2 in zip(dhash_es1, dhash_es2):
                if h1 == h2 and h1 is not None:
                    match_count += 1
                if match_count >= max_dhash_match:
                    break

            if low_dhash_match <= match_count <= max_dhash_match:
                # Use .join() or f-strings to create the double-bar row
                print(f"Match Found: {match_count} hits between {path1} and {path2}")
                row = f"{path1}||{path2}||{match_count}\n"
                f.write(row)

conn1.close()
conn2.close()
print("Process Complete.")
