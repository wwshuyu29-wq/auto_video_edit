---
name: tk-video-editor
description: "Use as the orchestrator for TikTok short-video workflows: deconstruct viral references into viral pattern cards, rewrite product-native scripts, match footage to script beats, and render captioned vertical videos."
---

# TK Video Editor

## Purpose

Use this skill when the user wants a repeatable TikTok/TK short-video workflow for competitor teardown, product script rewriting, footage matching, automated editing, captions, and batch creative variants.

This skill is the orchestrator. It coordinates modules and preserves intermediate artifacts. It should not silently combine the thinking steps.

## Core Architecture

```text
tk-video-editor orchestrator
├── modules/orchestrator              -> coordinates all module outputs
├── modules/viral_deconstruction      -> output/viral_pattern_card.json
├── modules/product_script_rewrite    -> output/product_script_card.json
├── modules/asset_matching            -> output/shot_matching_plan.json
├── modules/video_rendering           -> output/final_video.mp4 + output/render_report.json
└── modules/publishing_copy_rewrite   -> output/publishing_copy_card.json
```

The stable products are the cards/plans. Treat these as the source of truth for debugging and iteration.

## Boundary Rules

- `viral_deconstruction` only extracts why a reference account/video works. It does not write the user's product script.
- `product_script_rewrite` only adapts a viral pattern card into product scripts. It does not choose footage.
- `asset_matching` only maps script beats to assets and identifies missing footage. It does not rewrite the core script.
- `video_rendering` only executes the approved shot plan and render assets. It does not re-decide content.
- `publishing_copy_rewrite` only writes TikTok title/caption/hashtags from the approved video, subtitles, product facts, and reference post copy. It does not change subtitles, cover, footage, or render outputs.

If a later module finds a problem from an earlier module, return a revision flag such as `needs_script_revision` with a clear reason. Do not silently rewrite another module's work.

## Operating Logic

Always preserve this order:

1. Competitor logic before product script.
2. Product truth before creative imitation.
3. Shot matching before rendering.
4. Preview and QA before final export.

If direct TikTok access is blocked, continue from uploaded videos, screenshots, captions, transcripts, metadata, or manually supplied frame summaries.

## Workflow

### 1. Intake

Collect only what is needed for the current stage:

- Competitor account URLs or viral video URLs.
- Reference video files, screenshots, captions, transcripts, or frame summaries.
- Product name, category, target user, features, pain points, proof points, forbidden claims, offer, and CTA.
- Footage folder or `asset_library` JSON.
- Desired output count, duration, language, subtitle style, and export format.

Do not force all questions at once if the next stage can proceed.

For a full workflow input JSON, run:

```bash
python3 modules/orchestrator/run.py --input examples/full_workflow_input.json --output-dir output
```

For older or loose input shapes, normalize first:

```bash
python3 modules/legacy_adapter/run.py --input <legacy_input.json> --out output/orchestrator_input.json
python3 modules/orchestrator/run.py --input output/orchestrator_input.json --output-dir output
```

### 2. Viral Deconstruction

Use `references/viral-pattern-card.md` and `modules/viral_deconstruction/schema.json`.

Input: account/video evidence.

Output:

```text
output/viral_pattern_card.json
```

Independent runner:

```bash
python3 modules/viral_deconstruction/run.py --input <account_data.json> --out output/viral_pattern_card.json
```

The card must answer why the video/account works, how the opening grabs attention, how the middle proves the tool, how the ending converts, what can be reused, and what cannot be copied.

For short-form reference videos with visible subtitles, always extract `caption_logic` before rewriting:

- exact visible subtitle sequence
- role of each subtitle line
- punctuation pattern such as `!`, `?`, parentheses, ellipses
- command verbs such as `Click`, `Type`, `Select`, `Generate`
- CTA placement and strength
- result-proof wording

Do not treat this as optional. Structure-level imitation is not enough for this workflow.

### 3. Product Script Rewrite

Use `references/product-script-card.md` and `modules/product_script_rewrite/schema.json`.

Input: `viral_pattern_card.json` plus product profile.

Output:

```text
output/product_script_card.json
```

Independent runner:

