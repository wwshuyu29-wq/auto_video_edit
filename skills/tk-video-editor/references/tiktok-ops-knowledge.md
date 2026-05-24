# TK Video Operations Knowledge Base

This reference stores reusable TikTok/TK operating patterns learned from analyzed competitor videos.

## research.connect

Account: https://www.tiktok.com/@research.connect

### Core Pattern

Use a familiar academic website or document as the first-frame trust object, then overlay a bold subtitle hook that promises an easier or smarter academic workflow.

Formula:

```text
Familiar academic interface
+ high-status academic identity
+ easy/smart/legit shortcut
+ product/tool reveal
+ visible proof output
```

### Google Scholar Cover Pattern

- Handheld laptop/tablet screen.
- Google Scholar homepage or academic-search-like page.
- White page, browser chrome visible, imperfect angle.
- Bold white caption with black outline.
- 3-5 short lines, centered or slightly below center.

Hook examples:

- "How to write your thesis paper like a PhD/Master student (The easy way)"
- "Still using ChatGPT to write your RRL?"
- "How to write a research paper (The legit way)"
- "How to write an RRL/Literature review (The smart way)"

### Video 7633832153922489621

Caption sequence:

1. "How to write your thesis paper like a PhD/Master student (The easy way)"
2. "Just go to this website!"
3. "Click researcher"
4. "Type your research paper topic"
5. "Pro tip! use latex for pdfs"
6. "Then watch it do its magic in 2-3 mins"
7. "Its done! lets see..."
8. "A complete research paper!"
9. "With meaningful visualizations!"

Storyboard:

```text
0-3s: Academic trust object + status-upgrade hook
3-6s: Product reveal
6-10s: Click relevant mode
10-13s: Enter academic task/topic
13-16s: Show expert/pro setting
16-19s: Promise short processing time
19-23s: Reveal completed academic output
23-27s: Show bonus proof such as citations, charts, tables, or visualizations
```

Operational lesson:

The video borrows Google Scholar's academic trust, then moves attention to the creator's product. Adaptations should preserve the trust-doorway structure while making every claim map to the user's product features.

## First Literfy Run Lessons

### Caption Grammar Must Be Extracted

Do not stop at structure-level imitation. Before rewriting scripts, extract the reference video's caption grammar:

```text
How to [task] like a [high-status user] ([easy/smart/legit] way)
Just go to this website!
Click [mode/button]
Type [input]
Pro tip! [setting or user-controlled step]
Then [generate/let it work]
It's done! let's see...
[result proof]!
```

The rewritten product script should preserve this sentence rhythm, punctuation, and short-command style while replacing the claims with product-truth-safe equivalents.

### Strong CTA Visual Rule

The second-line CTA such as `Just go to this website!` must map to a landing page, homepage, or public website reveal. Do not map this beat to an internal proof result.

### Literfy-Specific Adaptation

Safe result proof:

```text
A review draft based on real papers!
```

This preserves the reference video's result-proof slot while avoiding claims that Literfy writes a perfect or submission-ready literature review.

### Native Framing Note

Do not over-correct the Google Scholar opening shot into a perfectly centered software demo. The reference style uses handheld, slightly imperfect screen framing. Off-center browser/logo placement is acceptable if the hook text is readable and the academic trust object is recognizable.

### Follow-Up Creative Queue

- After the first approved captioned cut, produce 2-3 caption/script variants for A/B testing.
- Then decide whether to add creator-style voiceover and low-volume BGM.
- Keep PNG caption overlays as the default preview path; install a fuller FFmpeg build only when final subtitle/filter compositing requires it.

### Render QA Lessons

- Never loop a short source clip to fill a longer beat. It creates obvious flashbacks to the clip's first frame. Prefer trimming the beat, using a longer source range, setting playback speed, or freezing the tail.
- Check cut boundaries with frames just before and just after each cut, not only midpoint screenshots.
- A CTA landing-page beat should hold long enough for the logo/brand mark to appear.
- If two asset files are byte-identical, treat them as one clip with multiple usable segments and avoid assigning the same visual moment to adjacent beats.
- Final proof beats need enough screen time to reveal the result as an actual output. For long documents, use a longer segment at 1.25x-1.5x speed.

