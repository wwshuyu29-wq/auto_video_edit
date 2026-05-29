#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_BATCH = ROOT / "projects" / "batch" / "ariana-study-7637977216189500685"
TARGET_BATCH = ROOT / "projects" / "batch" / "ariana-study-7637977216189500685-16-ai-humans"
HUMAN_HOOK_RUNNER = ROOT / "skills" / "tk-video-editor" / "modules" / "human_hook_generation" / "run.py"
VIDEO_RENDER_RUNNER = ROOT / "skills" / "tk-video-editor" / "modules" / "video_rendering" / "run.py"


PRODUCTS = ["literfy", "figpad", "clearfy", "citely"]


HOOK_TEXT: dict[str, list[str]] = {
    "literfy": [
        "bro... advisors are checking sources now...",
        "wait... my advisor asked where every source came from...",
        "me realizing random tabs are not a research trail...",
        "when the lit review needs receipts now...",
    ],
    "figpad": [
        "bro... PIs can tell when a figure is just AI now...",
        "me when the lab asks for editable figures...",
        "wait... this figure has to survive slide edits...",
        "when a diagram can't just be a flat image anymore...",
    ],
    "clearfy": [
        "bro... professors are checking AI wording now...",
        "me rereading the sentence that sounds too robotic...",
        "wait... this paragraph sounds suspiciously AI...",
        "when the draft needs to sound like me again...",
    ],
    "citely": [
        "bro... professors are checking fake citations now...",
        "me when one citation looks a little too perfect...",
        "wait... I need to prove this source is real...",
        "when the reference list starts looking suspicious...",
    ],
}


PERSONAS: list[dict[str, str]] = [
    {
        "name": "mouth_cover_desk_lamp",
        "framing": "vertical 9:16 close-up selfie, face in the upper half, lower-middle clear for captions",
        "scene": "small dorm desk with a silver laptop, open notebook, sticky notes, and one warm desk lamp",
        "emotion": "caught-off-guard academic panic with nervous amusement",
        "motion": "covers part of the mouth, raises eyebrows, glances down at the laptop, then gives a tiny point toward the screen",
        "camera": "front-facing phone selfie with a slight lean-in and gentle handheld drift",
        "lighting": "warm desk lamp lighting with soft shadows",
        "outfit": "dark hoodie and simple wired earbuds",
    },
    {
        "name": "forehead_hold_window",
        "framing": "vertical 9:16 medium close-up selfie, shoulders visible, caption-safe lower center",
        "scene": "daytime student room near a window, laptop on a clean desk, loose paper stack on one side",
        "emotion": "stressed but trying not to laugh",
        "motion": "presses fingers to the forehead, looks into camera, looks sideways at the laptop, then exhales with a small hand flip",
        "camera": "front-facing phone camera with a tiny wobble, held slightly below eye level",
        "lighting": "soft daylight from a side window",
        "outfit": "light crewneck sweatshirt and thin glasses",
    },
    {
        "name": "pencil_freeze_library",
        "framing": "vertical 9:16 close-up selfie, face clear, desk visible at bottom edge",
        "scene": "quiet library table with laptop, pencil, highlighter, and a plain water bottle",
        "emotion": "frozen realization, anxious but funny",
        "motion": "holds a pencil near the lips, freezes, widens eyes, then slowly points the pencil toward the laptop",
        "camera": "front-facing phone selfie, mostly steady with natural hand movement",
        "lighting": "neutral library lighting, not dramatic",
        "outfit": "soft cardigan over a plain t-shirt",
    },
    {
        "name": "hoodie_side_eye",
        "framing": "vertical 9:16 close selfie with the face slightly off-center and captions below",
        "scene": "messy late-night study desk with laptop, coffee cup, notebook, and a few printed pages",
        "emotion": "side-eye panic turning into a knowing look",
        "motion": "leans close to the phone, gives a side-eye toward the laptop, half covers the mouth, then nods once",
        "camera": "handheld phone selfie with subtle vertical sway",
        "lighting": "dim warm bedroom lighting with laptop glow",
        "outfit": "oversized zip hoodie and small hair clip",
    },
]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(cmd: list[str], log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log:
        proc = subprocess.run(cmd, cwd=ROOT, text=True, stdout=log, stderr=subprocess.STDOUT)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(cmd)}; see {log_path}")


def copy_non_hook_assets(product: str, variant_dir: Path) -> None:
    src_library = read_json(SOURCE_BATCH / product / "output" / "asset_library.json")
    assets = src_library.get("assets") if isinstance(src_library, dict) else src_library
    kept = [item for item in assets if isinstance(item, dict) and item.get("clip_id") != "ai_human_hook"]
    if isinstance(src_library, dict):
        src_library["assets"] = kept
        src_library["asset_count"] = len(kept)
        write_json(variant_dir / "output" / "asset_library.json", src_library)
    else:
        write_json(variant_dir / "output" / "asset_library.json", kept)


