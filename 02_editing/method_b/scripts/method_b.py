#!/usr/bin/env python3
"""
Method B: rule-based photo editing (no AI image generation).

Searches systematically over crop, brightness, saturation, contrast and
sharpness. It is reproducible and serves as the baseline for Method A.

Where the settings come from
  Directions   Study 1 (our paper on the economic value of image memorability):
               brighter, less saturated, sharper photographs with fewer objects
               have higher predicted memorability (estimated by ResMem).
  Grid         our choice: crop 100/80/65 %, -modulate brightness
               70/85/100/115/130 and saturation 70/100/130,
               -brightness-contrast 0,-20/0/+20, -blur 0x1.2 / none /
               -unsharp 0x1.5+1.2+0.02. 405 combinations, one of which leaves
               the photograph unchanged.
  Colourspace  brightness and saturation are changed in HSV, the space in
               which Study 1 measures them (ImageMagick calls it HSB).
  B2 targets   our choice: P85 of brightness, P15 of saturation, P85 of
               sharpness among real food photographs, computed once by
               corpus_percentiles.py and saved in corpus_percentiles.json,
               which this program reads.
  Artifacts    rule: remove candidates with visible artifacts. Automatic
               screen: an edit is rejected if it turns more than 2 % of the
               picture extra into pure white or pure black. Other artifacts
               (sharpening halos, blur from enlargement, unnatural colour) are
               checked by eye on the contact sheet.
  Operators    ImageMagick's formulas (see imops.py for the source of
               each), reimplemented in Python so ImageMagick need not be
               installed.

For every photograph this produces:
  sidorov   Sidorov's (2019) nine tools as in PHOTO_EDITING.m, one setting each
  B1        the grid on the whole frame (404 edited versions), best three by
            ResMem among those that pass the artifact pre-screen
  B2        no search: Study 1's direction applied directly. Crop tight to the
            dish, then raise brightness towards P85, lower saturation towards
            P15 and sharpen towards P85. Each adjustment stops early if it
            would pass the most extreme setting B1 tries (crop 0.65,
            brightness 130 %, saturation 70 %, sharpening gain/amount 1.2) or fail
            the artifact screen; the reached_* columns (1 = yes, 0 = no) record whether
            brightness, saturation and sharpness got to their target.

ResMem picks the B1 versions, so its score for them is flattered by the
picking. ViTMem scores everything afterwards (score_vitmem.py,
merge_scores.py); compare methods on ViTMem.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import os
import platform
import sys
import time
from datetime import datetime

import cv2
import numpy as np
from PIL import Image, ImageDraw

import imops
import sidorov

# ------------------------------------------------------------------- settings
AXES = ["crop", "brightness", "saturation", "contrast", "sharpness"]
IDENTITY = {"crop": 1.0, "brightness": 100, "saturation": 100, "contrast": 0,
            "sharpness": "none"}
GRIDS = {
    "full": {                                   
        "crop":       [1.0, 0.8, 0.65],         # fraction of each side kept
        "brightness": [70, 85, 100, 115, 130],  # -modulate B,100   (HSB)
        "saturation": [70, 100, 130],           # -modulate 100,S   (HSB)
        "contrast":   [-20, 0, 20],             # -brightness-contrast 0,C
        "sharpness":  ["blur", "none", "unsharp"],
    },
    "quick": {                                  # a subset, for a first test
        "crop":       [1.0, 0.8],
        "brightness": [100, 115],
        "saturation": [70, 100],
        "contrast":   [0, 20],
        "sharpness":  ["none", "unsharp"],
    },
}
# sharpness levels: "blur" = slight Gaussian blur; "unsharp" = sharpening by
# unsharp mask (see imops.unsharp_f); "none" = unchanged
BLUR_SIGMA = 1.2                                       # -blur 0x1.2
UNSHARP_SIGMA, UNSHARP_GAIN, UNSHARP_THRESHOLD = 1.5, 1.2, 0.02   # -unsharp 0x1.5+1.2+0.02: sigma, gain (sharpening strength), threshold

# P15 / P85 of real food photographs, for B2's targets. 
CORPUS: dict = {}
CORPUS_INFO: dict = {}
FEATURES = ["value", "saturation", "sharpness"]


def load_corpus(path):
    """Fill CORPUS from corpus_percentiles.json."""
    if not os.path.exists(path):
        sys.exit(f"{path} not found. Compute it once from the food photographs:\n"
                 f"    python scripts/corpus_percentiles.py food_photos.zip")
    with open(path, encoding="utf-8") as f:
        info = json.load(f)
    for k in FEATURES:
        CORPUS[k] = (info["percentiles"][k]["P15"], info["percentiles"][k]["P85"])
    CORPUS_INFO.update(info)



# Artifact pre-screen (rule: remove candidates with visible artifacts).
MAX_EXTRA_CLIPPED = 0.02   # reject an edit that turns more than 2 % of the picture extra into pure white or pure black

# Dish mask (where the dish is; used to centre crops and for Sidorov's background edits).
FEATHER_SIGMA = 8.0        # soften the mask's edge by 8 px, so background edits fade in instead of ending at a hard line


# ------------------------------------------------------------------- features
def features(rgb):
    """Study 1's three perceptual features, measured as in
    corpus_percentiles.py: HSV brightness and saturation as in Study 1;
    sharpness on a grayscale image converted from the colour image."""
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    return {"value": float(hsv[..., 2].mean()), "saturation": float(hsv[..., 1].mean()),
            "sharpness": float(cv2.Laplacian(gray, cv2.CV_64F).var())}


def clipped(rgb):
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    return float((g >= 252).mean() + (g <= 3).mean())


# ----------------------------------------------------------------- the edits
def load_rgb(path):
    with Image.open(path) as im:
        return np.asarray(im.convert("RGB"))


def dish_mask(rgb):
    """Where the dish is: GrabCut (OpenCV), told that a 2 % strip along each
    edge of the photograph is background and left to decide everything
    inside; the edge of the result is then softened by FEATHER_SIGMA.
    1 = dish, 0 = background."""
    h, w = rgb.shape[:2]
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    m = .02
    rect = (int(w * m), int(h * m), int(w * (1 - 2 * m)), int(h * (1 - 2 * m)))
    mask = np.zeros((h, w), np.uint8)
    cv2.setRNGSeed(0)                 # GrabCut is random without a fixed seed, here set seed=0
    try:
        cv2.grabCut(bgr, mask, rect, np.zeros((1, 65)), np.zeros((1, 65)), 4,
                    cv2.GC_INIT_WITH_RECT)
        fg = np.isin(mask, (cv2.GC_FGD, cv2.GC_PR_FGD)).astype(np.float32)
    except cv2.error:
        fg = np.zeros((h, w), np.float32)
    if fg.mean() < .02:                 # if area of the dish too small, GrabCut found nothing
        fg[:] = 1.0
    return np.clip(cv2.GaussianBlur(fg, (0, 0), FEATHER_SIGMA), 0, 1)


def crop_on_dish(rgb, mask, frac):
    """Keep `frac` of each side, same aspect ratio, with the window centred
    on the dish where the frame allows, then resize back to the
    original size. 
    """
    if frac >= 1.0:
        return rgb, mask
    h, w = rgb.shape[:2]
    ys, xs = np.nonzero(mask > .5)
    cy, cx = (ys.mean(), xs.mean()) if len(ys) else (h / 2, w / 2)
    nh, nw = round(h * frac), round(w * frac)
    y0 = int(round(min(max(cy - nh / 2, 0), h - nh)))
    x0 = int(round(min(max(cx - nw / 2, 0), w - nw)))
    r = cv2.resize(rgb[y0:y0 + nh, x0:x0 + nw], (w, h), interpolation=cv2.INTER_LANCZOS4)
    m = cv2.resize(mask[y0:y0 + nh, x0:x0 + nw], (w, h), interpolation=cv2.INTER_LINEAR)
    return r, m


def dish_crop_frac(mask, lo):
    """Smallest crop (not below `lo`) whose window, centred as in
    crop_on_dish, still contains the whole dish."""
    h, w = mask.shape
    ys, xs = np.nonzero(mask > .5)
    if not len(ys):
        return 1.0
    for frac in np.arange(lo, 1.0, 0.01):
        nh, nw = round(h * frac), round(w * frac)
        cy, cx = ys.mean(), xs.mean()
        y0 = min(max(cy - nh / 2, 0), h - nh)
        x0 = min(max(cx - nw / 2, 0), w - nw)
        if ys.min() >= y0 and ys.max() < y0 + nh and xs.min() >= x0 and xs.max() < x0 + nw:
            return round(float(frac), 2)
    return 1.0


def tone(x, b, s, c, sharp, gain=None):
    """Float RGB in [0, 1]. Order: -modulate, -brightness-contrast, then
    -blur or -unsharp (crop first, colour after)."""
    x = imops.modulate_hsb_f(x, b, s)
    x = imops.brightness_contrast_f(x, 0, c)
    if sharp == "blur":
        x = imops.blur_f(x, BLUR_SIGMA)
    elif sharp == "unsharp":
        x = imops.unsharp_f(x, UNSHARP_SIGMA, UNSHARP_GAIN if gain is None else gain,
                            UNSHARP_THRESHOLD)
    return x


def is_identity(p):
    return all(p[a] == IDENTITY[a] for a in AXES)


# ------------------------------------------------------------------------ B2
def _bisect(fn, lo, hi, target, increasing=True, steps=14):
    """v in [lo, hi] with fn(v) = target, fn monotone; an end if out of reach."""
    if increasing:
        if fn(hi) <= target:
            return hi
        if fn(lo) >= target:
            return lo
    else:
        if fn(hi) >= target:
            return hi
        if fn(lo) <= target:
            return lo
    for _ in range(steps):
        mid = (lo + hi) / 2
        if (fn(mid) < target) == increasing:
            lo = mid
        else:
            hi = mid
    return hi


def B2_edit(rgb, mask, grid):
    """Study 1's direction, pushed to the corpus percentile, limited to the
    grid's range and the artifact pre-screen. 
    """
    lo_crop = min(GRIDS["full"]["crop"])
    frac = dish_crop_frac(mask, lo_crop)
    base, _ = crop_on_dish(rgb, mask, frac)
    x = imops._f(base)
    small = cv2.resize(base, (base.shape[1] // 4, base.shape[0] // 4),
                       interpolation=cv2.INTER_AREA)
    xs = imops._f(small)
    f0 = features(base)
    v_t, s_t = CORPUS["value"][1], CORPUS["saturation"][0]
    b_max, s_min = max(grid["brightness"]), min(grid["saturation"])

    def feat(b, s, img=xs):
        return features(imops._u8(imops.modulate_hsb_f(img, b, s)))

    s_floor = min(CORPUS["saturation"][0], f0["saturation"])
    clip0 = clipped(rgb)                     # the original photograph, as for B1

    def clean_img(img):
        return clipped(imops._u8(img)) - clip0 <= MAX_EXTRA_CLIPPED

    def clean(b, s):
        return clean_img(imops.modulate_hsb_f(x, b, s))

    def largest_ok(ok, lo, hi):
        """Return the highest setting between lo and hi that passes the check ok.
        Example: the brightest setting that keeps every rule."""
        if ok(hi):
            return hi
        for _ in range(14):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if ok(mid) else (lo, mid)
        return lo

    b, s = 100.0, 100.0
    for _ in range(3):
        if f0["value"] < v_t:
            # brighten as far as possible while brightness stays at or below P85,
            # saturation stays at or above its floor, and the artifact check passes
            b = largest_ok(lambda v: (lambda f: f["value"] <= v_t and
                                      f["saturation"] >= s_floor)(feat(v, s))
                           and clean(v, s), 100.0, b_max)
        if f0["saturation"] > s_t:
            s = _bisect(lambda v: feat(b, v)["saturation"], s_min, 100.0, s_t)
    y = imops.modulate_hsb_f(x, b, s)
    gain = 0.0
    sh_t = CORPUS["sharpness"][1]
    if features(imops._u8(y))["sharpness"] < sh_t:
        sg, t = UNSHARP_SIGMA, UNSHARP_THRESHOLD
        gain = largest_ok(lambda g: (lambda im: features(imops._u8(im))["sharpness"] <= sh_t
                                     and clean_img(im))(imops.unsharp_f(y, sg, g, t)),
                          0.0, UNSHARP_GAIN)
        y = imops.unsharp_f(y, sg, gain, t)
    out = imops._u8(y)
    f = features(out)
    params = {"crop": frac, "brightness": round(b, 1), "saturation": round(s, 1),
              "contrast": 0, "sharpness": f"unsharp gain {gain:.2f}" if gain else "none"}
    reached = {"value": f["value"] >= v_t - 1 or f0["value"] >= v_t,
               "saturation": f["saturation"] <= s_t + 1 or f0["saturation"] <= s_t,
               "sharpness": f["sharpness"] >= sh_t * .98}
    return out, params, reached


# ------------------------------------------------------------------- scoring
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
                x = self.torch.stack([self.tf(Image.fromarray(a))
                                      for a in images[i:i + batch]])
                out += [float(v) for v in self.model(x).view(-1)]
        return out


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def label(im, text):
    im = Image.fromarray(im).copy()
    im.thumbnail((300, 300))
    canvas = Image.new("RGB", (300, im.height + 34), "white")
    canvas.paste(im, ((300 - im.width) // 2, 0))
    d = ImageDraw.Draw(canvas)
    for k, line in enumerate(text.split("\n")):
        d.text((4, im.height + 2 + 15 * k), line, fill="black")
    return canvas


def tag(p):
    short = {"crop": "crop", "brightness": "B", "saturation": "S", "contrast": "C",
             "sharpness": ""}
    return " ".join(f"{short[a]}{p[a]}" for a in AXES if p[a] != IDENTITY[a])


# ---------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="one photograph, or a folder (searched recursively)")
    ap.add_argument("--out", default="results_method_b")
    ap.add_argument("--corpus", default="corpus_statistics/corpus_percentiles.json",
                    help="percentiles written by corpus_percentiles.py")
    ap.add_argument("--grid", choices=GRIDS, default="full")
    ap.add_argument("--top", type=int, default=3,
                    help="B1 candidates kept per photograph (default 3)")
    args = ap.parse_args()
    load_corpus(args.corpus)
    print(f"B2 targets from {args.corpus} ({CORPUS_INFO.get('source', '?')}, "
          f"n = {CORPUS_INFO.get('n', '?'):,}): brightness P85 {CORPUS['value'][1]}, "
          f"saturation P15 {CORPUS['saturation'][0]}, sharpness P85 {CORPUS['sharpness'][1]}")

    # The input folder may hold the photographs directly or in one sub-folder
    # per food category (development_photos/pizza/xxx.jpg). The sub-folder name is kept as
    # the photograph's category and the outputs are filed the same way.
    if os.path.isdir(args.input):
        paths = sorted(os.path.join(r, f) for r, _, fs in os.walk(args.input) for f in fs
                       if f.lower().endswith((".jpg", ".jpeg", ".png")))
        root = args.input
    else:
        paths, root = [args.input], os.path.dirname(args.input)

    def category(path):
        rel = os.path.relpath(os.path.dirname(path), root)
        return "" if rel in (".", "") else rel.replace(os.sep, "/")

    if not paths:
        sys.exit(f"no photographs found in {args.input}")
    ids = [os.path.splitext(os.path.basename(p))[0] for p in paths]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        sys.exit(f"the same file name appears in two folders: {dup[:3]}")
    cats = sorted({category(p) for p in paths} - {""})
    if cats:
        print(f"categories: {', '.join(cats)}")

    os.makedirs(os.path.join(args.out, "for_scoring"), exist_ok=True)
    grid = GRIDS[args.grid]
    combos = [dict(zip(AXES, v)) for v in itertools.product(*(grid[a] for a in AXES))]
    n_B1 = sum(not is_identity(p) for p in combos)
    print(f"{len(paths)} photograph(s); grid '{args.grid}' = {len(combos)} points; "
          f"{n_B1 + 1 + len(sidorov.TOOLS)} candidates scored per photograph")

    print("loading ResMem ...", flush=True)
    score = ResMemScorer()

    grid_rows, cand_rows, sheet_rows = [], [], []
    t_all = time.time()
    for n, path in enumerate(paths, 1):
        t0 = time.time()
        pid = os.path.splitext(os.path.basename(path))[0]
        cat = category(path)
        pdir = os.path.join(args.out, cat, pid)              # out/<category>/<photo>/
        os.makedirs(pdir, exist_ok=True)
        rgb = load_rgb(path)
        mask = dish_mask(rgb)
        clip0 = clipped(rgb)
        s0 = score([rgb])[0]

        def save(name, img, method, params, s, extra=None):
            fn = f"{pid}__{name}.png"                     # PNG: no re-encoding loss
            Image.fromarray(img).save(os.path.join(pdir, fn))
            Image.fromarray(img).save(os.path.join(args.out, "for_scoring", fn))
            f = features(img)
            row = {"photo": pid, "category": cat, "candidate": name, "method": method,
                   "file": fn, "resmem": round(s, 4), "resmem_original": round(s0, 4),
                   "d_resmem": round(s - s0, 4),
                   **{a: params.get(a, "") for a in AXES},
                   **{"f_" + k: round(f[k], 1) for k in FEATURES},
                   "clipped": round(clipped(img), 4),
                   "artifact_free": int(clipped(img) - clip0 <= MAX_EXTRA_CLIPPED)}
            row.update(extra or {})
            cand_rows.append(row)

        save("original", rgb, "original", {}, s0)
        Image.fromarray((mask * 255).astype(np.uint8)).save(
            os.path.join(pdir, f"{pid}__dish_mask.png"))

        # --- Sidorov's nine, one setting each --------------------------------
        sid_imgs, sid_names = [], []
        for name, (fn, needs_map, _) in sidorov.TOOLS.items():
            sid_imgs.append(fn(rgb, mask) if needs_map else fn(rgb))
            sid_names.append(name)
        for name, img, s in zip(sid_names, sid_imgs, score(sid_imgs)):
            save(f"sidorov_{name}", img, "sidorov", {}, s,
                 {"sidorov_reported_change": sidorov.TOOLS[name][2]})

        # --- B1: the grid, whole frame ----------------------------------------
        crops = {c: crop_on_dish(rgb, mask, c) for c in grid["crop"]}

        last = {}

        def render(p):
            """Make the edited image for one grid combination p"""
            base, _ = crops[p["crop"]]
            key = (p["crop"], p["brightness"], p["saturation"])
            if last.get("key") != key:
                last["key"] = key
                last["x"] = imops.modulate_hsb_f(imops._f(base), p["brightness"],
                                                 p["saturation"])
            # then contrast and sharpness (100, 100 = brightness and saturation already done)
            return imops._u8(tone(last["x"], 100, 100, p["contrast"], p["sharpness"]))

        ranked = []
        batch = []

        def flush():
            for (p, img), s in zip(batch, score([b[1] for b in batch])):
                f, c = features(img), clipped(img)
                clean = c - clip0 <= MAX_EXTRA_CLIPPED
                grid_rows.append({"photo": pid, "category": cat, **p,
                                  "resmem": round(s, 4), "d_resmem": round(s - s0, 4),
                                  **{"f_" + k: round(f[k], 1) for k in FEATURES},
                                  "clipped": round(c, 4), "artifact_free": int(clean)})
                if clean:
                    ranked.append((s, p))
            batch.clear()

        for p in combos:
            if is_identity(p):
                continue
            batch.append((p, render(p)))
            if len(batch) >= 32:
                flush()
        if batch:
            flush()
        best = {}
        ranked.sort(key=lambda t: -t[0])
        for r, (s, p) in enumerate(ranked[:args.top], 1):
            img = render(p)
            save(f"B1_rank{r}", img, "B1", p, s, {"rank": r})
            if r == 1:
                best["B1"] = (img, s, p)

        # --- B2: Study 1's direction, no search -------------------------------
        img3, p3, reached = B2_edit(rgb, mask, GRIDS["full"])
        s3 = score([img3])[0]
        save("B2", img3, "B2", p3, s3,
             {f"reached_{k}": int(v) for k, v in reached.items()})
        best["B2"] = (img3, s3, p3)

        # --- one row of the contact sheet -------------------------------------
        tiles = [label(rgb, f"{(cat + ' / ') if cat else ''}{pid[:14]} original\nResMem {s0:.3f}")]
        for method in ("B1", "B2"):
            if method in best:
                img, s, p = best[method]
                t = tag(p) if method != "B2" else (f"crop{p['crop']} B{p['brightness']} "
                                                   f"S{p['saturation']}")
                tiles.append(label(img, f"{method}  {s - s0:+.3f}\n{t}"))
        i = sid_names.index("sharpening")
        d_sid = [r for r in cand_rows if r["candidate"] == "sidorov_sharpening"
                 and r["photo"] == pid][0]["d_resmem"]
        tiles.append(label(sid_imgs[i], f"Sidorov sharpening\n{d_sid:+.3f}"))
        sheet_rows.append(tiles)

        print(f"[{n}/{len(paths)}] {cat + '/' if cat else ''}{pid}: original {s0:.3f}"
              + "".join(f"  {m} {best[m][1] - s0:+.3f}" for m in best)
              + f"  (artifact-free grid points {len(ranked)}; {time.time() - t0:.0f}s)",
              flush=True)

    # ------------------------------------------------------------------ outputs
    def write_csv(name, rows):
        keys = []
        for r in rows:
            keys += [k for k in r if k not in keys]
        with open(os.path.join(args.out, name), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows({k: r.get(k, "") for k in keys} for r in rows)

    write_csv("candidates.csv", cand_rows)
    write_csv("grid_scores.csv", grid_rows)

    W = max(len(r) for r in sheet_rows) * 300
    H = sum(max(t.height for t in r) for r in sheet_rows)
    sheet, y = Image.new("RGB", (W, H), "white"), 0
    for r in sheet_rows:
        for k, t in enumerate(r):
            sheet.paste(t, (k * 300, y))
        y += max(t.height for t in r)
    sheet.save(os.path.join(args.out, "contact_sheet.jpg"), quality=92)

    
    import PIL, torch
    manifest = {
        "run": datetime.now().isoformat(timespec="seconds"),
        "command": " ".join(sys.argv),
        "grid_name": args.grid, "grid": grid,
        "corpus_percentiles": {k: {"P15": v[0], "P85": v[1]} for k, v in CORPUS.items()},
        "corpus": {k: CORPUS_INFO.get(k) for k in ("source", "source_fingerprint",
                                                   "photographs_found", "sample", "n")},
        "inputs": {os.path.relpath(p, root).replace(os.sep, "/"): sha256(p) for p in paths},
        "versions": {"python": platform.python_version(), "pillow": PIL.__version__,
                     "opencv": cv2.__version__, "numpy": np.__version__,
                     "torch": torch.__version__},
    }
    with open(os.path.join(args.out, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"\ndone in {time.time() - t_all:.0f}s -> {args.out}/")
    print("  contact_sheet.jpg   original | B1 | B2 | Sidorov sharpening")
    print("  candidates.csv      the 14 saved versions (original, B1 top 3, B2, Sidorov 9) per photograph: settings, features, ResMem")
    print("  grid_scores.csv     all 404 B1 versions per photograph: settings, features, ResMem")
    print("  <category>/<photo>/ the 14 saved images (original, B1 top 3, B2, Sidorov 9) and the dish mask")
    print("  for_scoring/        the same 14 images per photograph in one folder, for ViTMem\n")
    print("The ResMem gains printed above favour B1, because B1 was chosen by ResMem.")
    print("Next: run score_vitmem.py, then merge_scores.py, and compare the methods on ViTMem.")


if __name__ == "__main__":
    main()
