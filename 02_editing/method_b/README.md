# Method B: rule-based photo editing (no AI image generation)

Edit each food photograph with ordinary photo adjustments (crop, brightness, saturation, contrast, sharpness), search over them systematically, and use the result as a baseline for the AI-based Method A.

Each edited image is scored by two models that predict how memorable an image is: one is ResMem (used in Study 1), the other is ViTMem.

## The three kinds of edited image

| name | how it is made |
|---|---|
| **B1: search** | Every photograph is edited in all 405 combinations of five adjustments (3 crops × 5 brightness × 3 saturation × 3 contrast × 3 sharpness levels; see "Settings"). ResMem scores each combination; the three highest-scoring are kept. |
| **B2: Study 1 rule** | Each photograph is pushed in the direction Study 1 found more memorable: cropped tight to the dish, brighter, less saturated, sharper, up to the 85th / 15th percentile of real food photographs (see "Where B2's targets come from"). One image per photograph. |
| **Sidorov's tools ( reference** )| The nine fixed edits of Sidorov (2019), e.g. sharpening, grayscale, vignetting, one setting each, to check whether his findings hold for food photographs. |

## Files

Run the notebook and commands from the `method_b` folder. The development photographs are in the shared `../data/` folder.

| file | what it does |
|---|---|
| `run_method_b.ipynb` | the notebook that runs method B, step by step |
| `scripts/method_b.py` | the main program: for each photograph, makes the B1, B2 and Sidorov edits, scores them with ResMem, saves the images and the result tables |
| `scripts/imops.py` | the photo adjustments (brightness, saturation, contrast, blur, sharpening). They follow ImageMagick, a widely used free image-editing program: its formulas are translated from ImageMagick's open-source code into Python, so ImageMagick does not have to be installed.|
| `scripts/corpus_percentiles.py` | run once, before the main program. Computes the 15th, 50th and 85th percentile of brightness, saturation and sharpness among real food photographs, which B2 uses as targets. Saves them in `corpus_statistics/corpus_percentiles.json` |
| `scripts/sidorov.py` | Sidorov's nine edits, translated from his published MATLAB code (`PHOTO_EDITING.m`) into Python, one function per edit. Two differences: his "clarity" uses a MATLAB function whose code is not public, so it is approximated; his background edits used a face-attention map, replaced here by an outline of the dish |
| `scripts/score_vitmem.py` | scores every saved image with the second model, ViTMem (see "Why two models") |
| `scripts/merge_scores.py` | adds the ViTMem scores to the results table and prints the summary: how much each method raised predicted memorability |
| `corpus_statistics/corpus_percentiles.json` | created by `scripts/corpus_percentiles.py`, read by `scripts/method_b.py`.|
| `../data/development_photos/` | the original development photographs, shared with Method A |
| `scripts/requirements.txt` | the Python packages to install |

## Where B2's targets come from

B2 moves each photograph towards the brightness, saturation and sharpness
that are high (85th percentile) or low (15th percentile) among real food
photographs. `scripts/corpus_percentiles.py` measures every photograph in a folder or
.zip file of food photographs with Study 1's feature code and saves the percentiles:

```
python scripts/corpus_percentiles.py food_photos.zip
```

`--sample 20000` measures a random sample instead, which is faster. The outputs are recorded in `corpus_statistics/corpus_percentiles.json`.

## Why two models

ResMem picks the B1 winner out of 404 edited versions. Its score for that
winner is therefore flattered by the picking itself. ViTMem took no part in the picking, so its score for the same image is an independent check. Report ViTMem's change for all methods.

## Run

```
pip install -r scripts/requirements.txt
python scripts/corpus_percentiles.py food_photos.zip   # once
python scripts/method_b.py one_photo.jpg --out results_test --grid quick   # a quick first check
python scripts/method_b.py ../data/development_photos --out results_method_b  # all development photographs
python scripts/score_vitmem.py results_method_b
python scripts/merge_scores.py results_method_b results_method_b/vitmem_scores.csv --name vitmem
```

The notebook run_method_b.ipynb does the same.

## Input and output folders

The input folder holds in one sub-folder per food category (`../data/development_photos/pizza/xxx.jpg`). The images are saved the same way: `<out>/<category>/<photo>/`. `for_scoring/` holds the same images in one folder, which is what ViTMem reads.

## Settings and where they come from


| setting | value | basis |
|---|---|---|
| which direction to edit | brighter, less saturated, sharper, fewer objects (tighter crop) | Study 1 (our paper on the economic value of image memorability) |
| crop | keep 100 / 80 / 65 % of each side, centred on the dish | our choice. 65 % is a tight crop that keeps the whole dish in development photographs; it already enlarges the image 1.54× |
| brightness | 70 / 85 / 100 / 115 / 130 % | our choice: two steps down, two up. `scripts/corpus_percentiles.py` reports where 70 % and 130 % put a photograph of median brightness among the photographs it measured (`end_levels_on_median_photo` in `corpus_statistics/corpus_percentiles.json`)| 
| saturation | 70 / 100 / 130 % | our choice: one step down, one up.|
| contrast | −20 / 0 / +20 | our choice: one moderate step each way|
| sharpness | slight blur / none / sharpen | our choice: one step each way.|
| B2 targets | 85th percentile of brightness, 15th of saturation, 85th of sharpness among real food photographs.| computed by `scripts/corpus_percentiles.py` within the range of real food photographs, following study 1's direction |
| artifact screen | An edit is rejected if it turns more than 2 % of the picture extra into pure white or pure black. | rule: remove candidates with visible artifacts; 2 % threshold: our choice |

Brightness and saturation are changed in the same colour space Study 1 uses to
measure them (HSV). Crops are centred on the dish, not on the middle of the picture, so a tight crop cannot
cut the dish off.

## Outputs

| file or folder | what it is |
|---|---|
| `contact_sheet.jpg` | one row per photograph: original, best B1, B2, Sidorov's sharpening |
| `candidates.csv` | every saved image: its settings, its measured brightness / saturation / sharpness and its scores |
| `grid_scores.csv` | all 404 combinations per photograph (404: the 405 grid combinations minus the one that leaves the photograph unchanged) with their ResMem scores, including those not saved |
| `manifest.json` | the settings, software versions and fingerprint of input file, for reproducibility |
| `<category>/<photo>/` | the saved images (PNG) and `<photo>__dish_mask.png`, a black-and-white image used to centre the crop on the dish|
| `for_scoring/` | the same images in one folder, for ViTMem |
