# Shot Matching Plan

## Purpose

The shot matching plan is the stable output of `asset_matching`.

It maps each script beat to the best available clip, explains why, and identifies missing assets. This module strongly affects whether the final video feels native or AI-generated.

It does not rewrite the core script. If the script cannot be supported by assets, it sets `needs_script_revision`.

## Asset Label Shape

```json
{
  "clip_id": "handheld_001",
  "file_path": "/assets/handheld_001.mp4",
  "duration": 8.5,
  "orientation": "vertical",
  "quality_score": 8,
  "shot_type": "handheld laptop shot",
  "camera_motion": "slow push in",
  "scene": "desk / study room",
  "visible_objects": ["laptop", "hand", "notebook", "coffee"],
  "emotion": "focused",
  "best_use": ["opening hook", "study pain point", "transition"],
  "not_good_for": ["product proof", "final CTA"],
  "usable_segments": [
    {
      "start": 1.2,
      "end": 4.8,
      "reason": "stable handheld shot with clear laptop screen"
    }
  ],
  "text_overlay_safe_area": "top and center",
  "audio_quality": "not needed",
  "notes": "good for research/student style videos"
}
```

## Output Shape

The module must write `output/shot_matching_plan.json`.

```json
{
  "edit_plan": [
    {
      "beat": "hook",
      "time": "0-3s",
      "voiceover": "If your literature review starts with 30 random tabs open, this is for you.",
      "clip_id": "handheld_003",
      "clip_start": 0.8,
      "clip_end": 3.8,
      "reason": "Messy laptop shot matches the pain of research chaos.",
      "on_screen_text": "Still searching papers manually?",
      "transition": "hard cut",
      "subtitle_priority": "large"
    }
  ],
  "missing_assets": [
    {
      "need": "clear CTA ending shot",
      "suggestion": "Record one vertical shot of the product homepage with cursor hovering over Try Now."
    }
  ],
  "risk_notes": [
    "Opening shot is usable but not very visually strong."
  ],
  "needs_script_revision": false,
  "scores": {
    "visual_match": 8,
    "pace_match": 7,
    "asset_quality": 8,
    "opening_strength": 6,
    "product_proof_strength": 7
  }
}
```

## Matching Rules

- Hook beats need the strongest first-frame visual.
- Strong CTA beats such as `Just go to this website!` need landing page, homepage, or public website reveal footage.
- Pain beats can use messy, stressed, or manual-work footage.
- Solution beats need product UI, workflow, or clear transition from old way to new way.
- Proof beats need actual output, before/after, chart, document, or visible result.
- CTA beats need clean product page, final result, or simple hero shot.

For workflow demo videos, separate action clips from result clips:

- `Click Literature Review` -> dashboard/review entry.
- `Type your topic` -> input screen.
- `It finds real papers` -> paper list results.
- `Pro tip! select the papers first` -> paper selection clip.
- `Then generate the outline` -> click generate outline clip.
- `It's done! let's see...` -> generated outline result.
- `Now turn it into a review draft` -> click generate review clip.
- `A review draft based on real papers!` -> generated review result.

If product proof footage is missing, flag it. Do not hide the weakness by using pretty but irrelevant b-roll.
