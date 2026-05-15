# Material Library

## Goal

Turn raw handheld footage into a searchable library that can support repeated short-video edits.

## Indexing Pass

Run:

```bash
python3 scripts/inventory_materials.py <footage_dir> --out <edit_dir>/material_index.json
```

If the clips contain speech or useful ambient audio and `ELEVENLABS_API_KEY` is available, run:

```bash
python3 scripts/transcribe_batch.py <footage_dir> --edit-dir <edit_dir>
python3 scripts/pack_transcripts.py --edit-dir <edit_dir>
```

## Labeling Fields

Each useful clip should eventually have:

- `scene`: where it happens.
- `subject`: product, person, hand, screen, packaging, result, environment.
- `action`: unbox, use, tap, pour, clean, compare, show result, walk, close-up.
- `shot_type`: close-up, medium, POV, over-shoulder, screen, macro, wide.
- `quality`: usable, shaky, too dark, duplicate, keep for b-roll only.
- `best_ranges`: time ranges that look clean.
- `matched_beats`: script beats this clip can support.

## Matching Rules

- Hook needs the clearest, fastest-understood visual.
- Demo beats need real product action, not vague lifestyle footage.
- Proof beats need visible result or believable context.
- CTA can use product hero shot, packaging, app screen, or satisfying final state.
- If footage is missing, mark `needs_shot` instead of forcing a weak clip.

## Operator Notes

Handheld footage is valuable because it feels native. Do not over-polish it unless the product category demands premium trust. Use stabilization and color correction lightly.
