#!/usr/bin/env python3
"""
Score every saved image with ViTMem, the second memorability model as an independent check on ResMem's.
"""

import csv
import json
import os
import sys
from importlib.metadata import version


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    out = sys.argv[1]
    folder = os.path.join(out, "for_scoring")
    files = sorted(f for f in os.listdir(folder) if f.lower().endswith((".png", ".jpg")))
    if not files:
        sys.exit(f"no images in {folder}")

    from vitmem import ViTMem
    model = ViTMem()
    rows = []
    for i, f in enumerate(files, 1):
        rows.append({"file": f, "score": round(model(os.path.join(folder, f)), 6)})
        if i % 50 == 0 or i == len(files):
            print(f"  {i}/{len(files)}", flush=True)

    path = os.path.join(out, "vitmem_scores.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["file", "score"])
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(out, "vitmem_scores.meta.json"), "w", encoding="utf-8") as fh:
        json.dump({"model": "ViTMem (Hagen & Espeseth 2023)",
                   "weights": "huggingface.co/brainpriority/vitmem/"
                              "vitmem_base_patch16_224_miil_v1-f580d24a.pth",
                   "vitmem": version("vitmem"), "timm": version("timm"),
                   "torch": version("torch")}, fh, indent=2)
    print(f"wrote {path} ({len(rows)} images)")


if __name__ == "__main__":
    main()