```bash
python3 modules/product_script_rewrite/run.py --input <script_input.json> --out output/product_script_card.json
```

The output should normally include three variants:

- `safe_version`: truthful, specific, lower-risk.
- `viral_version`: stronger hook, faster rhythm.
- `native_creator_version`: casual creator recommendation.

Write like a creator sharing a useful workflow, not like a product homepage.

For scripts adapted from a specific reference video, preserve the reference video's caption grammar and punctuation rhythm when it is safe:

- `How to ... like a PhD/Master student (The easy way)`
- `Just go to this website!`
- `Click ...`
- `Type ...`
- `Pro tip! ...`
- `Then ...`
- `It's done! let's see...`
- `[result proof]!`

Replace only the task, product actions, and result proof with product-fact-safe equivalents.

### 4. Footage Index

Use `references/material-library.md`.

Build an initial asset library:

```bash
python3 scripts/inventory_materials.py <footage_dir> --out output/material_index.json
```

If clips contain speech and `ELEVENLABS_API_KEY` is available:

```bash
python3 scripts/transcribe_batch.py <footage_dir> --edit-dir output
python3 scripts/pack_transcripts.py --edit-dir output
```

For visual drill-down:

```bash
python3 scripts/timeline_view.py <video> <start_seconds> <end_seconds> -o <out.png>
```

### 5. Asset Matching

Use `references/shot-matching-plan.md` and `modules/asset_matching/schema.json`.

Input: `product_script_card.json` plus `asset_library`.

Output:

```text
output/shot_matching_plan.json
```

Independent runner:

```bash
python3 modules/asset_matching/run.py --input <matching_input.json> --out output/shot_matching_plan.json
```

This step must explain why each clip supports each beat and list missing assets. Missing product-proof footage is a serious risk, not a minor note.

### 6. Rendering

Use `references/edit-plan-schema.md`, `references/external-video-skills.md`,
`modules/video_rendering/schema.json`, and the existing scripts.

For this workflow, prefer the PNG-caption preview path first. It does not rely
on FFmpeg `drawtext` or `subtitles` filters, so it works on Homebrew FFmpeg
builds without libass/freetype subtitle support:

```bash
python3 modules/video_rendering/run.py \
  --input output/shot_matching_plan.json \
  --asset-library output/asset_library.json \
  --preview-render \
  --preview-out output/preview.mp4
```

This generates `preview.mp4`, `preview_midpoint_sheet.jpg`, `captions.json`,
`master.srt`, and `render_report.json`.

If the local FFmpeg build supports libass/freetype subtitle filters, EDL render
can still be used for final compositing:

```bash
python3 scripts/plan_to_edl.py <shot_plan.json> -o output/edl.json
python3 modules/video_rendering/run.py --input output/shot_matching_plan.json --edl output/edl.json --video-out output/final_video.mp4 --report-out output/render_report.json --render
```

If subtitle burning is needed separately:

```bash
python3 scripts/burn_subtitles.py <video.mp4> <captions.srt> <output.mp4>
```

For low-level FFmpeg failures, consult `references/external-video-skills.md`
for the `ffmpeg-video-editor` boundary: use it for command diagnostics,
trimming, concat, codec, and subtitle-render troubleshooting only. Do not let
rendering troubleshooting change script claims, shot logic, or product facts.

### 7. Publishing Copy

Use `modules/publishing_copy_rewrite/schema.json`.

Output:

```text
output/publishing_copy_card.json
output/publishing_copy_delivery.md
```

Every final video delivery must include the matching cover image, captioned
video, recommended TikTok title, recommended caption, hashtags, and keywords.
Do not leave publishing copy hidden only inside `product_script_card.json`.

Publishing copy must be grounded in:

- approved product facts
- the visible final video/subtitles
- reference account caption logic and hashtag category
- product compliance limits

The tone should feel like TikTok creator workflow sharing, not homepage
advertising.

Do not simply reuse the product script title or script caption as the final
publishing title/caption. The publishing copy must rewrite the reference post's
caption logic. For the Research Connect reference pattern:

```text
dont make the mistakes i did. Use this website now!!!
#research #phd #literaturereview #citation #researchpaper
```

