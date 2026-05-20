#!/usr/bin/env python3
"""Create a product_script_card.json from a viral pattern card and product profile.

The generator is reference-template driven. Product facts decide what can be
said; the viral pattern card decides sentence order, role, and rhythm.
"""

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
        "A researcher has a rough idea but cannot make a clean figure": "messy rough figure ideas",
        "A PhD student draws an ugly sketch and wants to turn it into a polished diagram": "ugly research sketches",
        "A student uses AI to generate references but is not sure whether they are real": "not knowing if AI references are real",
        "A citation looks real but points to the wrong paper": "citations that look real but point to the wrong paper",
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


def split_feature_words(product: dict) -> str:
    features = feature_items(product)
    return " ".join(feature_text(item, "feature_name", "") for item in features).lower()


def product_category(product: dict) -> str:
    return product_value(product, "category", "").lower()


def product_task(product: dict, variant: str) -> str:
    name = product_name(product)
    features = split_feature_words(product)
    category = product_category(product)
    joined = f"{features} {category}"

    if "citation" in joined or "reference" in joined:
        if variant == "viral_version":
            return "check AI-generated references before you trust them"
        if variant == "native_creator_version":
            return "trace sources before putting citations in your paper"
        return "verify references before you rely on them"
    if "figure" in joined or "svg" in joined or "ppt" in joined or "image" in joined:
        if variant == "viral_version":
            return "turn rough research visuals into editable figure drafts"
        if variant == "native_creator_version":
            return "make a scientific figure draft without starting from a blank canvas"
        return "turn a reference image into a scientific figure draft"
    if "paper" in joined or "literature" in joined or "review" in joined:
        if variant == "viral_version":
            return "find real papers before opening 50 random tabs"
        if variant == "native_creator_version":
            return "start a literature review from real papers"
        return "find real papers and organize them before writing"
    return f"use {name} for this workflow"


def result_proof(product: dict, variant: str) -> str:
    features = split_feature_words(product)
    category = product_category(product)
    joined = f"{features} {category}"
    if "citation" in joined or "reference" in joined:
        return "Reference details you can review before trusting them!"
    if "figure" in joined or "svg" in joined or "ppt" in joined or "image" in joined:
        return "A figure draft you can review and edit!"
    if "paper" in joined or "literature" in joined or "review" in joined:
        return "A structured starting point based on real papers!"
    return "A clearer workflow starting point!"


def soft_value_claim(product: dict, variant: str) -> str:
    features = split_feature_words(product)
    category = product_category(product)
    joined = f"{features} {category}"
    if "citation" in joined or "reference" in joined:
        return "it helps me check references before i trust them"
    if "figure" in joined or "svg" in joined or "ppt" in joined or "image" in joined:
        return "it gives me an editable figure draft instead of a static image"
    if "paper" in joined or "literature" in joined or "review" in joined:
        return "it helps me find relevant papers before i start writing"
    return f"it helps me use {product_name(product)} as a starting point"


def simple_instruction(product: dict) -> str:
    features = split_feature_words(product)
    if "citation" in features or "reference" in features or "source" in features:
        return "just paste the claim or reference and check the source"
    if "figure" in features or "svg" in features or "ppt" in features or "image" in features:
        return "just upload your reference or type the figure idea"
    if "paper" in features or "literature" in features or "review" in features:
        return "just type your topic and choose the papers first"
    return "just open the workflow and check the result"


def emotional_result_line(product: dict, variant: str, role: str) -> str:
    features = split_feature_words(product)
    category = product_category(product)
    joined = f"{features} {category}"
    if "citation" in joined or "reference" in joined:
        if "finished_output_relief" in role:
            return "now i know which references need a closer look, goodnight world 🥱💤"
        return "and boom, now i know what to check before trusting it 😭"
    if "figure" in joined or "svg" in joined or "ppt" in joined or "image" in joined:
        if "finished_output_relief" in role:
            return "now i can keep editing the figure instead of starting over 🥱💤"
        return "and boom, now the figure is actually editable 😭"
    if "paper" in joined or "literature" in joined or "review" in joined:
        if "finished_output_relief" in role:
            return "my review finally has a real-paper starting point, goodnight world 🥱💤"
        return "and boom, now i have a structure to review 😭"
    return "and boom, now i know the next step 😭"


def safe_hook(product: dict, variant: str, reference_hook: str = "") -> str:
    task = product_task(product, variant)
    lowered_hook = reference_hook.lower()
    if "saying goodbye" in lowered_hook:
        pain = short_caption(creator_pain(pain_point(product)), 34).lower()
        return f"saying goodbye to {pain} because i can now {task}"
    if "my professor said" in lowered_hook or "my teacher said" in lowered_hook:
        if "citation" in split_feature_words(product) or "reference" in split_feature_words(product):
            return "My professor said references can look real and still be wrong..."
        if "figure" in split_feature_words(product):
            return "My professor said research figures need to stay editable..."
        return "My professor said a review still needs real papers behind it..."
    if "how to" in lowered_hook:
        suffix = ""
        if "like a phd/master student" in lowered_hook:
            suffix = " like a PhD/Master student"
        if "the easy way" in lowered_hook:
            suffix += " (The easy way)"
        return f"How to {task}{suffix}"
    if "still" in lowered_hook or "?" in reference_hook:
        return f"Still doing this manually instead of using {product_name(product)}?"
    if "dont" in lowered_hook or "don't" in lowered_hook:
        return f"Don't make this mistake before you {task}"
    return product_angles(product, product_name(product), pain_point(product))[0]