### Publishing Audio Preference

For this Literfy/TikTok workflow, prioritize caption-only exports and add TikTok trending music inside TikTok. Generated voiceover/BGM workmixes can be used for timing QA, but they are not the preferred publishing output.

### Cover Rule

The cover should be built from the Google Scholar opening frame, not the product landing page. Place the hook caption in the middle in the same bold white text with black outline style as the reference account. The goal is to borrow the academic-search trust object before revealing Literfy inside the video.

For batch production, do not rewrite the cover caption text when only style variety is requested. Keep the caption text identical to the selected video variant. Create variety through small design differences: line spacing, word spacing, vertical position, one highlighted word/phrase, or light emoji use when it fits the niche.

Keep the cover as a separate image asset by default. Do not prepend the cover to the video unless the user explicitly asks again after seeing the separate cover workflow.

### Delivery Standard

Deliver each variant as a pair:

```text
cover.jpg + captioned_video.mp4
```

Do not include voiceover/BGM workmixes or old 35-second drafts in the final delivery set. The user will add TikTok trending music inside TikTok.

### Literfy Find Papers Workflow Assets

For Find Papers / save / citation videos, one uploaded clip may contain multiple product actions. Label it with separate usable segments:

- dashboard click -> `Click Find Papers`
- topic input/source selection -> `Type your research topic` / `Choose your sources`
- results list -> `It finds real papers`
- save/favorites -> `Save the useful papers`
- citation modal/copy -> `Copy the citation`

Do not force these into one long proof beat; split by visible action so the output still feels hand-edited.

### Speed And Segment Rules

Treat uploaded product footage as an action library. Do not use full clips by default.

For every subtitle beat:

1. Identify the visible action that proves the subtitle.
2. Cut only that range.
3. Add `playback_speed` when the product action is slow.
4. Add `speed_reason` explaining why the speed was used.

Never loop source clips to fill time. If timing does not fit, shorten the beat, increase speed, choose a better range, or freeze the final frame. Looping back to the first frame creates visible flash-frame errors.

### Subtitle Style And Animation

Default caption style stays close to the reference account: bold white text with black outline.

Allowed batch variations:

- one highlighted word or phrase
- slightly different line spacing
- slightly different text block position
- subtle keyword color
- restrained emoji when it fits the academic niche
- light animation such as hook pop-in, keyword pop, or quick fade-in

Do not rewrite subtitle content just to create style variation. Keep text fixed unless the user asks for copy changes.

### Feedback Capture

When the user corrects an output, update this knowledge base with the underlying rule, not just the one-off fix. Future runs should apply the learned rule without waiting for the same correction.

### Same-Creator Multi-Video Rule

Do not use creator/account as the unique reference key. A single TikTok creator can have multiple unrelated template patterns.

Reference storage should preserve:

```text
creator_id -> videos -> video_id -> reference.mp4 / reference.info.json / contact_sheet / template notes
```

When the user provides another URL from a creator already seen before:

1. Extract the `video_id` from the URL.
2. Store or register it as a separate video under that creator.
3. Compare the new video's visual/caption structure against prior videos from the same creator.
4. Select the template by `video_id` or observed pattern, not by creator name alone.

For `justin_write`, keep these separate:

- `7620697283176320269`: face-first reaction story followed by AI detector/humanizer result proof.
- `7621061020181744926`: POV suspicious observer/laptop angle about someone writing from a blank Google Doc.

### Citely Google Scholar Template Intake

For Citely, keep the same Google Scholar trust-doorway structure used in the Literfy run:

```text
Google Scholar hook / cover -> Citely landing page CTA -> product workflow -> result proof
```

Use only Citely product facts:

