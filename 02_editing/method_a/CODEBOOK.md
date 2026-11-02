# Codebook: Method A `candidates.csv`

One row per image: for each photograph, the original and every edited image
(3 versions × 4 seeds = 12). Written by `score_a.py`; `merge_scores.py` adds
the ViTMem columns.

| Column | Meaning |
| --- | --- |
| `photo` | Photograph ID: the Yelp photo ID |
| `category` | Dish category: the sub-folder the photograph is in (e.g. `pizza`); empty if none |
| `candidate` | Name of this image: `original`, or version and seed (e.g. `A_guided_s2`) |
| `method` | `original`, `A_guided` (the photograph's own instructions), `A_study1` (fixed instruction built from Study 1) or `A_empty` (blank instruction, the baseline) |
| `file` | Image file in `for_scoring/`: `<photo>__original.png` or `<photo>__<version>_s<seed>.png` |
| `resmem` | Predicted memorability of this image (ResMem, 0–1) |
| `resmem_original` | ResMem of the original photograph |
| `d_resmem` | Change in ResMem: `resmem` − `resmem_original` (positive = more memorable) |
| `f_value` | Brightness: mean HSV value (0–255) |
| `f_saturation` | Saturation: mean HSV saturation (0–255) |
| `f_sharpness` | Sharpness: variance of the Laplacian of the grayscale image (higher = sharper) |
| `seed` | FLUX seed, 0–3 |
| `model` | Image-editing model (`flux-kontext-pro`) |
| `prompt` | The exact instruction sent to FLUX (a single space for A_empty) |
| `request_id` | Black Forest Labs request ID, to trace the request |
| `rank` | Rank by ResMem among the four seeds of this photograph and version (1 = highest). Set before the human check; the final choice is in `final_selection.csv` |
| `vitmem` | Predicted memorability by ViTMem (0–1) |
| `d_vitmem` | Change in ViTMem: `vitmem` − ViTMem of the original |