preserve the regret/mistake warning, direct website CTA, and academic hashtag
cluster while replacing the action with the product-safe workflow shown in the
video.

### 8. Local Storage Cleanup

Use `scripts/cleanup_project.py` after preview/final delivery batches to control local disk usage.

Always dry-run first:

```bash
python3 scripts/cleanup_project.py <project_dir> --mode normal
```

Only delete after reviewing the report:

```bash
python3 scripts/cleanup_project.py <project_dir> --mode normal --execute
```

Cleanup policy:

- Preserve original raw materials.
- Preserve structured decision files such as `viral_pattern_card.json`, `product_script_card.json`, `shot_matching_plan.json`, manifests, and delivery notes.
- Preserve covers and manifest-referenced outputs.
- Remove regenerable temp folders such as `preview_render`, `segments`, `overlays`, `qa_frames`, and `__pycache__`.
- In `normal` mode, remove older versioned preview artifacts when newer `_vN` files exist.
- Use `aggressive` only when the user explicitly wants extra cleanup of extracted reference frames/contact sheets.

### 9. QA

Before presenting final outputs:

- Check first 2 seconds for hook clarity.
- Check product claims against product facts and forbidden claims.
- Check whether script, visuals, and subtitle text support the same beat.
- Check cut boundaries for black flashes, audio pops, and awkward jumps.
- Verify vertical 9:16 unless otherwise requested.
- Append reusable learnings to `references/tiktok-ops-knowledge.md` and the project knowledge base.

### 10. Publishing Copy

Use `references/publishing-copy-card.md`, `references/external-video-skills.md`,
and `modules/publishing_copy_rewrite/schema.json`.

Input: final delivery variants, video subtitles, product facts, and the reference post caption.

Output:

```text
output/publishing_copy_card.json
```

Independent runner:

```bash
python3 modules/publishing_copy_rewrite/run.py --input <publishing_copy_input.json> --out output/publishing_copy_card.json
```

This module rewrites the competitor post copy into safe TikTok publishing metadata:

- title options
- recommended title
- caption options
- recommended caption
- hashtags
- posting notes
- compliance notes

It must preserve product truth and the user's delivery standard: final assets are cover image + captioned video, with TikTok trending music added inside TikTok.

For TikTok caption/title/hashtag inspiration, consult
`references/external-video-skills.md` for the `tiktok-captions` boundary: use
it only for publishing metadata after the video and subtitles are approved.
Product facts and forbidden claims always override platform-native phrasing.

## References

- `references/orchestrator.md`: module data flow and test commands.
- `references/viral-pattern-card.md`: viral deconstruction output contract.
- `references/product-script-card.md`: product script output contract.
- `references/product-facts.md`: user-provided product facts and claim boundaries.
- `references/shot-matching-plan.md`: asset matching output contract.
- `references/material-library.md`: how to index and label handheld footage.
- `references/edit-plan-schema.md`: shot table and render EDL requirements.
- `references/publishing-copy-card.md`: TikTok title, caption, and hashtag output contract.
- `references/external-video-skills.md`: evaluated external video/caption skills and how they can safely influence this project.
- `references/tiktok-ops-knowledge.md`: accumulated operating patterns from analyzed TK reference videos.
- `references/reflection-first-run.md`: mistakes and fixes from the first Literfy run.
- `references/source-skills.md`: upstream skills and what was borrowed.

## Scripts And Modules

Modules:

- `modules/orchestrator/run.py`
- `modules/legacy_adapter/run.py`
- `modules/viral_deconstruction/run.py`
- `modules/product_script_rewrite/run.py`
- `modules/asset_matching/run.py`
- `modules/video_rendering/run.py`

Copied/adapted helper scripts:

- `render.py`, `timeline_view.py`, `grade.py`, `transcribe.py`, `transcribe_batch.py`, `pack_transcripts.py` from `browser-use/video-use`.
- `clip_video.py`, `burn_subtitles.py`, `utils.py` from `op7418/Youtube-clipper-skill`.

Local helper scripts:

- `inventory_materials.py`: build a metadata index for a footage directory.
- `plan_to_edl.py`: validate a shot plan and emit render-compatible EDL JSON.
- `make_srt.py`: generate SRT from timed caption JSON.
