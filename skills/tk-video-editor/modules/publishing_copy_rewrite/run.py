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
    if angle == "pain_question":
        return [
            "Stop opening random tabs for your literature review",
            "A better way to start your literature review",
            f"I tried {name} for literature review research",
        ]
    if angle == "workflow_direct":
        return [
            "Start a literature review without 50 tabs",
            "A faster literature review workflow",
            f"How I use {name} to start research",
        ]
    return [
        "How to start your literature review like a PhD/Master student",
        "The easy way to start a literature review",
        f"Starting a literature review with {name}",
    ]


def make_captions(captions: list[str], product: dict, reference: str) -> list[str]:
    name = product_name(product) or "Literfy"
    hook = captions[0] if captions else "How to start your literature review"
    angle = caption_angle(captions)

    proof_line = "It helps you find real papers, select sources, generate an outline, and turn it into a review draft you can review and edit."
    soft_cta = f"Try {name} before opening another pile of tabs."

    if angle == "pain_question":
        return [
            f"{hook} This is the workflow I would use instead. {proof_line} {soft_cta}",
            f"If your literature review starts with random Google Scholar tabs, try this workflow. {name} helps you move from topic → papers → outline → draft starting point.",
            f"Random tabs are not a research strategy. I used {name} to start from real papers and build a review outline first.",
        ]
    if angle == "workflow_direct":
        return [
            f"{hook}. I used {name} to find real papers first, select the useful ones, and create a structured starting point for the review.",
            f"One workflow for starting a literature review without living in 50 tabs: topic → real papers → selected sources → outline → draft.",
            f"Starting a literature review feels easier when the first step is real papers, not a blank doc. {soft_cta}",
        ]
    return [
        f"{hook}. Just go to the website, type your topic, select real papers, then generate an outline and review draft starting point.",
        f"How I would start a literature review now: find real papers first, select the sources, generate an outline, then review and edit the draft.",
        f"Literature review shortcut, but keep it honest: use real papers, review the output, and edit before you keep writing. {soft_cta}",
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
    notes = [
        "Do not imply the tool writes a perfect or submission-ready literature review.",
        "Keep the wording as a workflow starting point, not a replacement for academic judgment.",
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
            "adapted_logic": "Keep research.connect academic workflow framing and hashtag category, but rewrite around Literfy's real-paper literature-review workflow.",
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
            "Keep product claims tied to visible workflow steps: real papers, selected sources, outline, draft starting point.",
        ],
        "compliance_notes": compliance_notes(product, captions),
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