def feature_by_index(product: dict, index: int) -> dict:
    return pick_feature(product, index)


def title_case_feature(value: str) -> str:
    words = [word for word in re_words(value) if word not in {"relevant", "structured"}]
    return " ".join(word.capitalize() for word in words[:3]) or value.title()


def re_words(value: str) -> list[str]:
    import re
    return re.findall(r"[a-zA-Z0-9]+", value.lower())


def command_for_feature(feature_name: str, product: dict, index: int) -> str:
    lowered = feature_name.lower()
    joined = split_feature_words(product)
    if "find" in lowered and "paper" in lowered:
        return "Click Find Papers"
    if ("source" in lowered or "paper" in lowered) and index > 0:
        return "Pick the sources you want"
    if "verify" in lowered and "reference" in lowered:
        return "Open Verify References"
    if "find" in lowered and "source" in lowered:
        return "Open Find Sources"
    if "citation" in lowered or "reference" in lowered:
        return "Paste the citation first"
    if "image to image" in lowered or ("image" in lowered and "figure" in joined):
        return "Upload a reference image"
    if "text to figure" in lowered:
        return "Type your figure prompt"
    if "svg" in lowered:
        return "Open SVG Editor"
    if "ppt" in lowered or "export" in lowered:
        return "Export the editable file"
    if "review" in lowered and "draft" in lowered:
        return "Then generate the review draft"
    if "outline" in lowered:
        return "Then generate the outline"
    return f"Click {title_case_feature(feature_name)}"


def action_line(product: dict, role: str, index: int, variant: str) -> tuple[str, str, str]:
    name = product_name(product)
    feature = feature_by_index(product, index)
    feature_name = feature_text(feature, "feature_name", "product workflow")
    visual = feature_text(feature, "visual_need", "Product screen recording showing the workflow.")
    role = role.lower()

    if role in {"strong_cta", "cta"}:
        return "Just go to this website!", "website landing page with product logo and main CTA visible", ""
    if role in {"shortcut_action"}:
        if "citation" in split_feature_words(product) or "reference" in split_feature_words(product):
            return "So I check the sources first", visual, feature_name
        if "figure" in split_feature_words(product):
            return "So I keep the figure editable first", visual, feature_name
        return "So I start from real papers first", visual, feature_name
    if role in {"tool_value_claim"}:
        return soft_value_claim(product, variant), visual, feature_name
    if role in {"simple_action_instruction"}:
        return simple_instruction(product), visual, feature_name
    if role in {"quantity_result_proof", "result_proof_and_emotional_release", "finished_output_relief"}:
        return emotional_result_line(product, variant, role), visual, feature_name
    if role in {"command", "product_reveal", "tool_reveal"}:
        if index <= 0:
            return f"Open {name}", visual, feature_name
        return command_for_feature(feature_name, product, index), visual, feature_name
    if role in {"input", "topic_input"}:
        if "figure" in split_feature_words(product):
            return "Upload your reference image", visual, feature_name
        if "citation" in split_feature_words(product) or "reference" in split_feature_words(product):
            return "Paste the claim or citation text", visual, feature_name
        return "Type your research topic", visual, feature_name
    if role in {"pro_tip", "tip"}:
        if "citation" in split_feature_words(product) or "reference" in split_feature_words(product):
            return "Pro tip! check the source before you rely on it", visual, feature_name
        if "figure" in split_feature_words(product):
            return "Pro tip! review the details before exporting", visual, feature_name
        return "Pro tip! choose the sources first", visual, feature_name
    if role in {"time_promise", "workflow_progress"}:
        return "Then let it show the next step", visual, feature_name
    if role in {"reveal_setup"}:
        return "It's done! let's see...", visual, feature_name
    if role in {"result_proof", "bonus_proof", "proof"}:
        return result_proof(product, variant), visual, feature_name
    return f"Then use {feature_name}", visual, feature_name


def normalized_roles(caption_logic: dict) -> list[str]:
    roles = caption_logic.get("sentence_roles") or []
    if isinstance(roles, list) and roles:
        return [str(role) for role in roles]
    sequence = caption_logic.get("visible_sequence") or []
    fallback = ["hook", "strong_cta", "command", "input", "proof", "result_proof"]
    if isinstance(sequence, list) and sequence:
        return [fallback[min(i, len(fallback) - 1)] for i, _ in enumerate(sequence)]
    return fallback