- Find Sources: trace claims, references, or citation-like text back to source results.
- Verify References: check whether references correspond to real sources.
- Citation Metadata Checking: compare citation metadata such as title, authors, year, journal, and DOI.
- AI Citation Risk Check: check references that may have been generated by AI tools.

Do not claim 100% citation accuracy, universal source coverage, replacement of human academic judgment, manuscript acceptance, or that verified citations automatically prove an argument is correct.

For asset matching:

- `00_google_scholar_hook` -> opening hook / cover background.
- `01_citely_landing_page` -> strong CTA / website reveal.
- `02_click_find_sources` -> Find Sources entry click.
- `03_find_sources_input_claim` -> claim/reference input.
- `04_find_sources_results` -> source results proof.
- `05_click_verify_references` -> Verify References entry click.
- `06_verify_references_input` -> reference list/input.
- `07_verify_references_results` -> verification/metadata proof.

Input and result beats must use different proof clips. Do not reuse an input clip for a result subtitle just to fill time.

### Citely Reference Video 7556287949361450248

This reference uses a casual disbelief/reaction caption grammar, not a clean tutorial grammar:

```text
so you're telling me after [manual pain]......
that this website could've [helped outcome].....
just [simple action]
wait for [result] to load
its as easy as that....
no cuz wdym [result shock] smh...
And you can [bonus feature]...
for [benefit]..... just wow smh...
```

When adapting to Citely, preserve lowercase, long ellipses, and the casual `smh` reaction tone. Replace unsafe time/completion claims with product-safe checking language such as `helped me check`, `trace the source`, `shows citation details`, and `papers connected to the claim`.

Do not reuse the original's `less than 5 mins`, `3 mins`, or automated completion promises unless the user provides product-supported evidence and wants that claim.

### Delivery Communication For Script Variants

When generating multiple product script variants, always tell the user exactly how many versions were generated, name each version, and summarize each version's intended use. Do not only expand the recommended version without saying the other variants exist.

For this TikTok workflow, the user expects to compare creative angles before rendering. Preferred response:

```text
已生成 3 个版本:
1. reference_faithful_version - closest imitation
2. verify_reference_focus - feature/pain focus
3. find_sources_focus - alternate angle

推荐先跑: ...
完整结构化文件: ...
```

If only one script is pasted in detail, explicitly say the other variants are still in the script card.

### Cover QA Rule

Before delivering covers, inspect the cover contact sheet. Google Scholar must be fully visible and recognizable in the cover background. If a source crop cuts off the Google Scholar logo too much, use an approved centered Google Scholar base or manually re-crop before delivery.

Covers are separate JPG assets by default. Do not prepend them into the video unless explicitly requested.

### Emoji / Emotion Marker Rule

One short video can include 1-2 small emojis or emotion markers when they match the script and TikTok subtitle tone. They should amplify the creator reaction, not decorate every line.

Preferred placements:

- hook disbelief line
- result-shock line
- final casual reaction line

Good options for academic/research tool videos:

- `😭` for wasted time or frustration
- `👀` for discovery or "check this"
- `😳` / `🤯` for result shock
- `✅` for checked or verified workflow

Avoid emoji clusters, childish decoration, emoji-only beats, or emoji choices that make compliance-sensitive academic claims feel unserious. Keep bold white text with black outline as the dominant reference style.

### A/B/C Variant Visual Differentiation

A/B/C variants must be visually distinguishable in the first screen and cover, not only different in script text. If all variants share the same Google Scholar background and similar hook length, deliberately vary the subtitle layout:

- line count: avoid all variants breaking into the same three-line block
- vertical position inside safe center area
- line spacing
- word spacing / max text width
- one highlighted keyword or phrase only when needed
- 1 small emoji on selected variants only if it fits the creator tone

Keep the native reference look: bold white text, black outline, handheld academic screen. Do not overdesign. But before delivery, inspect the cover/contact sheet and confirm a profile-grid viewer can instantly tell the variants are different creative angles.