def build_human_hook_input(product: str, variant_index: int, persona: dict[str, str]) -> dict[str, Any]:
    source = read_json(SOURCE_BATCH / product / "output" / "human_hook_input.json")
    payload = copy.deepcopy(source)
    payload["variant_id"] = f"{product}_human_{variant_index:02d}"
    payload["human_hook_duration_s"] = 4
    payload["human_hook"] = {"enabled": True}
    payload["reference_variation_rule"] = (
        "Generate this as a unique original fictional student creator. "
        "Do not reuse faces, outfits, rooms, pose timing, or gesture sequence from other variants."
    )

    observation = payload.setdefault("human_hook_observation", {}).setdefault("observation", {})
    observation["person"] = {
        "count": 1,
        "role": "original fictional student creator / academic studytok creator",
        "framing": persona["framing"],
        "identity_policy": "do not copy the reference creator or any other generated variant; unique face and styling required",
    }
    observation["action"] = persona["motion"]
    observation["expression"] = persona["emotion"]
    observation["atmosphere"] = "Ariana-style academic panic before a useful workflow reveal, creator-native and confessional"
    observation["environment"] = persona["scene"]
    observation["camera"] = persona["camera"]
    observation["lighting_color"] = persona["lighting"]
    observation["differentiation_rule"] = (
        f"Variant {variant_index}: {persona['name']}. Use a different face, {persona['outfit']}, room layout, props, "
        "lighting, camera distance, and gesture timing from every other variant."
    )
    observation["prompt_inputs"] = {
        "scene": persona["scene"],
        "emotion": persona["emotion"],
        "motion": persona["motion"],
        "atmosphere": f"creator-native study panic, original person wearing {persona['outfit']}",
        "framing": persona["framing"],
        "camera_motion": persona["camera"],
        "must_change": [
            "face",
            "hair",
            "outfit",
            "desk layout",
            "props",
            "lighting",
            "gesture timing",
            "camera distance",
        ],
    }
    return payload


def build_shot_plan(product: str, variant_index: int, variant_dir: Path) -> None:
    plan = read_json(SOURCE_BATCH / product / "output" / "shot_matching_plan.json")
    plan["variant_id"] = f"{product}_human_{variant_index:02d}"
    plan["reference_template"] = "ariana-study-professors-evolving-human-hook"
    first = plan["edit_plan"][0]
    first["on_screen_text"] = HOOK_TEXT[product][variant_index - 1]
    first["voiceover"] = HOOK_TEXT[product][variant_index - 1]
    first["clip_id"] = "ai_human_hook"
    first["clip_start"] = 0
    first["clip_end"] = 4
    first["reason"] = "Unique AI silent selfie reaction for this exact variant; not reused across the batch."
    write_json(variant_dir / "output" / "shot_matching_plan.json", plan)


def generate_hook(product: str, variant_index: int) -> dict[str, Any]:
    variant_id = f"{product}_human_{variant_index:02d}"
    variant_dir = TARGET_BATCH / product / variant_id
    output_dir = variant_dir / "output"
    generated_dir = output_dir / "generated_hooks"
    persona = PERSONAS[variant_index - 1]

    existing_video = generated_dir / "ai_human_hook.mp4"
    existing_card = output_dir / "human_hook_card.json"
    if existing_video.exists() and existing_card.exists():
        card = read_json(existing_card)
        if card.get("status") == "generated":
            return {
                "product": product,
                "variant_id": variant_id,
                "hook_video": str(existing_video.resolve()),
                "human_hook_card": str(existing_card.resolve()),
                "reused_existing": True,
            }

    copy_non_hook_assets(product, variant_dir)
    build_shot_plan(product, variant_index, variant_dir)
    hook_input = build_human_hook_input(product, variant_index, persona)
    input_path = output_dir / "human_hook_input.json"
    write_json(input_path, hook_input)

    run(
        [
            sys.executable,
            str(HUMAN_HOOK_RUNNER),
            "--input",
            str(input_path),
            "--out",
            str(output_dir / "human_hook_card.json"),
            "--project-dir",
            str(variant_dir),
            "--asset-library",
            str(output_dir / "asset_library.json"),
            "--generated-dir",
            str(generated_dir),
            "--video-out",
            str(generated_dir / "ai_human_hook.mp4"),
            "--poll-timeout",
            "1200",
            "--poll-interval",
            "10",
        ],
        output_dir / "human_hook_generation.log",
    )

    card = read_json(output_dir / "human_hook_card.json")
    if card.get("status") != "generated":
        raise RuntimeError(f"{variant_id} hook was not generated: {card.get('generation')}")
    return {
        "product": product,
        "variant_id": variant_id,
        "hook_video": str((generated_dir / "ai_human_hook.mp4").resolve()),
        "human_hook_card": str((output_dir / "human_hook_card.json").resolve()),
        "reused_existing": False,
    }


