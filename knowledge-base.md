# TK Video Operations Knowledge Base

This is the growing operating knowledge base for TikTok/TK competitor teardown, script rewriting, and storyboard planning.

## Source: research.connect

Account: https://www.tiktok.com/@research.connect

### Core Account Pattern

The account repeatedly uses a familiar academic website or academic document as the first-frame trust object, then adds a bold subtitle hook promising an easier or smarter academic workflow.

Core formula:

```text
Familiar academic interface
+ high-status academic identity
+ easy/smart/legit shortcut
+ product/tool reveal
+ visible proof output
```

### Google Scholar Cover Pattern

Visual:

- Handheld laptop/tablet screen.
- Google Scholar homepage or academic-search-like page.
- White page, visible browser chrome, imperfect angle.
- Slight blur, screen glare, moire, or off-center framing is acceptable and can increase native feel.

Subtitle style:

- Centered or slightly below center.
- Bold white text with black outline.
- 3-5 short lines.
- No decorative graphics.
- Hook readable in under 2 seconds.

Hook formulas:

```text
How to write your [academic output] like a [PhD/Master/Harvard-level identity]
([easy/smart/legit] way)

Still using [old tool/workflow] to [academic task]?

Stop using [generic AI/tool] for [academic task]. Do this instead.
```

### Video 7633832153922489621

URL: https://www.tiktok.com/@research.connect/video/7633832153922489621

Visible caption sequence:

1. "How to write your thesis paper like a PhD/Master student (The easy way)"
2. "Just go to this website!"
3. "Click researcher"
4. "Type your research paper topic"
5. "Pro tip! use latex for pdfs"
6. "Then watch it do its magic in 2-3 mins"
7. "Its done! lets see..."
8. "A complete research paper!"
9. "With meaningful visualizations!"

Operational lesson:

This video does not sell Google Scholar directly. It uses Google Scholar as a trust doorway, then redirects the viewer to the product. The product proof is visual: generated paper pages, structured sections, and charts.

Reusable storyboard:

```text
0-3s: Academic trust object + status-upgrade hook
3-6s: "Go to this website" product reveal
6-10s: Click the relevant mode
10-13s: Enter the user's academic task/topic
13-16s: Show one expert/pro setting
16-19s: Promise short processing time
19-23s: Reveal completed academic output
23-27s: Show bonus proof such as citations, charts, tables, or visualizations
```

### Adaptation Rules

- Start from a real user pain: thesis, RRL, literature review, finding papers, citations, synthesis, summaries.
- Use academic identity gap carefully: "PhD/Master way" means better workflow, not guaranteed academic quality.
- Every claim must map to a product feature.
- End with visible proof. Do not end on abstract copy.
- If using Google Scholar visuals, avoid implying partnership or official affiliation.

## Future Entries

Append new teardown notes here whenever a new reference video or account is analyzed.

## Workflow Lessons From First Literfy Run

### Problem 1: Structure-Level Imitation Was Not Enough

Initial script rewriting copied the broad structure of the reference video but did not sufficiently imitate the sentence-level subtitle logic.

Required fix:

- Extract the reference video's exact caption grammar before rewriting.
- Preserve the role of each sentence:
  - `How to ... like a PhD/Master student (The easy way)`
  - `Just go to this website!`
  - `Click ...`
  - `Type ...`
  - `Pro tip! ...`
  - `Then ...`
  - `It's done! let's see...`
  - result proof with `!`
- Reuse rhythm, punctuation, and short-command style without copying unsupported claims.

### Problem 2: CTA Beat Needs Its Own Visual

The second line in the reference video is a strong CTA and should map to a landing page or public website, not a later product proof screen.

Required fix:

- `strong_cta` should prefer landing page / homepage / website reveal assets.
- Dashboard or internal workflow clips should be used for `Click ...` product-reveal beats.

### Problem 3: Asset Matching Cannot Rely Only On Keyword Similarity

The first matching attempt selected outline/result clips for the hook and CTA because of overlapping feature words.

Required fix:

- Add beat-specific hard preferences:
  - hook -> Google Scholar / academic trust object
  - strong_cta -> landing page
  - product_reveal -> dashboard/review entry
  - real_papers -> paper list results
  - select_papers -> select/filter papers
  - generate_outline -> click generate outline
  - outline_proof -> generated outline
  - generate_review -> click generate review
  - result_cta -> generated review result
