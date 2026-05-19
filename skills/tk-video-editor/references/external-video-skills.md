# External Video Skills Integration

This note records external skills that were evaluated for the auto video workflow and how they should influence `tk-video-editor`.

The rule for this project is conservative: `tk-video-editor` remains the orchestrator. External skills can inform a subtask, but they should not replace the existing module boundaries or rewrite product claims.

## Evaluated Skills

### `sundial-org/awesome-openclaw-skills@ffmpeg-video-editor`

Purpose:

- Helps turn video editing tasks into FFmpeg commands.
- Useful for trimming, concatenation, transcoding, resizing, compression, audio extraction, and troubleshooting FFmpeg failures.

Installation command:

```bash
npx skills add sundial-org/awesome-openclaw-skills@ffmpeg-video-editor -g -y
```

Current status:

- Installation was attempted but GitHub cloning timed out in this environment.
- Do not assume the skill is installed until `~/.codex/skills/ffmpeg-video-editor` exists.

How to use if installed:

- Ask for FFmpeg command help when the rendering layer fails.
- Use it for low-level video operations only, not for viral deconstruction, product scripting, or claim writing.

Best integration points:

- `scripts/render_tiktok_preview.py`: segment rendering, concat handling, aspect-ratio crop, codec settings.
- `scripts/plan_to_edl.py`: EDL validation and render compatibility.
- `scripts/clip_video.py` and `scripts/burn_subtitles.py`: safer command generation and clearer error messages.
- Web/worker preflight: make FFmpeg errors understandable to the user.

Project rules to preserve:

- Prefer PNG-caption preview rendering first because it avoids FFmpeg subtitle filter compatibility issues.
- Do not loop short clips to fill beat duration.
- Use speed, trim, freeze-tail, or better source ranges instead.
- Keep final delivery as cover image plus captioned video unless the user requests otherwise.

### `kostja94/marketing-skills@tiktok-captions`

Purpose:

- Helps generate TikTok-style captions, hooks, titles, hashtags, and publishing copy.
- Useful for creator-style wording and platform-native post metadata.

Installation command:

```bash
npx skills add kostja94/marketing-skills@tiktok-captions -g -y
```

Current status:

- Installation was attempted. The repository cloned, but `npx skills` did not find a valid installable skill in the resolved package shape.
- Treat it as a candidate/reference, not an installed skill.

How to use if a valid install path becomes available:

- Use it only after the video script and visible subtitles are approved.
- Use it for title, caption, hashtags, keywords, and CTA phrasing.
- Do not let it invent product features or exaggerated claims.

Best integration points:

- `modules/publishing_copy_rewrite/run.py`: title options, recommended caption, hashtags, keywords, posting notes.
- `references/publishing-copy-card.md`: stricter output contract for TikTok publishing metadata.
- `product-library/products.json`: enforce product facts and forbidden claims.

Project rules to preserve:

- Publishing copy must be based on the approved final video, subtitles, product facts, and reference post caption logic.
- The copy should sound like creator workflow sharing, not homepage advertising.
- For academic products, avoid claims such as perfect accuracy, guaranteed acceptance, publication-ready output, or replacement for human review.

### Installed Local Skills Already Available

#### `tk-video-editor`

Role:

- Main orchestrator for this project.
- Owns reference teardown, product script rewrite, asset matching, captioned rendering, cover delivery, and publishing copy.

How to invoke:

- Ask directly for TikTok workflow work, such as "use tk-video-editor to make a FigPad video from this reference."

#### `hyperframes` and `hyperframes-cli`

Role:

- HTML/GSAP video composition, animated title cards, overlays, captions, transitions, TTS, and audio-reactive motion.

Best use in this project:

- Future animated title cards.
- More stylized subtitle templates.
- Animated cover/video variants where the product needs stronger motion design.

Do not use by default for the current screen-recording workflow. The current TikTok style depends on real product footage and native-looking captions.

#### `remotion-best-practices`

Role:

- Remotion guidance for React-based video rendering, captions, audio, animation, and composition structure.

Best use in this project:

- Future migration from the current FFmpeg/Pillow preview renderer to a React/Remotion render engine.
- More complex animated captions or template libraries.

Do not migrate the renderer just to use Remotion. Use it only when the current PNG-caption/FFmpeg path becomes too limiting.

## Integration Decision

Do not add more active orchestrators.

Recommended layering:

```text
tk-video-editor
  -> use ffmpeg-video-editor concepts for low-level rendering and concat robustness
  -> use tiktok-captions concepts for publishing metadata only
  -> use HyperFrames/Remotion only for future animated templates
```

## Next Implementation Ideas

1. Add clearer FFmpeg diagnostics to `render_tiktok_preview.py`.
2. Add a render troubleshooting checklist to `video_rendering` reports.
3. Expand `publishing_copy_rewrite` to include `keywords`, not only hashtags.
4. Add platform-native caption variants while preserving product safety.
5. Add a future `render_engine` setting:
   - `png_caption_ffmpeg` for current fast TikTok previews.
   - `hyperframes` for animated HTML overlays.
   - `remotion` for React-based template videos.
