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
├── modules/reference_hook_analysis   -> output/human_hook_observation.json + output/hook_frame_index.json
├── modules/viral_deconstruction      -> output/viral_pattern_card.json
├── modules/human_hook_generation     -> output/human_hook_card.json + output/generated_hooks/ai_human_hook.mp4
├── modules/product_script_rewrite    -> output/product_script_card.json
├── modules/asset_matching            -> output/shot_matching_plan.json
├── modules/video_rendering           -> output/final_video.mp4 + output/render_report.json
└── modules/publishing_copy_rewrite   -> output/publishing_copy_card.json
```

The stable products are the cards/plans. Treat these as the source of truth for debugging and iteration.

## Boundary Rules

- `reference_hook_analysis` only finds or best-effort downloads a single reference video, extracts the first seconds as frames/contact sheet, and writes visual observation JSON. It does not write product scripts or generate the AI hook.
- `viral_deconstruction` only extracts why a reference account/video works. It does not write the user's product script.
- `human_hook_generation` only detects/analyzes a真人出镜 opening hook, writes a text-to-video prompt, and optionally generates an opening AI human hook clip. The generated AI human clip is a silent reaction/gesture asset only: no speaking, no lip-sync, no baked-in subtitles, no readable text. The hook copy is added later by `video_rendering` as overlays/subtitles. It does not rewrite the product script or choose later product footage.
- `product_script_rewrite` only adapts a viral pattern card into product scripts. It does not choose footage.
- `asset_matching` only maps script beats to assets and identifies missing footage. It does not rewrite the core script.
- `video_rendering` only executes the approved shot plan and render assets. It does not re-decide content.
- `publishing_copy_rewrite` only writes TikTok title/caption/hashtags from the approved video, subtitles, product facts, and reference post copy. It does not change subtitles, cover, footage, or render outputs.

If a later module finds a problem from an earlier module, return a revision flag such as `needs_script_revision` with a clear reason. Do not silently rewrite another module's work.

## Operating Logic

Always preserve this order:

1. Reference hook frame analysis before human hook generation when a local reference video is available.
2. Competitor logic before product script.
3. Human hook analysis/generation before product script if the reference opens with a真人出镜 hook.
4. Product truth before creative imitation.
5. Shot matching before rendering.
6. Preview and QA before final export.

If direct TikTok access is blocked, continue from uploaded videos, screenshots, captions, transcripts, metadata, or manually supplied frame summaries.

TikTok download is best-effort through `yt-dlp` for a single video URL. Do not promise account-wide scraping or stable TikTok download behavior; fall back to uploaded reference videos or recordings when access fails.

When the user sends a TikTok reference link with a real person on camera and asks for an AI真人/AI human-style video, the workflow may use the local environment variable `AI_REAL_PERSON_VIDEO_API_KEY` from the repository root `.env.local`. Never hardcode or print the key in generated artifacts, logs, docs, or final replies. Keep `.env.local` ignored by Git.

For reference-video visual understanding, prefer `OPENAI_API_KEY` against the official OpenAI Responses API. Evolink keys must not be sent to the official OpenAI endpoint. If visual understanding should go through Evolink, configure an OpenAI-compatible Evolink endpoint with `EVOLINK_OPENAI_RESPONSES_ENDPOINT`, `EVOLINK_RESPONSES_ENDPOINT`, `EVOLINK_OPENAI_CHAT_COMPLETIONS_ENDPOINT`, `EVOLINK_CHAT_COMPLETIONS_ENDPOINT`, or `EVOLINK_OPENAI_BASE_URL`; then use `EVOLINK_API_KEY` or `AI_REAL_PERSON_VIDEO_API_KEY` against that endpoint only. The module should send extracted frames, not raw API keys or full secret-bearing env files.

When a generated AI human hook is used, treat it as a normal asset library clip named `ai_human_hook`. The final edit should use that generated opening clip first, then continue matching the rest of the script to the user's uploaded product footage. The visible hook sentence belongs in the render plan/caption overlay, not inside the generated video prompt as spoken dialogue.

### AI Human Hook Prompt Rule

For AI真人 text-to-video hooks, imitate the reference hook's reusable visual grammar, not its exact footage.

Always split the reference hook into:

- person type and role: student, creator, researcher, office worker, etc.
- facial expression: anxious, shocked, amused, skeptical, relieved, confessional, etc.
- body action: lean-in, cover mouth, eyebrow raise, glance to laptop, point to screen, pause, small hand gesture.
- atmosphere: messy study desk, late-night dorm, quiet office, casual creator bedroom, urgent submission mood, etc.
- scene and objects: laptop, notebook, desk lamp, paper, browser window, document, etc.
- framing: close-up selfie, medium close-up, over-desk creator shot, handheld phone angle.
- camera motion: subtle handheld shake, phone selfie drift, quick push-in, stationary desk shot.
- lighting and color feel: warm indoor, cool monitor glow, natural daylight, low-light study vibe.
- text safe area: where captions can be burned later without covering the face or key object.

Then convert the analysis into a Seedance prompt for a clean reaction clip:

```text
[original fictional person] + [scene] + [expression] + [small action] + [camera/framing] + [atmosphere] + [silent/no text/no lip-sync constraints]
```

Do not generate a clip that is one-to-one with the reference. Change at least 3 visible attributes such as face, outfit, room layout, props, lighting, camera distance, angle, or gesture timing. Keep the emotional function and hook rhythm, not the original person's identity, exact clothing, exact room, exact action sequence, or exact caption.

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

Use `references/viral-pattern-card.md`, `references/template-library.json`, and
`modules/viral_deconstruction/schema.json`.

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

Treat this module as a standard sub-skill with a strict output contract:

- It writes reusable template logic, not product scripts.
- It must identify `template_id`, `caption_logic`, `template_fingerprint`, `rewrite_boundaries`, and `evidence_gaps`.
- It should preserve the reference video's sentence roles, CTA position, punctuation rhythm, and result-proof structure.
- It should match known reference videos through `references/template-library.json` when the URL/account/template is recognized.
- If evidence is missing, it should say what is missing instead of inventing certainty.

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

For scripts adapted from a specific reference video, preserve the reference video's caption grammar and punctuation rhythm when it is safe. The script logic must come from `viral_pattern_card.caption_logic`, not from a product-specific hardcoded template. Literfy, Citely, and FigPad all follow the same rule:

```text
reference video/template -> caption_logic -> product-safe script
```

If the user sends a new TikTok URL, regenerate or update `viral_pattern_card` first. If the template is unchanged, reuse the same `caption_logic` for new product angles.

Common reference grammar examples:

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

Use `modules/publishing_copy_rewrite/schema.json` and the
`overseas-tiktok-publish-copywriting` skill for overseas TikTok caption,
hashtags, and pinned comment strategy.

Output:

```text
output/publishing_copy_card.json
output/publishing_copy_delivery.md
```

Independent runner:

```bash
python3 modules/publishing_copy_rewrite/run.py --input <publishing_copy_input.json> --out output/publishing_copy_card.json
```

Every final video delivery must include the matching cover image, captioned
video, recommended TikTok title, recommended caption, hashtags, pinned
comment, and keywords.
Do not leave publishing copy hidden only inside `product_script_card.json`.

Publishing copy must be grounded in:

- approved product facts
- the visible final video/subtitles
- reference TikTok post title, caption logic, CTA rhythm, and hashtag category
- reference TikTok caption/posting style and viral structure
- product compliance limits

The task is not to write marketing copy. It is to automatically deconstruct
viral publishing-copy structure from the reference TikTok video and generate
caption, hashtags, and pinned comment for overseas TikTok. The output must feel
like a real overseas creator post, not translated Chinese, homepage copy, or a
formal ad.

Do not simply reuse the product script title or script caption as the final
publishing title/caption. The publishing copy must classify the reference
post's publishing template type, summarize the title/caption pattern, then
rewrite that pattern around product truth. Product-specific safe directions:

- Literfy: paper discovery, saved sources, structured review starting point.
- Citely: source tracing, reference detail review, checking before relying.
- FigPad: scientific figure draft, editable/reviewable output, user detail checking.

For the Research Connect reference pattern:

```text
dont make the mistakes i did. Use this website now!!!
#research #phd #literaturereview #citation #researchpaper
```

preserve the regret/mistake warning, direct website CTA, and academic hashtag
cluster while replacing the action with the product-safe workflow shown in the
video.

For every publishing-copy run, include `template_type_summaries` covering the
main reusable posting formats: mistake/urgency CTA, how-to/easy-way,
pain-question solution, workflow-direct demo, and result reveal.

For overseas TikTok publishing copy, also include:

- product understanding: user pain, feature, visible result, emotional angle
- reference caption breakdown: hook type, structure, viral mechanism, reusable pattern, avoid list
- caption strategy: the best TikTok angle for the video
- at least 8 caption options: most viral, pain-point, curiosity, POV, soft-selling, comment-bait, save-worthy, direct conversion
- 3-6 relevant hashtags only: broad, niche, and product/use-case tags
- optional pinned comment for each option
- risk check: overpromise, ad tone, unrelated hashtags, close copying, weak hook

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
