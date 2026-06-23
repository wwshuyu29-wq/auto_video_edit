#!/usr/bin/env python3
"""Build 16 videos from crying-selfie hooks plus product function proof clips."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SOURCE_BATCH = REPO / "projects/batch/ariana-study-7637977216189500685-16-ai-humans"
HOOK_DIR = REPO / "projects/generated/2026-06-01_16-videos_crying-selfie-hooks/output/final_16_snapchat_subtitled"
TARGET_BATCH = REPO / "projects/batch/2026-06-03_16-videos_crying-selfie-product-function"
RENDERER = REPO / "skills/tk-video-editor/modules/video_rendering/run.py"
PYTHON = REPO / ".venv/bin/python3"

PRODUCTS = ["clearfy", "literfy", "figpad", "citely"]
HOOK_SECONDS = 4.083

PRODUCT_COPY = {
    "clearfy": [
        [
            "Paste the draft into Clearfy",
            "Check the AI-heavy sentences",
            "Then humanize only the flagged parts",
            "Read it once before submitting",
            "Keep the meaning. Fix the tone.",
        ],
        [
            "Don't guess what sounds AI",
            "Run the detector first",
            "Find the robotic parts fast",
            "Rewrite with a natural flow",
            "Review the final draft yourself",
        ],
        [
            "Check before your professor does",
            "Clearfy shows risky wording",
            "Use the result as your edit list",
            "Humanize the rough lines",
            "Submit only after reading it",
        ],
        [
            "Deadline mode: scan fast",
            "Spot the AI-looking parts",
            "Clean up the awkward wording",
            "Keep your own argument",
            "One more read, then submit",
        ],
    ],
    "literfy": [
        [
            "Stop opening random paper tabs",
            "Search papers in Literfy",
            "Pick the sources you'll actually use",
            "Save citations while reading",
            "Turn the source list into an outline",
        ],
        [
            "Start with a real paper trail",
            "Find papers by topic",
            "Keep useful sources together",
            "Build the review structure",
            "Write with evidence beside you",
        ],
        [
            "Your lit review needs structure",
            "Collect relevant papers first",
            "Select what supports the argument",
            "Let Literfy organize the outline",
            "Draft from sources, not panic",
        ],
        [
            "Don't cite from memory",
            "Find the source list first",
            "Group the evidence by theme",
            "Export the citation workflow",
            "Then write the review section",
        ],
    ],
    "figpad": [
        [
            "A paper figure can't look messy",
            "Generate a clean figure draft",
            "Open it in SVG Edit",
            "Fix labels and layout yourself",
            "Export PPTX or SVG",
        ],
        [
            "Turn the rough idea into a figure",
            "Use FigPad to draft the visual",
            "Edit the labels online",
            "Tighten the research diagram",
            "Export it for slides",
        ],
        [
            "Don't ship a flat AI image",
            "Make the figure editable",
            "Adjust labels and arrows",
            "Clean up the layout",
            "Export to PPTX",
        ],
        [
            "Research visuals need edits",
            "Generate the science diagram",
            "Refine it in the editor",
            "Make the labels readable",
            "Use it in slides or papers",
        ],
    ],
    "citely": [
        [
            "Fake citations are dangerous",
            "Open Citely first",
            "Paste the suspicious reference",
            "Check what actually matches",
            "Trace it to real sources",
        ],
        [
            "Don't trust random references",
            "Verify the citation",
            "Compare the source matches",
            "Use only what checks out",
            "Keep a source trail",
        ],
        [
            "Before you cite it, verify it",
            "Paste the reference into Citely",
            "Review the match result",
            "Find supporting sources",
            "Then cite with confidence",
        ],
        [
            "Source credibility matters",
            "Run the citation check",
            "See what looks reliable",
            "Find the source evidence",
            "Don't let fake references slide",
        ],
    ],
}

HIGHLIGHTS = {
    "clearfy": ["Clearfy", "AI-heavy", "detector", "humanize", "flagged", "scan"],
    "literfy": ["Literfy", "papers", "sources", "citations", "outline", "review"],
    "figpad": ["FigPad", "figure", "SVG", "PPTX", "labels", "diagram"],
    "citely": ["Citely", "citations", "reference", "verify", "sources", "credible"],
}

HIGHLIGHT_COLORS = {
    "clearfy": [142, 255, 178, 255],
    "literfy": [255, 232, 105, 255],
    "figpad": [126, 221, 255, 255],
    "citely": [255, 175, 214, 255],
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


def style_for(product: str, beat: str, text: str) -> dict:
    style = {
        "font_size": 58,
        "min_font_size": 42,
        "max_width": 720,
        "max_height": 330,
        "y_ratio": 0.48,
        "line_gap": 6,
        "highlight_terms": HIGHLIGHTS[product],
        "highlight_fill": HIGHLIGHT_COLORS[product],
    }
    if beat in {"result", "citation_proof", "source_proof", "action"}:
        style["y_ratio"] = 0.50
    if len(text) > 34:
        style["font_size"] = 54
    return style


def product_texts(product: str, variant_index: int, count: int) -> list[str]:
    texts = PRODUCT_COPY[product][variant_index - 1]
    if count <= len(texts):
        return texts[:count]
    return texts + [texts[-1]] * (count - len(texts))


def make_variant(product: str, variant_index: int, hook_path: Path) -> dict:
    source_id = f"{product}_human_{variant_index:02d}"
    target_id = f"{product}_crying_selfie_{variant_index:02d}"
    source_output = SOURCE_BATCH / product / source_id / "output"
    target_output = TARGET_BATCH / product / target_id / "output"
    target_output.mkdir(parents=True, exist_ok=True)

    plan = read_json(source_output / "shot_matching_plan.json")
    assets = read_json(source_output / "asset_library.json")
    plan["variant_id"] = target_id
    plan["reference_template"] = "crying-selfie-snapchat-caption-hook-plus-product-proof"
    plan["risk_notes"] = [
        "Opening hook is a fictional AI-generated crying selfie clip with burned Snapchat-style upper-middle caption.",
        "The burned hook caption is retained; no second subtitle layer is added during the hook segment.",
        "Product proof copy is framed as a workflow aid, not a guarantee or academic misconduct instruction.",
    ]

    edit_plan = plan.get("edit_plan") or []
    product_beats = [item for item in edit_plan if item.get("beat") != "hook"]
    replacement_texts = product_texts(product, variant_index, len(product_beats))

    for item in edit_plan:
        if item.get("beat") == "hook":
            item["voiceover"] = ""
            item["on_screen_text"] = ""
            item["clip_id"] = "ai_human_hook"
            item["clip_start"] = 0
            item["clip_end"] = HOOK_SECONDS
            item["playback_speed"] = 1
            item["reason"] = "Unique crying-selfie hook with burned Snapchat-style upper-middle caption; used once in this batch."
            item["caption_style"] = {
                "font_size": 1,
                "max_width": 1,
                "max_height": 1,
                "y_ratio": 0.50,
            }
            continue

        text = replacement_texts.pop(0)
        item["voiceover"] = text
        item["on_screen_text"] = text
        item["caption_style"] = style_for(product, str(item.get("beat") or ""), text)

    asset_items = assets.get("assets") if isinstance(assets, dict) else assets
    for asset in asset_items:
        if asset.get("clip_id") == "ai_human_hook":
            asset["file_path"] = str(hook_path)
            asset["duration"] = HOOK_SECONDS
            asset["orientation"] = "vertical_ai_crying_selfie_hook"
            asset["scene"] = "close handheld crying selfie, study panic, Snapchat-style upper-middle caption already burned in"
            asset["emotion"] = "teary academic panic hook"
            asset["notes"] = "Unique hook from final_16_snapchat_subtitled; do not add extra hook subtitle overlay."

    if isinstance(assets, dict):
        assets["updated_at"] = "2026-06-03T00:00:00+08:00"
        assets["note"] = "AI hook replaced with unique crying-selfie Snapchat-captioned clip; product clips retained."

    shot_plan = target_output / "shot_matching_plan.json"
    asset_library = target_output / "asset_library.json"
    video = target_output / f"{target_id}_crying_selfie_product_video.mp4"
    report = target_output / "render_report.json"
    write_json(shot_plan, plan)
    write_json(asset_library, assets)

    return {
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
    stream = meta["streams"][0]
    item["duration_seconds"] = round(float(meta["format"]["duration"]), 3)
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

    assignments = []
    hook_index = 0
    for product in PRODUCTS:
        for variant_index in range(1, 5):
            assignments.append(make_variant(product, variant_index, hooks[hook_index].resolve()))
            hook_index += 1

    write_json(
        TARGET_BATCH / "hook_assignment_manifest.json",
        {
            "status": "prepared",
            "source_hook_dir": str(HOOK_DIR),
            "rule": "16 Snapchat-captioned crying-selfie hooks are assigned one time each; no hook repeats.",
            "products": PRODUCTS,
            "variants_per_product": 4,
            "unique_hook_count": len({item["hook_video"] for item in assignments}),
            "assignments": assignments,
        },
    )

    rendered = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(render_variant, item): item for item in assignments}
        for future in as_completed(futures):
            result = future.result()
            rendered.append(result)
            print(f"rendered {result['variant_id']} {result['width']}x{result['height']} {result['duration_seconds']}s")

    rendered.sort(key=lambda item: (PRODUCTS.index(item["product"]), item["variant_id"]))
    deliverables = []
    for index, item in enumerate(rendered, 1):
        deliverables.append(
            {
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
                "template_label": "Crying-selfie Snapchat hook + product function proof",
                "asset_type": "captioned product video",
                "folder_layout": "product/variant/output",
            }
        )

    product_counts = {product: sum(1 for item in deliverables if item["product"] == product) for product in PRODUCTS}
    batch_manifest = {
        "status": "ready",
        "requested_count": 16,
        "products": PRODUCTS,
        "product_counts": product_counts,
        "variants_per_product": 4,
        "unique_hook_count": len({item["hook_video"] for item in deliverables}),
        "rule": "4 products x 4 videos; the first hook is never repeated and product proof captions are product-specific.",
        "render_results": rendered,
        "deliverables": deliverables,
    }
    write_json(TARGET_BATCH / "batch_manifest.json", batch_manifest)
    write_json(
        TARGET_BATCH / "output/final_delivery_manifest.json",
        {
            "status": "ready",
            "label": "Crying-selfie 4 products x 4 product-function videos",
            "source_manifest": "batch_manifest.json",
            "deliverables": deliverables,
        },
    )
    write_json(
        TARGET_BATCH / "project_job.json",
        {
            "project_id": TARGET_BATCH.name,
            "project_dir": f"projects/batch/{TARGET_BATCH.name}",
            "product_name": "Crying-selfie hooks 4 products 16 videos",
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