- If the same clip is selected for semantically different beats, review manually before rendering.

### Problem 4: Compliance Has To Be Baked Into Result Proof

Literfy can say the draft is based on real papers. It should not say the output is perfect, publication-ready, or safe to submit without review.

Preferred result proof:

```text
A review draft based on real papers!
```

Avoid:

```text
A complete perfect literature review!
```

### Problem 5: Google Scholar Framing Should Stay Native

The first Google Scholar hook does not need to be perfectly centered. The reference account also uses imperfect handheld framing, and the slightly off-center browser/screen look makes the video feel native instead of overproduced.

### Next Creative Iterations To Remind User

- Create 2-3 caption/script variants for A/B testing after the first usable cut.
- Consider a voiceover/BGM version after the caption-first version is approved.
- If scaling final renders, install a fuller FFmpeg build such as `ffmpeg-full` with subtitle/text libraries, but keep the PNG-caption preview path as the reliable fallback.

## Preview V2 Fixes From User Review

- Do not use source-video looping to fill a target beat duration. If a source range is too short, either shorten the beat, increase playback speed, choose a longer range, or freeze the last frame. Looping causes visible jumps back to the source first frame.
- The `Just go to this website!` CTA needs enough hold time for the landing page logo/brand to be visible before cutting away.
- If two uploaded clips are duplicate files, split them into different time ranges instead of treating them as different visual proof.
- For final proof beats such as generated review drafts, use a longer range and moderate speed-up so the viewer sees the output as a full document, not only the top of the page.

## Literfy First Video A/B Variants

- Variant A: reference-faithful PhD/Master hook. Best baseline for close imitation.
- Variant B: pain-question hook around random Google Scholar tabs. Likely strongest for first-3-second retention.
- Variant C: direct workflow hook around avoiding 50 tabs. Clearer utility promise, slightly more product/utility coded.

When testing, keep footage fixed and only compare caption angle first.

## 25s Voice/BGM Workmix

- Three 25-second versions were created for A/B/C.
- Visual sequence stayed fixed; beat durations were compressed and workflow/proof clips were sped up.
- Local macOS TTS was used only as a replaceable timing voiceover.
- Generated low-volume BGM was used only as a placeholder.
- Final publication audio should use a human/creator voice or preferred TTS voice and a TikTok-safe BGM track.

## User Approval And Corrections - Audio/Cover

- User is satisfied with the three A/B captioned video directions.
- Do not use the generated voiceover/BGM workmix for publication.
- Preferred publishing workflow: use captioned video only, then add TikTok trending music inside TikTok.
- Cover image should use the Google Scholar opening frame with a centered bold subtitle hook.
- Google Scholar itself should be centered in the cover background, not pushed to the left.
- Cover should imitate the reference account's first-frame cover: Google Scholar / academic trust object in the background, large white text with black outline in the middle.
- Do not use the Literfy landing page or product UI as the cover for this first video; the cover needs the Google Scholar trust hook.

## Cover Style Correction And Decision

- Do not change the cover caption text when creating style variants. Only adjust style: line spacing, word spacing, vertical position, subtle highlight, or light emoji usage if appropriate.
- Batch-produced Google Scholar covers should not look identical. Keep the same white bold text with black outline, but allow small variations such as one highlighted word, slightly different line spacing, or slightly different text block position.
- A single key word or phrase can have a different style, but the full sentence must stay the same as the chosen video caption.
- Do not insert the cover as a video first-frame segment by default. Keep the cover as a separate JPG asset for TikTok upload/cover selection.
- Failed/partial `*_with_cover.mp4` outputs should be removed to avoid confusing them with approved captioned exports.

## Delivery Standard Going Forward

- Final delivery should contain only the cover image and the corresponding captioned video.
- Do not deliver 35-second legacy versions unless the user explicitly asks for archive/debug files.
- Do not deliver generated voiceover/BGM workmixes. The publishing workflow is captioned video + TikTok trending music added inside TikTok.
- Clean old or rejected video files from the delivery folder once the final direction is chosen, while preserving source materials and structured JSON artifacts.

## Literfy Find Papers Material Intake

