#!/usr/bin/env python3
"""Create a shot_matching_plan.json from a product script card and asset library."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from _shared import base_parser, load_json, write_json


def tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 2}


def asset_text(asset: dict) -> str:
    fields = [
        asset.get("clip_id", ""),
        asset.get("shot_type", ""),
        asset.get("camera_motion", ""),
        asset.get("scene", ""),
        asset.get("emotion", ""),
        asset.get("text_overlay_safe_area", ""),
        asset.get("notes", ""),
    ]
    for key in ["visible_objects", "best_use", "not_good_for"]:
        value = asset.get(key)
        if isinstance(value, list):
            fields.extend(str(v) for v in value)
    return " ".join(str(f) for f in fields)


def best_segment(asset: dict) -> tuple[float, float]:
    ranges = asset.get("usable_segments")
    if isinstance(ranges, list) and ranges:
        first = ranges[0]
        return float(first.get("start", 0)), float(first.get("end", min(asset.get("duration", 3), 3)))
    duration = float(asset.get("duration", 3) or 3)
    return 0.0, min(duration, 3.0)


def values_for(asset: dict, key: str) -> list[str]:
    value = asset.get(key)
    if isinstance(value, list):
        return [str(v).lower() for v in value]
    if isinstance(value, str):
        return [value.lower()]
    return []


def beat_asset_boost(beat: dict, asset: dict, used: set[str]) -> int:
    beat_name = str(beat.get("beat", "")).lower()
    visual_need = str(beat.get("visual_need", "")).lower()
    product_feature = str(beat.get("product_feature", "")).lower()
    clip_id = str(asset.get("clip_id", "")).lower()
    best_use = " ".join(values_for(asset, "best_use"))
    not_good = " ".join(values_for(asset, "not_good_for"))
    text = asset_text(asset).lower()

    boost = 0

    if beat_name == "hook":
        if "opening hook" in best_use or "google_scholar" in clip_id or "google scholar" in text:
            boost += 18
        if "product proof" in best_use or "final proof" in text:
            boost -= 10

    if beat_name == "pain":
        if any(term in text for term in ["google scholar", "topic input", "academic search", "many tabs", "study pain"]):
            boost += 10
        if any(term in best_use for term in ["result proof", "final cta"]):
            boost -= 8

    if beat_name == "solution":
        if "product reveal" in best_use or "workflow proof" in best_use or "solution" in best_use:
            boost += 8

    if beat_name in {"strong_cta", "product_reveal"}:
        if beat_name == "strong_cta" and any(term in text for term in ["landing page", "website landing", "homepage", "literature review button", "go to website"]):
            boost += 90
        elif beat_name == "strong_cta":
            boost -= 20
        if any(term in text for term in ["dashboard", "literfy dashboard", "review entry point", "product menu"]):
            boost += 60
        else:
            boost -= 40
        if any(term in text for term in ["generated review outline", "structured outline", "generated review draft", "final proof"]):
            boost -= 50

    if beat_name in {"input_topic"}:
        if any(term in text for term in ["topic input", "typing a research topic", "research topic input"]):
            boost += 16

    if beat_name in {"real_papers"}:
        if "paper_list_results" in clip_id:
            boost += 40
        if any(term in text for term in ["paper results", "paper list", "real papers", "related papers"]):
            boost += 18
        if any(term in text for term in ["select papers", "selected papers", "before generating outline"]):
            boost -= 16

    if beat_name in {"select_papers"}:
        if "select_papers" in clip_id:
            boost += 40
        if any(term in text for term in ["select papers", "selected papers", "checkboxes", "before generating outline"]):
            boost += 18

    if beat_name in {"generate_outline"}:
        if any(term in text for term in ["click generate outline", "generate outline button", "outline action"]):
            boost += 22
        if any(term in text for term in ["generated review outline", "structured outline"]):
            boost -= 8

    if beat_name in {"outline_proof"}:
        if any(term in text for term in ["generated review outline", "structured outline", "review outline"]):
            boost += 22
        if any(term in text for term in ["click generate outline", "generate outline button"]):
            boost -= 8

    if beat_name in {"generate_review"}:
        if any(term in text for term in ["generate full review", "click generate full review", "result trigger"]):
            boost += 22
        if any(term in text for term in ["generated review draft", "paragraphs"]):
            boost -= 8

    if beat_name in {"result_cta"}:
        if any(term in text for term in ["generated review draft", "final proof", "generated review", "paragraphs"]):
            boost += 22

    if beat_name in {"proof", "outline_proof", "result_cta"}:
        if product_feature and product_feature in text:
            boost += 16
        if any(term in text for term in ["outline", "generated review", "real papers", "paper results", "review draft"]):
            boost += 12
        if "opening hook" in best_use:
            boost -= 10

    if beat_name == "cta":
        if any(term in best_use for term in ["final cta", "result proof"]) or any(term in text for term in ["generated review", "dashboard", "homepage"]):
            boost += 10
        if "opening hook" in best_use:
            boost -= 8

    if product_feature and product_feature in text:
        boost += 12

    if beat_name in not_good or any(term in not_good for term in [beat_name, visual_need]):
        boost -= 10

    clip_id_full = str(asset.get("clip_id") or asset.get("id") or Path(asset.get("file_path", "")).stem)
    if clip_id_full in used:
        boost -= 18

    return boost


def choose_asset(beat: dict, assets: list[dict], used: set[str]) -> tuple[dict | None, int]:
    query = " ".join([
        beat.get("beat", ""),
        beat.get("visual_need", ""),
        beat.get("on_screen_text", ""),
        beat.get("voiceover", ""),
    ])
    query_tokens = tokens(query)
    ranked = []
    for asset in assets:
        clip_id = str(asset.get("clip_id") or asset.get("id") or Path(asset.get("file_path", "")).stem)
        overlap = len(query_tokens & tokens(asset_text(asset)))
        quality = int(asset.get("quality_score", 5) or 5)
        ranked.append((overlap * 3 + quality + beat_asset_boost(beat, asset, used), asset))
    ranked.sort(key=lambda item: item[0], reverse=True)
    if not ranked or ranked[0][0] < 5:
        return None, 0
    return ranked[0][1], ranked[0][0]


def selected_script(card: dict) -> dict:
    scripts = card.get("scripts") or []
    if not scripts:
        return {"full_script": []}
    for script in scripts:
        if script.get("type") == "native_creator_version":
            return script
    return scripts[0]


def build_plan(data: dict) -> dict:
    if "shot_matching_plan" in data and isinstance(data["shot_matching_plan"], dict):
        return data["shot_matching_plan"]

    script_card = data.get("product_script_card") or data
    script = selected_script(script_card)
    beats = script.get("full_script") or []
    assets = data.get("asset_library") or data.get("assets") or []
    editing_style = data.get("editing_style") or {
        "pace": "fast",
        "average_clip_duration": "1.5-2.5s",
        "platform": "TikTok",
        "aspect_ratio": "9:16",
    }

    used: set[str] = set()
    edit_plan = []
    missing_assets = []
    risk_notes = []
    matched = 0

    for beat in beats:
        asset, match_score = choose_asset(beat, assets, used)
        if asset is None:
            missing_assets.append({
                "beat": beat.get("beat", ""),
                "need": beat.get("visual_need", ""),
                "suggestion": "Record or upload a vertical clip that clearly supports this beat.",
            })
            edit_plan.append({
                "beat": beat.get("beat", ""),
                "time": beat.get("time", ""),
                "voiceover": beat.get("voiceover", ""),
                "clip_id": "needs_asset",
                "reason": "No asset in the library clearly matches this beat.",
                "on_screen_text": beat.get("on_screen_text", ""),
                "transition": "hard cut",
                "subtitle_priority": "large" if beat.get("beat") == "hook" else "normal",
            })
            continue

        clip_id = str(asset.get("clip_id") or asset.get("id") or Path(asset.get("file_path", "")).stem)
        used.add(clip_id)
        start, end = best_segment(asset)
        matched += 1
        edit_plan.append({
            "beat": beat.get("beat", ""),
            "time": beat.get("time", ""),
            "voiceover": beat.get("voiceover", ""),
            "clip_id": clip_id,
            "clip_start": start,
            "clip_end": end,
            "reason": f"Matches visual need with score {match_score}: {beat.get('visual_need', '')}",
            "on_screen_text": beat.get("on_screen_text", ""),
            "transition": "hard cut" if editing_style.get("pace") == "fast" else "quick dissolve",
            "subtitle_priority": "large" if beat.get("beat") == "hook" else "normal",
        })

    if missing_assets:
        risk_notes.append("Some beats have no strong matching asset; do not render final without revising assets or script.")
    proof_beats = {"proof", "outline_proof", "result_cta", "real_papers"}
    if not any(item.get("beat") in proof_beats and item.get("clip_id") != "needs_asset" for item in edit_plan):
        risk_notes.append("Product proof section is weak or missing matching footage.")

    total = max(len(beats), 1)
    visual_match = round(matched / total * 10)
    return {
        "editing_style": editing_style,
        "edit_plan": edit_plan,
        "missing_assets": missing_assets,
        "risk_notes": risk_notes,
        "needs_script_revision": bool(missing_assets),
        "scores": {
            "visual_match": visual_match,
            "pace_match": 7 if editing_style.get("pace") == "fast" else 6,
            "asset_quality": round(sum(int(a.get("quality_score", 5) or 5) for a in assets) / max(len(assets), 1)),
            "opening_strength": 8 if edit_plan and edit_plan[0].get("clip_id") != "needs_asset" else 4,
            "product_proof_strength": 8 if "Product proof section is weak or missing matching footage." not in risk_notes else 4,
        },
    }


def main() -> None:
    parser = base_parser(__doc__ or "", "output/shot_matching_plan.json")
    args = parser.parse_args()
    data = load_json(args.input)
    write_json(args.out, build_plan(data))


if __name__ == "__main__":
    main()
