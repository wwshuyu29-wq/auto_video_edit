#!/usr/bin/env python3
"""Create a viral_pattern_card.json from competitor account/video inputs.

This module extracts reusable template logic. It must not write product copy.
When evidence is thin, it writes evidence gaps instead of pretending the
analysis is complete.
"""

from __future__ import annotations

import sys
import re
import json
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from _shared import base_parser, first_nonempty, load_json, score_from_count, write_json


COMMAND_RE = re.compile(r"^(click|open|type|select|choose|upload|paste|generate|go to|use|try|watch|copy|save)\b", re.I)
TEMPLATE_LIBRARY = Path(__file__).resolve().parents[2] / "references" / "template-library.json"


def compact(value: str) -> str:
    return " ".join(str(value or "").replace("\r", "\n").split())


def split_candidate_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw in str(text or "").splitlines():
        cleaned = raw.strip(" -•\t")
        if 3 <= len(cleaned) <= 160:
            lines.append(cleaned)
    if lines:
        return lines

    chunks = re.split(r"(?<=[.!?。！？])\s+", str(text or ""))
    return [chunk.strip() for chunk in chunks if 3 <= len(chunk.strip()) <= 160][:12]


def infer_visible_sequence(videos: list[dict]) -> list[str]:
    explicit: list[str] = []
    for video in videos:
        for key in ["visible_subtitles", "on_screen_text", "subtitle_sequence"]:
            value = video.get(key)
            if isinstance(value, list):
                explicit.extend(str(item).strip() for item in value if str(item).strip())
            elif isinstance(value, str):
                explicit.extend(split_candidate_lines(value))
        transcript = first_nonempty(video.get("transcript"), default="")
        if transcript:
            explicit.extend(split_candidate_lines(transcript))
        frames = first_nonempty(video.get("frames_summary"), default="")
        if frames:
            explicit.extend(split_candidate_lines(frames))
    deduped: list[str] = []
    for line in explicit:
        if line and line not in deduped:
            deduped.append(line)
    return deduped[:12]


def infer_role(line: str, index: int, total: int) -> str:
    lowered = line.lower()
    if index == 0:
        return "hook"
    if index == 1 and any(term in lowered for term in ["website", "site", "go to", "use this", "try this"]):
        return "strong_cta"
    if "pro tip" in lowered or "tip" in lowered:
        return "pro_tip"
    if "done" in lowered or "let's see" in lowered or "lets see" in lowered or "wait" in lowered:
        return "reveal_setup"
    if index >= total - 2 and any(mark in line for mark in ["!", "！"]):
        return "result_proof"
    if COMMAND_RE.search(line):
        if any(term in lowered for term in ["type", "paste", "upload"]):
            return "input"
        return "command"
    if any(term in lowered for term in ["then", "now", "next"]):
        return "workflow_progress"
    if index >= total - 1:
        return "result_proof"
    return "proof"


def punctuation_pattern(lines: list[str], roles: list[str]) -> str:
    marks = []
    joined = " ".join(lines)
    if "?" in joined:
        marks.append("question hook")
    if "!" in joined:
        marks.append("exclamation CTA/proof")
    if "(" in joined and ")" in joined:
        marks.append("parenthetical qualifier")
    if "..." in joined or "…" in joined:
        marks.append("ellipsis reveal")
    if any(role == "pro_tip" for role in roles):
        marks.append("Pro tip beat")
    if any(role == "command" for role in roles):
        marks.append("short command beats")
    return ", ".join(marks) or "short high-contrast captions with direct workflow progression"


