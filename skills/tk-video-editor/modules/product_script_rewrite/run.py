#!/usr/bin/env python3
"""Create a product_script_card.json from a viral pattern card and product profile."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from _shared import base_parser, load_json, score_from_count, write_json


def product_value(product: dict, key: str, fallback: str) -> str:
    value = product.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, list) and value:
        first = value[0]
        if isinstance(first, str):
            return first
        if isinstance(first, dict):
            for candidate in ["user_benefit", "feature_name", "description", "visual_need"]:
                if isinstance(first.get(candidate), str) and first[candidate].strip():
                    return first[candidate].strip()
    return fallback


def product_name(product: dict) -> str:
    return product_value(product, "product_name", product_value(product, "name", "the tool"))


def target_user(product: dict) -> str:
    return product_value(product, "target_users", product_value(product, "target_user", "people doing this workflow"))


def pain_point(product: dict) -> str:
    return product_value(
        product,
        "most_painful_user_scenarios",
        product_value(product, "main_pain_points", "wasting time before the real work starts"),
    )


def feature_items(product: dict) -> list[dict]:
    features = product.get("core_features", [])
    if not isinstance(features, list):
        return []
    out: list[dict] = []
    for item in features:
        if isinstance(item, dict):
            out.append(item)
        elif isinstance(item, str):
            out.append({"feature_name": item, "description": item, "user_benefit": item, "visual_need": ""})
    return out


def pick_feature(product: dict, index: int = 0) -> dict:
    features = feature_items(product)
    if not features:
        return {
            "feature_name": "product workflow",
            "description": "supported product workflow",
            "user_benefit": "helps users move through the workflow faster",
            "visual_need": "Product screen recording showing the workflow.",
        }
    return features[min(index, len(features) - 1)]


def feature_text(feature: dict, key: str, fallback: str = "") -> str:
    value = feature.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback


def creator_action(text: str) -> str:
    cleaned = text.strip().rstrip(".")
    prefixes = [
        "Helps users ",
        "helps users ",
        "Help users ",
        "help users ",
    ]
    for prefix in prefixes:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):]
            break
    return cleaned[:1].lower() + cleaned[1:] if cleaned else "move faster through the workflow"


def creator_pain(text: str) -> str:
    cleaned = text.strip().rstrip(".")
    replacements = {
        "A student starts a literature review and opens 30-50 random tabs": "starting a literature review with 30-50 random tabs open",
        "A student wastes hours before actually writing anything": "wasting hours before actually writing anything",
        "A PhD or Master student does not know which papers are worth reading first": "not knowing which papers are worth reading first",
        "A researcher has papers but does not know how to organize them into a review structure": "having papers but no clear review structure",
    }
    return replacements.get(cleaned, cleaned)


def short_caption(text: str, max_len: int = 46) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= max_len:
        return cleaned
    words = cleaned.split()
    out: list[str] = []
    for word in words:
        candidate = " ".join(out + [word])
        if len(candidate) > max_len:
            break
        out.append(word)
    return " ".join(out) if out else cleaned[:max_len].rstrip()


def product_angles(product: dict, name: str, pain: str) -> list[str]:
    angles = product.get("good_tiktok_angles")
    if isinstance(angles, list) and angles:
        return [str(a) for a in angles[:3]]
    return [
        f"If your workflow starts with {pain}, this is for you.",
        f"Stop doing {pain} manually.",
        f"I wish I knew {name} before wasting time on {pain}.",
    ]


def build_script(product: dict, script_type: str, style: str, angle: str, hook: str, feature_index: int) -> dict:
    name = product_name(product)
    target = target_user(product)
    pain = creator_pain(pain_point(product))
    feature = pick_feature(product, feature_index)
    proof_feature = pick_feature(product, min(feature_index + 1, max(len(feature_items(product)) - 1, 0)))
    feature_name = feature_text(feature, "feature_name", "product workflow")
    feature_benefit = creator_action(feature_text(feature, "user_benefit", feature_text(feature, "description", "move through the workflow faster")))
    feature_visual = feature_text(feature, "visual_need", "Product screen recording that shows the specific feature being used.")
    proof_name = feature_text(proof_feature, "feature_name", feature_name)
    proof_benefit = creator_action(feature_text(proof_feature, "user_benefit", feature_benefit))
    proof_visual = feature_text(proof_feature, "visual_need", feature_visual)
    cta = product.get("cta") or "try it"

    return {
        "type": script_type,
        "style": style,
        "script_title": hook,
        "script_angle": angle,
        "target_viewer": target,
        "version": "TikTok native creator style",
        "full_script": [
            {
                "time": "0-3s",
                "beat": "hook",
                "voiceover": hook,
                "on_screen_text": short_caption(hook),
                "visual_need": "Strong opening shot showing the user's pain or familiar workflow.",
                "product_feature": "",
            },
            {
                "time": "3-8s",
                "beat": "pain",
                "voiceover": f"I used to waste so much time just {pain} before I could even start writing.",
                "on_screen_text": "Too much time before real work",
                "visual_need": "Handheld laptop shot, messy tabs, scrolling, or frustrated study/work scene.",
                "product_feature": "",
            },
            {
                "time": "8-16s",
                "beat": "solution",
                "voiceover": f"Now I use {name}'s {feature_name} to {feature_benefit}",
                "on_screen_text": feature_name,
                "visual_need": feature_visual,
                "product_feature": feature_name,
            },
            {
                "time": "16-24s",
                "beat": "proof",
                "voiceover": f"Then I use {proof_name} to {proof_benefit}. That gives me a clearer starting point.",
                "on_screen_text": "A clearer starting point",
                "visual_need": proof_visual,
                "product_feature": proof_name,
            },
            {
                "time": "24-30s",
                "beat": "cta",
                "voiceover": f"If this is part of your workflow, {cta} before opening another pile of tabs.",
                "on_screen_text": cta,
                "visual_need": "Clean product end screen, homepage, CTA button, or result hero shot.",
                "product_feature": "",
            },
        ],
        "caption": f"{pain.capitalize()} does not have to be the hardest part.",
        "hashtags": ["#aitools", "#productivity", "#researchtools", "#studenttok", "#workflow"],
        "compliance_notes": product.get("forbidden_claims", []) or [
            "Avoid guaranteed outcomes.",
            "Do not imply the product replaces user judgment.",
        ],
    }


def literfy_hook(script_type: str) -> str:
    if script_type == "safe_version":
        return "Still starting your literature review with 50 random tabs?"
    if script_type == "viral_version":
        return "Still using Google Scholar like this for your literature review?"
    return "How to start your literature review like a PhD/Master student (The easy way)"


def build_literfy_workflow_script(product: dict, script_type: str, style: str, hook: str) -> dict:
    name = product_name(product)
    cta = product.get("cta") or "try Literfy"
    opening_hook = literfy_hook(script_type)
    return {
        "type": script_type,
        "style": style,
        "script_title": opening_hook,
        "script_angle": "Google Scholar trust hook to real-papers literature review workflow",
        "caption_adaptation": {
            "reference_style": "research.connect Google Scholar academic workflow demo",
            "grammar_preserved": [
                "How to ... like a PhD/Master student (The easy way)",
                "Just go to this website!",
                "Click ...",
                "Type ...",
                "Pro tip! ...",
                "Then ...",
                "It's done! let's see...",
                "[result proof]!"
            ],
            "safety_change": "Result proof is rewritten as a review draft based on real papers, not a perfect or submission-ready literature review."
        },
        "target_viewer": target_user(product),
        "version": "TikTok native creator style",
        "full_script": [
            {
                "time": "0-3s",
                "beat": "hook",
                "voiceover": opening_hook,
                "on_screen_text": opening_hook,
                "visual_need": "Google Scholar or familiar academic search screen as trust object.",
                "product_feature": "",
            },
            {
                "time": "3-5s",
                "beat": "strong_cta",
                "voiceover": "Just go to this website!",
                "on_screen_text": "Just go to this website!",
                "visual_need": "Literfy landing page or website homepage with Literature Review button visible.",
                "product_feature": "Literature Review Outline",
            },
            {
                "time": "5-8s",
                "beat": "product_reveal",
                "voiceover": "Click Literature Review",
                "on_screen_text": "Click Literature Review",
                "visual_need": "Literfy dashboard with Literature Review or review button visible.",
                "product_feature": "Literature Review Outline",
            },
            {
                "time": "8-11s",
                "beat": "input_topic",
                "voiceover": "Type your literature review topic",
                "on_screen_text": "Type your literature review topic",
                "visual_need": "Screen recording of typing a research topic.",
                "product_feature": "Find Papers",
            },
            {
                "time": "11-15s",
                "beat": "real_papers",
                "voiceover": "It finds real papers for your topic",
                "on_screen_text": "It finds real papers for your topic",
                "visual_need": "Paper results list, related papers, ranked papers, or real academic paper cards.",
                "product_feature": "Paper Discovery / Related Papers",
            },
            {
                "time": "15-18s",
                "beat": "select_papers",
                "voiceover": "Pro tip! select the papers first",
                "on_screen_text": "Pro tip! select the papers first",
                "visual_need": "Selecting or filtering papers before generating an outline.",
                "product_feature": "Paper Discovery / Related Papers",
            },
            {
                "time": "18-22s",
                "beat": "generate_outline",
                "voiceover": "Then generate the outline",
                "on_screen_text": "Then generate the outline",
                "visual_need": "Click generate outline button or outline generation action.",
                "product_feature": "Literature Review Outline",
            },
            {
                "time": "22-26s",
                "beat": "outline_proof",
                "voiceover": "It's done! let's see...",
                "on_screen_text": "It's done! let's see...",
                "visual_need": "Generated literature review outline with sections.",
                "product_feature": "Literature Review Outline",
            },
            {
                "time": "26-30s",
                "beat": "generate_review",
                "voiceover": "Now turn it into a review draft",
                "on_screen_text": "Now turn it into a review draft",
                "visual_need": "Click generate full review button.",
                "product_feature": "AI Literature Review Draft",
            },
            {
                "time": "30-35s",
                "beat": "result_cta",
                "voiceover": f"A literature review draft based on real papers! Review and edit before you keep writing. {cta}.",
                "on_screen_text": "A review draft based on real papers!",
                "visual_need": "Generated literature review draft based on selected papers.",
                "product_feature": "AI Literature Review Draft",
            },
        ],
        "caption": "A literature review should start from real papers, not chaos.",
        "hashtags": ["#literaturereview", "#researchtools", "#phdstudent", "#gradstudent", "#aitools"],
        "compliance_notes": product.get("forbidden_claims", []) or [
            "Do not tell users to submit AI output directly.",
            "Do not claim perfect accuracy or replacement of real research.",
        ],
    }


def build_card(data: dict) -> dict:
    product = data.get("product") or {}
    if "product_script_card" in data and isinstance(data["product_script_card"], dict):
        return data["product_script_card"]

    name = product_name(product)
    pain = pain_point(product)

    hooks = product_angles(product, name, pain)
    while len(hooks) < 3:
        hooks.append(f"I wish I knew {name} before wasting time on {pain}.")

    if product_name(product).lower() == "literfy":
        scripts = [
            build_literfy_workflow_script(product, "safe_version", "truthful, specific, not exaggerated", hooks[0]),
            build_literfy_workflow_script(product, "viral_version", "stronger hook, faster rhythm", hooks[1]),
            build_literfy_workflow_script(product, "native_creator_version", "casual user recommendation", hooks[2]),
        ]
    else:
        scripts = [
            build_script(product, "safe_version", "truthful, specific, not exaggerated", "pain-saving workflow", hooks[0], 0),
            build_script(product, "viral_version", "stronger hook, faster rhythm", "anti-manual-work shortcut", hooks[1], 0),
            build_script(product, "native_creator_version", "casual user recommendation", "I wish I knew this earlier", hooks[2], 1),
        ]

    return {
        "viral_pattern_card_ref": data.get("viral_pattern_card_ref", ""),
        "platform": data.get("platform", "TikTok"),
        "video_length": data.get("video_length", "25-35s"),
        "tone": data.get("tone", "native creator style, casual, not too salesy"),
        "product": product,
        "scripts": scripts,
        "allowed_feature_names": [feature_text(f, "feature_name", "") for f in feature_items(product)],
        "forbidden_claims": product.get("forbidden_claims", []),
        "scores": {
            "hook_strength": 8,
            "product_fit": score_from_count(len(feature_items(product))),
            "native_tiktok_feel": 7,
            "clarity": 8,
            "conversion_potential": 7,
            "claim_safety": 8 if product.get("forbidden_claims") else 6,
        },
    }


def main() -> None:
    parser = base_parser(__doc__ or "", "output/product_script_card.json")
    args = parser.parse_args()
    data = load_json(args.input)
    write_json(args.out, build_card(data))


if __name__ == "__main__":
    main()
