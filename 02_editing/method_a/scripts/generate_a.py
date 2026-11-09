#!/usr/bin/env python3
"""
Method A: send each photograph and its instructions to FLUX.1 Kontext.

  A_guided   the photograph's instructions (instructions.csv), followed by a
             sentence that keeps the food the same (see "KEEP" below)
  A_study1   one fixed instruction built from Study 1 (see "STUDY1" below),
             followed by the same "KEEP" sentence
  A_empty    a blank instruction, as the baseline (Laiti et al., 2026)

"""

import argparse
import base64
import csv
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import cv2
import numpy as np
import requests

API = "https://api.bfl.ai/v1"

KEEP = ("Keep the food itself exactly the same: the same dish, the same "
        "ingredients, the same portion and arrangement. Do not add any new "
        "objects, garnish or text.")


# A_study1: the Study 1 features that can be edited without changing the dish and whose
# effect is at least 0.01 per SD in the restaurant sample (Table 2): total objects (fewer)
# and brightness (HSV value). 
STUDY1 = ("Remove only the non-food objects around the dish, such as cutlery, "
          "napkins, napkin holders, empty plates, pens, phones and empty "
          "wrappers, and make the whole photograph brighter. Every drink, sauce "
          "and seasoning, with its glass, cup or bottle, counts as food: keep "
          "them all, and keep every dish and side. Keep the cloths or placemats "
          "under the plates, and the same framing, camera angle, table and "
          "background.")

ARMS = ("A_guided", "A_study1", "A_empty")



def prompt_for(arm, actions):
    if arm == "A_empty":
        return " "  
    if arm == "A_study1":
        return STUDY1 + " " + KEEP                       
    return " ".join(a.rstrip(".") + "." for a in actions) + " " + KEEP


def aspect(w, h):
    """Nearest simple ratio inside BFL's 3:7 .. 7:3 window, so the editor keeps
    the photograph's shape instead of re-framing it. see: https://docs.bfl.ai/guides/prompting_unified_technical#aspect-ratios"""
    cands = [(3, 7), (1, 2), (9, 16), (2, 3), (3, 4), (1, 1),
             (4, 3), (3, 2), (16, 9), (2, 1), (7, 3)]
    a, b = min(cands, key=lambda ab: abs(ab[0] / ab[1] - w / h))
    return f"{a}:{b}"


def as_json(r):
    try:
        return r.json()
    except ValueError:
        raise RuntimeError(f"{r.status_code} {r.text[:200]}")


def edit(key, model, path, prompt, seed, timeout=300):
    """One Kontext request. Returns (edited image as BGR array, request id,
    (width, height) of the original)."""
    with open(path, "rb") as f:
        raw = f.read()
    img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
    h, w = img.shape[:2]
    body = {"prompt": prompt,
            "input_image": base64.b64encode(raw).decode("ascii"),
            "aspect_ratio": aspect(w, h),
            "seed": int(seed),
            "prompt_upsampling": False,      # keep our prompt verbatim
            "safety_tolerance": 2,  # by default
            "output_format": "png"}
    hdr = {"accept": "application/json", "x-key": key, "Content-Type": "application/json"}
    sub = as_json(requests.post(f"{API}/{model}", headers=hdr, json=body, timeout=60))
    url, rid = sub.get("polling_url"), sub.get("id")
    if not url:
        raise RuntimeError(f"submit failed: {sub}")
    t0 = time.time()
    while True:
        time.sleep(1.5)
        js = as_json(requests.get(url, headers={"accept": "application/json", "x-key": key},
                                  timeout=30))
        status = js.get("status")
        if status == "Ready":
            break
        if status != "Pending":
            raise RuntimeError(f"{rid}: {status} {js.get('details') or ''}")
        if time.time() - t0 > timeout:
            raise RuntimeError(f"{rid}: still pending after {timeout}s")
    sample = (js.get("result") or {}).get("sample")
    blob = requests.get(sample, timeout=120)        # signed URL, valid ~10 minutes
    blob.raise_for_status()
    out = cv2.imdecode(np.frombuffer(blob.content, np.uint8), cv2.IMREAD_COLOR)
    if out is None:
        raise RuntimeError(f"{rid}: could not decode the returned image")
    return out, rid, (w, h)