def load_template_library() -> list[dict]:
    if not TEMPLATE_LIBRARY.exists():
        return []
    try:
        data = json.loads(TEMPLATE_LIBRARY.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    templates = data.get("templates")
    return templates if isinstance(templates, list) else []


def text_blob(data: dict, lines: list[str]) -> str:
    joined = " ".join(lines).lower()
    account = str(data.get("account_url", "")).lower()
    urls = " ".join(str(v.get("video_url", "")) for v in data.get("video_list") or []).lower()
    captions = " ".join(str(v.get("caption", "")) for v in data.get("video_list") or []).lower()
    requested_template = str(data.get("template_id", "")).lower()
    return " ".join([requested_template, account, urls, captions, joined])


def match_template(data: dict, lines: list[str]) -> dict | None:
    blob = text_blob(data, lines)
    for template in load_template_library():
        if str(template.get("template_id", "")).lower() and str(template.get("template_id", "")).lower() in blob:
            return template
        match = template.get("match") if isinstance(template.get("match"), dict) else {}
        for key in ["accounts", "video_ids", "keywords"]:
            values = match.get(key) if isinstance(match.get(key), list) else []
            if any(str(value).lower() in blob for value in values if str(value).strip()):
                return template
    return None


def template_id(data: dict, lines: list[str]) -> str:
    template = match_template(data, lines)
    if template and template.get("template_id"):
        return str(template["template_id"])
    joined = " ".join(lines).lower()
    account = str(data.get("account_url", "")).lower()
    urls = " ".join(str(v.get("video_url", "")) for v in data.get("video_list") or []).lower()
    if "research.connect" in account or "research.connect" in urls or "google scholar" in joined:
        return "research_connect_google_scholar"
    if "soft.student.era" in account or "soft.student.era" in urls:
        return "soft_student_era_human_hook"
    if "ice.uni" in account or "ice.uni" in urls:
        return "ice_uni_paper_hook"
    return "custom_reference_template"


def build_caption_logic(data: dict, videos: list[dict]) -> tuple[dict, list[str]]:
    supplied = data.get("caption_logic")
    if isinstance(supplied, dict):
        return supplied, []

    lines = infer_visible_sequence(videos)
    gaps: list[str] = []
    template = match_template(data, lines)
    if template and isinstance(template.get("caption_logic"), dict):
        if not lines:
            gaps.append("No explicit visible subtitle sequence was supplied; using canonical caption logic from template-library.json.")
        return dict(template["caption_logic"]), gaps

    if not lines:
        gaps.append("No visible subtitle sequence, transcript, or frame-summary lines were supplied.")
        lines = [
            "Stop doing this manually",
            "Go to this website",
            "Open the workflow",
            "Show the result",
        ]
    roles = [infer_role(line, idx, len(lines)) for idx, line in enumerate(lines)]
    return {
        "template_id": template_id(data, lines),
        "visible_sequence": lines,
        "sentence_roles": roles,
        "punctuation_pattern": punctuation_pattern(lines, roles),
        "command_grammar": [line for line in lines if COMMAND_RE.search(line)],
        "hook_formula": lines[0] if lines else "",
        "cta_position": "early" if any(role == "strong_cta" for role in roles[:3]) else "late_or_soft",
        "result_proof_position": "ending" if roles and roles[-1] in {"result_proof", "bonus_proof"} else "middle_or_missing",
        "reuse_rule": "Preserve sentence roles, pacing, and punctuation rhythm; replace task, product actions, and proof with product-safe equivalents.",
    }, gaps


def build_card(data: dict) -> dict:
    if "viral_pattern_card" in data and isinstance(data["viral_pattern_card"], dict):
        return data["viral_pattern_card"]

    videos = data.get("video_list") or []
    account_url = data.get("account_url", "")
    platform = data.get("target_platform", "TikTok")
    hook_examples = []
    source_videos = []

    for video in videos:
        caption = first_nonempty(video.get("caption"), video.get("title"), default="")
        transcript = first_nonempty(video.get("transcript"), default="")
        frames = first_nonempty(video.get("frames_summary"), default="")
        if caption:
            hook_examples.append(caption[:140])
        source_videos.append({
            "video_url": video.get("video_url", ""),
            "views": video.get("views"),
            "likes": video.get("likes"),
            "comments": video.get("comments"),
            "caption": caption,
            "available_signals": {
                "has_transcript": bool(transcript),
                "has_frames_summary": bool(frames),
                "has_metrics": any(video.get(k) is not None for k in ["views", "likes", "comments"]),
            },
        })

    if not hook_examples:
        hook_examples = [
            "Stop doing this manually",
            "I wish I knew this earlier",
        ]

    caption_logic, evidence_gaps = build_caption_logic(data, videos)
    visible_sequence = caption_logic.get("visible_sequence") if isinstance(caption_logic.get("visible_sequence"), list) else []
    roles = caption_logic.get("sentence_roles") if isinstance(caption_logic.get("sentence_roles"), list) else []
    template_name = str(caption_logic.get("template_id") or template_id(data, [str(x) for x in visible_sequence]))
    library_template = match_template(data, [str(x) for x in visible_sequence])
    account_positioning = str((library_template or {}).get("account_positioning") or "Reference account/video positions a familiar workflow pain as a shortcut demo. Refine with audience and creator voice when more account samples are available.")
    main_content_logic = str((library_template or {}).get("main_content_logic") or "Reference hook -> early CTA or product reveal -> concrete workflow steps -> visible proof -> conversion or save-worthy ending.")
    rewrite_boundaries = (library_template or {}).get("rewrite_boundaries")
    if not isinstance(rewrite_boundaries, list):
        rewrite_boundaries = [
            "Do not write product script in this module.",
            "Do not copy exact reference wording unless it is generic platform grammar.",
            "Only preserve template roles, pacing, and rhetorical shape.",
            "Product claims must be introduced later by product_script_rewrite from product facts.",
        ]
    library_fingerprint = (library_template or {}).get("template_fingerprint")
    if not isinstance(library_fingerprint, dict):
        library_fingerprint = {}

    return {
        "account_url": account_url,
        "target_platform": platform,
        "analysis_goal": data.get("analysis_goal", "Extract reusable product-marketing video structures"),
        "template_id": template_name,
        "account_positioning": account_positioning,
        "main_content_logic": main_content_logic,
        "caption_logic": caption_logic,
        "template_fingerprint": {
            "line_count": len(visible_sequence),
            "roles": roles,
            "has_early_cta": library_fingerprint.get("has_early_cta", any(str(role) == "strong_cta" for role in roles[:3])),
            "has_command_chain": library_fingerprint.get("has_command_chain", any(str(role) in {"command", "input", "simple_action_instruction"} for role in roles)),
            "has_result_reveal": library_fingerprint.get("has_result_reveal", any(str(role) in {"reveal_setup", "result_proof", "bonus_proof", "result_proof_and_emotional_release", "finished_output_relief"} for role in roles)),
            "punctuation_pattern": caption_logic.get("punctuation_pattern", ""),
        },
        "rewrite_boundaries": rewrite_boundaries,
        "viral_patterns": [
            {
                "pattern_name": f"{template_name} workflow shortcut demo",
                "hook_type": "Reference-derived hook: pain/status gap/result promise",
                "hook_examples": hook_examples[:5],
                "opening_0_3s": str(visible_sequence[0]) if visible_sequence else "Open with a specific user pain, status upgrade, or visible result. Avoid slow context.",
                "middle_structure": [
                    "Preserve the reference video's sentence roles.",
                    "Reveal one specific tool or workflow at the same point as the reference.",
                    "Show concrete steps with screen, handheld, or human proof.",
                    "Show the finished or intermediate output instead of only describing benefits.",
                ],
                "ending_cta": "Prompt viewers to try, save, comment a keyword, or visit the tool.",
                "visual_style": {
                    "camera": "Handheld screen footage and/or screen recording",
                    "pace": "One information beat every 1-3 seconds",
                    "subtitle_style": "Large short captions, high contrast, platform-safe placement",
                    "music": "Light background music that does not compete with voice or captions",
                },
                "why_it_works": [
                    "The pain is concrete.",
                    "The workflow feels immediately usable.",
                    "The result is visible.",
                    "The viewer can imagine using the same shortcut.",
                ],
                "reuse_risk": "Do not copy exact wording, brand identity, or unsupported claims. Reuse only the structure.",
            }
        ],
        "recommended_templates": [
            {
                "template_name": "Problem-Solution-Demo-CTA",
                "timeline": [
                    {"time": "0-2s", "purpose": "hook", "content": "State a high-frequency pain or status gap."},
                    {"time": "2-6s", "purpose": "product appears", "content": "Reveal the tool, interface, or result."},
                    {"time": "6-15s", "purpose": "proof", "content": "Show 2-3 key workflow steps."},
                    {"time": "15-22s", "purpose": "result", "content": "Show before/after or finished output."},
                    {"time": "22-28s", "purpose": "CTA", "content": "Invite trial, save, or comment."},
                ],
            }
        ],
        "scores": {
            "hook_clarity": score_from_count(len(hook_examples) + (1 if visible_sequence else 0)),
            "structure_reusability": 8,
            "product_adaptability": 8 if visible_sequence else 5,
            "copy_risk": 3,
            "evidence_strength": score_from_count(len(source_videos)),
        },
        "evidence_gaps": evidence_gaps,
        "source_videos": source_videos,
    }


def main() -> None:
    parser = base_parser(__doc__ or "", "output/viral_pattern_card.json")
    args = parser.parse_args()
    data = load_json(args.input)
    write_json(args.out, build_card(data))


if __name__ == "__main__":
    main()