def render_variant(product: str, variant_index: int) -> dict[str, Any]:
    variant_id = f"{product}_human_{variant_index:02d}"
    variant_dir = TARGET_BATCH / product / variant_id
    output_dir = variant_dir / "output"
    video_out = output_dir / f"{variant_id}_ariana_763797_ai_human_video.mp4"
    run(
        [
            sys.executable,
            str(VIDEO_RENDER_RUNNER),
            "--input",
            str(output_dir / "shot_matching_plan.json"),
            "--asset-library",
            str(output_dir / "asset_library.json"),
            "--preview-render",
            "--preview-out",
            str(video_out),
            "--report-out",
            str(output_dir / "render_report.json"),
        ],
        output_dir / "video_rendering.log",
    )
    report = read_json(output_dir / "render_report.json")
    return {
        "product": product,
        "variant_id": variant_id,
        "video": str(video_out.resolve()),
        "sheet": str(Path(report["outputs"]["preview_sheet"]).resolve()),
        "midpoint_sheet": str(Path(report["outputs"]["preview_midpoint_sheet"]).resolve()),
        "render_report": str((output_dir / "render_report.json").resolve()),
    }


def main() -> None:
    TARGET_BATCH.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE_BATCH / "reference_template_breakdown.json", TARGET_BATCH / "reference_template_breakdown.json")
    shutil.copytree(SOURCE_BATCH / "input", TARGET_BATCH / "input", dirs_exist_ok=True)
    shutil.copytree(SOURCE_BATCH / "references", TARGET_BATCH / "references", dirs_exist_ok=True)

    planned = [
        {"product": product, "variant_id": f"{product}_human_{index:02d}", "persona": PERSONAS[index - 1]["name"]}
        for product in PRODUCTS
        for index in range(1, 5)
    ]
    write_json(TARGET_BATCH / "planned_variants.json", planned)

    hook_results: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    pending = [(product, index) for product in PRODUCTS for index in range(1, 5)]
    for attempt in range(1, 4):
        if not pending:
            break
        print(f"hook generation attempt {attempt}: {len(pending)} pending", flush=True)
        next_pending: list[tuple[str, int]] = []
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = {
                pool.submit(generate_hook, product, index): (product, index)
                for product, index in pending
            }
            for future in as_completed(futures):
                product, index = futures[future]
                variant_id = f"{product}_human_{index:02d}"
                try:
                    result = future.result()
                    print(f"generated {variant_id}", flush=True)
                    hook_results = [item for item in hook_results if item["variant_id"] != variant_id]
                    hook_results.append(result)
                    write_json(TARGET_BATCH / "hook_generation_manifest.partial.json", sorted(hook_results, key=lambda x: x["variant_id"]))
                except Exception as error:
                    print(f"failed {variant_id}: {error}", flush=True)
                    next_pending.append((product, index))
                    failures.append({"attempt": attempt, "variant_id": variant_id, "error": str(error)})
                    write_json(TARGET_BATCH / "hook_generation_failures.partial.json", failures)
        pending = next_pending
        if pending and attempt < 3:
            time.sleep(20)

    if pending:
        raise RuntimeError(f"failed to generate all human hooks after retries: {pending}")

    render_results = []
    for product in PRODUCTS:
        for index in range(1, 5):
            result = render_variant(product, index)
            print(f"rendered {result['variant_id']}", flush=True)
            render_results.append(result)
            write_json(TARGET_BATCH / "render_manifest.partial.json", render_results)

    manifest = {
        "reference_url": "https://www.tiktok.com/@ariana.study/video/7637977216189500685",
        "requested_count": 16,
        "products": PRODUCTS,
        "variants_per_product": 4,
        "rule": "Every variant has a separately generated AI real-person opening hook; no opening human video is reused.",
        "hook_results": sorted(hook_results, key=lambda x: x["variant_id"]),
        "render_results": render_results,
    }
    write_json(TARGET_BATCH / "batch_manifest.json", manifest)
    print(f"done: {TARGET_BATCH / 'batch_manifest.json'}", flush=True)


if __name__ == "__main__":
    main()
