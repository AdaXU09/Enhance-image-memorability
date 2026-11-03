# Codebook: Method B `candidates.csv`

One row per saved image: for each photograph, the original, Sidorov's nine
tools, the best three B1 edits and the B2 edit (14 rows). Written by
`method_b.py`; `merge_scores.py` adds the ViTMem columns. 

| Column | Meaning |
|---|---|
| `photo` | Photograph ID: the Yelp photo ID |
| `category` | Dish category: the sub-folder the photograph is in (e.g. `pizza`); empty if none |
| `candidate` | Name of this image: `original`, `sidorov_<tool>`, `B1_rank1`–`B1_rank3` or `B2` |
| `method` | `original`, `sidorov` (Sidorov's 2019 tools, one setting each), `B1` (search over the settings below) or `B2` (Study 1's direction applied directly) |
| `file` | Image file in `for_scoring/`: `<photo>__<candidate>.png` |
| `resmem` | Predicted memorability of this image (ResMem, 0–1) |
| `resmem_original` | ResMem of the original photograph |
| `d_resmem` | Change in ResMem: `resmem` − `resmem_original` (positive = more memorable) |
| `crop` | Fraction of each side kept, centred on the dish (1.0 = whole frame; B1: 1.0, 0.8 or 0.65; B2: the tightest crop that keeps the dish, at least 0.65) |
| `brightness` | Brightness multiplier applied, in % (100 = unchanged). B1: 70, 85, 100, 115 or 130. B2: where the rule stopped, 100–130 |
| `saturation` | Saturation multiplier applied, in % (100 = unchanged). B1: 70, 100 or 130. B2: where the rule stopped, 70–100 |
| `contrast` | Contrast change (0 = unchanged). B1: −20, 0 or +20. B2: always 0 |
| `sharpness` | B1: `blur`, `none` or `unsharp` (strength 1.2). B2: `unsharp gain <g>`, the strength used (0–1.2), or `none` |
| `f_value` | Brightness: mean HSV value (0–255) |
| `f_saturation` | Saturation: mean HSV saturation (0–255) |
| `f_sharpness` | Sharpness: variance of the Laplacian of the grayscale image (higher = sharper) |
| `clipped` | Share of pixels that are pure white or pure black (0–1) |
| `artifact_free` | 1 if the edit adds at most 2 percentage points of pure white or black pixels to the original, else 0 |
| `sidorov_reported_change` | Change in memorability that Sidorov (2019, Table 3) reports for this tool, for comparison |
| `rank` | B1 only: rank by ResMem among the artifact-free settings (1 = highest) |
| `reached_value` | B2 only: 1 if brightness reached its target (85th percentile of food photographs), else 0 |
| `reached_saturation` | B2 only: 1 if saturation reached its target (15th percentile), else 0 |
| `reached_sharpness` | B2 only: 1 if sharpness reached its target (85th percentile), else 0 |
| `vitmem` | Predicted memorability by ViTMem (0–1), an independent model |
| `d_vitmem` | Change in ViTMem: `vitmem` − ViTMem of the original |

For B2, `brightness` `saturation` and `sharpness` are the settings the rule stopped at: where the image reached its target (85th or 15th percentile of food photographs), or where it hit the grid’s limit (e.g. 130% brightness, 70% saturation) or the 2% white-or-black check. Whether each target was reached is in the column `reached_value`, `reached_saturation` and `reached_sharpness`.

The score of every B1 setting, not only the best three, is in
`grid_scores.csv`.
