# Source Skills And Adaptation Notes

## browser-use/video-use

Source: https://github.com/browser-use/video-use

Borrowed:

- EDL-first editing workflow.
- `render.py`, `timeline_view.py`, `grade.py`, transcription helpers.
- Cut-boundary QA and subtitle-last rendering principle.

Adapted for this skill:

- The workflow is now TikTok product-operations first, not generic video editing.
- Strategy confirmation means script + shot matching confirmation, not only editing style.
- Captions are treated as conversion assets, not just accessibility text.

## op7418/Youtube-clipper-skill

Source: https://github.com/op7418/Youtube-clipper-skill

Borrowed:

- FFmpeg clipping helper.
- Subtitle burning helper.
- Practical handling of FFmpeg/libass issues.

Adapted for this skill:

- YouTube-specific chapter workflow is not primary.
- Subtitle tools are used for final packaging or reference-video processing.

## remotion-dev/skills

Source: https://github.com/remotion-dev/skills

Borrowed:

- Remotion best practices for programmatic motion graphics.
- Caption, timing, sequencing, and FFmpeg reference patterns.

Adapted for this skill:

- Remotion is optional. Use it for overlays, labels, comparison frames, or template videos, not as the default replacement for native handheld footage.