- New uploaded product footage was moved into the active Literfy project `materials/raw` folder.
- `09_click_find_papers_button.mov`: transition beat for `Click Find Papers`.
- `10_find_papers_search_topic.mov`: can be split into topic input, source selection, search/loading, and paper results.
- `12_save_and_citation_export_workflow.mov`: one video contains both save/favorites and citation/export workflow; split it into separate usable segments instead of treating it as one beat.
- For the next Find Papers video, keep the same Google Scholar template and cover logic, but adapt the command sequence to: click Find Papers -> type topic -> choose sources -> find real papers -> save useful papers -> copy citation.

## Editing Rules From User Feedback

- Uploaded product footage should be treated as an action library, not as fixed full-length clips.
- Subtitle/caption beats decide the edit rhythm.
- For every subtitle beat, choose the shortest visible action segment that proves the line.
- Product operation clips should usually be sped up. Use playback speeds such as `1.25x`, `1.5x`, or `2x` when the operation is slower than the caption rhythm.
- Asset matching output should include `clip_start`, `clip_end`, `playback_speed`, and `speed_reason`.
- Never loop source clips to fill time. Looping caused the earlier flash-frame problem where a clip jumped back to its first frame.
- If a segment is too short for the beat, choose one of these instead: shorten the beat, increase playback speed, select a longer range, or freeze the last frame.

## Subtitle Style Rules From User Feedback

- Subtitle text does not always need to change; style variation can be enough.
- Keep the main reference style: bold white text with black outline.
- Add light variation through highlight words, line spacing, word spacing, vertical position, one keyword color, subtle background, or restrained emoji.
- Good highlight targets: `PhD/Master`, `Google Scholar`, `50 tabs`, `real papers`, `Pro tip`, `citation`.
- Animation should be light: hook pop-in, keyword pop, quick fade-in, or subtle proof zoom. Avoid overdesigned effects that break the handheld academic style.
- Batch production should use small subtitle style variations so the homepage grid does not look fully duplicated.

## Feedback Loop Rule

- Whenever the user asks for changes, summarize what went wrong, what rule should change, and write the learning into this knowledge base.
- Apply the same learning to the skill reference files when it affects future workflow behavior.

## Citely Google Scholar Template Material Intake

- Citely should reuse the Google Scholar trust-doorway template: Google Scholar opening/cover first, then Citely website/workflow proof.
- Current Citely raw footage was organized under `projects/citely/research-connect-google-scholar-template/materials/raw`.
- Indexed clips:
  - `00_google_scholar_hook.mov`: opening hook / cover background.
  - `01_citely_landing_page.mov`: website reveal / strong CTA.
  - `02_click_find_sources.mov`: click Find Sources transition.
  - `03_find_sources_input_claim.mov`: Find Sources input / claim or citation-like text.
  - `04_find_sources_results.mov`: source results proof.
  - `05_click_verify_references.mov`: click Verify References transition.
  - `06_verify_references_input.mov`: Verify References input.
  - `07_verify_references_results.mov`: verification result / metadata proof.
- For Citely scripts, keep claims framed as checking, tracing, verifying, or catching citation risk. Do not say Citely guarantees 100% accuracy, replaces human academic judgment, verifies every possible source, or guarantees acceptance.
- For matching, do not reuse the same Find Sources input clip as result proof. Input beats and result beats must use different visual proof clips.
- Subtitle wording for Citely is not finalized yet; the current task only indexes and labels footage for later script/matching work.

## Citely Reference Video 7556287949361450248

- This reference is not the earlier command/tutorial style. It is a casual disbelief/reaction style:
  - `so you're telling me after ...`
  - `that this website could've ...`
  - `just ...`
  - `wait for ...`
  - `its as easy as that....`
  - `no cuz wdym ... smh...`
  - `And you can ...`
  - `for ... just wow smh...`
- For Citely, preserve the lowercase, ellipses, disbelief, and `smh` creator tone.
- Replace unsafe speed/completion claims with safer language: `helped me check`, `trace the source`, `shows citation details`, `papers connected to the claim`.
- Do not repeat the original video's exact time promises such as `less than 5 mins` or `3 mins` unless the user provides product-supported proof.
- Recommended first Citely test script is `reference_faithful_version` in the current Citely `product_script_card.json`.

## Delivery Communication Rule For Script Variants

