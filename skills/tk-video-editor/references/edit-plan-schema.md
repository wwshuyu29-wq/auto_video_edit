# Edit Plan Schema

## Shot Matching Table

Before creating an EDL, produce this table:

| Beat | Copy | Visual need | Source | Start | End | Reason | Backup |
|---|---|---|---|---:|---:|---|---|
| HOOK | ... | ... | C001.mp4 | 1.2 | 3.8 | ... | needs_shot |

## Shot Plan JSON

`plan_to_edl.py` accepts this format:

```json
{
  "sources": {
    "C001": "/abs/path/C001.mp4",
    "C002": "/abs/path/C002.mp4"
  },
  "segments": [
    {
      "source": "C001",
      "start": 1.2,
      "end": 3.8,
      "beat": "HOOK",
      "copy": "Your caption or spoken line",
      "reason": "Why this shot supports the beat"
    }
  ],
  "grade": "warm_cinematic",
  "subtitles": "master.srt",
  "overlays": []
}
```

## Render EDL JSON

`plan_to_edl.py` emits:

```json
{
  "version": 1,
  "sources": {"C001": "/abs/path/C001.mp4"},
  "ranges": [
    {
      "source": "C001",
      "start": 1.2,
      "end": 3.8,
      "beat": "HOOK",
      "quote": "Your caption or spoken line",
      "reason": "Why this shot supports the beat"
    }
  ],
  "grade": "warm_cinematic",
  "overlays": [],
  "subtitles": "master.srt",
  "total_duration_s": 2.6
}
```

## Editing Defaults

- Format: 1080x1920 vertical.
- Duration: 18-35 seconds for product tests unless the user requests otherwise.
- Cut rhythm: fast hook, slightly slower proof/demo, clean CTA.
- Captions: large, readable, platform safe, no tiny dense paragraphs.
- Audio: avoid hard cuts; use short fades at segment boundaries.

## Preview Render

For script/shot QA before final voiceover and music, use the PNG-caption preview path:

```bash
python modules/video_rendering/run.py \
  --input output/shot_matching_plan.json \
  --asset-library output/asset_library.json \
  --preview-render \
  --preview-out output/preview.mp4
```

This writes:

- `preview.mp4`: 1080x1920 captioned video preview.
- `preview_midpoint_sheet.jpg`: one frame per script beat for fast visual QA.
- `captions.json` and `master.srt`: the approved caption sequence.
- `render_report.json`: render metadata and output paths.
