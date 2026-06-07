#!/usr/bin/env python3
"""Build 16 meme-copy product videos for Literfy, FigPad, and Citely only."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SOURCE_BATCH = REPO / "projects/batch/ariana-study-7637977216189500685-16-ai-humans"
TARGET_DATE = os.environ.get("SAME_GIRL_BATCH_DATE", "2026-06-07")
HOOK_DIR = REPO / f"projects/generated/{TARGET_DATE}_same-girl-new-ai-human-hooks/output/final_16"
TARGET_BATCH = REPO / f"projects/batch/{TARGET_DATE}_16-videos_3-products-meme-same-girl"
RENDERER = REPO / "skills/tk-video-editor/modules/video_rendering/run.py"
PYTHON = REPO / ".venv/bin/python3"

PRODUCT_SEQUENCE = (
    ["literfy"] * 6
    + ["figpad"] * 5
    + ["citely"] * 5
)
PRODUCT_ORDER = ["literfy", "figpad", "citely"]
YELLOW = [255, 232, 105, 255]
WHITE = [255, 255, 255, 255]
BLACK = [0, 0, 0, 245]

HIGHLIGHTS = {
    "literfy": [
        "Literfy",
        "sources",
        "source",
        "papers",
        "paper",
        "trail",
        "outline",
        "tabs",
    ],
    "figpad": [
        "FigPad",
        "figure",
        "figures",
        "chart",
        "SVG",
        "PPTX",
        "editable",
        "labels",
    ],
    "citely": [
        "Citely",
        "citation",
        "citations",
        "reference",
        "references",
        "sources",
        "source",
        "claim",
    ],
}

MEME_COPY = {
    "literfy": [
        [
            "me after opening 47 tabs for one paragraph",
            "Literfy said: stop cosplaying chaos",
            "actual papers in one trail",
            "outline first, panic later",
        ],
        [
            "my source list was giving group project energy",
            "drop the topic in Literfy",
            "real papers show up together",
            "suddenly I have a plan",
        ],
        [
            "advisor asked for receipts and I saw my life flash",
            "Literfy keeps the source trail visible",
            "pick the papers I used",
            "the outline is not vibes-based",
        ],
        [
            "POV: your tabs are fighting for custody",
            "Literfy pulls the papers into one place",
            "save the sources before writing",
            "less tab soup, more research",
        ],
        [
            "me pretending random tabs are a methodology",
            "Literfy makes the paper trail obvious",
            "choose sources on purpose",
            "now the outline has receipts",
        ],
        [
            "the browser tabs were one bad decision from collapse",
            "Literfy keeps papers and notes together",
            "the source trail stays clean",
            "academic chaos got nerfed",
        ],
    ],
    "figpad": [
        [
            "when the figure looks like it survived a group chat",
            "FigPad turns the idea into a figure",
            "open it in SVG edit",
            "fix labels like a normal person",
        ],
        [
            "my chart was giving screenshot energy",
            "FigPad makes it editable",
            "labels are still changeable",
            "PPTX export saves the day",
        ],
        [
            "PI said make it cleaner and I entered flight mode",
            "FigPad generates the first pass",
            "SVG edit handles the cleanup",
            "not stuck with a flat image",
        ],
        [
            "that figure was not conference-ready, be serious",
            "FigPad gets the layout started",
            "edit the labels after",
            "export as SVG or PPTX",
        ],
        [
            "me making a science figure with pure hope",
            "FigPad does the heavy layout",
            "then I tweak the details",
            "editable figure, less suffering",
        ],
    ],
    "citely": [
        [
            "when the citation looks a little too confident",
            "Citely checks the reference trail",
            "paste the suspicious citation",
            "see what actually matches",
        ],
        [
            "fake citation jumpscare? no thank you",
            "open Citely before trusting it",
            "verify the reference",
            "trace it back to real sources",
        ],
        [
            "me trusting a random reference like it raised me",
            "Citely makes me verify first",
            "check the claim",
            "then follow the source trail",
        ],
        [
            "that reference had main character energy",
            "Citely puts it on trial",
            "verify references fast",
            "only cite what checks out",
        ],
        [
            "citation list said trust me bro",
            "Citely said run the check",
            "match the reference",
            "sources or it did not happen",
        ],
    ],
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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


def source_index(target_index: int) -> int:
    return ((target_index - 1) % 4) + 1


def caption_style(product: str, beat: str, text: str) -> dict:
    style = {
        "font_size": 56,
        "min_font_size": 40,
        "max_width": 720,
        "max_height": 320,
        "y_ratio": 0.50,
        "line_gap": 6,
        "fill": WHITE,
        "stroke_fill": BLACK,
        "highlight_terms": HIGHLIGHTS[product],
        "highlight_fill": YELLOW,
    }
    if beat == "hook":
        style["font_size"] = 54
        style["y_ratio"] = 0.55
    if len(text) > 38:
        style["font_size"] = 50
    return style


def product_copy(product: str, target_index: int) -> list[str]:
    variants = MEME_COPY[product]
    return variants[(target_index - 1) % len(variants)]


def selected_product_beats(product: str, edit_plan: list[dict]) -> list[dict]:
    product_beats = [deepcopy(item) for item in edit_plan if item.get("beat") != "hook"]
    if product == "literfy":
        return product_beats[:3]
    if product == "figpad":
        return product_beats[:3]
    if product == "citely":
        return product_beats[:3]
    raise ValueError(product)


def set_segment_duration(item: dict, duration: float) -> None:
    start = float(item.get("clip_start") or 0)
    item["clip_end"] = round(start + duration, 3)


def make_variant(product: str, product_index: int, global_index: int, hook_path: Path) -> dict:
    source_id = f"{product}_human_{source_index(product_index):02d}"
    target_id = f"{product}_meme_girl_{product_index:02d}"
    source_output = SOURCE_BATCH / product / source_id / "output"
    target_output = TARGET_BATCH / product / target_id / "output"
    target_output.mkdir(parents=True, exist_ok=True)

    plan = read_json(source_output / "shot_matching_plan.json")
    assets = read_json(source_output / "asset_library.json")
    copy = product_copy(product, product_index)

    hook = deepcopy(plan["edit_plan"][0])
    hook["beat"] = "hook"
    hook["clip_id"] = "ai_human_hook"
    hook["clip_start"] = 0
    hook["clip_end"] = 4
    hook["playback_speed"] = 1
    hook["voiceover"] = copy[0]
    hook["on_screen_text"] = copy[0]
    hook["reason"] = f"New {TARGET_DATE} same-girl AI hook with native meme copy; unique across the 16-video batch."
    hook["caption_style"] = caption_style(product, "hook", copy[0])

    product_beats = selected_product_beats(product, plan.get("edit_plan") or [])
    durations = [3, 3, 3.5]
    rebuilt = [hook]
    for beat_item, text, duration in zip(product_beats, copy[1:], durations):
        beat_item["voiceover"] = text
        beat_item["on_screen_text"] = text
        set_segment_duration(beat_item, duration)
        beat_item["caption_style"] = caption_style(product, str(beat_item.get("beat") or ""), text)
        rebuilt.append(beat_item)

    plan["variant_id"] = target_id
    plan["reference_template"] = "same-girl-meme-copy-short-product-proof"
    plan["edit_plan"] = rebuilt
    plan["risk_notes"] = [
        f"Clearfy is intentionally excluded because the product is upgrading; this batch uses {PRODUCT_ORDER} only.",
        f"Opening hook uses a newly generated {TARGET_DATE} same-girl fictional student clip and is not reused.",
        "Caption styling is restrained: white text, black stroke, yellow highlights only.",
        "Copy uses casual US/EU-native meme phrasing while keeping product claims workflow-safe.",
        "Runtime target is 12-15 seconds by using hook plus three product proof beats.",
    ]

    asset_items = assets.get("assets") if isinstance(assets, dict) else assets
    for asset in asset_items:
        if asset.get("clip_id") == "ai_human_hook":
            asset["file_path"] = str(hook_path)
            asset["duration"] = 4.042
            asset["orientation"] = "vertical_ai_same_girl_selfie_intro"
            asset["scene"] = "small StudyTok girl at desk with laptop, coy reaction before product proof"
            asset["emotion"] = "meme-style academic panic / amused discovery"
            asset["notes"] = f"Unique newly generated {TARGET_DATE} same-girl AI opening hook assigned from final_16."

    if isinstance(assets, dict):
        assets["updated_at"] = f"{TARGET_DATE}T00:00:00+08:00"
        assets["note"] = "AI hook replaced with unique newly generated same-girl clip; only yellow subtitle highlights used."

    shot_plan = target_output / "shot_matching_plan.json"
    asset_library = target_output / "asset_library.json"
    video = target_output / f"{target_id}_meme_product_video.mp4"
    report = target_output / "render_report.json"
    write_json(shot_plan, plan)
    write_json(asset_library, assets)
    return {
        "index": global_index,
        "product": product,
        "variant_id": target_id,
        "source_variant_id": source_id,
        "hook_video": str(hook_path),
        "shot_plan": str(shot_plan),
        "asset_library": str(asset_library),
        "video": str(video),
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

    if TARGET_BATCH.exists():
        shutil.rmtree(TARGET_BATCH)
    (TARGET_BATCH / "output").mkdir(parents=True, exist_ok=True)

    per_product_seen: Counter[str] = Counter()
    assignments: list[dict] = []
    for global_index, (product, hook_path) in enumerate(zip(PRODUCT_SEQUENCE, hooks), 1):
        per_product_seen[product] += 1
        assignments.append(make_variant(product, per_product_seen[product], global_index, hook_path.resolve()))

    write_json(
        TARGET_BATCH / "hook_assignment_manifest.json",
        {
            "status": "prepared",
            "target_date": TARGET_DATE,
            "rule": "16 unique same-girl hooks; products distributed as Literfy 6, FigPad 5, Citely 5; Clearfy excluded.",
            "products": PRODUCT_ORDER,
            "excluded_products": ["clearfy"],
            "assignments": assignments,
        },
    )

    rendered: list[dict] = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(render_variant, item): item for item in assignments}
        for future in as_completed(futures):
            result = future.result()
            rendered.append(result)
            print(f"rendered {result['variant_id']} {result['width']}x{result['height']} {result['duration_seconds']}s")

    rendered.sort(key=lambda item: item["index"])
    deliverables = []
    for item in rendered:
        deliverables.append(
            {
                "index": item["index"],
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
                "template_label": "Same-girl meme hook + short product proof",
                "asset_type": "captioned product video",
                "folder_layout": "product/variant/output",
            }
        )

    batch_manifest = {
        "status": "ready",
        "target_date": TARGET_DATE,
        "requested_count": 16,
        "products": PRODUCT_ORDER,
        "excluded_products": ["clearfy"],
        "product_counts": dict(Counter(item["product"] for item in rendered)),
        "rule": "16 total videos; Literfy 6, FigPad 5, Citely 5; Clearfy paused while upgrading; all videos target 12-15 seconds.",
        "render_results": rendered,
        "deliverables": deliverables,
    }
    write_json(TARGET_BATCH / "batch_manifest.json", batch_manifest)
    write_json(
        TARGET_BATCH / "output/final_delivery_manifest.json",
        {
            "status": "ready",
            "label": "Same-girl meme 3 products 16 videos",
            "source_manifest": "batch_manifest.json",
            "deliverables": deliverables,
        },
    )
    write_json(
        TARGET_BATCH / "project_job.json",
        {
            "project_id": TARGET_BATCH.name,
            "project_dir": f"projects/batch/{TARGET_BATCH.name}",
            "product_name": "Same-girl meme 3 products 16 videos",
            "workflow_mode": "mixed",
            "stages": [],
            "delivery": {
                "mode": "batch_manifest_import",
                "render_report": "output/final_delivery_manifest.json",
            },
        },
    )
    print(f"done {TARGET_BATCH}")


if __name__ == "__main__":
    main()
