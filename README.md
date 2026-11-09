# Editing food photographs to be more memorable

Code for the photo-editing study in *When Do Memorable Review Images Pay Off?
Evidence on Marketplace Evaluation and Valuation* (Xu, Yang & Lin). We edit
Yelp food photographs so that they are predicted to be more memorable.

The authors wrote the code together with Claude Opus 5.5 (Anthropic) and checked all of it.

## Selecting the photographs

1. **Download the data.** Get the Yelp Open Dataset from
   [Yelp](https://business.yelp.com/data/resources/open-dataset/). 
2. **Keep food photographs.** `01_preprocessing/01_food_photos/food_photos.py`
   copies the photographs labelled "food" in the dataset.
3. **Prefilter to about 1,000 candidates.**
   `01_preprocessing/02_prefilter/run_prefilter.ipynb` runs
   `01_preprocessing/02_prefilter/scripts/prefilter.py`. It drops photographs
   too small or too oddly shaped to crop, draws a random sample, and measures
   colour (HSV), sharpness, clipping, framing (an automatic estimate of how much of the image the foreground, usually the food, fills) and predicted memorability
   (ResMem). It rejects only technical defects (blur, clipping, near-greyscale
   images, collages and added borders) and duplicates. Output:
   `01_preprocessing/02_prefilter/results/pool_final.csv`.
4. **AI selection.** Give an AI model
   `01_preprocessing/03_photo_selection/photo_selection_prompt.docx` and the
   photographs listed in
   `01_preprocessing/02_prefilter/results/pool_final.csv`. It screens out photographs with people, text, collages, poor quality or no clear main dish, then picks a set spread across framing (how much of the image the main dish fills), complexity (how many non-main-dish objects are in view), dish categories and brightness, with dishes that are easy to tell apart; photographs with three or more dishes are kept to a minority. Outputs are in `01_preprocessing/03_photo_selection/AI_selection_run/`:
   `outputs/screening.csv`, `outputs/selected.csv`, `outputs/summary.txt` and
   the photographs in `selected/<category>/`.  The researcher then checked every selected photograph against the inclusion criteria. Photographs that failed are marked keep = 0 with a reason; photographs in the wrong category are given the right one in
   `change_to_folder` (new categories, e.g. `others`, are listed in
   `NEW_FOLDERS` at the top of the script). Decisions are in `manual_check.csv`.
   `apply_manual_check.py` then copies the kept photographs to
   `checked/<category>/` and lists them in `checked/checked.csv`.
5. **Development set.** `01_preprocessing/04_development_set/pick_dev.py`
   draws a smaller set of photographs that later is used to edit from `checked/checked.csv` (step 4), which covers the range of ResMem scores, framing and complexity, and as many dish categories as possible. Output: `01_preprocessing/04_development_set/results/development_photos/`.

## Editing the photographs

1. **Method B: rule-based edits** (`02_editing/method_b/`).
   `02_editing/method_b/scripts/corpus_percentiles.py` measures all food
   photographs from Step 2 once, to set target levels for brightness,
   saturation and sharpness. `02_editing/method_b/run_method_b.ipynb` then
   edits each photograph three ways: Sidorov's (2019) nine editing tools; B1 (grid search),
   a search over crop, brightness, saturation, contrast and sharpness; and B2 (study 1 rule),
   Study 1's direction applied directly. Outputs:
   `02_editing/method_b/results_method_b/candidates.csv`, the saved edits and
   their scores ([codebook](02_editing/method_b/CODEBOOK.md)), and
   `grid_scores.csv`, the ResMem score of every B1 setting.
2. **Method A: AI edits** (`02_editing/method_a/`). FLUX.1 Kontext edits each
   photograph with three instructions, four times each: the photograph's own
   instructions written by an LLM (A_guided), one fixed instruction built from
   Study 1 (A_study1), and a blank instruction as the baseline (A_empty).
   `02_editing/method_a/run_method_a.ipynb` runs every step. Output:
   `02_editing/method_a/results_method_a/candidates.csv`
   ([codebook](02_editing/method_a/CODEBOOK.md)).
3. **Independent check.** Where a method makes several versions of a photograph (Method A and B1), 
   it uses ResMem to pick the best, which inflates those ResMem gains. `scripts/score_vitmem.py` and 
   `scripts/merge_scores.py` in each method folder add ViTMem scores to each `candidates.csv`; compare the methods on ViTMem.
4. **Stimuli.** On the development set, the method whose gain is large and consistent across both models (ResMem and ViTMem) is chosen. Every edited image is checked by hand: it fails if the dish changes, any food or drink is removed or cropped out, or objects or text are added. Where the method makes several versions of a photograph (e.g. the four runs of each instruction in Method A), ResMem picks, among those that pass, the version it predicts as most memorable. Each original and its edited image are exported as a matched pair for the experiment.

Each method folder has its own README with more details and a list of required packages to run the script: `scripts/requirements.txt`.
