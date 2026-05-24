# Xiaoyu Reaction Hook Library

This folder stores real-person Xiaoyu opening-hook clips.

Use these clips like generated AI human hooks: the first beat can use a Xiaoyu reaction clip, then the rest of the video continues with product footage from Clearfy, Literfy, Citely, or FigPad.

## Folder Layout

```text
materials/raw
  Original Xiaoyu reaction videos, renamed with stable hook ids.

materials/contact_sheets/timelines
  Generated visual contact sheets for reviewing expression and motion.

output/material_index.json
  Technical metadata: duration, resolution, fps, audio.

output/asset_library.json
  Human-readable hook library for matching: expression, action, best_use, usable_segments.
```

## Naming Guide

Current clips:

```text
00_xiaoyu_hook_IMG_5541.mov  shocked, covers mouth, leans closer
01_xiaoyu_hook_IMG_5550.mov  panic/stress, hands near head
02_xiaoyu_hook_IMG_5551.mov  skeptical/confused, thinking pose
03_xiaoyu_hook_IMG_5557.mov  side surprise, hand to chest, covers mouth
04_xiaoyu_hook_IMG_5564.mov  frozen wide-eyed shock
05_xiaoyu_hook_IMG_5567.mov  neutral to sudden surprise, short hook
06_xiaoyu_hook_IMG_5568.mov  points/reaches, covers mouth, extreme close-up
```

## Matching Rules

- Use these only for opening hook or reaction beats.
- Do not use them as product proof.
- Product proof should still come from the product asset library.
- Good hook labels: `human hook`, `creator reaction`, `confused`, `surprised`, `stressed`, `relieved`, `pointing`, `student POV`.
- For vertical TikTok output, crop around Xiaoyu's face and keep the key hand gesture visible.
