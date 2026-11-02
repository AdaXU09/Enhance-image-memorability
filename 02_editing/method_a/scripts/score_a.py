#!/usr/bin/env python3
"""
Score Method A's edited images with ResMem and lay them out for review.

Reads the originals from the photo folder and the edited images that
generate_a.py put in <out>/for_scoring. Writes, in <out>:

  candidates.csv     one row per image: version, seed, prompt, ResMem score,
                     brightness, saturation, sharpness, and rank by ResMem
                     within its version.
  contact_sheet.jpg  per photograph: original | the four A_guided seeds |
                     the best A_study1 |the best A_empty
  review.csv         one row per edited image for the human check; fill in
                     `reject` (1) and `reason`. On a re-run, the reject, reason
                     and note already filled in are carried over (matched by
                     file name); everything else is recomputed. To start the
                     review afresh, rename or delete review.csv first
"""

import argparse
import csv
import json
import os
import shutil
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw

# possible reasons:
REASONS = ("dish_changed | ingredients_changed | portion_changed | "
           "object_or_text_added | visible_artifact | not_a_credible_photo")


def features(rgb):
    """Study 1's three features: HSV brightness and saturation as in Study 1;
    sharpness on a grayscale image converted from the colour image."""
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    return {"value": float(hsv[..., 2].mean()), "saturation": float(hsv[..., 1].mean()),
            "sharpness": float(cv2.Laplacian(gray, cv2.CV_64F).var())}


def load(path):
    with Image.open(path) as im:
        return np.asarray(im.convert("RGB"))


class ResMemScorer:
    def __init__(self):
        import torch
        from resmem import ResMem, transformer
        self.torch, self.tf = torch, transformer
        self.model = ResMem(pretrained=True).eval()

    def __call__(self, images, batch=16):
        out = []
        with self.torch.no_grad():
            for i in range(0, len(images), batch):
                x = self.torch.stack([self.tf(Image.fromarray(a)) for a in images[i:i + batch]])
                out += [float(v) for v in self.model(x).view(-1)]
        return out


