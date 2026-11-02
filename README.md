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
   colour (HSV), sharpness, clipping, framing and predicted memorability
   (ResMem). It rejects only technical defects: blur, clipping, near-greyscale
   images, collages and added borders. Output:
   `01_preprocessing/02_prefilter/results/pool_final.csv`.
4. **AI selection.** Give an AI model
   `01_preprocessing/03_photo_selection/photo_selection_prompt.docx` and the
   photographs listed in
   `01_preprocessing/02_prefilter/results/pool_final.csv`. It screens out
   photographs with people, text, collages or poor quality, then picks a set
   spread across framing, dish categories and complexity. Outputs are in
   `01_preprocessing/03_photo_selection/AI_selection_run/`:
   `outputs/screening.csv`, `outputs/selected.csv`, `outputs/summary.txt` and
   the photographs in `selected/<category>/`.
5. **Development set.** `01_preprocessing/04_development_set/pick_dev.py`
   draws a smaller set from Step 4 that covers a range of ResMem scores and as
   many dish categories as possible.

## Editing the photographs

1. **Method B: rule-based edits** (`02_editing/method_b/`).
   `02_editing/method_b/scripts/corpus_percentiles.py` measures all food
   photographs from Step 2 once, to set target levels for brightness,
   saturation and sharpness. `02_editing/method_b/run_method_b.ipynb` then
   edits each photograph three ways: Sidorov's (2019) nine editing tools; B1,
   a search over crop, brightness, saturation, contrast and sharpness; and B2,
   Study 1's direction applied directly. Output:
   `02_editing/method_b/results_method_b/candidates.csv` the saved edits and
   their scores ([codebook](02_editing/method_b/CODEBOOK.md)), and
   `grid_scores.csv`, the ResMem score of every B1 setting.
2. **Method A: AI edits** (`02_editing/method_a/`). FLUX.1 Kontext edits each
   photograph with three instructions, four times each: the photograph's own
   instructions written by an LLM (A_guided), one fixed instruction built from
   Study 1 (A_study1), and a blank instruction as the baseline (A_empty).
   `02_editing/method_a/run_method_a.ipynb` runs every step. Output:
   `02_editing/method_a/results_method_a/candidates.csv`
   ([codebook](02_editing/method_a/CODEBOOK.md)).
3. **Independent check.** Both methods choose the best among their edits with ResMem,
   which inflates their ResMem gains. `scripts/score_vitmem.py` and
   `scripts/merge_scores.py` in each method folder add ViTMem scores to each
   `candidates.csv`; compare the methods on ViTMem.
4. **Stimuli.** In Method A, every edited image is checked by hand. Finally, only one edited image is
   chosen per photograph, and each original and its edited image are exported
   as a matched pair for the experiment.

Each method folder has its own README with the details and a
`scripts/requirements.txt`.
