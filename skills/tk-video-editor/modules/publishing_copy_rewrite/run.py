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


def read_optional_json(path: str | None) -> dict:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    return load_json(p)


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


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


def make_titles(captions: list[str], product: dict) -> list[str]:
    hook = captions[0] if captions else "How to start a literature review"
    name = product_name(product) or "this tool"
    angle = caption_angle(captions)
    copy = product_copy(product)
    task = copy["task"]
    if angle == "pain_question":
        return [
            f"Stop doing this manually: {task}",
            f"A better way to {task}",
            f"I tried {name} for this research workflow",
        ]
    if angle == "workflow_direct":
        return [
            f"How I use {name} to {task}",
            f"A faster research workflow for {task}",
            f"{task.capitalize()} without the messy workaround",
        ]
    if "dont" in hook.lower() or "don't" in hook.lower():
        return [
            f"dont make the mistakes i did. {task}",
            f"Use this before you {task}",
            f"I wish I checked this workflow earlier",
        ]
    return [
        f"How to {task}",
        f"The easier way to {task}",
        f"Using {name} for this research workflow",
    ]


def make_captions(captions: list[str], product: dict, reference: str) -> list[str]:
    name = product_name(product) or "this tool"
    hook = captions[0] if captions else "How to start your literature review"
    angle = caption_angle(captions)
    copy = product_copy(product)
    task = copy["task"]
    proof_line = f"It helps you {copy['proof']}."
    soft_cta = f"Try {name} before doing the whole workflow manually."

    reference_lower = reference.lower()
    reference_uses_mistake_cta = "mistake" in reference_lower or "use this website" in reference_lower

    if reference_uses_mistake_cta:
        return [
            f"dont make the mistakes i did. Use this website before you {task}!!! {proof_line}",
            f"Use this website before you {task}. {proof_line} Still review the result before using it.",
            f"I would not {task} without checking the workflow first. {proof_line}",
        ]
    if angle == "pain_question":
        return [
            f"{hook} This is the workflow I would use instead. {proof_line} {soft_cta}",
            f"If this workflow still feels messy, try {name}. {proof_line}",
            f"Manual work is not a strategy. I used {name} to {task} with a clearer starting point.",
        ]
    if angle == "workflow_direct":
        return [
            f"{hook}. I used {name} to {task}. {proof_line}",
            f"One workflow for {task}: open the tool, run the key step, review the output, then keep editing.",
            f"This feels easier when the first step is a visible workflow, not a blank screen. {soft_cta}",
        ]
    return [
        f"{hook}. Just go to the website, follow the workflow, and review the result before using it.",
        f"How I would {task} now: use the tool for the first pass, then review and edit the result myself.",
        f"Workflow shortcut, but keep it honest: use the output as a starting point and review it before you keep working. {soft_cta}",
    ]


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
    return deduped[:11]


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


def build_variant_copy(variant: dict, product: dict, reference: str) -> dict:
    captions = captions_from_variant(variant)
    title_options = make_titles(captions, product)
    caption_options = make_captions(captions, product, reference)
    tags = make_hashtags(product, reference, captions)
    return {
        "variant_id": variant.get("id") or variant.get("variant_id") or "variant",
        "video": variant.get("video", ""),
        "cover": variant.get("cover", ""),
        "source_hook": captions[0] if captions else "",
        "reference_adaptation": {
            "reference_caption": reference,
            "adapted_logic": f"Keep the reference post rhythm and hashtag category, but rewrite around {product_name(product) or 'the product'} and the visible video workflow.",
            "do_not_copy_directly": True,
        },
        "title_options": title_options,
        "recommended_title": title_options[0],
        "caption_options": caption_options,
        "recommended_caption": caption_options[0],
        "hashtags": tags,
        "posting_notes": [
            "Use the matching Google Scholar cover image for this video.",
            "Add TikTok trending music inside TikTok; do not use generated voiceover/BGM.",
            "Keep product claims tied to visible workflow steps and product facts.",
        ],
        "compliance_notes": compliance_notes(product, captions),
        "keywords": [product_name(product), *product_copy(product).get("keywords", [])],
        "scores": {
            "reference_fit": 9 if caption_angle(captions) == "reference_faithful" else 8,
            "native_tiktok_feel": 8,
            "product_truth_safety": 9,
            "hashtag_relevance": 9,
        },
    }


def build_card(data: dict) -> dict:
    product = data.get("product") or {}
    if not product and data.get("product_script_card_path"):
        product = read_optional_json(data.get("product_script_card_path")).get("product", {})

    reference = reference_caption(data)
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
            "caption": reference,
            "rewrite_rule": "Adapt the reference post's academic niche and hashtag logic; do not copy unsupported claims or exact caption as-is.",
        },
        "publishing_variants": [build_variant_copy(v, product, reference) for v in variants],
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
