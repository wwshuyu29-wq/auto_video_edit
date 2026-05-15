#!/usr/bin/env python3
"""Create a viral_pattern_card.json from competitor account/video inputs.

This deterministic runner is a scaffold and validator. Codex should refine the
output with human-grade judgment when transcripts, frames, and account context
are available.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from _shared import base_parser, first_nonempty, load_json, score_from_count, write_json


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

    caption_logic = data.get("caption_logic")
    if not isinstance(caption_logic, dict):
        # Default from the first analyzed research.connect reference. Codex should
        # refine this from actual visible subtitles whenever available.
        caption_logic = {
            "visible_sequence": [
                "How to write your thesis paper like a PhD/Master student (The easy way)",
                "Just go to this website!",
                "Click researcher",
                "Type your research paper topic",
                "Pro tip! use latex for pdfs",
                "Then watch it do its magic in 2-3 mins",
                "It's done! let's see...",
                "A complete research paper!",
                "With meaningful visualizations!",
            ],
            "sentence_roles": [
                "hook",
                "strong_cta",
                "command",
                "command",
                "pro_tip",
                "time_promise",
                "reveal_setup",
                "result_proof",
                "bonus_proof",
            ],
            "punctuation_pattern": "How to... (The easy way), exclamation CTA, short commands, Pro tip!, Then..., ellipsis before reveal, exclamation result proof",
            "reuse_rule": "Preserve rhythm, sentence roles, and punctuation; replace claims with product-safe equivalents.",
        }

    return {
        "account_url": account_url,
        "target_platform": platform,
        "analysis_goal": data.get("analysis_goal", "Extract reusable product-marketing video structures"),
        "account_positioning": "Needs analyst refinement: describe the account's audience, pain category, and creator voice.",
        "main_content_logic": "Pain or status-gap hook -> tool/workflow reveal -> concrete demo -> visible result -> soft CTA.",
        "caption_logic": caption_logic,
        "viral_patterns": [
            {
                "pattern_name": "Workflow shortcut demo",
                "hook_type": "Pain/status gap/result promise",
                "hook_examples": hook_examples[:5],
                "opening_0_3s": "Open with a specific user pain, status upgrade, or visible result. Avoid slow context.",
                "middle_structure": [
                    "Name the inefficient current workflow.",
                    "Reveal one specific tool or workflow.",
                    "Show 2-3 concrete steps with screen or handheld proof.",
                    "Show the finished output instead of only describing benefits.",
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
            "hook_clarity": score_from_count(len(hook_examples)),
            "structure_reusability": 8,
            "product_adaptability": 7,
            "copy_risk": 3,
            "evidence_strength": score_from_count(len(source_videos)),
        },
        "source_videos": source_videos,
    }


def main() -> None:
    parser = base_parser(__doc__ or "", "output/viral_pattern_card.json")
    args = parser.parse_args()
    data = load_json(args.input)
    write_json(args.out, build_card(data))


if __name__ == "__main__":
    main()
