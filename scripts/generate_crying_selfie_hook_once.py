#!/usr/bin/env python3
"""Generate one female crying-selfie AI human hook for quick review."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "skills/tk-video-editor/modules"))

import human_hook_generation.run as hhg  # type: ignore  # noqa: E402


PROJECT_DIR = ROOT / "projects/generated/2026-06-01_16-videos_crying-selfie-hooks"
SINGLE_OUT_DIR = ROOT / "projects/generated/2026-06-01_crying-selfie-hook-test/output/generated_hooks_v2"
SINGLE_VIDEO_OUT = SINGLE_OUT_DIR / "crying_female_selfie_hook.mp4"
REFERENCE_APPROVED_HOOK = SINGLE_VIDEO_OUT
FINAL_DIR = PROJECT_DIR / "output/final_16"


VARIANTS = [
    {
        "slug": "late_night_ai_score",
        "pain": "AI-score panic after seeing a draft flagged too high",
        "gesture": "stares down at a laptop, blinks through tears, presses lips together, then looks up like she cannot believe it happened again",
        "look": "dark oversized t-shirt, slightly messy middle-part hair, bare face",
        "room": "dim dorm desk with a laptop glow and a pile of loose paper partly visible",
    },
    {
        "slug": "professor_comment",
        "pain": "professor-comment panic after getting feedback that the writing sounds robotic",
        "gesture": "holds the phone too close, glances sideways at a screen, gives a tiny defeated head shake, then swallows back tears",
        "look": "gray hoodie, loose low ponytail, tired swollen eyes",
        "room": "small bedroom study corner with a warm desk lamp and plain wall",
    },
    {
        "slug": "submission_deadline",
        "pain": "deadline panic because the essay still sounds like AI",
        "gesture": "looks down first, breathes shakily, eyebrows pinch upward, then leans closer with a silent cry-laugh",
        "look": "black t-shirt, messy shoulder-length hair, natural skin shine",
        "room": "night dorm room with soft overhead light and scattered notebooks below frame",
    },
    {
        "slug": "citation_draft_mess",
        "pain": "research-paper panic because the draft sounds unnatural and stiff",
        "gesture": "keeps her eyes lowered, wipes one cheek with the back of her hand, then looks into the camera embarrassed",
        "look": "navy sweatshirt, damp-looking loose hair strands near face",
        "room": "quiet bedroom desk with laptop glow on one side, no readable text",
    },
    {
        "slug": "turnitin_fear",
        "pain": "AI detector fear before submission",
        "gesture": "freezes, squints at the screen, slowly looks at the camera with watery eyes, then makes a tiny helpless smile",
        "look": "plain white sleep shirt, messy bun, red nose",
        "room": "dim student apartment study nook with warm lamp and blank wall",
    },
    {
        "slug": "rewrite_again",
        "pain": "having to rewrite the same paragraph again",
        "gesture": "rests one hand near her mouth, tries not to cry, lowers her gaze, then shakes her head in disbelief",
        "look": "charcoal tee, long dark hair falling over one cheek",
        "room": "bedroom desk at night with notebooks stacked behind her",
    },
    {
        "slug": "abstract_sounds_ai",
        "pain": "abstract still sounding too AI-written",
        "gesture": "mouth trembles, eyes glossy, she looks from laptop to camera and silently mouths a tiny 'no' without clear speech",
        "look": "soft beige hoodie, loose strands of hair, flushed cheeks",
        "room": "warm dorm light, plain wall, desk clutter below frame",
    },
    {
        "slug": "essay_not_human",
        "pain": "essay not sounding human enough",
        "gesture": "holds the camera slightly low, raises her eyes slowly, gives a defeated blink, then leans closer",
        "look": "dark green t-shirt, natural face, puffy under-eyes",
        "room": "small study corner, laptop edge visible, low warm lamp",
    },
    {
        "slug": "midnight_check",
        "pain": "midnight AI check panic",
        "gesture": "looks exhausted, sniffles silently, presses lips together, then gives a tiny embarrassed cry-smile",
        "look": "oversized gray t-shirt, messy half-up hair, red nose",
        "room": "dark dorm bedroom with only desk lamp lighting her face",
    },
    {
        "slug": "draft_rejected",
        "pain": "draft rejection panic because the writing feels machine-made",
        "gesture": "turns her eyes down and left, shakes her head once, then looks back into camera with watery eyes",
        "look": "black hoodie, hair tucked behind one ear, flushed nose",
        "room": "plain bedroom wall, study desk below frame, soft shadows",
    },
    {
        "slug": "paragraph_too_stiff",
        "pain": "paragraph sounding too stiff and unnatural",
        "gesture": "pinches eyebrows, exhales silently, tries to smile but becomes teary, then looks down again",
        "look": "washed blue sweatshirt, loose hair, minimal makeup",
        "room": "student desk with a closed notebook and laptop glow, no readable text",
    },
    {
        "slug": "grammar_robotic",
        "pain": "grammar cleanup making everything sound robotic",
        "gesture": "leans close, eyes red and glossy, gives a small confused frown, then tilts her head helplessly",
        "look": "plain brown t-shirt, messy long hair, shiny skin",
        "room": "warm dim bedroom corner, blank wall, desk clutter out of focus",
    },
    {
        "slug": "teacher_suspects_ai",
        "pain": "teacher suspecting AI writing",
        "gesture": "looks at the camera like she has been caught, blinks back tears, then gives a tiny nervous cry-laugh",
        "look": "gray zip hoodie, tired face, red-rimmed eyes",
        "room": "night study room with laptop glow and soft lamp light",
    },
    {
        "slug": "humanize_deadline",
        "pain": "needing to humanize a draft before deadline",
        "gesture": "holds still for a beat, eyes wet, lowers her chin, then leans toward the camera as if asking for help",
        "look": "dark oversized sweatshirt, loose messy hair, natural skin texture",
        "room": "dim dorm corner, plain wall, notebook stack behind her",
    },
    {
        "slug": "final_paper_panic",
        "pain": "final paper panic from AI-likeness checks",
        "gesture": "starts looking down, squeezes eyes a little, breathes shakily, then looks up with a defeated cry-smile",
        "look": "black sleep shirt, messy hair framing face, tear track on one cheek",
        "room": "late-night study desk with warm lamp and no readable screen text",
    },
]


PROMPT = (
    "Realistic vertical 9:16 smartphone selfie video, 4 seconds. "
    "An original fictional young Asian woman student, age 20-26, films herself with a front phone camera at night. "
    "Extreme close-up face first, forehead and chin slightly cropped, imperfect Snapchat-style selfie framing. "
    "She is crying quietly from academic panic: wet puffy eyes, red nose, pinched eyebrows, trembling lips, glossy skin, "
    "one visible tear track on her cheek, slightly messy dark hair, plain dark t-shirt, no glamorous makeup. "
    "She starts looking down at her phone or laptop, slowly lifts her eyes into the camera, gives a tiny helpless head shake, "
    "swallows like she is trying not to sob, then leans closer with a silent cry-laugh expression. "
    "Dim dorm bedroom or study corner, plain wall, messy desk just below frame, warm low indoor lamp, phone camera noise, "
    "subtle shaky handheld motion, raw private UGC feeling, painfully relatable and slightly funny. "
    "No readable text, no captions baked in, no logos, no product UI, no speaking, no lip-sync, no dialogue."
)

NEGATIVE = (
    "male, man, boy, beard, mustache, masculine face, fashion model, glamour beauty, perfect studio lighting, "
    "commercial ad, cinematic shot, professional camera, readable text, subtitles, watermark, logo, product UI, "
    "speaking, talking mouth, lip-sync, dialogue, voiceover, exaggerated horror crying, distorted hands, extra limbs, "
    "uncanny face, plastic skin, one-to-one copy of the reference person's face or identity"
)


BASE_NEGATIVE = (
    "male, man, boy, beard, mustache, masculine face, fashion model, glamour beauty, perfect studio lighting, "
    "commercial ad, cinematic shot, professional camera, readable text, subtitles, watermark, logo, product UI, "
    "speaking, talking mouth, lip-sync, dialogue, voiceover, exaggerated horror crying, distorted hands, extra limbs, "
    "uncanny face, plastic skin, one-to-one copy of the reference person's face or identity"
)


def build_variant_prompt(variant: dict[str, str]) -> tuple[str, str]:
    prompt = (
        "Realistic vertical 9:16 smartphone selfie video, 4 seconds. "
        "An original fictional young Asian woman student, age 20-26, films herself with a front phone camera at night. "
        f"She is in {variant['room']}. "
        "Extreme close-up face first, forehead or chin slightly cropped, imperfect Snapchat-style selfie framing. "
        f"She is crying quietly from {variant['pain']}: wet puffy eyes, red nose, pinched eyebrows, trembling lips, glossy natural skin, "
        "one visible tear track on her cheek, no glamorous makeup. "
        f"Appearance: {variant['look']}. "
        f"Motion: {variant['gesture']}. "
        "Raw private UGC feeling, painfully relatable and slightly funny, subtle shaky handheld motion, phone camera noise, warm low indoor light. "
        "No readable text, no captions baked in, no logos, no product UI, no speaking, no lip-sync, no dialogue."
    )
    return prompt, BASE_NEGATIVE


def create_task(index: int, variant: dict[str, str], api_key: str, out_dir: Path) -> dict[str, str]:
    prompt, negative = build_variant_prompt(variant)
    variant_dir = out_dir / f"{index:02d}_{variant['slug']}"
    variant_dir.mkdir(parents=True, exist_ok=True)
    create_path = variant_dir / "evolink_task_create.json"
    if create_path.exists():
        create = json.loads(create_path.read_text(encoding="utf-8"))
    else:
        create = hhg.create_video_task(prompt, negative, 4, api_key)
        hhg.write_json(create_path, create)
    task_id = str(create.get("id") or create.get("task_id") or "")
    if not task_id:
        raise RuntimeError(f"missing task id for variant {index:02d}_{variant['slug']}")
    card = {
        "index": index,
        "slug": variant["slug"],
        "task_id": task_id,
        "prompt": prompt,
        "negative_prompt": negative,
        "variant_dir": str(variant_dir),
        "video_path": str(variant_dir / "ai_human_hook.mp4"),
    }
    hhg.write_json(variant_dir / "hook_request_card.json", card)
    return card


def poll_and_download(card: dict[str, str], api_key: str) -> bool:
    variant_dir = Path(card["variant_dir"])
    video_path = Path(card["video_path"])
    if video_path.exists() and video_path.stat().st_size > 1000:
        return True
    status = hhg.poll_task(card["task_id"], api_key, timeout_s=18, interval_s=6)
    hhg.write_json(variant_dir / "evolink_task_status.json", status)
    result_url = hhg.generated_url(status)
    if str(status.get("status", "")).lower() in {"completed", "succeeded", "success"} and result_url:
        hhg.download_file(result_url, video_path, api_key)
        return True
    return False


def package_final(cards: list[dict[str, str]]) -> None:
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, object]] = []
    if REFERENCE_APPROVED_HOOK.exists():
        dest = FINAL_DIR / "01_approved_crying_female_selfie_hook.mp4"
        shutil.copy2(REFERENCE_APPROVED_HOOK, dest)
        manifest.append({
            "index": 1,
            "variant_id": "approved_crying_female_selfie_hook",
            "source": str(REFERENCE_APPROVED_HOOK),
            "file_path": str(dest),
        })
    for offset, card in enumerate(cards, start=2):
        src = Path(card["video_path"])
        if not src.exists():
            continue
        dest = FINAL_DIR / f"{offset:02d}_{card['slug']}.mp4"
        shutil.copy2(src, dest)
        manifest.append({
            "index": offset,
            "variant_id": card["slug"],
            "source": str(src),
            "file_path": str(dest),
        })
    hhg.write_json(FINAL_DIR / "crying_selfie_16_manifest.json", {
        "label": "2026-06-01 16 crying selfie AI human hooks",
        "count": len(manifest),
        "items": manifest,
    })


def generate_batch(count: int) -> None:
    api_key = hhg.load_env_value("EVOLINK_API_KEY") or hhg.load_env_value("AI_REAL_PERSON_VIDEO_API_KEY")
    if not api_key:
        raise SystemExit("missing EVOLINK_API_KEY or AI_REAL_PERSON_VIDEO_API_KEY")
    if count > len(VARIANTS):
        raise SystemExit(f"count {count} exceeds available variants {len(VARIANTS)}")

    batch_dir = PROJECT_DIR / "output/generated_hooks_new_15"
    batch_dir.mkdir(parents=True, exist_ok=True)
    cards = [create_task(i, variant, api_key, batch_dir) for i, variant in enumerate(VARIANTS[:count], start=1)]
    hhg.write_json(batch_dir / "task_manager.json", {"count": len(cards), "items": cards})

    pending = {card["task_id"]: card for card in cards}
    deadline = time.time() + 900
    while pending and time.time() < deadline:
        completed: list[str] = []
        for task_id, card in list(pending.items()):
            if poll_and_download(card, api_key):
                completed.append(task_id)
        for task_id in completed:
            pending.pop(task_id, None)
        if pending:
            time.sleep(8)

    if pending:
        hhg.write_json(batch_dir / "pending_tasks.json", {"pending": list(pending.values())})
        raise RuntimeError(f"{len(pending)} tasks still pending after timeout")
    package_final(cards)
    print(str(FINAL_DIR))


def generate_single() -> None:
    api_key = hhg.load_env_value("EVOLINK_API_KEY") or hhg.load_env_value("AI_REAL_PERSON_VIDEO_API_KEY")
    if not api_key:
        raise SystemExit("missing EVOLINK_API_KEY or AI_REAL_PERSON_VIDEO_API_KEY")

    OUT_DIR = SINGLE_OUT_DIR
    VIDEO_OUT = SINGLE_VIDEO_OUT
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    create = hhg.create_video_task(PROMPT, NEGATIVE, 4, api_key)
    hhg.write_json(OUT_DIR / "evolink_task_create.json", create)
    task_id = str(create.get("id") or create.get("task_id") or "")
    if not task_id:
        raise RuntimeError("Video provider did not return a task id")

    status = hhg.poll_task(task_id, api_key, timeout_s=420, interval_s=6)
    hhg.write_json(OUT_DIR / "evolink_task_status.json", status)
    result_url = hhg.generated_url(status)
    if str(status.get("status", "")).lower() not in {"completed", "succeeded", "success"} or not result_url:
        raise RuntimeError(f"Video task did not complete successfully: {status.get('status', 'unknown')}")

    hhg.download_file(result_url, VIDEO_OUT, api_key)
    card = {
        "status": "generated",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "task_id": task_id,
        "video_path": str(VIDEO_OUT),
        "prompt": PROMPT,
        "negative_prompt": NEGATIVE,
    }
    hhg.write_json(OUT_DIR / "crying_female_selfie_hook_card.json", card)
    print(str(VIDEO_OUT))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--batch", action="store_true")
    args = parser.parse_args()
    if args.batch or args.count != 1:
        generate_batch(args.count)
    else:
        generate_single()


if __name__ == "__main__":
    main()