- When a module generates multiple script variants, the final response must explicitly say how many versions were generated.
- Do not only paste the recommended version. Also list every version name and its strategic use case.
- For this workflow, script outputs usually need A/B/C visibility because the user is comparing creative angles before rendering.
- Preferred response structure after script generation:
  - `已生成 3 个版本`
  - version names
  - one-line purpose for each version
  - recommended first render
  - file path to the structured script card
- If only one version is shown in detail, state clearly that the other versions are still present in the JSON file.

## Cover QA Rule

- Before delivering cover images, inspect the cover contact sheet.
- Google Scholar should be fully visible and recognizable in the cover background. If the current product footage crop cuts off the logo too much, use the previously approved centered Google Scholar base or re-crop manually.
- Covers remain separate JPG assets by default; do not prepend them into videos unless the user explicitly asks.

## Emoji / Small Emotion Marker Rule

- A video may include 1-2 small emojis or emotion markers in subtitles when they fit the content and TikTok tone.
- Emojis should support the creator reaction, not decorate every line.
- Best placements:
  - hook disbelief line
  - result-shock line
  - final casual reaction line
- Good options for academic/research tool videos:
  - `😭` for wasted time / frustration
  - `👀` for "check this" / discovery
  - `😳` or `🤯` for result shock
  - `✅` for checked/verified workflow
- Avoid overusing emojis, large emoji-only beats, childish emoji clusters, or emojis that make compliance-sensitive claims feel unserious.
- Keep the reference subtitle style dominant: bold white text, black outline, short creator-style lines. Emojis are accents only.

## A/B/C Variant Visual Differentiation Rule

- A/B/C script variants must not only differ in wording. The first screen and cover must look visibly different enough for a TikTok homepage/grid viewer to recognize them as distinct tests.
- If all variants use the same Google Scholar background and similar hook length, the caption layout must vary deliberately:
  - different line count where possible, such as 2-line vs 3-line vs 4-line composition
  - different vertical position within the safe center area
  - different line spacing
  - slightly different word spacing or text block width
  - one highlighted keyword or phrase per variant
  - optional 1 small emoji on only one or two variants when it supports the tone
- Do not make all cover hooks break into the same three-line block.
- Do not leave all variants with identical white text + black outline layout when the user is comparing A/B/C creative directions.
- Do not overuse colored keyword highlights. If line count, position, line spacing, or text block width already separates the variants, do not add more highlights.
- Avoid blue or green highlights for this Google Scholar academic template; they look cheap in the current visual style. If a highlight is needed, use one restrained warm/yellow highlight on only one variant.
- Not every video needs a highlighted word. A/B/C differentiation can come from layout alone.
- The visual difference should still stay native to the reference account: bold white text, black outline, handheld academic screen, not overdesigned.
- Before delivery, inspect the cover/contact sheet and ask: would a user scrolling the profile grid instantly notice these are different angles? If not, revise layout before delivery.
- For Citely's current three variants:
  - `reference_faithful_version`: may use one restrained warm/yellow highlight if needed.
  - `verify_reference_focus`: differentiate by line break, line spacing, and y position, not colored highlight.
  - `find_sources_focus`: differentiate by narrower text block and lower/upper text position, not colored highlight.
- Citely V3 correction: remove blue/green highlights; keep only one subtle warm highlight at most, and rely mainly on layout variation.

## Subtitle Placement Composition Rule

- Do not default every subtitle to the exact visual center. That can make the video feel too clean, mechanical, and templated.
- Subtitle position should respond to the frame composition:
  - If the product UI or important button is in the center, move the subtitle slightly above or below the UI.
  - If the main visible proof is lower on the screen, place the subtitle upper-middle or mid-top.
  - If the top area contains the browser/logo/search bar that must stay readable, keep the subtitle center-lower.
  - If the screen has large empty space on one side, a slightly shifted text block is acceptable, but only within safe TikTok reading zones.
- A 25s video can have 1-2 subtitle beats that are not centered to create a more hand-edited TikTok feel.
- Do not move every subtitle away from center. The default should still be stable, readable, and reference-native.
- Avoid random, diagonal, or chaotic placement. The variation should feel designed: small y-position changes, upper-middle/lower-middle placement, or a subtly narrower text block.
- For each shot matching plan, caption placement can be set per beat through `caption_style.y_ratio`, `max_width`, `line_gap`, and forced `lines`.
- QA question before delivery: does the subtitle avoid covering the most important UI element while still feeling like the reference account's bold TikTok caption style?