Do not overuse colored highlights. Avoid blue and green highlights for this Google Scholar academic template; they read cheap in the current style. If a highlight is needed, use one restrained warm/yellow highlight on only one variant. If layout already makes the variants distinct, do not add highlights.

For Citely-style variants:

- `reference_faithful_version`: closest reference layout; can use one restrained warm/yellow highlight.
- `verify_reference_focus`: differentiate through line breaks, line spacing, and y position.
- `find_sources_focus`: differentiate through narrower text block and different y position.

Citely V3 correction: do not make every variant highlighted. Remove blue/green highlights and rely mainly on layout variation.

### Subtitle Placement Composition

Do not place every subtitle at the exact visual center. That can make the edit feel too mechanical. Subtitle position should respond to the frame composition:

- If important product UI or a button is centered, move the subtitle slightly above or below it.
- If proof/results are lower on the screen, use upper-middle or mid-top placement.
- If the browser/logo/search area must remain readable, use center-lower placement.
- If one area has large empty space, a subtle text-block shift is acceptable within safe TikTok zones.

A 25s video can have 1-2 non-centered subtitle beats for a more hand-edited TikTok feel. Do not move every subtitle away from center. Avoid random, diagonal, or chaotic placements. Variation should be designed through small y-position changes, upper-middle/lower-middle placement, narrower text blocks, or line breaks.

Use `caption_style.y_ratio`, `max_width`, `line_gap`, and forced `lines` per beat in the shot plan. Before delivery, check whether the subtitle avoids covering the most important UI element while preserving the bold white text + black outline reference style.

### Apply Style Feedback To Current Outputs

When the user adds a style rule, apply it to the current active previews instead of only writing it into future knowledge. For emoji/emotion markers, add exactly one restrained marker per variant when appropriate and verify the renderer does not output tofu/square glyphs.

Examples:

- `😭` for regret/wasted effort hooks.
- `😳` for surprising risk or "looked real" moments.
- `👀` for discovery/source-check moments.

Correction: Do not add emoji to every A/B/C variant. A batch should usually have emoji on only 1-2 variants; other variants can differ through layout, y position, line spacing, or text block width.

If the user expects native emoji appearance such as `😊`, do not silently replace it with a custom-drawn marker. The current Pillow PNG caption path cannot reliably render Apple Color Emoji directly. Use a real emoji asset pipeline or a rendering path that supports color emoji, or confirm with the user before using simplified drawn markers.

Native emoji rendering preference: use macOS Swift/AppKit or HTML/Chromium rendering to create transparent PNG overlays with system emoji fonts. Keep Pillow for normal subtitles if useful, but route emoji-containing caption lines through native text rendering. CapCut UI automation is not preferred for batch workflows because it is harder to automate reliably.

Native emoji overlay QA fix: when using Swift/AppKit, the transparent PNG must be exported at the exact render canvas size, usually `1080x1920`. AppKit can produce Retina `2160x3840` images if rendered through `NSImage.lockFocus()`, and FFmpeg will crop that oversized overlay when compositing onto a 1080x1920 video. The native emoji renderer should use a pixel-exact bitmap context, and every emoji delivery should inspect one overlay with `file <overlay.png>` plus one full rendered frame.

### Local Storage Cleanup

Local workflows produce large regenerable artifacts: downloaded references, preview videos, temporary segment clips, overlay PNGs, contact sheets, and old A/B/C versions.

After each delivery round, run cleanup in dry-run mode first:

```bash
python3 scripts/cleanup_project.py <project_dir> --mode normal
```

Only use `--execute` after reviewing `output/cleanup_report.json`.

Never delete raw user footage, structured JSON/MD decision artifacts, covers, or manifest-referenced delivery outputs unless the user explicitly asks. Safe cleanup targets include `preview_render`, `segments`, `overlays`, `qa_frames`, `__pycache__`, and older versioned preview artifacts when newer `_vN` files exist.
