#!/usr/bin/env python3
"""
Cut a large photo folder down to a fewer amount of candidates for the AI step.

    python tools/prefilter/prefilter.py photos/ --out-dir pool/ --target 1000 --auto

Stage A reads each file, and drops photos too small or too oddly shaped for the later edits to work on. Stage B opens a
random sample of the rest and measures it: colour, sharpness as our paper defines them, framing, collages, memorability.

--auto then sets the cuts for you: sharpness at the 5th percentile of your
own photographs, because that measurement spreads out smoothly; clipping and
saturation at fixed values, because almost every normal photo scores zero on
the first and far above zero on the second, so a percentile there would cut
into the healthy middle. Collages and framed are rejected as well. It prints where
each cut landed and writes contact sheets that span it.

To move a cut, with no re-measuring:

    python tools/prefilter/prefilter.py photos/ --out-dir pool/ --reuse --min-sharpness 120

Output: pool.csv holding every measured row, and a folder of the kept photos.
Requirements: opencv-python, numpy, Pillow, and resmem for the
memorability score. See tools/prefilter/requirements.txt, or:
pip install -r tools/prefilter/requirements.txt
Diagnostic contact sheets are written beside the output pool in diagnostics/.
"""

import argparse
import csv
import hashlib
import os
import random
import shutil
import sys
import time
from collections import Counter
from datetime import datetime

try:
    import cv2
    import numpy as np
    from PIL import Image
except ImportError as e:
    sys.exit(f"missing package: {e.name}\n"
             f"  pip install -r tools/prefilter/requirements.txt\n"
             f"  (or: pip install opencv-python numpy Pillow resmem)")

Image.MAX_IMAGE_PIXELS = None


# ---------------------------------------------------------------------------
# 1. MEASURE  colour and sharpness, same definitions as our paper 
# ---------------------------------------------------------------------------
def study1_features(bgr):
    """Native scales. sharpness_measure doubles.
    """
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    grey = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    return {
        "average_hue":        round(float(hsv[:, :, 0].mean()), 2),
        "average_saturation": round(float(hsv[:, :, 1].mean()), 2),
        "average_value":      round(float(hsv[:, :, 2].mean()), 2),
        "sharpness_measure":  round(float(cv2.Laplacian(grey, cv2.CV_64F).var()), 1),
        "clipped":            round(float((grey >= 252).mean() + (grey <= 3).mean()), 3),
    }


# ---------------------------------------------------------------------------
# 2. MEASURE  how much of the frame the dish fills
# ---------------------------------------------------------------------------
def auto_bbox(bgr, iters=4):
    """GrabCut from a central rectangle, then the foreground bounding box.
    """
    h, w = bgr.shape[:2]
    s = 320 / max(h, w)
    small = cv2.resize(bgr, (int(w * s), int(h * s))) if s < 1 else bgr
    sh, sw = small.shape[:2]

    m = .02
    cap = round((1 - 2 * m) * 100)                     # 96
    mask = np.zeros((sh, sw), np.uint8)
    rect = (int(sw * m), int(sh * m), int(sw * (1 - 2 * m)), int(sh * (1 - 2 * m)))
    try:
        cv2.grabCut(small, mask, rect, np.zeros((1, 65), np.float64),
                    np.zeros((1, 65), np.float64), iters, cv2.GC_INIT_WITH_RECT)
    except cv2.error:
        return None, None, None, "grabcut_failed"

    fg = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 1, 0).astype(np.uint8)
    area = fg.mean()
    if area < .02:
        return None, None, None, "no_foreground"
    if area > .97:
        return 100, 100, 100, "fills_frame"

    ys, xs = np.where(fg > 0)
    bw = (xs.max() - xs.min() + 1) / sw * 100
    bh = (ys.max() - ys.min() + 1) / sh * 100
    fill = area / max((bw / 100) * (bh / 100), 1e-6)
    flag = [] if fill > .45 else ["scattered_mask"]
    if round(bw) >= cap - 1 or round(bh) >= cap - 1:
        flag.append("touches_edge")
    return round(bw), round(bh), round(bw * bh / 100), "|".join(flag)

