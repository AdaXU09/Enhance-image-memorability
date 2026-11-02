#!/usr/bin/env python3
"""
Export the chosen pairs as experiment stimuli: original and edited image of
each photograph, processed identically.

    python export_stimuli.py --out results_method_a                    # native size (no resampling)
    python export_stimuli.py --out results_method_a --height 800       # both enlarged to 800 px high
    python export_stimuli.py --out results_method_a --height 800 --rescore

Reads <out>/final_selection.csv (run select_a.py first). For every photograph:

  - the original and the chosen A_guided image are taken from for_scoring/,
    i.e. at the size they were scored at (the original photograph's size).
  - with --height, both are resized to that height with the same filter
    (Lanczos), keeping the aspect ratio.
  - both are saved as PNG

Writes <out>/stimuli/<category>/<photo>_original.png and _edited.png, and
<out>/stimuli/stimuli.csv with sizes and the measured brightness, saturation
and sharpness of both images.

--rescore scores the exported files again with ResMem and ViTMem, to confirm
that resizing did not change the scores. 
"""

import argparse
import csv
import os
import sys

import numpy as np
from PIL import Image

from score_a import features


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="results_method_a")
    ap.add_argument("--height", type=int, help="display height in pixels (default: native)")
    ap.add_argument("--rescore", action="store_true", help="score the exported files again")
    args = ap.parse_args()

    sel_path = os.path.join(args.out, "final_selection.csv")
    if not os.path.exists(sel_path):
        sys.exit(f"{sel_path} not found: run select_a.py first")
    sel = [r for r in csv.DictReader(open(sel_path, encoding="utf-8"))
           if r["method"] == "A_guided"]
    src = os.path.join(args.out, "for_scoring")
    dest = os.path.join(args.out, "stimuli")

    rows = []
    for r in sel:
        pid, cat = r["photo"], r.get("category", "")
        d = os.path.join(dest, cat)
        os.makedirs(d, exist_ok=True)
        pair = {}
        for version, fname in (("original", f"{pid}__original.png"), ("edited", r["file"])):
            im = Image.open(os.path.join(src, fname)).convert("RGB")
            if args.height and im.height != args.height:
                w = round(im.width * args.height / im.height)
                im = im.resize((w, args.height), Image.LANCZOS)
            path = os.path.join(d, f"{pid}_{version}.png")
            im.save(path)
            pair[version] = (path, im)
        (po, io), (pe, ie) = pair["original"], pair["edited"]
        if io.size != ie.size:
            sys.exit(f"{pid}: original {io.size} and edited {ie.size} differ in size")
        fo, fe = features(np.asarray(io)), features(np.asarray(ie))
        rows.append({"photo": pid, "category": cat, "width": io.width, "height": io.height,
                     "original_file": os.path.relpath(po, dest).replace(os.sep, "/"),
                     "edited_file": os.path.relpath(pe, dest).replace(os.sep, "/"),
                     "edited_from": r["file"], "seed": int(float(r["seed"])),
                     "resmem_original": r["resmem_original"], "resmem_edited": r["resmem"],
                     "vitmem_original": round(float(r["vitmem"]) - float(r["d_vitmem"]), 4)
                     if r.get("vitmem") else "",
                     "vitmem_edited": r.get("vitmem", ""),
                     **{f"{k}_original": round(v, 1) for k, v in fo.items()},
                     **{f"{k}_edited": round(v, 1) for k, v in fe.items()}})

    if args.rescore:
        from score_a import ResMemScorer
        print("rescoring the exported files ...", flush=True)
        rm = ResMemScorer()
        imgs = [np.asarray(Image.open(os.path.join(dest, r[k])).convert("RGB"))
                for r in rows for k in ("original_file", "edited_file")]
        s = rm(imgs)
        try:
            from vitmem import ViTMem
            vm = ViTMem()
            v = [vm(os.path.join(dest, r[k])) for r in rows for k in ("original_file", "edited_file")]
        except Exception as e:                 # not installed, or weights unreachable
            print(f"  ViTMem not available ({e.__class__.__name__}); ResMem only")
            v = None
        for i, r in enumerate(rows):
            r["resmem_original_exported"] = round(s[2 * i], 4)
            r["resmem_edited_exported"] = round(s[2 * i + 1], 4)
            if v:
                r["vitmem_original_exported"] = round(v[2 * i], 4)
                r["vitmem_edited_exported"] = round(v[2 * i + 1], 4)
        for model in ("resmem", "vitmem"):
            if f"{model}_edited_exported" in rows[0] and rows[0][f"{model}_edited"] != "":
                before = np.array([float(r[f"{model}_edited"]) - float(r[f"{model}_original"])
                                   for r in rows])
                after = np.array([r[f"{model}_edited_exported"] - r[f"{model}_original_exported"]
                                  for r in rows])
                print(f"  {model}: gain as scored {before.mean():+.4f}, "
                      f"as exported {after.mean():+.4f}")

    with open(os.path.join(dest, "stimuli.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    size = f"{args.height} px high (Lanczos)" if args.height else "native size, unchanged"
    print(f"{len(rows)} pairs -> {dest}/  ({size}, PNG)")


if __name__ == "__main__":
    main()
