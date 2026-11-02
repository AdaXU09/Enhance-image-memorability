import json, os, shutil

PHOTOS_JSON = "photos.json"    # JSON Lines: one record per line, with label and photo_id
PHOTO_DIR   = "photos"         # source directory containing <photo_id>.jpg files
OUT_DIR     = "food"           # output folder

os.makedirs(OUT_DIR, exist_ok=True)
copied = missing = 0

for line in open(PHOTOS_JSON, encoding="utf-8"):
    rec = json.loads(line)                
    if rec["label"] != "food":
        continue
    src = os.path.join(PHOTO_DIR, rec["photo_id"] + ".jpg")
    if os.path.exists(src):
        shutil.copy2(src, OUT_DIR)         
        copied += 1
    else:
        missing += 1
    if (copied + missing) % 5000 == 0:
        print(f"{copied + missing} processed...", flush=True)

print(f"done. copied {copied}, missing {missing}")
