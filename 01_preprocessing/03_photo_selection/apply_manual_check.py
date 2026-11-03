"""
Manual check of the AI-selected photographs.   Run: python apply_manual_check.py

First run: writes manual_check.csv (keep = 1 for every photograph) and contact
sheets in manual_check_sheets/. Label keep = 0 and a reason for each photograph
that fails the inclusion criteria, and save as CSV.

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

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(HERE, "AI_selection_run")
CHECK = os.path.join(HERE, "manual_check.csv")
SHEETS = os.path.join(HERE, "manual_check_sheets")
OUT = os.path.join(HERE, "checked")


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def contact_sheets(rows, per_page=20, cols=5, cell=240):
    os.makedirs(SHEETS, exist_ok=True)
    cats = sorted({r["category"] for r in rows})
    for cat in cats:
        items = [r for r in rows if r["category"] == cat]
        for p in range(0, len(items), per_page):
            page = items[p:p + per_page]
            sheet = Image.new("RGB", (cols * cell, -(-len(page) // cols) * (cell + 20)), "white")
            draw = ImageDraw.Draw(sheet)
            for i, r in enumerate(page):
                x, y = i % cols * cell, i // cols * (cell + 20)
                im = Image.open(os.path.join(RUN, r["new_path"])).convert("RGB")
                im.thumbnail((cell - 8, cell - 8))
                sheet.paste(im, (x + (cell - im.width) // 2, y + 4))
                draw.text((x + 4, y + cell + 4), r["filename"], fill="black")
            sheet.save(os.path.join(SHEETS, f"{cat}_{p // per_page + 1}.jpg"))


selected = read_csv(os.path.join(RUN, "outputs", "selected.csv"))

if not os.path.exists(CHECK):             # first run
    with open(CHECK, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["filename", "category", "keep", "reason"])
        for r in sorted(selected, key=lambda r: (r["category"], r["filename"])):
            w.writerow([r["filename"], r["category"], 1, ""])
    contact_sheets(selected)
    sys.exit(f"Wrote manual_check.csv and manual_check_sheets/ for {len(selected)} photographs. "
             "Mark failures (keep = 0, reason), save, and run again.")

# second run
check = {r["filename"]: r for r in read_csv(CHECK)}
for r in selected:
    c = check.get(r["filename"])
    if c is None or c["keep"].strip() not in ("0", "1") or (c["keep"].strip() == "0" and not c["reason"].strip()):
        sys.exit(f"Fix manual_check.csv for {r['filename']}; keep must be 0 or 1, and keep = 0 needs a reason.")

kept = [r for r in selected if check[r["filename"]]["keep"].strip() == "1"]
shutil.rmtree(OUT, ignore_errors=True)
for r in kept:
    os.makedirs(os.path.join(OUT, r["category"]), exist_ok=True)
    shutil.copy2(os.path.join(RUN, r["new_path"]), os.path.join(OUT, r["category"], r["filename"]))
with open(os.path.join(OUT, "checked.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=selected[0].keys())
    w.writeheader()
    w.writerows(kept)
print(f"Kept {len(kept)} of {len(selected)} photographs in checked/.")
