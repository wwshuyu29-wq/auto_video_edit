#!/usr/bin/env python3
"""Build 16 product videos using newly generated same-girl AI hook clips."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
OLD_BATCH = REPO / "projects/batch/ariana-study-7637977216189500685-16-ai-humans"
TARGET_DATE = os.environ.get("SAME_GIRL_BATCH_DATE", "2026-05-31")
HOOK_DIR = REPO / f"projects/generated/{TARGET_DATE}_same-girl-new-ai-human-hooks/output/final_16"
NEW_BATCH = REPO / f"projects/batch/{TARGET_DATE}_16-videos_new-ai-human-hooks-product-function"
RENDERER = REPO / "skills/tk-video-editor/modules/video_rendering/run.py"
PYTHON = REPO / ".venv/bin/python3"

PRODUCTS = ["literfy", "figpad", "clearfy", "citely"]

HOOK_TEXTS = {
    "literfy": [
        "bro... advisors check sources now 😳",
        "my paper tabs were chaos 😭",
        "wait... this source trail actually helps 👀",
        "no more random paper tabs ✅",
    ],
    "figpad": [
        "when the figure needs to look legit 😳",
        "my chart draft was embarrassing 😭",
        "watch the messy data turn into a figure 👀",
        "need a science figure, not a sketch ✅",
    ],
    "clearfy": [
        "showing the draft I reviewed before submitting 😳",
        "why trust polished AI wording blindly 👀",
        "I check the AI-ish parts first ✅",
        "this draft needed a real cleanup 😭",
    ],
    "citely": [
        "when the reference looks sus 😳",
        "I don't trust random citations anymore 👀",
        "checking the source before I cite it ✅",
        "this citation needed a second look 😭",
    ],
}

HIGHLIGHTS = {
    "literfy": ["sources", "paper", "papers", "trail", "Literfy", "outline"],
    "figpad": ["figure", "chart", "science", "draft", "FigPad"],
    "clearfy": ["draft", "AI", "AI-ish", "reviewed", "cleanup", "Clearfy"],
    "citely": ["reference", "citations", "source", "cite", "Citely"],
}

HIGHLIGHT_COLORS = {
    "literfy": [255, 232, 105, 255],
    "figpad": [126, 221, 255, 255],
    "clearfy": [162, 255, 178, 255],
    "citely": [255, 175, 214, 255],
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ffprobe_duration(path: Path) -> float:
    proc = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(proc.stdout.strip())


def ffprobe_video(path: Path) -> dict:
    proc = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=width,height:format=duration",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


def tune_caption_style(product: str, item: dict, variant_index: int) -> None:
    style = dict(item.get("caption_style") or {})
    style.setdefault("font_size", 58)
    style.setdefault("max_width", 900)
    style.setdefault("line_gap", 6)
    style["highlight_terms"] = HIGHLIGHTS[product]
    style["highlight_fill"] = HIGHLIGHT_COLORS[product]
    if item.get("beat") == "hook":
        style["y_ratio"] = 0.56
        style["font_size"] = 56
        style["max_height"] = 360
    elif variant_index % 2 == 0 and item.get("beat") in {"proof_reveal", "result", "citation_proof"}:
        style["y_ratio"] = 0.50
    item["caption_style"] = style


def add_light_emoji(product: str, item: dict, variant_index: int) -> None:
    if variant_index % 2 != 0:
        return
    beat = item.get("beat")
    text = str(item.get("on_screen_text") or "")
    if any(mark in text for mark in ["👀", "✅", "😭", "😳", "🤯"]):
        return
    if beat in {"proof_reveal", "real_papers", "selection"}:
        item["on_screen_text"] = f"{text} 👀"
        item["voiceover"] = item["on_screen_text"]
    elif beat in {"result", "citation_proof"}:
        item["on_screen_text"] = f"{text} ✅"
        item["voiceover"] = item["on_screen_text"]


def make_variant(product: str, variant_index: int, hook_path: Path) -> dict:
    old_id = f"{product}_human_{variant_index:02d}"
    new_id = f"{product}_girl_{variant_index:02d}"
    old_output = OLD_BATCH / product / old_id / "output"
    new_output = NEW_BATCH / product / new_id / "output"
    new_output.mkdir(parents=True, exist_ok=True)

    plan = read_json(old_output / "shot_matching_plan.json")
    assets = read_json(old_output / "asset_library.json")

    plan["variant_id"] = new_id
    plan["reference_template"] = "same-girl-mouth-cover-desk-laptop-hook"
    plan.setdefault("risk_notes", [])
    plan["risk_notes"] = [
        note for note in plan["risk_notes"] if "Opening AI hook" not in str(note)
    ] + [
        f"Opening AI hook uses a newly generated {TARGET_DATE} same-girl fictional student clip and is not reused within this 16-video batch.",
        "Product claims remain inherited from the previous approved product-proof plan.",
    ]

    edit_plan = plan.get("edit_plan") or []
    if edit_plan:
        edit_plan[0]["voiceover"] = HOOK_TEXTS[product][variant_index - 1]
        edit_plan[0]["on_screen_text"] = HOOK_TEXTS[product][variant_index - 1]
        edit_plan[0]["clip_id"] = "ai_human_hook"
        edit_plan[0]["clip_start"] = 0
        edit_plan[0]["clip_end"] = 4
        edit_plan[0]["playback_speed"] = 1
        edit_plan[0]["reason"] = f"Newly generated {TARGET_DATE} same-girl mouth-cover desk/laptop AI human hook; unique within the batch."
    for item in edit_plan:
        tune_caption_style(product, item, variant_index)
        add_light_emoji(product, item, variant_index)

    asset_items = assets.get("assets") if isinstance(assets, dict) else assets
    for asset in asset_items:
        if asset.get("clip_id") == "ai_human_hook":
            asset["file_path"] = str(hook_path)
            asset["duration"] = 4.042
            asset["orientation"] = "vertical_ai_same_girl_selfie_intro"
            asset["scene"] = "warm dorm desk, laptop draft, notebook, coy smiling student covering mouth then presenting screen"
            asset["emotion"] = "shy proud StudyTok reveal"
            asset["notes"] = f"Unique newly generated {TARGET_DATE} same-girl AI opening hook assigned from the new final_16 folder."

    if isinstance(assets, dict):
        assets["updated_at"] = f"{TARGET_DATE}T00:00:00+08:00"
        assets["note"] = "AI hook replaced with unique newly generated same-girl mouth-cover desk/laptop clip."

    write_json(new_output / "shot_matching_plan.json", plan)
    write_json(new_output / "asset_library.json", assets)

    out_video = new_output / f"{new_id}_same_girl_product_video.mp4"
    report = new_output / "render_report.json"
    return {
        "product": product,
        "variant_id": new_id,
        "source_variant_id": old_id,
        "hook_video": str(hook_path),
        "shot_plan": str(new_output / "shot_matching_plan.json"),
        "asset_library": str(new_output / "asset_library.json"),
        "video": str(out_video),
        "report": str(report),
    }


def render_variant(item: dict) -> dict:
    cmd = [
        str(PYTHON if PYTHON.exists() else Path(sys.executable)),
        str(RENDERER),
        "--input",
        item["shot_plan"],
        "--asset-library",
        item["asset_library"],
        "--preview-render",
        "--preview-out",
        item["video"],
        "--report-out",
        item["report"],
    ]
    subprocess.run(cmd, check=True)
    meta = ffprobe_video(Path(item["video"]))
    duration = float(meta["format"]["duration"])
    stream = meta["streams"][0]
    item["duration_seconds"] = round(duration, 3)
    item["width"] = stream["width"]
    item["height"] = stream["height"]
    item["cover"] = str(Path(item["video"]).with_name(f"{Path(item['video']).stem}_sheet.jpg"))
    item["midpoint_sheet"] = str(Path(item["video"]).with_name(f"{Path(item['video']).stem}_midpoint_sheet.jpg"))
    return item


def main() -> None:
    hooks = sorted(HOOK_DIR.glob("*.mp4"))
    if len(hooks) != 16:
        raise SystemExit(f"Expected 16 hooks in {HOOK_DIR}, found {len(hooks)}")

    if NEW_BATCH.exists():
        shutil.rmtree(NEW_BATCH)
    (NEW_BATCH / "output").mkdir(parents=True, exist_ok=True)

    assignments: list[dict] = []
    hook_iter = iter(hooks)
    for product in PRODUCTS:
        for variant_index in range(1, 5):
            assignments.append(make_variant(product, variant_index, next(hook_iter).resolve()))

    write_json(NEW_BATCH / "hook_assignment_manifest.json", {
        "status": "prepared",
        "rule": f"Each newly generated {TARGET_DATE} same-girl opening clip is used once; no repeated hook video.",
        "products": PRODUCTS,
        "variants_per_product": 4,
        "assignments": assignments,
    })

    rendered: list[dict] = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(render_variant, item): item for item in assignments}
        for future in as_completed(futures):
            result = future.result()
            rendered.append(result)
            print(f"rendered {result['variant_id']} {result['width']}x{result['height']} {result['duration_seconds']}s")

    rendered.sort(key=lambda item: (PRODUCTS.index(item["product"]), item["variant_id"]))

    deliverables = []
    for index, item in enumerate(rendered, 1):
        deliverables.append({
            "index": index,
            "variant": f"{item['product']} / {item['variant_id']}",
            "product": item["product"],
            "video": item["video"],
            "source_video": item["video"],
            "cover": item.get("cover"),
            "midpoint_sheet": item.get("midpoint_sheet"),
            "hook_video": item["hook_video"],
            "duration_seconds": item["duration_seconds"],
            "width": item["width"],
            "height": item["height"],
            "template_label": "Same-girl mouth-cover hook + product function proof",
            "asset_type": "captioned product video",
            "folder_layout": "product/variant/output",
        })

    batch_manifest = {
        "status": "ready",
        "requested_count": 16,
        "products": PRODUCTS,
        "variants_per_product": 4,
        "rule": f"4 products x 4 videos; the first 4 seconds use 16 newly generated {TARGET_DATE} same-girl AI hooks with no repeats.",
        "render_results": rendered,
        "deliverables": deliverables,
    }
    write_json(NEW_BATCH / "batch_manifest.json", batch_manifest)
    write_json(NEW_BATCH / "output/final_delivery_manifest.json", {
        "status": "ready",
        "label": "Same-girl mouth-cover 4 products x 4 videos",
        "source_manifest": "batch_manifest.json",
        "deliverables": deliverables,
    })
    write_json(NEW_BATCH / "project_job.json", {
        "project_id": NEW_BATCH.name,
        "project_dir": f"projects/batch/{NEW_BATCH.name}",
        "product_name": "Same-girl 4 products 16 videos",
        "workflow_mode": "mixed",
        "stages": [],
        "delivery": {
            "mode": "batch_manifest_import",
            "render_report": "output/final_delivery_manifest.json",
        },
    })
    print(f"done {NEW_BATCH}")


if __name__ == "__main__":
    main()
