#!/usr/bin/env python3
"""
Add ViTMem scores to candidates.csv and print a summary for each method.
"""

import argparse
import csv
import os
import re
import sys

import numpy as np


def read_scores(path):
    scores = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            toks = [t.strip().strip('"\'') for t in re.split(r"[,\s;]+", line) if t.strip()]
            name = next((os.path.basename(t) for t in toks
                         if t.lower().endswith((".png", ".jpg", ".jpeg"))), None)
            num = None
            for t in toks:
                try:
                    v = float(t)
                except ValueError:
                    continue
                if 0.0 <= v <= 1.0:
                    num = v
            if name and num is not None:
                scores[name] = num
    return scores


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out")
    ap.add_argument("scores")
    ap.add_argument("--name", default="vitmem", help="column name for this model")
    a = ap.parse_args()
    out, name = a.out, a.name
    am = read_scores(a.scores)
    if not am:
        sys.exit(f"no 'filename score' pairs found in {a.scores}; check that each line has an image file name and a score between 0 and 1")
    label = {"vitmem": "ViTMem"}.get(name, name)

    path = os.path.join(out, "candidates.csv")
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    orig = {r["photo"]: am.get(r["file"]) for r in rows if r["candidate"] == "original"}
    missing = 0
    for r in rows:
        a, a0 = am.get(r["file"]), orig.get(r["photo"])
        r[name] = "" if a is None else round(a, 4)
        r["d_" + name] = "" if a is None or a0 is None else round(a - a0, 4)
        missing += a is None
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"merged {len(rows) - missing} of {len(rows)} candidates into {path}")
    if missing:
        print(f"  {missing} had no {label} score — check that it scored all of for_scoring/")

    def summary(sel, what):
        d_r = np.array([float(r["d_resmem"]) for r in sel])
        d_a = np.array([float(r["d_" + name]) for r in sel if r["d_" + name] != ""])
        if len(d_a) == 0:
            return
        print(f"  {what:<26} n={len(sel):<3} ResMem {d_r.mean():+.3f}   {label} {d_a.mean():+.3f}"
              f"   {label}>0 in {np.mean(d_a > 0):.0%}")

    labels = {"B1": "B1 search, best per photo", "B2": "B2 Study 1 rule",
              "A_guided": "A_guided best of seeds", "A_empty": "A_empty best of seeds"}
    pick = {}
    for m in labels:
        sel = [r for r in rows if r["method"] == m]
        if any(r.get("rank") for r in sel):
            sel = [r for r in sel if str(r.get("rank")).split(".")[0] == "1"]
        if sel:
            pick[m] = sel
    print(f"\nmean change from the original   (B1 and Method A were chosen by ResMem; so {label} is a comparison check)")
    for m, sel in pick.items():
        summary(sel, labels[m])

    def paired(a, b):
        if a not in pick or b not in pick:
            return
        da = {r["photo"]: float(r["d_" + name]) for r in pick[a] if r["d_" + name] != ""}
        db = {r["photo"]: float(r["d_" + name]) for r in pick[b] if r["d_" + name] != ""}
        common = sorted(set(da) & set(db))
        if len(common) >= 2:
            diff = np.array([da[p] - db[p] for p in common])
            print(f"  {a} - {b}   mean {diff.mean():+.4f}   {a} better in "
                  f"{int((diff > 0).sum())} of {len(common)}")

    print(f"\npaired, same photographs, {label}")
    paired("B2", "B1")
    paired("A_guided", "A_empty")
    tools = sorted({r["candidate"] for r in rows if r["method"] == "sidorov"})
    if tools:
        print("\nSidorov's tools")
    for tool in tools:
        summary([r for r in rows if r["candidate"] == tool], tool[8:])

    both = [(float(r["d_resmem"]), float(r["d_" + name])) for r in rows
            if r["method"] != "original" and r["d_" + name] != ""]
    if len(both) > 3:
        x, y = np.array(both).T
        print(f"\nResMem vs {label} change, all candidates: r = {np.corrcoef(x, y)[0, 1]:.2f}"
              "  (low r means the two models disagree on what an edit does)")


if __name__ == "__main__":
    main()
