#!/usr/bin/env python3
"""
Compare each edited image with the original and record decisions in <out>/review.csv
(1 in `reject`, and a reason). Then run select_a.py. 
"""

import argparse
import csv
import os

from PIL import Image, ImageDraw

ARMS = ("A_guided", "A_study1", "A_empty")


def is_reject(cell):
    """1, 1.0, yes, y, x or true (any case) all mean rejected; blank means kept."""
    return str(cell or "").strip().lower() in {"1", "1.0", "yes", "y", "x", "true"}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="results_method_a")
    args = ap.parse_args()

    with open(os.path.join(args.out, "candidates.csv"), encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    notes = {}
    rpath = os.path.join(args.out, "review.csv")
    if os.path.exists(rpath):
        with open(rpath, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                flag = "REJECT " + r.get("reason", "") if is_reject(r.get("reject")) else ""
                text = " ".join(x for x in (flag, r.get("note", "")) if x).strip()
                if text:
                    notes[r["file"]] = text

    dest = os.path.join(args.out, "review_sheets")
    os.makedirs(dest, exist_ok=True)
    for old in os.listdir(dest):                 # pages are rebuilt each run; 
        if old.lower().endswith(".jpg"):
            os.remove(os.path.join(dest, old))
    photos = sorted({r["photo"] for r in rows})

    def label(r):
        """'dResMem +0.034  dViTMem +0.012'; the original shows its own scores."""
        if r["method"] == "original":
            return "ORIGINAL   " + "  ".join(f"{name} {float(r[k]):.3f}" for k, name in
                                             (("resmem", "ResMem"), ("vitmem", "ViTMem")) if r.get(k))
        return f"{r['candidate']}   " + "  ".join(
            f"d{name} {float(r[k]):+.3f}" for k, name in
            (("d_resmem", "ResMem"), ("d_vitmem", "ViTMem")) if r.get(k))

    def tile(r):
        with Image.open(os.path.join(args.out, "for_scoring", r["file"])) as im:
            im = im.convert("RGB")
        im.thumbnail((420, 300))
        c = Image.new("RGB", (420, 346), "white")
        c.paste(im, ((420 - im.width) // 2, 0))
        d = ImageDraw.Draw(c)
        d.text((4, 304), label(r), fill="black")
        if r["file"] in notes:
            d.text((4, 320), notes[r["file"]][:68], fill=(190, 0, 0))
        return c

    for n, pid in enumerate(photos, 1):
        mine = [r for r in rows if r["photo"] == pid]
        grid = [[r for r in mine if r["method"] == "original"]]       # first row: the original
        for arm in ARMS:                                               # then one row per version
            seeds = sorted((r for r in mine if r["method"] == arm), key=lambda r: int(float(r["seed"])))
            if seeds:
                grid.append(seeds)
        cols = max(len(g) for g in grid)
        sheet = Image.new("RGB", (420 * cols, 346 * len(grid)), "white")
        for i, g in enumerate(grid):
            for k, r in enumerate(g):
                sheet.paste(tile(r), (k * 420, i * 346))
        sheet.save(os.path.join(dest, f"{n:02d}_{pid}.jpg"), quality=88)
    print(f"{len(photos)} pages -> {dest}")


if __name__ == "__main__":
    main()
