# Orchestrator

The main `tk-video-editor` skill is an orchestrator. It should preserve state, call modules in order, and save intermediate artifacts. It should not silently merge module responsibilities.

## Data Flow

```text
reference videos/account data
  -> viral_deconstruction
  -> output/viral_pattern_card.json

viral_pattern_card + product profile
  -> product_script_rewrite
  -> output/product_script_card.json

product_script_card + asset library
  -> asset_matching
  -> output/shot_matching_plan.json

shot_matching_plan + EDL/subtitles
  -> video_rendering
  -> output/final_video.mp4 + output/render_report.json
```

## Module Boundary Rules

- `viral_deconstruction` only extracts repeatable viral structures. It does not write product scripts.
- `product_script_rewrite` only adapts structures into product scripts. It does not select clips.
- `asset_matching` only maps script beats to assets. It does not rewrite the core script.
- `video_rendering` only executes the approved plan. It does not re-decide content.

If a later module finds a problem from an earlier module, it should set a revision flag and explain the reason rather than silently rewriting another module's output.

## Required Intermediate Files

- `output/viral_pattern_card.json`
- `output/product_script_card.json`
- `output/shot_matching_plan.json`
- `output/render_report.json`
- `output/final_video.mp4` when rendering is requested

## Independent Test Commands

Full orchestrated workflow:

```bash
python3 modules/orchestrator/run.py --input examples/full_workflow_input.json --output-dir output
```

Normalize old input first:

```bash
python3 modules/legacy_adapter/run.py --input <legacy_input.json> --out output/orchestrator_input.json
python3 modules/orchestrator/run.py --input output/orchestrator_input.json --output-dir output
```

Individual modules:

```bash
python3 modules/viral_deconstruction/run.py --input examples/account_data.json --out output/viral_pattern_card.json
python3 modules/product_script_rewrite/run.py --input examples/script_input.json --out output/product_script_card.json
python3 modules/asset_matching/run.py --input examples/matching_input.json --out output/shot_matching_plan.json
python3 modules/video_rendering/run.py --input output/shot_matching_plan.json --report-out output/render_report.json
```

Rendering from an EDL:

```bash
python3 modules/video_rendering/run.py --input output/shot_matching_plan.json --edl output/edl.json --video-out output/final_video.mp4 --report-out output/render_report.json --render
```
