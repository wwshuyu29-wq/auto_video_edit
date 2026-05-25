#!/usr/bin/env python3
"""Generate TikTok publishing title, caption, and hashtags from subtitles."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from _shared import base_parser, load_json, write_json


ACADEMIC_TAGS = [
    "#literaturereview",
    "#research",
    "#phd",
    "#gradschool",
    "#masterstudent",
    "#researchpaper",
]

AI_TOOL_TAGS = [
    "#aitools",
    "#studytok",
    "#academictok",
]

PRODUCT_TAGS = {
    "literfy": ["#literfy", "#researchtools"],
    "citely": ["#citely", "#citationcheck", "#researchtools"],
    "figpad": ["#figpad", "#scientificfigures", "#researchtools"],
}

PRODUCT_COPY = {
    "literfy": {
        "task": "start a literature review from real papers",
        "proof": "find real papers, save useful sources, and build a structured starting point you can review",
        "risk": "Do not imply Literfy writes a perfect or submission-ready literature review.",
        "keywords": ["literature review", "real papers", "paper discovery", "research workflow"],
    },
    "citely": {
        "task": "check AI-generated references before trusting them",
        "proof": "trace source trails and review citation details before you rely on them",
        "risk": "Do not imply Citely guarantees every citation is correct.",
        "keywords": ["citation check", "AI references", "source tracing", "reference verification"],
    },
    "figpad": {
        "task": "turn research visuals into editable scientific figure drafts",
        "proof": "generate a figure direction, review the details, and keep editing the output",
        "risk": "Do not imply FigPad guarantees scientifically accurate or journal-ready figures.",
        "keywords": ["scientific figure", "figure draft", "SVG editor", "research visuals"],
    },
}

TEMPLATE_TYPE_SUMMARIES = [
    {
        "template_type": "mistake_urgency_cta",
        "title_logic": "Warn from regret or a past mistake, then point to the safer workflow.",
        "caption_logic": "Short regret line + direct website/tool CTA + proof of the workflow shown in the video.",
        "best_for": "Citation checking, source verification, figure correction, or any task where the user can avoid rework.",
        "example_title_shape": "dont make the mistakes i did. [product-safe task]",
        "example_caption_shape": "dont make the mistakes i did. Use this website before you [risky/manual task]!!! [visible workflow proof].",
    },
    {
        "template_type": "how_to_easy_way",
        "title_logic": "Promise a practical method for a specific academic task.",
        "caption_logic": "Name the task, show the shortcut workflow, and remind users to review the output.",
        "best_for": "Literature review, paper discovery, citation generation, and structured research workflows.",
        "example_title_shape": "How to [task] like a PhD/Master student",
        "example_caption_shape": "How I [task] now: use the tool for the first pass, then review and edit the result.",
    },
    {
        "template_type": "pain_question_solution",
        "title_logic": "Start from a familiar pain or question, then position the product as the cleaner next step.",
        "caption_logic": "Repeat the pain in creator language, introduce the workflow, and show the practical improvement.",
        "best_for": "Messy research starts, too many tabs, confusing citations, or unclear visual drafts.",
        "example_title_shape": "Still [pain]? Try this workflow",
        "example_caption_shape": "[Pain question]. This is the workflow I would use instead. [visible workflow proof].",
    },
    {
        "template_type": "workflow_direct_demo",
        "title_logic": "Lead with a direct workflow promise, usually framed as how the creator uses the tool.",
        "caption_logic": "Give step-like instructions and tie every claim to a visible screen action.",
        "best_for": "Screen-recording demos where the value is obvious from the product steps.",
        "example_title_shape": "How I use [product] to [task]",
        "example_caption_shape": "One workflow for [task]: open the tool, run the key step, review the output, then keep editing.",
    },
    {
        "template_type": "result_reveal",
        "title_logic": "Tease a before/after or visible result that appears in the video.",
        "caption_logic": "Set up the before state, reveal the product-assisted result, and add a review/edit caveat.",
        "best_for": "Figure generation, cover/output comparisons, and videos with a strong visual transformation.",
        "example_title_shape": "I turned [before] into [reviewable result]",
        "example_caption_shape": "Started with [before], used [product] for the first draft, then reviewed and edited the details.",
    },
]

TEMPLATE_BY_TYPE = {item["template_type"]: item for item in TEMPLATE_TYPE_SUMMARIES}


def read_optional_json(path: str | None) -> dict:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    return load_json(p)


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def strip_hashtags(text: str) -> str:
    return clean_text(re.sub(r"#[a-zA-Z0-9_]+", "", text))


def captions_from_variant(variant: dict) -> list[str]:
    if isinstance(variant.get("captions"), list):
        return [clean_text(str(item)) for item in variant["captions"] if str(item).strip()]
    captions_path = variant.get("captions_path")
    if captions_path:
        data = read_optional_json(captions_path)
        segments = data.get("segments", [])
        return [clean_text(str(item.get("text", ""))) for item in segments if item.get("text")]
    return []


def product_name(product: dict) -> str:
    return str(product.get("product_name") or product.get("name") or "").strip()


def product_key(product: dict) -> str:
    return product_name(product).lower()


def product_copy(product: dict) -> dict:
    key = product_key(product)
    if key in PRODUCT_COPY:
        return PRODUCT_COPY[key]
    features = product.get("core_features") or []
    feature_names = []
    for item in features:
        if isinstance(item, dict):
            feature_names.append(str(item.get("feature_name") or item.get("description") or "workflow"))
        else:
            feature_names.append(str(item))
    task = feature_names[0] if feature_names else "use this workflow"
    return {
        "task": task,
        "proof": "move through the workflow with a clearer starting point you can review",
        "risk": "Do not imply guaranteed results or replacement of user judgment.",
        "keywords": feature_names[:4],
    }


def product_pain(product: dict, captions: list[str] | None = None) -> str:
    key = product_key(product)
    if key == "literfy":
        return "starting a literature review from a blank page or random tabs"
    if key == "citely":
        return "AI citations can look real even when the source trail is messy"
    if key == "figpad":
        return "AI can give you a research figure that is still hard to edit"
    for field in ["main_user_pain_points", "pain_points", "pain_point", "user_pain"]:
        value = product.get(field)
        if isinstance(value, str) and value.strip():
            return clean_text(value)
        if isinstance(value, list) and value:
            return clean_text(str(value[0]))
    if captions:
        return strip_hashtags(captions[0])
    return "the manual workflow takes too much time"


def visible_result(product: dict) -> str:
    copy = product_copy(product)
    return copy["proof"]


def product_understanding(product: dict, captions: list[str]) -> dict:
    copy = product_copy(product)
    return {
        "user_pain": product_pain(product, captions),
        "feature": copy["task"],
        "visible_result": visible_result(product),
        "emotional_angle": "relief from a familiar workflow frustration",
        "best_tiktok_angle": "creator-style pain-to-workflow proof",
    }


def forbidden_terms(product: dict) -> list[str]:
    terms = ["perfect", "guaranteed", "submit directly", "publication-ready", "replace real research"]
    for claim in product.get("forbidden_claims", []) or []:
        if isinstance(claim, str):
            lowered = claim.lower()
            for term in ["perfect", "100%", "replace", "submit", "guaranteed", "publication-ready"]:
                if term in lowered and term not in terms:
                    terms.append(term)
    return terms


def caption_angle(captions: list[str]) -> str:
    hook = captions[0].lower() if captions else ""
    if "random google scholar tabs" in hook or "still starting" in hook:
        return "pain_question"
    if "50 tabs" in hook or "without opening" in hook:
        return "workflow_direct"
    return "reference_faithful"


def reference_caption(data: dict) -> str:
    explicit = data.get("reference_post", {}).get("caption", "")
    if explicit:
        return str(explicit)
    viral = data.get("viral_pattern_card") or read_optional_json(data.get("viral_pattern_card_path"))
    patterns = viral.get("viral_patterns") or []
    if patterns:
        examples = patterns[0].get("hook_examples") or []
        if examples:
            return str(examples[0])
    return "How to write a research paper like a phd/master student!!! #research #phd #literaturereview #citation #researchpaper"


def reference_title(data: dict) -> str:
    explicit = data.get("reference_post", {}).get("title", "")
    if explicit:
        return clean_text(str(explicit))
    viral = data.get("viral_pattern_card") or read_optional_json(data.get("viral_pattern_card_path"))
    patterns = viral.get("viral_patterns") or []
    if patterns:
        examples = patterns[0].get("hook_examples") or []
        if examples:
            return strip_hashtags(str(examples[0]))
    return ""


def detect_template_type(reference_title_text: str, reference_caption_text: str, captions: list[str]) -> str:
    blob = " ".join([reference_title_text, reference_caption_text, *captions]).lower()
    if "mistake" in blob or "mistakes" in blob or "wish i" in blob or "before you" in blob:
        return "mistake_urgency_cta"
    if "how to" in blob or "easy way" in blob or "phd/master" in blob or "master student" in blob:
        return "how_to_easy_way"
    if "?" in blob or "still" in blob or "too many" in blob or "messy" in blob or "stuck" in blob:
        return "pain_question_solution"
    if "turn" in blob or "into" in blob or "before after" in blob or "draft" in blob:
        return "result_reveal"
    return "workflow_direct_demo"


def title_pattern(reference_title_text: str, template_type: str) -> str:
    if reference_title_text:
        if template_type == "mistake_urgency_cta":
            return "regret warning + safer action"
        if template_type == "how_to_easy_way":
            return "How to + specific academic task + credibility/ease qualifier"
        if template_type == "pain_question_solution":
            return "pain question + cleaner workflow promise"
        if template_type == "result_reveal":
            return "before state + transformed reviewable result"
        return "direct workflow demo promise"
    return TEMPLATE_BY_TYPE[template_type]["example_title_shape"]


def caption_pattern(reference_caption_text: str, template_type: str) -> str:
    tags = re.findall(r"#[a-zA-Z0-9_]+", reference_caption_text)
    tag_note = f" Hashtag cluster: {', '.join(tags[:6])}." if tags else ""
    return TEMPLATE_BY_TYPE[template_type]["caption_logic"] + tag_note


def reference_post_analysis(reference_title_text: str, reference_caption_text: str, captions: list[str]) -> dict:
    template_type = detect_template_type(reference_title_text, reference_caption_text, captions)
    return {
        "template_type": template_type,
        "title_pattern": title_pattern(reference_title_text, template_type),
        "caption_pattern": caption_pattern(reference_caption_text, template_type),
        "hashtag_pattern": "Mix reference-style academic tags with product and workflow tags.",
    }


def task_phrase(product: dict) -> str:
    return str(product_copy(product)["task"])


def adapt_reference_title(reference_title_text: str, product: dict, template_type: str) -> str:
    name = product_name(product) or "this tool"
    task = task_phrase(product)
    if template_type == "mistake_urgency_cta":
        return f"dont make the mistakes i did. {task}"
    if template_type == "how_to_easy_way":
        if "like" in reference_title_text.lower():
            return f"How to {task} like a PhD/Master student"
        return f"How to {task}"
    if template_type == "pain_question_solution":
        return f"Still doing this manually? A better way to {task}"
    if template_type == "result_reveal":
        return f"I used {name} to {task}"
    return f"How I use {name} to {task}"


def make_titles(captions: list[str], product: dict, reference_title_text: str = "", template_type: str = "") -> list[str]:
    hook = captions[0] if captions else "How to start a literature review"
    name = product_name(product) or "this tool"
    angle = caption_angle(captions)
    template_type = template_type or detect_template_type(reference_title_text, "", captions)
    copy = product_copy(product)
    task = copy["task"]
    reference_adapted = adapt_reference_title(reference_title_text, product, template_type)
    if angle == "pain_question":
        return dedupe_keep_order([
            reference_adapted,
            f"Stop doing this manually: {task}",
            f"A better way to {task}",
            f"I tried {name} for this research workflow",
        ])
    if angle == "workflow_direct":
        return dedupe_keep_order([
            reference_adapted,
            f"How I use {name} to {task}",
            f"A faster research workflow for {task}",
            f"{task.capitalize()} without the messy workaround",
        ])
    if "dont" in hook.lower() or "don't" in hook.lower():
        return dedupe_keep_order([
            reference_adapted,
            f"dont make the mistakes i did. {task}",
            f"Use this before you {task}",
            f"I wish I checked this workflow earlier",
        ])
    return dedupe_keep_order([
        reference_adapted,
        f"How to {task}",
        f"The easier way to {task}",
        f"Using {name} for this research workflow",
    ])


def dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        key = clean_text(item).lower()
        if key and key not in seen:
            seen.add(key)
            result.append(clean_text(item))
    return result


def adapt_reference_caption(reference: str, product: dict, template_type: str) -> str:
    name = product_name(product) or "this tool"
    copy = product_copy(product)
    task = copy["task"]
    proof_line = f"It helps you {copy['proof']}."
    if template_type == "mistake_urgency_cta":
        return f"dont make the mistakes i did. Use this website before you {task}!!! {proof_line}"
    if template_type == "how_to_easy_way":
        return f"How I would {task} now: use {name} for the first pass, then review and edit the result yourself."
    if template_type == "pain_question_solution":
        return f"If {task} still feels messy, try this workflow instead. {proof_line}"
    if template_type == "result_reveal":
        return f"Start with the rough version, use {name} for a reviewable draft, then check and edit the details yourself."
    return f"One workflow for {task}: open {name}, run the key step, review the output, then keep editing."


def make_captions(captions: list[str], product: dict, reference: str, reference_title_text: str = "", template_type: str = "") -> list[str]:
    name = product_name(product) or "this tool"
    hook = captions[0] if captions else "How to start your literature review"
    angle = caption_angle(captions)
    template_type = template_type or detect_template_type(reference_title_text, reference, captions)
    copy = product_copy(product)
    task = copy["task"]
    proof_line = f"It helps you {copy['proof']}."
    soft_cta = f"Try {name} before doing the whole workflow manually."
    adapted_caption = adapt_reference_caption(reference, product, template_type)

    reference_lower = reference.lower()
    reference_uses_mistake_cta = "mistake" in reference_lower or "use this website" in reference_lower

    if reference_uses_mistake_cta:
        base_options = [
            adapted_caption,
            f"dont make the mistakes i did. Use this website before you {task}!!! {proof_line}",
            f"Use this website before you {task}. {proof_line} Still review the result before using it.",
            f"I would not {task} without checking the workflow first. {proof_line}",
        ]
    elif angle == "pain_question":
        base_options = [
            adapted_caption,
            f"{hook} This is the workflow I would use instead. {proof_line} {soft_cta}",
            f"If this workflow still feels messy, try {name}. {proof_line}",
            f"Manual work is not a strategy. I used {name} to {task} with a clearer starting point.",
        ]
    elif angle == "workflow_direct":
        base_options = [
            adapted_caption,
            f"{hook}. I used {name} to {task}. {proof_line}",
            f"One workflow for {task}: open the tool, run the key step, review the output, then keep editing.",
            f"This feels easier when the first step is a visible workflow, not a blank screen. {soft_cta}",
        ]
    else:
        base_options = [
            adapted_caption,
            f"{hook}. Just go to the website, follow the workflow, and review the result before using it.",
            f"How I would {task} now: use the tool for the first pass, then review and edit the result myself.",
            f"Workflow shortcut, but keep it honest: use the output as a starting point and review it before you keep working. {soft_cta}",
        ]
    return expand_caption_options(base_options, captions, product, template_type)


def expand_caption_options(base_options: list[str], captions: list[str], product: dict, template_type: str) -> list[str]:
    name = product_name(product) or "this tool"
    copy = product_copy(product)
    task = copy["task"]
    pain = product_pain(product, captions)
    proof = copy["proof"]
    extra_options = [
        f"save this if {pain}. I use {name} to {task}, then review the result before I keep working.",
        f"why did nobody tell me this workflow existed for {task}? {name} gives you a clearer starting point you can actually check.",
        f"POV: you are tired of {pain}. Open {name}, run the workflow, and keep editing instead of starting from zero.",
        f"not an ad, just the workflow I would use when {pain}. {name} helps you {proof}.",
        f"comment if you want the exact workflow for this. I used {name} to {task} without pretending the output is perfect.",
        f"if your workflow still starts with {pain}, this is your sign to try a cleaner first pass.",
        f"for students/researchers who need to {task}: use {name} for the first pass, then check the details yourself.",
        f"the annoying part is not the idea, it is {pain}. {name} makes the next step easier to review.",
    ]
    if template_type == "result_reveal":
        extra_options.insert(0, f"started with the messy version, ended with something I could actually review and edit in {name}.")
    return dedupe_keep_order([*base_options, *extra_options])[:10]


def make_pinned_comments(product: dict, captions: list[str]) -> list[str]:
    name = product_name(product) or "this tool"
    task = product_copy(product)["task"]
    pain = product_pain(product, captions)
    return dedupe_keep_order([
        f"Would you use this for {task}?",
        f"Save this before your next research workflow.",
        f"The key is still reviewing the output yourself.",
        f"Comment if you want the step-by-step workflow.",
        f"This is for when {pain}.",
        f"Tool: {name}",
    ])[:4]


def make_hashtags(product: dict, reference: str, captions: list[str]) -> list[str]:
    name = product_name(product).lower()
    tags: list[str] = []
    for tag in PRODUCT_TAGS.get(name, ["#researchtools"]):
        tags.append(tag)

    ref_tags = re.findall(r"#[a-zA-Z0-9_]+", reference)
    for tag in ref_tags:
        normalized = tag.lower()
        if normalized not in tags:
            tags.append(normalized)

    for tag in ACADEMIC_TAGS + AI_TOOL_TAGS:
        if tag not in tags:
            tags.append(tag)

    if captions and "google scholar" in " ".join(captions).lower():
        tags.append("#googlescholar")

    deduped: list[str] = []
    for tag in tags:
        if tag not in deduped:
            deduped.append(tag)
    return deduped[:6]


def risk_check(caption: str, reference: str, hashtags: list[str]) -> dict:
    lower = caption.lower()
    ref_lower = strip_hashtags(reference).lower()
    copied_reference = bool(ref_lower and ref_lower in lower)
    return {
        "overpromises": any(term in lower for term in ["100%", "guaranteed", "perfect", "fully replaces"]),
        "sounds_too_much_like_an_ad": any(term in lower for term in ["revolutionary", "game-changing", "best-in-class", "boost productivity"]),
        "uses_unrelated_hashtags": len(hashtags) > 6,
        "copies_reference_too_closely": copied_reference,
        "has_weak_tiktok_hook": len(caption.split()) > 0 and len(caption.split()[:8]) > 7 and not any(marker in lower for marker in ["pov", "save this", "why", "stop", "me ", "if "]),
    }


def compliance_notes(product: dict, captions: list[str]) -> list[str]:
    copy = product_copy(product)
    notes = [
        copy["risk"],
        "Keep the wording as a workflow starting point, not a replacement for user judgment.",
        "If mentioning Google Scholar, do not imply affiliation or partnership.",
    ]
    blocked = forbidden_terms(product)
    joined = " ".join(captions).lower()
    if any(term in joined for term in blocked):
        notes.append("Review captions for forbidden claim language before publishing.")
    return notes


def build_variant_copy(variant: dict, product: dict, reference: str, reference_title_text: str, reference_analysis: dict) -> dict:
    captions = captions_from_variant(variant)
    template_type = reference_analysis["template_type"]
    title_options = make_titles(captions, product, reference_title_text, template_type)
    caption_options = make_captions(captions, product, reference, reference_title_text, template_type)
    tags = make_hashtags(product, reference, captions)
    pinned_comment_options = make_pinned_comments(product, captions)
    return {
        "variant_id": variant.get("id") or variant.get("variant_id") or "variant",
        "video": variant.get("video", ""),
        "cover": variant.get("cover", ""),
        "source_hook": captions[0] if captions else "",
        "publishing_template": {
            "template_type": template_type,
            "reference_title": reference_title_text,
            "reference_caption": reference,
            "title_pattern": reference_analysis["title_pattern"],
            "caption_pattern": reference_analysis["caption_pattern"],
            "rewrite_method": "Preserve the reference post's publishing structure, emotional rhythm, CTA placement, and hashtag category; replace claims with product-safe facts from the final video.",
        },
        "reference_adaptation": {
            "reference_caption": reference,
            "adapted_logic": f"Keep the reference post rhythm and hashtag category, but rewrite around {product_name(product) or 'the product'} and the visible video workflow.",
            "do_not_copy_directly": True,
        },
        "product_understanding": product_understanding(product, captions),
        "caption_strategy": "Use the reference structure as a publishing template, then lead with user pain and visible product proof in native TikTok English.",
        "title_options": title_options,
        "recommended_title": title_options[0],
        "caption_options": caption_options,
        "recommended_caption": caption_options[0],
        "pinned_comment_options": pinned_comment_options,
        "recommended_pinned_comment": pinned_comment_options[0] if pinned_comment_options else "",
        "hashtags": tags,
        "posting_notes": [
            "Use the matching Google Scholar cover image for this video.",
            "Add TikTok trending music inside TikTok; do not use generated voiceover/BGM.",
            "Keep product claims tied to visible workflow steps and product facts.",
        ],
        "compliance_notes": compliance_notes(product, captions),
        "keywords": [product_name(product), *product_copy(product).get("keywords", [])],
        "risk_check": risk_check(caption_options[0], reference, tags),
        "scores": {
            "reference_fit": 9 if caption_angle(captions) == "reference_faithful" else 8,
            "native_tiktok_feel": 8,
            "viral_hook_strength": 8,
            "product_pain_fit": 8,
            "product_truth_safety": 9,
            "hashtag_relevance": 9,
        },
    }


def build_card(data: dict) -> dict:
    product = data.get("product") or {}
    if not product and data.get("product_script_card_path"):
        product = read_optional_json(data.get("product_script_card_path")).get("product", {})

    reference = reference_caption(data)
    ref_title = reference_title(data)
    ref_analysis = reference_post_analysis(ref_title, reference, [])
    variants = data.get("variants") or []
    if not variants and data.get("final_delivery_manifest_path"):
        manifest = read_optional_json(data.get("final_delivery_manifest_path"))
        for variant_id, payload in (manifest.get("variants") or {}).items():
            variants.append({
                "id": variant_id,
                "video": payload.get("video", ""),
                "cover": payload.get("cover", ""),
                "captions_path": payload.get("captions_path", ""),
            })

    return {
        "platform": data.get("platform", "TikTok"),
        "product_name": product_name(product),
        "reference_post": {
            "title": ref_title,
            "caption": reference,
            **ref_analysis,
            "rewrite_rule": "Adapt the reference post's academic niche and hashtag logic; do not copy unsupported claims or exact caption as-is.",
        },
        "template_type_summaries": TEMPLATE_TYPE_SUMMARIES,
        "publishing_variants": [
            build_variant_copy(
                v,
                product,
                reference,
                ref_title,
                reference_post_analysis(ref_title, reference, captions_from_variant(v)),
            )
            for v in variants
        ],
        "global_rules": [
            "Final delivery pairs cover image + captioned video.",
            "Publishing caption should feel like a creator sharing a useful workflow, not a product ad.",
            "Use TikTok trending music inside TikTok.",
            "Do not claim perfect output, guaranteed accuracy, or replacement of real research.",
        ],
    }


def main() -> None:
    parser = base_parser(__doc__ or "", "output/publishing_copy_card.json")
    args = parser.parse_args()
    data = load_json(args.input)
    write_json(args.out, build_card(data))


if __name__ == "__main__":
    main()