def reference_lines(caption_logic: dict) -> list[str]:
    sequence = caption_logic.get("visible_sequence") or []
    if isinstance(sequence, list) and sequence:
        return [str(item) for item in sequence]
    return []


def time_range(index: int, total: int, max_seconds: int = 30) -> str:
    if total <= 1:
        return f"0-{max_seconds}s"
    if index == 0:
        return "0-3s"
    remaining = max_seconds - 3
    slot = remaining / max(total - 1, 1)
    start = 3 + slot * (index - 1)
    end = 3 + slot * index
    return f"{start:.1f}-{end:.1f}s".replace(".0", "")


def script_has_forbidden_claims(script: dict, product: dict) -> bool:
    forbidden = " ".join(str(item).lower() for item in product.get("forbidden_claims", []) or [])
    if not forbidden:
        return False
    text = " ".join(
        f"{beat.get('voiceover', '')} {beat.get('on_screen_text', '')}"
        for beat in script.get("full_script", [])
    ).lower()
    risky_terms = ["perfect", "100%", "guarantee", "guaranteed", "submit directly", "publication-ready", "replace"]
    return any(term in text for term in risky_terms if term in forbidden or term in text)


def build_reference_driven_script(product: dict, viral_card: dict, script_type: str, style: str) -> dict:
    caption_logic = viral_card.get("caption_logic") if isinstance(viral_card.get("caption_logic"), dict) else {}
    roles = normalized_roles(caption_logic)
    refs = reference_lines(caption_logic)
    if len(refs) < len(roles):
        refs.extend([""] * (len(roles) - len(refs)))

    hook = safe_hook(product, script_type, refs[0] if refs else "")
    action_index = 0
    beats: list[dict] = []
    for idx, role in enumerate(roles):
        role_key = str(role).lower()
        if idx == 0 or role_key == "hook":
            line = hook
            visual_need = "Opening shot that visually matches the reference template and makes the workflow familiar."
            product_feature = ""
            beat_name = "hook"
        else:
            line, visual_need, product_feature = action_line(product, role_key, action_index, script_type)
            if role_key in {
                "command",
                "input",
                "topic_input",
                "product_reveal",
                "tool_reveal",
                "proof",
                "result_proof",
                "bonus_proof",
                "shortcut_action",
                "tool_value_claim",
                "simple_action_instruction",
                "quantity_result_proof",
                "result_proof_and_emotional_release",
                "finished_output_relief",
            }:
                action_index += 1
            beat_name = role_key

        beats.append({
            "time": time_range(idx, len(roles)),
            "beat": beat_name,
            "voiceover": line,
            "on_screen_text": line,
            "visual_need": visual_need,
            "product_feature": product_feature,
            "reference_line": refs[idx] if idx < len(refs) else "",
            "reference_role": role,
        })

    script = {
        "type": script_type,
        "style": style,
        "script_title": hook,
        "script_angle": f"Reference-template adaptation: {viral_card.get('main_content_logic', 'workflow demo')}",
        "caption_adaptation": {
            "source": "viral_pattern_card.caption_logic",
            "roles_preserved": roles,
            "punctuation_pattern": caption_logic.get("punctuation_pattern", ""),
            "reuse_rule": caption_logic.get("reuse_rule", "Preserve structure and replace with product-safe facts."),
            "boundary": "Template logic comes from the reference video; product claims come only from product facts.",
        },
        "target_viewer": target_user(product),
        "version": "TikTok native creator style",
        "full_script": beats,
        "caption": f"Use {product_name(product)} as a workflow starting point, then review the result yourself.",
        "hashtags": ["#researchtools", "#aitools", "#studytok", "#academictok", "#workflow"],
        "compliance_notes": product.get("forbidden_claims", []) or [
            "Avoid guaranteed outcomes.",
            "Do not imply the product replaces user judgment.",
        ],
    }
    if script_has_forbidden_claims(script, product):
        script["needs_claim_review"] = True
    return script


def build_card(data: dict) -> dict:
    product = data.get("product") or {}
    if "product_script_card" in data and isinstance(data["product_script_card"], dict):
        return data["product_script_card"]

    viral_card = data.get("viral_pattern_card") if isinstance(data.get("viral_pattern_card"), dict) else {}
    scripts = [
        build_reference_driven_script(product, viral_card, "safe_version", "truthful, specific, not exaggerated"),
        build_reference_driven_script(product, viral_card, "viral_version", "stronger hook, faster rhythm"),
        build_reference_driven_script(product, viral_card, "native_creator_version", "casual user recommendation"),
    ]

    return {
        "viral_pattern_card_ref": data.get("viral_pattern_card_ref", ""),
        "platform": data.get("platform", "TikTok"),
        "video_length": data.get("video_length", "25-35s"),
        "tone": data.get("tone", "native creator style, casual, not too salesy"),
        "product": product,
        "template_source": {
            "type": "viral_pattern_card",
            "template_id": viral_card.get("template_id", ""),
            "caption_logic_used": bool(viral_card.get("caption_logic")),
            "main_content_logic": viral_card.get("main_content_logic", ""),
        },
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
