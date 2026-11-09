"""
Manual check of the AI-selected photographs.   Run: python apply_manual_check.py

First run: writes manual_check.csv and contact sheets in manual_check_sheets/
(each photograph is labelled with its number, no, in manual_check.csv).
In manual_check.csv:
  - keep = 0 and a reason for each photograph that fails the inclusion criteria;
  - change_to_folder (keep = 1 only): leave empty, or enter another category
    (an existing one, or one listed in NEW_FOLDERS below) to move it there.
Save as CSV. Do not sort, add or delete rows: rows are matched by their order.

Second run: copies the kept photographs to checked/<category>/ and lists them
in checked/checked.csv. checked/ is rebuilt on every run.
"""
import csv
import os
import shutil
import subprocess
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:                       # installs Pillow once, only if missing
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    from PIL import Image, ImageDraw

# New category folders, e.g. NEW_FOLDERS = ["others"]. Leave empty if none.
NEW_FOLDERS = []

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(HERE, "AI_selection_run")
CHECK = os.path.join(HERE, "manual_check.csv")
SHEETS = os.path.join(HERE, "manual_check_sheets")
OUT = os.path.join(HERE, "checked")


def read_csv(path):
    for enc in ("utf-8-sig", "gbk"):      # Excel on Chinese Windows saves as GBK
        try:
            with open(path, encoding=enc, newline="") as f:
                return list(csv.DictReader(f))
        except UnicodeDecodeError:
            pass


def contact_sheets(rows, per_page=20, cols=5, cell=240):
    os.makedirs(SHEETS, exist_ok=True)
    for cat in sorted({r["category"] for r in rows}):
        items = [(no, r) for no, r in enumerate(rows, 1) if r["category"] == cat]
        for p in range(0, len(items), per_page):
            page = items[p:p + per_page]
            sheet = Image.new("RGB", (cols * cell, -(-len(page) // cols) * (cell + 20)), "white")
            draw = ImageDraw.Draw(sheet)
            for i, (no, r) in enumerate(page):
                x, y = i % cols * cell, i // cols * (cell + 20)
                im = Image.open(os.path.join(RUN, r["new_path"])).convert("RGB")
                im.thumbnail((cell - 8, cell - 8))
                sheet.paste(im, (x + (cell - im.width) // 2, y + 4))
                draw.text((x + 4, y + cell + 4), f"{no}   {r['filename']}", fill="black")
            sheet.save(os.path.join(SHEETS, f"{cat}_page{p // per_page + 1}.jpg"))


# same order as the rows of manual_check.csv
selected = sorted(read_csv(os.path.join(RUN, "outputs", "selected.csv")),
                  key=lambda r: (r["category"], r["filename"]))

if not os.path.exists(CHECK):             # first run
    with open(CHECK, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["no", "filename", "category", "keep", "change_to_folder", "reason"])
        for no, r in enumerate(selected, 1):
            w.writerow([no, r["filename"], r["category"], 1, "", ""])
    contact_sheets(selected)
    print(f"Wrote manual_check.csv and manual_check_sheets/ for {len(selected)} photographs.")
    sys.exit()

# second run: row n of manual_check.csv is photograph n (Excel may show some
# file names as #NAME?, so rows are matched by order, not by file name)
rows = read_csv(CHECK)
folders = {r["category"] for r in selected} | set(NEW_FOLDERS)
if len(rows) != len(selected) or any(c["category"] != r["category"] for r, c in zip(selected, rows)):
    sys.exit("Rows of manual_check.csv were added, deleted or re-sorted.")
for no, c in enumerate(rows, 1):
    keep, move = c["keep"].strip(), (c.get("change_to_folder") or "").strip()
    if keep not in ("0", "1") or (keep == "0" and not c["reason"].strip()) or (move and move not in folders):
        sys.exit(f"Check row {no} of manual_check.csv: keep must be 0 or 1; keep = 0 needs a reason; "
                 "change_to_folder must be a category or listed in NEW_FOLDERS.")

shutil.rmtree(OUT, ignore_errors=True)
for name in NEW_FOLDERS:
    os.makedirs(os.path.join(OUT, name), exist_ok=True)
kept = []
for r, c in zip(selected, rows):
    if c["keep"].strip() == "1":
        r = dict(r, original_category=r["category"])
        r["category"] = (c.get("change_to_folder") or "").strip() or r["category"]
        os.makedirs(os.path.join(OUT, r["category"]), exist_ok=True)
        shutil.copy2(os.path.join(RUN, r["new_path"]), os.path.join(OUT, r["category"], r["filename"]))
        kept.append(r)

with open(os.path.join(OUT, "checked.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(selected[0].keys()) + ["original_category"])
    w.writeheader()
    w.writerows(kept)
print(f"Kept {len(kept)} of {len(selected)} photographs in checked/.")
