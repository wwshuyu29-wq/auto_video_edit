#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TARGET_DATE = os.environ.get("SAME_GIRL_BATCH_DATE", "2026-06-07")
TARGET = ROOT / f"projects/generated/{TARGET_DATE}_same-girl-new-ai-human-hooks"
OUTPUT = TARGET / "output"
FINAL_16 = OUTPUT / "final_16"
RUNNER = ROOT / "skills/tk-video-editor/modules/human_hook_generation/run.py"
PYTHON = ROOT / ".venv/bin/python3"


BASE_CHARACTER = (
    "a petite fictional young adult college student creator, soft round face, "
    "long light-brown hair, natural no-makeup look, cozy StudyTok energy"
)


PERSONAS: list[dict[str, str]] = [
    {
        "name": "01_close_coy_mouth_cover",
        "scene": "warm beige dorm desk, silver laptop on the right, open notebook and pastel sticky notes",
        "framing": "vertical 9:16 close-up selfie, face upper center, laptop visible at the side, lower middle clear for captions",
        "emotion": "shy proud surprise, like she just caught a mistake before submitting",
        "motion": "smiles softly, lightly covers the lower half of her mouth, glances to the laptop, then gives a tiny palm-up reveal",
        "camera": "front-facing phone selfie, slight lean-in, gentle handheld movement",
        "lighting": "soft warm daylight from a nearby window",
        "outfit": "light gray sweatshirt",
    },
    {
        "name": "02_notebook_peek",
        "scene": "small dorm desk with laptop, notebook in foreground, one pink highlighter, tidy paper stack",
        "framing": "vertical 9:16 medium close selfie, shoulders visible, notebook at bottom edge",
        "emotion": "curious and amused, a quiet wait-look-at-this reaction",
        "motion": "peeks over the notebook, raises eyebrows, points one finger toward the laptop without touching the screen",
        "camera": "front-facing phone held slightly above eye level, small natural wobble",
        "lighting": "clean morning window light with a warm desk lamp fill",
        "outfit": "cream cardigan over a white tee",
    },
    {
        "name": "03_laptop_side_eye",
        "scene": "late-night study desk with laptop glow, open lined notebook, pencil cup, plain mug",
        "framing": "vertical 9:16 close selfie, face slightly left of center, laptop over shoulder",
        "emotion": "playful side-eye concern turning into relief",
        "motion": "leans close to camera, gives a side-eye to the laptop, half covers her mouth, then nods once",
        "camera": "handheld phone selfie with subtle vertical sway",
        "lighting": "dim warm bedroom lighting mixed with laptop glow",
        "outfit": "oversized navy hoodie and small hair clip",
    },
    {
        "name": "04_pencil_freeze",
        "scene": "quiet library table with laptop, pencil, yellow highlighter, water bottle, printed draft pages",
        "framing": "vertical 9:16 close-up selfie, face clear, desk visible at bottom edge",
        "emotion": "frozen realization, anxious but funny",
        "motion": "holds a pencil near her lips, freezes, widens eyes, then slowly points the pencil toward the laptop",
        "camera": "front-facing phone selfie, mostly steady with natural hand movement",
        "lighting": "neutral library lighting with soft shadows",
        "outfit": "soft green cardigan over a plain shirt",
    },
    {
        "name": "05_screen_present",
        "scene": "cozy study corner, laptop angled toward her, notebook open, small desk lamp, no readable screen text",
        "framing": "vertical 9:16 medium close-up, laptop clearly beside her but blurred enough to avoid readable text",
        "emotion": "quietly excited and a little smug",
        "motion": "looks at camera, tucks hair behind ear, glances at laptop, then presents it with both hands low in frame",
        "camera": "front-facing phone, gentle handheld drift, authentic casual framing",
        "lighting": "golden desk lamp with soft daylight in background",
        "outfit": "pale blue crewneck sweatshirt",
    },
    {
        "name": "06_forehead_hold",
        "scene": "student room near a window, laptop on a clean desk, loose paper stack on one side",
        "framing": "vertical 9:16 medium close-up selfie, shoulders visible, caption-safe lower center",
        "emotion": "stressed but trying not to laugh",
        "motion": "presses fingertips to her forehead, looks into camera, looks sideways at the laptop, then exhales with a small hand flip",
        "camera": "front-facing phone camera, held slightly below eye level",
        "lighting": "soft daylight from a side window",
        "outfit": "lavender crewneck sweatshirt and thin glasses",
    },
    {
        "name": "07_draft_reveal",
        "scene": "minimal dorm desk, laptop, tablet, open planner, small stack of index cards",
        "framing": "vertical 9:16 close-to-medium selfie, face near upper third, laptop on lower right",
        "emotion": "nervous confession turning into confident reveal",
        "motion": "pulls the planner slightly into view, makes a tiny wince, then tilts her head toward the laptop with a small smile",
        "camera": "front-facing phone selfie with small handheld sway",
        "lighting": "warm indoor lamp and soft window spill",
        "outfit": "white zip hoodie",
    },
    {
        "name": "08_chin_hand_smile",
        "scene": "bright dorm desk with laptop, notebook, sticky tabs, and a plain ceramic cup",
        "framing": "vertical 9:16 close-up selfie, face centered, desk only partly visible",
        "emotion": "suspicious at first, then pleasantly surprised",
        "motion": "rests chin on one hand, squints at the laptop, breaks into a small smile, then gestures downward to the screen",
        "camera": "front-facing phone, steady close selfie, tiny focus breathing",
        "lighting": "bright natural daylight, soft and clean",
        "outfit": "sage green sweatshirt",
    },
    {
        "name": "09_window_turn",
        "scene": "desk beside a window, laptop open, notebook and gel pens neatly arranged",
        "framing": "vertical 9:16 side-angle selfie, face three-quarter view, laptop behind shoulder",
        "emotion": "soft surprised oh-wait moment",
        "motion": "turns from the laptop back to camera, covers a smile with fingertips, then lifts eyebrows like she found something useful",
        "camera": "front-facing phone held at a slight side angle",
        "lighting": "cool daylight from window plus warm desk lamp accent",
        "outfit": "beige knit sweater",
    },
    {
        "name": "10_mug_pause",
        "scene": "messy thesis desk with laptop, open notebook, coffee mug, tabs and printed paper edges",
        "framing": "vertical 9:16 medium close-up, mug at lower edge, laptop visible at side",
        "emotion": "caught mid-scroll, amused disbelief",
        "motion": "holds a mug near her chest, pauses, looks at camera with raised eyebrows, then points the mug slightly toward the laptop",
        "camera": "front-facing phone selfie, casual hand-held desk angle",
        "lighting": "warm evening desk lighting",
        "outfit": "charcoal oversized sweatshirt",
    },
    {
        "name": "11_earbud_glance",
        "scene": "clean study desk, laptop, wireless earbuds case, planner, and one highlighter",
        "framing": "vertical 9:16 close-up selfie, face upper center, laptop blurred behind",
        "emotion": "secretive useful-tip energy",
        "motion": "adjusts one earbud, glances at the laptop, covers a grin, then gives a quick tiny thumbs-up",
        "camera": "front-facing phone with gentle handheld movement",
        "lighting": "soft warm indoor daylight",
        "outfit": "soft pink hoodie",
    },
    {
        "name": "12_printed_pages",
        "scene": "library study table, laptop, annotated printed pages, pen and clear folder",
        "framing": "vertical 9:16 close-to-medium selfie, printed pages in foreground, lower-center caption room",
        "emotion": "academic panic softened by relief",
        "motion": "fans two printed pages briefly, grimaces, then lowers them and points to the laptop with a relieved smile",
        "camera": "front-facing phone, stable with slight handheld drift",
        "lighting": "neutral library overhead softened by window light",
        "outfit": "brown cardigan and simple white tee",
    },
    {
        "name": "13_sticky_note_raise",
        "scene": "warm dorm desk, laptop, notebook, three colorful sticky notes, no readable text",
        "framing": "vertical 9:16 close-up selfie, face slightly right of center, desk visible lower left",
        "emotion": "playful 'you need to see this' excitement",
        "motion": "raises a blank sticky note, hides a smile behind it for a beat, then lowers it and gestures to the laptop",
        "camera": "front-facing phone selfie, casual close framing",
        "lighting": "warm desk lamp with soft ambient room light",
        "outfit": "light oatmeal sweater",
    },
    {
        "name": "14_over_shoulder_check",
        "scene": "student desk with laptop behind her shoulder, notebook, plain pen, small lamp",
        "framing": "vertical 9:16 over-the-shoulder selfie angle, face close, laptop in background",
        "emotion": "checking something twice, then amused confidence",
        "motion": "looks over shoulder at laptop, turns back to camera, half covers mouth, then gives a tiny nod",
        "camera": "front-facing phone held close, slight shoulder turn movement",
        "lighting": "soft warm indoor light with laptop glow",
        "outfit": "dark green zip hoodie",
    },
    {
        "name": "15_tab_chaos",
        "scene": "busy study desk, laptop, notebook with tabs, several loose papers, clear caption space",
        "framing": "vertical 9:16 medium close-up, face upper third, desk chaos at bottom edge",
        "emotion": "overwhelmed for one second, then relieved",
        "motion": "looks down at papers, makes a tiny panic face, then looks back at camera and sweeps one hand toward the laptop",
        "camera": "front-facing phone, small natural shake like a real TikTok clip",
        "lighting": "mixed daylight and warm lamp, realistic student room",
        "outfit": "black sweatshirt with no logo",
    },
    {
        "name": "16_final_soft_reveal",
        "scene": "cozy dorm desk, laptop centered behind her, open notebook, pastel pen, lamp and window",
        "framing": "vertical 9:16 close selfie, face centered, laptop behind and slightly blurred",
        "emotion": "soft impressed smile, quiet confidence",
        "motion": "starts with a neutral face, notices the laptop result, smiles, lightly covers mouth, then presents the laptop with a small palm-up gesture",
        "camera": "front-facing phone, gentle handheld drift, native TikTok feel",
        "lighting": "soft warm daylight with clean face light",
        "outfit": "pale yellow sweatshirt",
    },
]


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def run(cmd: list[str], log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log:
        proc = subprocess.run(cmd, cwd=ROOT, text=True, stdout=log, stderr=subprocess.STDOUT)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed ({proc.returncode}); see {log_path}")


def build_input(index: int, persona: dict[str, str]) -> dict[str, Any]:
    return {
        "variant_id": f"new_same_girl_{index:02d}",
        "product_name": "study workflow tool",
        "human_hook_duration_s": 4,
        "human_hook": {"enabled": True},
        "reference_hook_summary": "same small StudyTok girl template: coy mouth-cover reaction at a desk, laptop proof reveal after the hook",
        "reference_variation_rule": (
            "This must be a newly generated AI real-person opening, not copied from yesterday's same-girl batch. "
            "Keep the template mood but change visible motion, outfit, prop layout, and camera angle."
        ),
        "human_hook_observation": {
            "detected": True,
            "status": "vision_analyzed",
            "observation": {
                "person": {
                    "count": 1,
                    "role": BASE_CHARACTER,
                    "framing": persona["framing"],
                    "identity_policy": "fictional AI student only; do not copy a real creator or any previously generated face",
                },
                "environment": persona["scene"],
                "expression": persona["emotion"],
                "action": persona["motion"],
                "camera": persona["camera"],
                "lighting_color": persona["lighting"],
                "atmosphere": f"{BASE_CHARACTER}, creator-native study panic before a useful product workflow reveal, wearing {persona['outfit']}",
                "differentiation_rule": (
                    f"New {TARGET_DATE} generation {index:02d}: {persona['name']}. "
                    "Do not reuse yesterday's generated clip, exact pose timing, room layout, or outfit."
                ),
                "prompt_inputs": {
                    "scene": persona["scene"],
                    "emotion": persona["emotion"],
                    "motion": persona["motion"],
                    "atmosphere": f"{BASE_CHARACTER}, wearing {persona['outfit']}, creator-native and natural",
                    "framing": persona["framing"],
                    "camera_motion": persona["camera"],
                    "must_change": [
                        "new generated clip",
                        "gesture timing",
                        "camera angle",
                        "outfit",
                        "desk layout",
                        "props",
                        "lighting balance",
                    ],
                },
            },
        },
    }


def generate_one(index: int, persona: dict[str, str]) -> dict[str, Any]:
    variant_id = f"new_same_girl_{index:02d}_{persona['name']}"
    variant_dir = OUTPUT / "generated_hooks_new_16" / variant_id
    video_out = variant_dir / "ai_human_hook.mp4"
    card_out = variant_dir / "human_hook_card.json"
    input_path = variant_dir / "human_hook_input.json"

    if video_out.exists() and card_out.exists():
        card = read_json(card_out)
        if card.get("status") == "generated":
            return {
                "index": index,
                "variant_id": variant_id,
                "video": str(video_out.resolve()),
                "human_hook_card": str(card_out.resolve()),
                "reused_existing_in_new_folder": True,
            }

    write_json(input_path, build_input(index, persona))
    run(
        [
            str(PYTHON if PYTHON.exists() else Path(sys.executable)),
            str(RUNNER),
            "--input",
            str(input_path),
            "--out",
            str(card_out),
            "--project-dir",
            str(variant_dir),
            "--generated-dir",
            str(variant_dir),
            "--video-out",
            str(video_out),
            "--poll-timeout",
            "1200",
            "--poll-interval",
            "10",
        ],
        variant_dir / "human_hook_generation.log",
    )
    card = read_json(card_out)
    if card.get("status") != "generated":
        raise RuntimeError(f"{variant_id} hook generation failed: {card.get('generation')}")
    return {
        "index": index,
        "variant_id": variant_id,
        "video": str(video_out.resolve()),
        "human_hook_card": str(card_out.resolve()),
        "reused_existing_in_new_folder": False,
    }


def build_final_16(results: list[dict[str, Any]]) -> None:
    if FINAL_16.exists():
        shutil.rmtree(FINAL_16)
    FINAL_16.mkdir(parents=True, exist_ok=True)

    final_items: list[dict[str, Any]] = []
    for item in sorted(results, key=lambda payload: payload["index"]):
        src = Path(item["video"])
        final_name = f"{item['index']:02d}_{item['variant_id']}.mp4"
        dest = FINAL_16 / final_name
        shutil.copy2(src, dest)
        final_items.append(
            {
                "index": item["index"],
                "variant_id": item["variant_id"],
                "source_video": str(src),
                "final_video": str(dest.resolve()),
                "human_hook_card": item["human_hook_card"],
                "generation_date": TARGET_DATE,
                "new_generation": True,
            }
        )

    write_json(
        FINAL_16 / "same_girl_16_manifest.json",
        {
            "status": "ready",
            "label": f"{TARGET_DATE} newly generated same-girl AI human hooks",
            "requested_count": 16,
            "actual_count": len(final_items),
            "rule": f"All 16 clips were generated in this {TARGET_DATE} folder and are not copied from the prior same-girl-clearfy-preview final_16 folder.",
            "items": final_items,
        },
    )


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    write_json(
        TARGET / "planned_variants.json",
        [{"index": index, "variant_id": f"new_same_girl_{index:02d}_{persona['name']}"} for index, persona in enumerate(PERSONAS, 1)],
    )

    pending = list(enumerate(PERSONAS, 1))
    results: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for attempt in range(1, 4):
        if not pending:
            break
        print(f"new hook generation attempt {attempt}: {len(pending)} pending", flush=True)
        next_pending: list[tuple[int, dict[str, str]]] = []
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = {pool.submit(generate_one, index, persona): (index, persona) for index, persona in pending}
            for future in as_completed(futures):
                index, persona = futures[future]
                variant_id = f"new_same_girl_{index:02d}_{persona['name']}"
                try:
                    result = future.result()
                    print(f"generated {variant_id}", flush=True)
                    results = [item for item in results if item["index"] != index]
                    results.append(result)
                    write_json(TARGET / "hook_generation_manifest.partial.json", sorted(results, key=lambda item: item["index"]))
                except Exception as error:
                    print(f"failed {variant_id}: {error}", flush=True)
                    failures.append({"attempt": attempt, "variant_id": variant_id, "error": str(error)})
                    write_json(TARGET / "hook_generation_failures.partial.json", failures)
                    next_pending.append((index, persona))
        pending = next_pending
        if pending and attempt < 3:
            time.sleep(20)

    if pending:
        raise RuntimeError(f"failed to generate all new same-girl hooks after retries: {[item[0] for item in pending]}")

    build_final_16(results)
    write_json(
        TARGET / "hook_generation_manifest.json",
        {
            "status": "ready",
            "requested_count": 16,
            "generated_count": len(results),
            "final_16": str(FINAL_16.resolve()),
            "items": sorted(results, key=lambda item: item["index"]),
        },
    )
    print(f"done: {FINAL_16}", flush=True)


if __name__ == "__main__":
    main()