# ---------------------------------------------------------------------------
# 3. MEASURE  is it a collage, or does it have an added white frame
# ---------------------------------------------------------------------------
def layout_flags(bgr):
    """Collage seams and added white or black frames.
    Both require the line to be near-white or near-black as well as uniform;
    """
    g = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
    h, w = g.shape
    out = []

    def seam(line):
        return line.std() < 2.5 and (line.mean() > 235 or line.mean() < 20)

    e = max(2, int(min(h, w) * .015))
    if all(seam(b) for b in (g[:e], g[-e:], g[:, :e], g[:, -e:])):
        out.append("uniform_border")
    if (any(seam(g[y]) for y in range(int(h * .15), int(h * .85)))
            or any(seam(g[:, x]) for x in range(int(w * .15), int(w * .85)))):
        out.append("interior_seam")
    return "|".join(out)


# ---------------------------------------------------------------------------
# 4. SHOW  grid of the worst 20 on one measurement, each labelled
# ---------------------------------------------------------------------------
def contact_sheet(rows, key, lowest, path, photo_dir, n=20, cols=5, cell=220):
    """A grid of the n most extreme images on one measurement, each labelled
    with its value, so a threshold can be read off a picture instead of
    guessed from a number."""
    from PIL import ImageDraw
    have = [r for r in rows if r.get(key) is not None]
    if not have:
        return None
    have.sort(key=lambda r: r[key], reverse=not lowest)
    have = have[:n]

    rowsn = (len(have) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell, rowsn * (cell + 18)), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    for i, r in enumerate(have):
        try:
            with Image.open(os.path.join(photo_dir, r["filename"])) as im:
                im = im.convert("RGB")
                im.thumbnail((cell, cell), Image.BILINEAR)
        except Exception:
            continue
        x, y = (i % cols) * cell, (i // cols) * (cell + 18)
        sheet.paste(im, (x + (cell - im.width) // 2, y + (cell - im.height) // 2))
        draw.text((x + 4, y + cell + 3), f"{r[key]:g}", fill=(0, 0, 0))
    sheet.save(path)
    return have[-1][key]


# ---------------------------------------------------------------------------
# 5. DECIDE  what the cut-off for each measurement is
# ---------------------------------------------------------------------------
def percentile(vals, p):
    v = sorted(x for x in vals if x is not None)
    return v[min(int(p * len(v)), len(v) - 1)] if v else None


def resolve_cuts(args, measured=None):
    """The value of thresholds that we passed always wins. Otherwise, with --auto, sharpness is cut
    at a percentile of our own photographs and clipping and saturation at
    fixed values.
    """
    auto = args.auto and measured
    cuts = {}

    def by_percentile(name, explicit, col, p, lower):
        """For a measurement whose values spread out smoothly."""
        if explicit is not None:
            cuts[name] = (explicit, "you set this")
        elif auto:
            v = percentile([r.get(col) for r in measured], p)
            if v is not None:
                cuts[name] = (v, f"{'bottom' if lower else 'top'} "
                                 f"{int((p if lower else 1-p)*100)}% of your photos")

    def by_absolute(name, explicit, value, why):
        """Percentile cut off can be bad instrument. E.g., Nearly all food photos
        have no clipped pixels at all, so the 95th percentile of clipping
        lands on roughly zero and the rule accidentally becomes "reject any photo with even a single white dot"—which throws out perfectly 
        good photos just because they have a shiny reflection on the sauce. Saturation is the same: Only a few photos are true 
        black-and-white (zero saturation), while the rest are much higher. A bottom 
        2% cut-off would reach too high into the normal color photos, accidentally 
        deleting good images just because their colors are softer or muted.
        """
        if explicit is not None:
            cuts[name] = (explicit, "you set this")
        elif auto:
            cuts[name] = (value, why)

    by_percentile("min_sharpness", args.min_sharpness, "sharpness_measure", .05, True)
    by_absolute("max_clipped", args.max_clipped, 0.10,
                "fixed: >10% of pixels blown or crushed")
    by_absolute("min_saturation", args.min_saturation, 10.0,
                "fixed: true greyscale only (0-255 scale)")
    if args.value_range is not None:
        cuts["value_range"] = (args.value_range, "you set this")
    if args.drop_flagged or args.auto:
        cuts["drop_flagged"] = (1, "you set this" if args.drop_flagged else "--auto")
    return cuts


# flags that mean "this file is not a single photograph"—unlike the
# GrabCut warnings, which describe the measurement rather than the photo
LAYOUT_DEFECTS = ("uniform_border", "interior_seam")


def early_reject(args, r, cuts=None):
    """Why this photo is out, or None. """
    if cuts is None:
        cuts = resolve_cuts(args)
    get = lambda k: cuts[k][0] if k in cuts else None

    v = get("min_sharpness")
    if v is not None and (r.get("sharpness_measure") or 0) < v:
        return "blurred"
    v = get("max_clipped")
    if v is not None and (r.get("clipped") or 0) > v:
        return "clipped"
    v = get("min_saturation")
    if v is not None and (r.get("average_saturation") or 0) < v:
        return "near-greyscale"
    v = get("value_range")
    if v is not None and not (v[0] <= (r.get("average_value") or 0) <= v[1]):
        return "too dark or bright"
    # Only layout defects are grounds for rejection. scattered_mask,
    # grabcut_failed and no_foreground say the SEGMENTATION struggled, not
    # that the photograph is bad; rejecting on them would favour photos that
    # segment easily, which means simple compositions—a bias on exactly the
    # framing axis the pool is supposed to spread across.
    if "drop_flagged" in cuts:
        bad = [f for f in (r.get("flags") or "").split("|") if f in LAYOUT_DEFECTS]
        if bad:
            return "|".join(bad)
    return None


# ---------------------------------------------------------------------------
# 6. RUN
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("photo_dir")
    ap.add_argument("--out-dir", default="pool")
    ap.add_argument("--out-csv", default="pool.csv")
    ap.add_argument("--target", type=int, default=1000,
                    help="how many photos you want to end up with. Without "
                         "--auto the run keeps going until that many survive. "
                         "With --auto it measures 35%% extra, a "
                         "heavier rejection rate can leave you short "
                         "(default 1000)")
    ap.add_argument("--min-side", type=int, default=400,
                    help="drop photos whose shorter side is below this. The "
                         "memorability model resizes to 227 px, the 30-percent "
                         "crop needs 325 for 227 to remain, the tightest crop "
                         "needs 455 (default 400)")
    ap.add_argument("--max-aspect", type=float, default=2.0)
    ap.add_argument("--no-resmem", action="store_true")
    ap.add_argument("--seed", type=int, default=0)

    # Thresholds. Without --auto they are all off, so a first run measures
    # everything and cuts nothing; you read the contact sheets and come back
    # with numbers. With --auto they are filled in for you, and anything you
    # pass here overrides that one. Either way they are tested on the cheap
    # measurements before GrabCut and ResMem.
    ap.add_argument("--min-sharpness", type=float, default=None)
    ap.add_argument("--max-clipped", type=float, default=None)
    ap.add_argument("--min-saturation", type=float, default=None,
                    help="0-255, catches greyscale photos")
    ap.add_argument("--value-range", type=float, nargs=2, default=None,
                    metavar=("LO", "HI"), help="0-255, e.g. 40 235")
    ap.add_argument("--drop-flagged", action="store_true",
                    help="reject collages and framed exports instead of "
                         "only flagging them")
    ap.add_argument("--auto", action="store_true",
                    help="measure first, then cut: sharpness at the 5th "
                         "percentile of your own photos, clipping above 0.10 "
                         "and saturation below 10 as fixed values, plus "
                         "anything flagged. Any threshold you pass by hand "
                         "overrides that one.")
    ap.add_argument("--reuse", action="store_true",
                    help="skip measuring: read --out-csv and re-apply the "
                         "thresholds. Takes a second instead of minutes.")
    args = ap.parse_args()

    # A check of folders. The following STEP 3 empties --out-dir before refilling it, so pointing it at the
    # source folder would delete the originals.
    if os.path.abspath(args.out_dir) == os.path.abspath(args.photo_dir):
        print("--out-dir must not be the folder your photos are in; "
              "it gets emptied before each run.")
        return

    # --- STEP 1: get a measurement for every candidate photo ---------------
    if args.reuse:
        if not os.path.exists(args.out_csv):
            print(f"--reuse needs {args.out_csv}, which does not exist. "
                  f"Run once without it first.")
            return
        ints = {"width", "height", "short_side",
                "auto_width_pct", "auto_height_pct", "auto_bbox_pct"}
        measured = []
        for row in csv.DictReader(open(args.out_csv, encoding="utf-8")):
            for k, v in list(row.items()):
                if k in ("filename", "base_id", "flags", "rejected", "pixel_md5"):
                    continue
                row[k] = None if v in ("", None) else (
                    int(float(v)) if k in ints else float(v))
            measured.append(row)
        model = True if any(r.get("memory_score") is not None for r in measured) else None
        print(f"reusing {len(measured):,} measurements from {args.out_csv}")
    else:
        files = sorted(f for f in os.listdir(args.photo_dir)
                       if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")))
        print(f"found                {len(files):>8,}")

        # 1a. read every file header, drop unusable sizes, shuffle
        t0, kept, drop = time.time(), [], Counter()
        for fn in files:
            try:
                with Image.open(os.path.join(args.photo_dir, fn)) as im:
                    w, h = im.size
            except Exception:
                drop["unreadable"] += 1
                continue
            if min(w, h) < args.min_side:
                drop["too small"] += 1
            elif max(w, h) / max(min(w, h), 1) > args.max_aspect:
                drop["extreme aspect"] += 1
            else:
                kept.append({"filename": fn, "base_id": os.path.splitext(fn)[0],
                             "width": w, "height": h, "short_side": min(w, h)})

        print(f"A  usable size       {len(kept):>8,}   ({time.time()-t0:.0f}s)")
        for k, v in drop.most_common():
            print(f"     dropped, {k:<15} {v:>8,}")
        if not kept:
            print("\nNothing passed. --min-side is probably above your photos' size.")
            return

        random.Random(args.seed).shuffle(kept)

        # 1b. load the memorability model
        model = None
        if not args.no_resmem:
            try:
                from resmem import ResMem, transformer
                model = ResMem(pretrained=True).eval()
                print("   ResMem loaded (CPU)")
            except Exception as e:
                print(f"   ResMem unavailable ({e}); continuing without it",
                      file=sys.stderr)

        # --auto needs the whole distribution before it can choose a cut, so it
        # cannot reject early; it measures instead and cuts after.
        # Without --auto it rejects as it goes, so it keeps going until target photos have actually survived.
        budget = int(args.target * 1.35) if args.auto else len(kept)
        print(f"\nB  measuring {'' if args.auto else 'until '}"
              f"{budget if args.auto else args.target:,}"
              f"{'' if args.auto else ' survive'}...")

        t0, measured, n_kept, seen = time.time(), [], 0, set()
        for r in kept:
            if (len(measured) >= budget) if args.auto else (n_kept >= args.target):
                break
            path = os.path.join(args.photo_dir, r["filename"])
            bgr = cv2.imread(path)
            if bgr is None:
                r["rejected"] = "unreadable"
                measured.append(r)
                continue

            # ------------------------------------------------
            r["pixel_md5"] = hashlib.md5(bgr.tobytes()).hexdigest()[:16]
            if r["pixel_md5"] in seen:
                r["rejected"] = "duplicate"
                measured.append(r)
                continue
            seen.add(r["pixel_md5"])
            r.update(study1_features(bgr))
            r["flags"] = layout_flags(bgr)

            # with explicit thresholds and no --auto, we can discard some photos without measuring all the images. 
            if not args.auto:
                why = early_reject(args, r)
                if why:
                    r["rejected"] = why
                    measured.append(r)
                    continue

            # -------------------------------------------
            bw, bh, ba, bflag = auto_bbox(bgr)
            r.update(auto_width_pct=bw, auto_height_pct=bh, auto_bbox_pct=ba)
            if bflag:
                r["flags"] = "|".join(x for x in (bflag, r["flags"]) if x)
            if model is not None:
                import torch
                with torch.no_grad():
                    im = Image.open(path).convert("RGB")
                    r["memory_score"] = round(
                        float(model(transformer(im).view(-1, 3, 227, 227))), 3)
            r["rejected"] = ""
            measured.append(r)
            n_kept += 1
            if len(measured) % 100 == 0:
                print(f"     kept {n_kept}, examined {len(measured)}   "
                      f"{len(measured)/(time.time()-t0):.1f} img/s", flush=True)
        print(f"B  measured          {len(measured):>8,}   ({time.time()-t0:.0f}s)")

    # --- STEP 2: decide the cut-offs, then mark who is out -----------------
    cuts = resolve_cuts(args, measured)
    if cuts:
        print("\ncuts applied")
        for name, (val, how) in cuts.items():
            print(f"  {name:<20} {val!s:<10} {how}")

    # Re-judge every row, unreadable files are permanently out.
    for r in measured:
        if r.get("rejected") in ("unreadable", "duplicate"): 
            continue
        r["rejected"] = early_reject(args, r, cuts) or ""

    # A row rejected early in a previous non-auto run never reached the
    # expensive measurements, but it cannot simply be let back in. An empty auto_bbox_pct means GrabCut was skipped
    # or that it ran but failed—these flags tell the two apart.
    attempted = ("grabcut_failed", "no_foreground")
    half = 0
    for r in measured:
        if (not r["rejected"] and r.get("auto_bbox_pct") is None
                and not any(f in (r.get("flags") or "") for f in attempted)):
            r["rejected"] = "not fully measured"
            half += 1

    passing = [r for r in measured if not r["rejected"]]
    sample = passing[:args.target]
    # Anything past --target is not copied into the pool, so it must not be
    # left with an empty `rejected` either: downstream reads that column as
    # "this photograph is in the pool folder", and the two have to agree.
    for r in passing[args.target:]:
        r["rejected"] = "over --target"
    rejected = Counter(r["rejected"] for r in measured if r["rejected"])

    print(f"\nkept                 {len(sample):>8,} of {len(measured):,}")
    for k, v in rejected.most_common():
        print(f"     rejected, {k:<14} {v:>8,}")
    if not sample:
        print("\nNothing kept. The thresholds are too strict.")
        return
    if half:
        print(f"\n  {half} photo(s) would now pass but were skipped before the "
              f"expensive\n  measurements in an earlier run. Re-run without "
              f"--reuse to include them.")
    if len(sample) < args.target:
        print(f"\n  short of --target {args.target:,}; raise it and re-run "
              f"without --reuse")

    # --- STEP 3: write the CSV and copy the kept photos --------------------
    os.makedirs(args.out_dir, exist_ok=True)
    for f in os.listdir(args.out_dir):
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            os.remove(os.path.join(args.out_dir, f))
    for r in sample:
        src_path = os.path.join(args.photo_dir, r["filename"])
        if os.path.exists(src_path):
            shutil.copy2(src_path, args.out_dir)

    # every measured row is written, including the rejected ones, so --reuse
    # has the full distribution to re-cut against
    fields = ["filename", "base_id", "width", "height", "short_side", "memory_score",
              "average_hue", "average_saturation", "average_value",
              "sharpness_measure", "clipped",
              "auto_width_pct", "auto_height_pct", "auto_bbox_pct",
              "pixel_md5", "flags", "rejected"]
    with open(args.out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(measured)
    print(f"\nwrote {args.out_csv} ({len(measured):,} rows, rejected ones kept "
          f"so --reuse can re-cut)")
    print(f"copied {len(sample)} images to {args.out_dir}/")

    summary = os.path.splitext(args.out_csv)[0] + "_summary.txt"
    append = args.reuse and os.path.exists(summary)
    with open(summary, "a" if append else "w", encoding="utf-8") as f:
        if append:
            f.write("\n" + "-" * 68 + "\n\n")
        f.write(f"prefilter.py  {datetime.now():%Y-%m-%d %H:%M}\n")
        f.write(f"command: {' '.join(sys.argv)}\n\n")
        # every photograph is accounted for: each indented line is a loss, and
        # the line below it is what remained
        passed = len(passing)
        if not args.reuse:
            f.write(f"files found                  {len(files):>8,}\n")
            for k, v in drop.most_common():
                f.write(f"  stage A, {k:<22} {v:>8,}\n")
            f.write(f"usable size                  {len(kept):>8,}\n")
            if len(kept) > len(measured):
                f.write(f"  not sampled                  {len(kept)-len(measured):>8,}\n")
            f.write(f"measured                     {len(measured):>8,}\n")
        else:
            f.write(f"reused measurements          {len(measured):>8,}\n")
        for k, v in rejected.most_common():
            if k == "over --target":      # reported on its own line below
                continue
            f.write(f"  stage B, {k:<22} {v:>8,}\n")
        f.write(f"passed                       {passed:>8,}\n")
        if passed > len(sample):
            f.write(f"  over --target {args.target:<12,} {passed-len(sample):>8,}\n")
        f.write(f"kept                         {len(sample):>8,}\n\n")
        f.write("thresholds\n")
        for name, (val, how) in cuts.items():
            f.write(f"  {name:<18} {val!s:<12} {how}\n")
    print(f"wrote {summary} — the exclusion funnel, for the methods section\n")

    # --- STEP 4: print the distributions -----------------------------------
    def dist(key, fmt="{:.1f}", note=""):
        v = sorted(r[key] for r in sample if r.get(key) is not None)
        if not v:
            return
        q = lambda p: v[min(int(p * len(v)), len(v) - 1)]
        print(f"  {key:<20} min {fmt.format(v[0])}  p5 {fmt.format(q(.05))}  "
              f"p25 {fmt.format(q(.25))}  med {fmt.format(q(.50))}  "
              f"p75 {fmt.format(q(.75))}  max {fmt.format(v[-1])}")
        if note:
            print(f"  {'':<20} {note}")

    print("measured from study 1 regression, nothing cut on these—you set the lines after looking")
    dist("average_value", "{:.0f}", "beta = +0.0163, the dominant perceptual effect")
    dist("sharpness_measure", "{:.0f}", "beta = +0.0019; also the blur indicator — "
                                        "open the lowest few to set a floor")
    dist("average_saturation", "{:.0f}", "beta = -0.0018, NEGATIVE")
    dist("auto_bbox_pct", "{:.0f}", "not in Study 1; needed because crop is an edit")
    dist("clipped", "{:.3f}", "fraction of blown or crushed pixels")
    if model is not None:
        hi = sum(1 for r in sample if (r.get("memory_score") or 0) >= .90)
        dist("memory_score", "{:.3f}", f"{hi} at or above 0.90 — no headroom for any edit")

    fl = Counter(x for r in sample for x in (r.get("flags") or "").split("|") if x)
    if fl:
        print("\nflags")
        for k, v in fl.most_common():
            print(f"  {k:<18} {v:>5}")

    # --- STEP 5: draw the contact sheets so you can check the cuts ---------
    diagnostic_dir = os.path.join(os.path.dirname(os.path.abspath(args.out_dir)), "diagnostics")
    os.makedirs(diagnostic_dir, exist_ok=True)
    def draw(group, rows):
        print(f"\n{group}")
        for key, lowest, opt, what in rows:
            p = os.path.join(diagnostic_dir, f"_sheet_{key}.png")
            edge = contact_sheet(measured, key, lowest, p, args.photo_dir)
            if edge is None:
                continue
            print(f"  {os.path.basename(p):<34} {what}")
            cur = cuts.get(opt.lstrip("-").replace("-", "_")) if opt else None
            where = f"; cut is at {cur[0]:g}" if cur else ""
            print(f"  {'':<34} 20th is at {edge:g}{where}")

    # the worst on each measurement, drawn from features measured
    draw("the worst 20 on each measurement",
         [("sharpness_measure",  True,  "--min-sharpness",  "blurriest first"),
          ("clipped",            False, "--max-clipped",    "most blown out first"),
          ("average_saturation", True,  "--min-saturation", "greyest first")])

    # Nothing is cut on these. A photograph already at the top of an
    # axis cannot be pushed further along it, so an edit that raises that axis
    # has nothing to do. 
    headroom = [("average_value", False, None, "brightest first—is there room to brighten these?"),
                ("auto_bbox_pct", False, None, "tightest framing first—is there room to crop closer?")]
    if model is not None:
        headroom.append(("memory_score", False, None,
                         "highest first—can any edit still move these?"))
    draw("headroom — nothing is cut on these, they are for your judgement", headroom)

    print("\nNext step is using AI to do further filter: dish category, people, text")



if __name__ == "__main__":
    main()
