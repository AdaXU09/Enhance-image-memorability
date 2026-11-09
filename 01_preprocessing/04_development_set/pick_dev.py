"""Select development images from the manually checked photographs.

Sort images by memorability score and divide them into three equal-sized
groups: low, middle and high. Select TARGET_N images in total, split 
as evenly as possible across the three memorability groups, 
while balancing food categories, framing, complexity and scores.

Usage:
    python pick_dev.py

By default, checked.csv and the images are read from 03_photo_selection/checked,
and memorability scores from 02_prefilter/results/pool_final.csv. 
Override the two CSV paths (checked.csv first, then pool_final.csv) as positional arguments if needed.

Images and metadata are saved in results/ beside this script by default.
Use --image-dir and --output-dir to change the image directories.
"""
import argparse
import shutil
from pathlib import Path

import pandas as pd

TARGET_N = 20
SCRIPT_DIR = Path(__file__).resolve().parent
PREPROCESSING_DIR = SCRIPT_DIR.parent
CHECKED_DIR = PREPROCESSING_DIR / "03_photo_selection" / "checked"
PREFILTER_RESULTS = PREPROCESSING_DIR / "02_prefilter" / "results"

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("sel_csv", nargs="?", type=Path, default=CHECKED_DIR / "checked.csv")
parser.add_argument("pool_csv", nargs="?", type=Path, default=PREFILTER_RESULTS / "pool_final.csv")
parser.add_argument("--image-dir", type=Path,
                    default=CHECKED_DIR,
                    help="Source image directory with category subfolders or flat images (default: 03_photo_selection/checked)")
parser.add_argument("--output-dir", type=Path, default=SCRIPT_DIR / "results" / "development_photos",
                    help="Destination root; images go in category subfolders (default: results/development_photos beside this script)")
args = parser.parse_args()
sel_csv, pool_csv = args.sel_csv, args.pool_csv
sel = pd.read_csv(sel_csv)
pool = pd.read_csv(pool_csv)

d = (sel.merge(pool[["filename", "memory_score"]], on="filename")
        .sort_values(["memory_score", "filename"]).reset_index(drop=True))
d["framing"] = pd.qcut(d["main_dish_bbox_pct"].rank(method="first"), 4,
                       labels=["Q1", "Q2", "Q3", "Q4"]).astype(str)
d["mem_third"] = pd.qcut(d["memory_score"].rank(method="first"), 3,
                         labels=["low", "mid", "high"]).astype(str)
d["complexity"] = d["complexity"].astype("string").str.strip().str.lower()
bad = d.loc[~d["complexity"].isin(["simple", "medium", "complex"]), "filename"].tolist()
if bad:
    raise ValueError(f"Complexity missing or not simple/medium/complex for: {bad}")

if len(d) < TARGET_N:
    raise ValueError(f"Need at least {TARGET_N} matched photographs; found {len(d)}.")

per_third, remainder = divmod(TARGET_N, 3)
quota = {third: per_third + (i < remainder)
         for i, third in enumerate(("low", "mid", "high"))}
chosen = []
for third, k in quota.items():
    pool_t = d[d["mem_third"] == third]
    picked = []
    while len(picked) < k:
        cats = {r["category"] for r in chosen}
        fr = pd.Series([r["framing"] for r in chosen]).value_counts()
        cx = pd.Series([r["complexity"] for r in chosen]).value_counts()
        best, best_key = None, None
        for _, r in pool_t.iterrows():
            if r["filename"] in {p["filename"] for p in picked}:
                continue
            gap = min((abs(r["memory_score"] - p["memory_score"]) for p in picked),
                      default=1.0)
            ncat = sum(1 for c in chosen if c["category"] == r["category"])
            key = (r["category"] not in cats, -ncat,
                   -fr.get(r["framing"], 0), -cx.get(r["complexity"], 0), gap)
            if best_key is None or key > best_key:
                best, best_key = r, key
        picked.append(best)
        chosen.append(best)

cols = ["filename", "category", "memory_score", "mem_third", "framing",
        "main_dish_bbox_pct", "complexity", "n_dishes", "note"]
out = pd.DataFrame(chosen)
out = out[[c for c in cols if c in out]]
sources = []
for filename, category in zip(out["filename"], out["category"]):
    source = args.image_dir / category / filename
    if not source.is_file():
        source = args.image_dir / filename
    sources.append(source)
missing = [str(source) for source in sources if not source.is_file()]
if missing:
    raise FileNotFoundError("Selected images were not found:\n" + "\n".join(missing))
if args.image_dir.resolve() == args.output_dir.resolve():
    raise ValueError("The source and destination image directories must differ.")
if args.output_dir.exists() and any(args.output_dir.iterdir()):
    raise ValueError(f"{args.output_dir} is not empty; move or delete the old development photos first.")
args.output_dir.mkdir(parents=True, exist_ok=True)
for source, category in zip(sources, out["category"]):
    category_dir = args.output_dir / category
    category_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, category_dir / source.name)
out_csv = args.output_dir.parent / "development_photos.csv"
out.to_csv(out_csv, index=False)
print(out.to_string(index=False))
print()
print("categories:", out["category"].nunique(), dict(out["category"].value_counts()))
print("framing:   ", dict(out["framing"].value_counts().sort_index()))
print("complexity:", dict(out["complexity"].value_counts().sort_index()))
if "n_dishes" in out:
    print("n_dishes:  ", dict(out["n_dishes"].astype(str).value_counts().sort_index()))
print("memory:     min %.3f  max %.3f" % (out.memory_score.min(), out.memory_score.max()))
print(f"Saved {len(out)} photographs to {out_csv}")
print("Copied %d images to: %s" % (len(sources), args.output_dir.resolve()))