def to_original_size(img, w, h):
    """Trim FLUX's larger output to the original's shape and shrink it to the
    original's size, so the original and the edited image are compared at the
    same size."""
    ih, iw = img.shape[:2]
    if iw / ih > w / h:
        nw = round(ih * w / h)
        img = img[:, (iw - nw) // 2:(iw - nw) // 2 + nw]
    else:
        nh = round(iw * h / w)
        img = img[(ih - nh) // 2:(ih - nh) // 2 + nh]
    return cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("photos", help="folder of the original photographs")
    ap.add_argument("--out", default="results_method_a")
    ap.add_argument("--instructions", default="../data/instructions.csv")
    ap.add_argument("--arms", nargs="+", default=list(ARMS), choices=ARMS)
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2, 3])
    ap.add_argument("--model", default="flux-kontext-pro")
    ap.add_argument("--limit", type=int, help="only the first N photographs (testing)")
    ap.add_argument("--workers", type=int, default=3, help="requests in parallel")
    ap.add_argument("--dry-run", action="store_true", help="print the prompts and stop")
    args = ap.parse_args()

    with open(args.instructions, encoding="utf-8") as f:
        actions = {r["photo"]: json.loads(r["actions"])["actions"] for r in csv.DictReader(f)}
    photos = sorted(os.path.join(r, f) for r, _, fs in os.walk(args.photos) for f in fs
                    if f.lower().endswith((".jpg", ".jpeg", ".png")))
    photos = [p for p in photos if os.path.splitext(os.path.basename(p))[0] in actions]
    if args.limit:
        photos = photos[:args.limit]
    if not photos:
        sys.exit(f"no photographs in {args.photos} match instructions.csv")

    jobs = []
    for p in photos:
        pid = os.path.splitext(os.path.basename(p))[0]
        for arm in args.arms:
            for seed in args.seeds:
                jobs.append((p, pid, arm, seed, prompt_for(arm, actions[pid])))

    if args.dry_run:
        for p, pid, arm, seed, prompt in jobs:
            if seed == args.seeds[0]:
                print(f"{pid} {arm}: {prompt!r}\n")
        print(f"{len(jobs)} requests would be sent to {args.model}")
        return

    key = os.environ.get("BFL_API_KEY", "")
    if not key:
        sys.exit("BFL_API_KEY is not set")
    for d in ("raw", "for_scoring"):
        os.makedirs(os.path.join(args.out, d), exist_ok=True)
    log_path = os.path.join(args.out, "generation_log.jsonl")
    done = set()
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            done = {json.loads(l)["file"] for l in f if '"ok": true' in l}
    todo = [j for j in jobs if f"{j[1]}__{j[2]}_s{j[3]}.png" not in done]
    print(f"{len(jobs)} requests; {len(jobs) - len(todo)} already done; {len(todo)} to send "
          f"to {args.model} with {args.workers} in parallel")

    def run(job):
        p, pid, arm, seed, prompt = job
        name = f"{pid}__{arm}_s{seed}.png"
        t0 = time.time()
        rec = {"file": name, "photo": pid, "arm": arm, "seed": seed, "prompt": prompt,
               "model": args.model, "api": API, "prompt_upsampling": False,
               "safety_tolerance": 2,
               "time": datetime.now().isoformat(timespec="seconds")}
        try:
            img, rid, (w, h) = edit(key, args.model, p, prompt, seed)
            cv2.imwrite(os.path.join(args.out, "raw", name), img)
            cv2.imwrite(os.path.join(args.out, "for_scoring", name), to_original_size(img, w, h))
            rec.update(ok=True, request_id=rid, raw_size=f"{img.shape[1]}x{img.shape[0]}",
                       aspect_ratio=aspect(w, h), seconds=round(time.time() - t0, 1))
        except Exception as e:                              # keep going; log it
            rec.update(ok=False, error=str(e)[:300], seconds=round(time.time() - t0, 1))
        return rec

    n_ok = n_err = 0
    with ThreadPoolExecutor(args.workers) as ex, open(log_path, "a", encoding="utf-8") as log:
        for k, fut in enumerate(as_completed([ex.submit(run, j) for j in todo]), 1):
            rec = fut.result()
            log.write(json.dumps(rec, ensure_ascii=False) + "\n")
            log.flush()
            n_ok += rec["ok"]
            n_err += not rec["ok"]
            print(f"[{k}/{len(todo)}] {rec['file']}  "
                  + (f"ok {rec['seconds']}s" if rec["ok"] else f"ERROR {rec['error']}"),
                  flush=True)
    print(f"\n{n_ok} generated, {n_err} failed -> {args.out}/for_scoring")
    if n_err:
        print("Run the same command again to retry the failed ones.")


if __name__ == "__main__":
    main()
