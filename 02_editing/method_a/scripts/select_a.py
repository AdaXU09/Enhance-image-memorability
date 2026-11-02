#!/usr/bin/env python3
"""
Apply the human review and choose one edited image per photograph.

    python select_a.py --out results_method_a

Reads <out>/candidates.csv and <out>/review.csv. A candidate is out if its
`reject` cell is 1. For each photograph and arm, the remaining candidate with
the highest ResMem is chosen.

Writes, in <out>:
  final_selection.csv   the chosen candidate per photograph and arm, scores
  final/                the chosen A_guided images, final/<category>/<photo>.png
  final_sheet.jpg       original | chosen A_guided | chosen A_study1 | chosen A_empty
and prints the ViTMem change, the number to report.
"""

import argparse
import csv
import os
import shutil

import numpy as np
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

    rows = list(csv.DictReader(open(os.path.join(args.out, "candidates.csv"), encoding="utf-8")))
    review = {r["file"]: r for r in csv.DictReader(open(os.path.join(args.out, "review.csv"),
                                                        encoding="utf-8"))}
    rejected = {f for f, r in review.items() if is_reject(r.get("reject"))}
    has_vit = "vitmem" in rows[0]

    chosen = []
    for pid in sorted({r["photo"] for r in rows}):
        for arm in ARMS:
            ok = [r for r in rows if r["photo"] == pid and r["method"] == arm
                  and r["file"] not in rejected]
            if ok:
                best = max(ok, key=lambda r: float(r["resmem"]))
                chosen.append({**best, "kept_of_4": len(ok),
                               "review_note": review.get(best["file"], {}).get("note", "")})

    keys = ["photo", "category", "method", "file", "seed", "kept_of_4", "resmem_original", "resmem",
            "d_resmem"] + (["vitmem", "d_vitmem"] if has_vit else []) + \
           ["f_value", "f_saturation", "f_sharpness", "prompt", "review_note"]
    with open(os.path.join(args.out, "final_selection.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(chosen)

    final = os.path.join(args.out, "final")
    if os.path.exists(final):
        shutil.rmtree(final)
    os.makedirs(final, exist_ok=True)
    for r in chosen:
        if r["method"] == "A_guided":                    # final/<category>/<photo>.png
            d = os.path.join(final, r.get("category", ""))
            os.makedirs(d, exist_ok=True)
            shutil.copy(os.path.join(args.out, "for_scoring", r["file"]),
                        os.path.join(d, r["photo"] + ".png"))

    # sheet: original | A_guided | A_study1 | A_empty
    tiles = []
    for pid in sorted({r["photo"] for r in rows}):
        row = [os.path.join(args.out, "for_scoring", f"{pid}__original.png")]
        labels = ["original"]
        for arm in ARMS:
            c = [r for r in chosen if r["photo"] == pid and r["method"] == arm]
            row.append(os.path.join(args.out, "for_scoring", c[0]["file"]) if c else None)
            labels.append(f"{arm} s{c[0]['seed']}" + (f"  dViTMem {float(c[0]['d_vitmem']):+.3f}"
                          if c and has_vit else "") if c else f"{arm}: none kept")
        tiles.append((row, labels))
    sheet = Image.new("RGB", (300 * (1 + len(ARMS)), 230 * len(tiles)), "white")
    d = ImageDraw.Draw(sheet)
    for i, (row, labels) in enumerate(tiles):
        for k, (p, lab) in enumerate(zip(row, labels)):
            if p:
                im = Image.open(p).convert("RGB")
                im.thumbnail((296, 200))
                sheet.paste(im, (k * 300, i * 230))
            d.text((k * 300 + 2, i * 230 + 204), lab, fill="black")
    sheet.save(os.path.join(args.out, "final_sheet.jpg"), quality=90)

    print(f"{len(rejected)} candidates rejected in review.csv")
    for arm in ARMS:
        c = [r for r in chosen if r["method"] == arm]
        line = f"  {arm:<9} chosen for {len(c)} photographs   ResMem " \
               f"{np.mean([float(r['d_resmem']) for r in c]):+.3f}"
        if has_vit:
            v = np.array([float(r["d_vitmem"]) for r in c])
            line += f"   ViTMem {v.mean():+.3f}   ViTMem>0 in {np.mean(v > 0):.0%}"
        print(line)
    print(f"-> {args.out}/final_selection.csv, final/, final_sheet.jpg")


if __name__ == "__main__":
    main()
