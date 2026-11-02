# Method A: written editing instructions, applied by FLUX.1 Kontext

For each food photograph, we used an LLM (Claude, Anthropic) to write short
instructions on how to make it more memorable. FLUX.1 Kontext, an AI image
editor, then applied them.

## Three versions

| name | instruction given to FLUX |
|---|---|
| **A_guided** | the photograph's corresponding instructions, plus a fixed sentence: keep the dish, ingredients, portion and arrangement the same; add no objects, garnish or text |
| **A_study1** | one fixed instruction for every photograph, built from Study 1: the features that can be edited without changing the dish and whose effect is at least 0.01 per SD in the restaurant sample (fewer objects, brighter). "Remove the non-food objects around the dish, such as cutlery, napkins, phones, bags and packaging, so that fewer objects are in the photograph, and make the whole photograph brighter. Keep the same framing and camera angle.", followed by the same fixed sentence |
| **A_empty** | a blank instruction: shows what FLUX changes on its own. It serves as a baseline. |

Each version is run four times per photograph, with seeds 0–3.

## Where the instructions come from
We follow the zero-shot protocol of Laiti et al. (2026, CVPR): the model sees
the photograph and is asked "Determine the actions required to improve the
memorability of this image", answering with a short list of actions. Claude
(`claude-opus-5-5`) wrote them without seeing any memorability score.

Laiti et al.'s own model, MemCoach, was not used: it was built on portrait
photographs, and its suggestions are mostly about posing. 

`../data/instructions.csv` holds the instructions for our development photographs.
For other photographs, ask an LLM the same question for each photograph and
add one row per photograph: `photo` (file name without extension) and
`actions` (e.g. `{"actions": ["Crop closer to the plate", "Brighten the lighting"]}`).

## Files

Run the notebook from the `method_a` folder so that its relative paths resolve correctly.

| file | what it does |
|---|---|
| `run_method_a.ipynb` | the notebook that runs everything, step by step |
| `../data/development_photos/` | the original development photographs |
| `../data/instructions.csv` | the instructions for our development photographs (see "Where the instructions come from") |
| `scripts/generate_a.py` | sends each photograph and its instruction to FLUX.1 Kontext; saves the edited images |
| `scripts/score_a.py` | scores originals and edited images with ResMem, measures brightness, saturation and sharpness; writes `candidates.csv`, `contact_sheet.jpg` (all photographs at a glance: original, the four A_guided versions, the best A_study1 and the best A_empty) and `review.csv`, a table to fill in during the human check |
| `scripts/score_vitmem.py` | scores the same images with ViTMem |
| `scripts/merge_scores.py` | adds the ViTMem scores to the results table and prints a summary |
| `scripts/review_sheets.py` | one page per photograph: the original and all twelve edited versions (3 versions × 4 seeds), for the human check |
| `scripts/select_a.py` | removes the versions rejected in `review.csv` and picks one per photograph |
| `scripts/export_stimuli.py` | saves each original and its chosen edited version as a matched pair for the experiment |
| `scripts/requirements.txt` | the Python packages to install |

## How the edited image is chosen

1. **Human check.** `scripts/score_a.py` writes `review.csv` in the results folder,
   one row per edited image. On the review sheets, compare each edited image
   with its original, and record your decision in `review.csv`: to reject
   an edited image, put 1 in its `reject` column and a short reason in
   `reason`; leave `reject` empty to keep it. Reject it if the dish,
   ingredients or portion changed, objects or text were added, it has visible
   defects, or it no longer looks like a real food photograph. Save
   `review.csv` (as CSV) before running `scripts/select_a.py`.
2. **Pick.** Among the edited images that pass, the one with the highest
   ResMem score is chosen.

ResMem did the picking, so its score for the chosen image would be inflated.
ViTMem is served as an indepdent check.

## FLUX settings

`flux-kontext-pro`; the instruction is sent word for word (`prompt_upsampling`
off); `safety_tolerance` 2; PNG output; output shape matched to the
photograph. Each request's id, seed and instruction are in
`generation_log.jsonl`.

## Folders

| folder | what it holds |
|---|---|
| `raw/` | FLUX's output as returned |
| `for_scoring/` | the same images cropped to the original's shape and size, plus the originals; everything is scored and reviewed from here |
| `review_sheets/` | one page per photograph, for the human check |
| `final/<category>/` | the chosen edited image for each photograph; details in `final_selection.csv` |
| `stimuli/<category>/` | each original and its chosen edited version as a matched pair, both PNG, same size; `stimuli.csv` lists their scores, brightness, saturation and sharpness |


The stimuli use the edited images in `for_scoring/` (same size as the original), not the larger FLUX output in `raw/`, so the edited image cannot look sharper just because it has more pixels. 

## Re-running

`scripts/generate_a.py` skips any request already listed as successful in
`generation_log.jsonl`, so an interrupted run can simply be started again.
It recognises a request by file name only (photo, version, seed), not by
instruction or model. To start afresh, or after changing the instructions or
the model, use a new results folder (`OUT` in the notebook)，or delete the
old one first.