def tile(img, text, width=240):
    im = Image.fromarray(img).copy()
    im.thumbnail((width, width))
    c = Image.new("RGB", (width, im.height + 32), "white")
    c.paste(im, ((width - im.width) // 2, 0))
    d = ImageDraw.Draw(c)
    for k, line in enumerate(text.split("\n")):
        d.text((3, im.height + 2 + 14 * k), line, fill="black")
    return c


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("photos")
    ap.add_argument("--out", default="results_method_a")
    args = ap.parse_args()

    log_path = os.path.join(args.out, "generation_log.jsonl")
    if not os.path.exists(log_path):
        sys.exit(f"{log_path} not found: run generate_a.py first")
    gen = {}
    with open(log_path, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            if rec.get("ok"):
                gen[rec["file"]] = rec               # a retry overwrites a failure
    if not gen:
        sys.exit(f"no successful requests in {log_path}")
    originals = {os.path.splitext(f)[0]: os.path.join(r, f)
                 for r, _, fs in os.walk(args.photos) for f in fs
                 if f.lower().endswith((".jpg", ".jpeg", ".png"))}

    def category(pid):
        """Sub-folder of the photo folder (../data/development_photos/pizza/xxx.jpg -> pizza), or ''."""
        rel = os.path.relpath(os.path.dirname(originals[pid]), args.photos)
        return "" if rel in (".", "") else rel.replace(os.sep, "/")
    photos = sorted({g["photo"] for g in gen.values()})
    missing = [p for p in photos if p not in originals]
    if missing:
        sys.exit(f"originals not found in {args.photos}: {missing[:3]}")

    print("loading ResMem ...", flush=True)
    score = ResMemScorer()
    fs_dir = os.path.join(args.out, "for_scoring")
    rows, sheet = [], []
    for n, pid in enumerate(photos, 1):
        orig = load(originals[pid])
        oname = f"{pid}__original.png"
        Image.fromarray(orig).save(os.path.join(fs_dir, oname))   # so ViTMem scores it too
        mine = sorted((g for g in gen.values() if g["photo"] == pid),
                      key=lambda g: (g["arm"], g["seed"]))
        imgs = [load(os.path.join(fs_dir, g["file"])) for g in mine]
        s0, *ss = score([orig] + imgs)
        f0 = features(orig)
        cat = category(pid)
        rows.append({"photo": pid, "category": cat, "candidate": "original",
                     "method": "original", "file": oname,
                     "resmem": round(s0, 4), "resmem_original": round(s0, 4), "d_resmem": 0.0,
                     **{"f_" + k: round(v, 1) for k, v in f0.items()}})
        mine_rows = []
        for g, img, s in zip(mine, imgs, ss):
            f = features(img)
            mine_rows.append({"photo": pid, "category": cat,
                              "candidate": f"{g['arm']}_s{g['seed']}",
                              "method": g["arm"], "file": g["file"], "seed": g["seed"],
                              "resmem": round(s, 4), "resmem_original": round(s0, 4),
                              "d_resmem": round(s - s0, 4),
                              **{"f_" + k: round(v, 1) for k, v in f.items()},
                              "model": g["model"], "prompt": g["prompt"],
                              "request_id": g.get("request_id", "")})
        for arm in sorted({r["method"] for r in mine_rows}):
            ranked = sorted((r for r in mine_rows if r["method"] == arm),
                            key=lambda r: -r["resmem"])
            for k, r in enumerate(ranked, 1):
                r["rank"] = k
        rows += mine_rows

        # contact-sheet row
        t = [tile(orig, f"{pid[:16]}\noriginal  ResMem {s0:.3f}")]
        for r, img in zip(mine_rows, imgs):
            if r["method"] == "A_guided":
                star = " *" if r.get("rank") == 1 else ""
                t.append(tile(img, f"A_guided seed {r['seed']}{star}\n{r['d_resmem']:+.3f}"))
        for arm in ("A_study1", "A_empty"):
            top = [(r, img) for r, img in zip(mine_rows, imgs)
                   if r["method"] == arm and r.get("rank") == 1]
            if top:
                t.append(tile(top[0][1], f"{arm} best\n{top[0][0]['d_resmem']:+.3f}"))
        sheet.append(t)
        best = {a: max((r["d_resmem"] for r in mine_rows if r["method"] == a and r.get("rank") == 1),
                       default=None) for a in ("A_guided", "A_empty", "A_empty")}
        print(f"[{n}/{len(photos)}] {pid}: original {s0:.3f}"
              + "".join(f"  {a} {v:+.3f}" for a, v in best.items() if v is not None), flush=True)

    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with open(os.path.join(args.out, "candidates.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows({k: r.get(k, "") for k in keys} for r in rows)

    review = os.path.join(args.out, "review.csv")
    earlier = {}
    if os.path.exists(review):
        shutil.copy(review, review + ".bak")
        with open(review + ".bak", encoding="utf-8-sig") as f:
            earlier = {r["file"]: r for r in csv.DictReader(f)}
        print("(previous review.csv saved as review.csv.bak; its decisions are carried over)")
    with open(review, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["photo", "file", "arm", "seed", "rank", "reject", "reason", "note"])
        for r in rows:
            if r["method"] != "original":
                e = earlier.get(r["file"], {})
                w.writerow([r["photo"], r["file"], r["method"], r["seed"], r.get("rank", ""),
                            e.get("reject", ""), e.get("reason", ""), e.get("note", "")])
        current = {r["file"] for r in rows}
        for f_, e in earlier.items():              # keep rows for images not in this run
            if f_ not in current:
                w.writerow([e.get(k, "") for k in ("photo", "file", "arm", "seed", "rank",
                                                   "reject", "reason", "note")])

    W = max(len(r) for r in sheet) * 240
    H = sum(max(t.height for t in r) for r in sheet)
    img, y = Image.new("RGB", (W, H), "white"), 0
    for r in sheet:
        for k, t in enumerate(r):
            img.paste(t, (k * 240, y))
        y += max(t.height for t in r)
    img.save(os.path.join(args.out, "contact_sheet.jpg"), quality=92)

    print(f"\nwrote {args.out}/candidates.csv, contact_sheet.jpg, review.csv")
    print(f"review.csv: mark reject = 1 and a reason ({REASONS})")
    print("next: score_vitmem.py and merge_scores.py on the same folder")


if __name__ == "__main__":
    main()