## Execution Checklist For Style Feedback

- When a style rule is added by the user, apply it to the current active previews, not only to future knowledge.
- Recent miss: after adding the emoji/emotion marker rule, Citely V3 still did not include emoji markers. The fix is to add exactly one restrained marker per variant where it fits:
  - `😭` for regret/wasted effort hooks.
  - `😳` for surprising risk or "looked real" moments.
  - `👀` for discovery/source-check moments.
- Verify the renderer displays the marker visually and does not output tofu/square glyphs.

## Reflection: Emoji Execution Mistake

- Mistake 1: The user said a video can include 1-2 fitting emojis, but I applied an emoji-like marker to all three A/B/C variants. That over-executed the instruction.
- Correction: For A/B/C batches, only 1-2 variants should include emoji. The remaining variant(s) should stay different through layout, timing, line breaks, or small spacing changes.
- Mistake 2: I used custom-drawn emoji-like markers because the current Pillow subtitle renderer cannot directly render Apple Color Emoji cleanly; this produced a different look from native platform emojis such as `😊`.
- Correction: If the user asks for real emoji style, do not substitute a hand-drawn marker silently. Either:
  - keep the actual emoji character in text only if the final rendering path supports color emoji,
  - use a real emoji PNG/SVG asset pipeline,
  - or ask/confirm before using a simplified marker.
- For TikTok-style subtitles, native-looking emoji is preferred over custom icon drawings unless the custom style is intentionally requested.
- Current Citely correction: keep emoji on only selected variants, not all three.

## Native Emoji Rendering Rule

- User wants native emoji quality like CapCut/mobile subtitle editing, not hand-drawn substitute icons.
- Do not use simplified drawn markers as a silent fallback.
- Verified local option: macOS Swift/AppKit can render system text with Apple Color Emoji into transparent PNG overlays.
- Other possible options:
  - HTML/Chromium subtitle rendering to PNG, which can use system emoji fonts.
  - Real emoji PNG/SVG asset pipeline if browser/AppKit is unavailable.
  - CapCut UI automation only as a last resort; it is not stable enough for batch production.
- Preferred batch implementation: keep the current PNG subtitle overlay workflow, but route subtitle lines containing emoji through a native emoji overlay renderer instead of Pillow's default font renderer.
- QA requirement: inspect one rendered frame with emoji to confirm it looks like native emoji and not a square/tofu glyph or custom icon.

## Local Storage Cleanup Rule

- Local runs can accumulate large files: raw `.mov`, downloaded reference videos, preview renders, temporary segment videos, overlay PNGs, contact sheets, and old A/B/C versions.
- Cleanup must be safe by default. Always run dry-run first and write `output/cleanup_report.json`.
- Preserve:
  - `materials/raw` original footage.
  - final delivery videos and manifest-referenced outputs.
  - cover images.
  - structured JSON/MD decision artifacts such as viral pattern cards, product script cards, shot plans, publishing copy, and delivery manifests.
- Safe to clean:
  - `preview_render/`
  - `segments/`
  - `overlays/`
  - `qa_frames/`
  - `__pycache__/`
  - old versioned previews when newer `_vN` versions exist.
- Use `normal` cleanup after a delivery round. Use `aggressive` only when explicitly cleaning extracted reference frames/contact sheets that can be regenerated.
- Never delete raw user footage or current delivery outputs without explicit user instruction.

## Native Emoji Overlay QA Fix

- When using macOS Swift/AppKit to render native emoji subtitles, the overlay PNG must be exported at the exact video canvas size, usually `1080x1920`.
- AppKit can accidentally create Retina `2160x3840` PNGs. If that 2x overlay is composited directly, FFmpeg crops the right/bottom area and captions appear cut off.
- Before delivering emoji-captioned videos, check one emoji overlay with `file <overlay.png>` and confirm it is `1080 x 1920`.
- Also inspect a full rendered frame, not only a contact sheet, because contact sheets can hide edge clipping.
- Fix applied: native emoji renderer now writes a pixel-exact `NSBitmapImageRep` instead of using Retina-scaled `NSImage.lockFocus()`.
