#!/usr/bin/env python3
"""Percentiles of brightness, saturation and sharpness among food photographs.
The three features, with the same code as Study 1 (raw_picture_data_process.ipynb):
  brightness   mean of the OpenCV HSV "value" channel, 0-255
  saturation   mean of the OpenCV HSV "saturation" channel, 0-255
  sharpness    variance of the Laplacian of the grayscale image
"""
import argparse
import hashlib
import json
import os
import sys
import zipfile
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime

import cv2
import numpy as np

FEATURES = ["value", "saturation", "sharpness"]
EXTENSIONS = (".jpg", ".jpeg", ".png")

def measure_bytes(raw):
    """Study 1's feature code, with one change: the grayscale image for
    sharpness is converted from the colour image (cv2.cvtColor), as
    method_b.py must do for edited images, which exist only as pixels.
    """
    buf = np.frombuffer(raw, np.uint8)
    image = cv2.imdecode(buf, cv2.IMREAD_COLOR)
    if image is None:
        return None
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    return (float(np.mean(hsv[:, :, 2])), float(np.mean(hsv[:, :, 1])),
            float(cv2.Laplacian(gray, cv2.CV_64F).var()))


# each worker process opens the zip once
_ZIP = None


def _open_zip(path):
    global _ZIP
    _ZIP = zipfile.ZipFile(path)


def _measure_member(name):
    return measure_bytes(_ZIP.read(name))


def _measure_file(path):
    with open(path, "rb") as f:
        return measure_bytes(f.read())


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="folder or .zip file of food photographs")
    ap.add_argument("--sample", type=int, help="measure a random sample of N photographs")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                  "corpus_statistics", "corpus_percentiles.json"))
    args = ap.parse_args()

    src = args.source
    is_zip = src.lower().endswith(".zip")
    if not os.path.exists(src):
        sys.exit(f"not found: {src}")
    if is_zip:
        with zipfile.ZipFile(src) as z:
            items = sorted((i.filename, i.file_size) for i in z.infolist()
                           if i.filename.lower().endswith(EXTENSIONS)
                           and not os.path.basename(i.filename).startswith("._"))
    else:
        items = sorted((os.path.relpath(os.path.join(r, f), src), os.path.getsize(os.path.join(r, f)))
                       for r, _, fs in os.walk(src) for f in fs if f.lower().endswith(EXTENSIONS))
    if not items:
        sys.exit(f"no .jpg/.jpeg/.png photographs in {src}")
    n_found = len(items)
    if args.sample and args.sample < n_found:
        idx = np.random.default_rng(0).choice(n_found, args.sample, replace=False)
        items = [items[i] for i in sorted(idx)]

    # fingerprint: the list of photographs used, with their sizes
    h = hashlib.sha256()
    for name, size in items:
        h.update(f"{name.replace(os.sep, '/')}:{size}\n".encode())

    print(f"measuring {len(items):,} photographs with {args.workers} processes ...", flush=True)
    names = [n for n, _ in items]
    if is_zip:
        ex = ProcessPoolExecutor(args.workers, initializer=_open_zip, initargs=(src,))
        fn = _measure_member
    else:
        ex = ProcessPoolExecutor(args.workers)
        fn, names = _measure_file, [os.path.join(src, n) for n in names]
    rows = []
    with ex:
        for k, r in enumerate(ex.map(fn, names, chunksize=64), 1):
            if r is not None:
                rows.append(r)
            if k % 5000 == 0:
                print(f"  {k:,}/{len(names):,}", flush=True)
    if not rows:
        sys.exit("no photograph could be read")
    data = {name: np.array([r[i] for r in rows]) for i, name in enumerate(FEATURES)}

    print(f"\n{len(rows):,} photographs measured"
          + (f" (random sample of {n_found:,})" if len(items) < n_found else "")
          + (f"; {len(items) - len(rows)} unreadable" if len(items) > len(rows) else ""))
    pct, check = {}, {}
    for name in FEATURES:
        x = data[name]
        pct[name] = {f"P{p}": round(float(np.percentile(x, p)), 1) for p in (15, 50, 85)}
        print(f"  {name:<11} P15 {pct[name]['P15']:8.1f}   P50 {pct[name]['P50']:8.1f}"
              f"   P85 {pct[name]['P85']:8.1f}")
        if name in ("value", "saturation"):
            med = np.median(x)
            check[name] = {f"{int(f * 100)}%": round(float((x < min(med * f, 255)).mean() * 100))
                           for f in (0.7, 1.3)}
    print("the grid's end levels (70 % and 130 %) applied to a median photograph land at:")
    for name, v in check.items():
        print(f"  {name:<11} 70% -> P{v['70%']}   130% -> P{v['130%']}")

    info = {"source": os.path.basename(os.path.abspath(src)),
            "source_fingerprint": h.hexdigest(),
            "photographs_found": n_found,
            "sample": len(items) if len(items) < n_found else None,
            "n": len(rows), "unreadable": len(items) - len(rows),
            "computed": datetime.now().isoformat(timespec="seconds"),
            "percentiles": pct, "end_levels_on_median_photo": check}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
