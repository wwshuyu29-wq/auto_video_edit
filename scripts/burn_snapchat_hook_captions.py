#!/usr/bin/env python3
"""Burn Snapchat-style hook captions onto the 16 crying-selfie hook videos."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "projects/generated/2026-06-01_16-videos_crying-selfie-hooks/output/final_16"
OUT_DIR = SOURCE_DIR.parent / "final_16_snapchat_subtitled"
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

CAPTIONS = {
    "01_approved_crying_female_selfie_hook.mp4": "Why is my AI score still so high?",
    "02_late_night_ai_score.mp4": "Why does my essay still sound AI?",
    "03_professor_comment.mp4": "Why does my professor think it's robotic?",
    "04_submission_deadline.mp4": "Why is this due tonight?",
    "05_citation_draft_mess.mp4": "Why does my draft sound so fake?",
    "06_turnitin_fear.mp4": "Why is Turnitin making me panic?",
    "07_rewrite_again.mp4": "Why am I rewriting this again?",
    "08_abstract_sounds_ai.mp4": "Why does my abstract sound AI?",
    "09_essay_not_human.mp4": "Why won't this essay sound human?",
    "10_midnight_check.mp4": "Why am I checking this at midnight?",
    "11_draft_rejected.mp4": "Why did my draft get flagged?",
    "12_paragraph_too_stiff.mp4": "Why is this paragraph so stiff?",
    "13_grammar_robotic.mp4": "Why did grammar cleanup make it robotic?",
    "14_teacher_suspects_ai.mp4": "Why does my teacher suspect AI?",
    "15_humanize_deadline.mp4": "Why do I still need to humanize this?",
    "16_final_paper_panic.mp4": "Why is my final paper still failing?",
}


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def probe(path: Path) -> dict:
    raw = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=codec_type,width,height,duration:format=duration",
            "-of",
            "json",
            str(path),
        ],
        text=True,
    )
    return json.loads(raw)


def burn_one(src: Path, dest: Path, caption: str, caption_file: Path) -> dict:
    caption_file.write_text(caption, encoding="utf-8")
    overlay_path = caption_file.with_suffix(".png")
    render_caption_overlay(caption, overlay_path)
    source_meta = probe(src)
    source_duration = float(source_meta["format"]["duration"])
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            str(src),
            "-loop",
            "1",
            "-i",
            str(overlay_path),
            "-t",
            f"{source_duration:.3f}",
            "-filter_complex",
            "[0:v][1:v]overlay=0:0:format=auto[v]",
            "-map",
            "[v]",
            "-r",
            "24",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            str(dest),
        ]
    )
    meta = probe(dest)
    video_stream = next(item for item in meta["streams"] if item.get("codec_type") == "video")
    return {
        "source": str(src),
        "file_path": str(dest),
        "caption": caption,
        "width": int(video_stream["width"]),
        "height": int(video_stream["height"]),
        "duration": round(float(meta["format"]["duration"]), 3),
    }


def render_caption_overlay(caption: str, out_path: Path) -> None:
    width, height = 720, 1280
    # Keep the Snapchat-style hook below TikTok's top app chrome.
    # 0.44 of a 1280px hook puts the strip in the upper-middle, not the top label zone.
    bar_h = 62
    bar_y = int(height * 0.44 - bar_h / 2)
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, bar_y, width, bar_y + bar_h), fill=(0, 0, 0, 164))
    font = ImageFont.truetype(FONT, 29)
    # Fit any long hook line inside the centered safe block.
    max_w = 680
    while True:
        bbox = draw.textbbox((0, 0), caption, font=font)
        if bbox[2] - bbox[0] <= max_w or font.size <= 22:
            break
        font = ImageFont.truetype(FONT, font.size - 1)
    bbox = draw.textbbox((0, 0), caption, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (width - text_w) // 2
    y = bar_y + (bar_h - text_h) // 2 - 2
    draw.text((x + 1, y + 1), caption, font=font, fill=(0, 0, 0, 85))
    draw.text((x, y), caption, font=font, fill=(255, 255, 255, 255))
    image.save(out_path)


def build_qa_sheet(items: list[dict]) -> Path:
    frames_dir = OUT_DIR / "qa_mid_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    for index, item in enumerate(items, 1):
        video = Path(item["file_path"])
        dur = float(item["duration"])
        run(
            [
                "ffmpeg",
                "-y",
                "-v",
                "error",
                "-ss",
                str(max(0.1, dur / 2)),
                "-i",
                str(video),
                "-frames:v",
                "1",
                "-vf",
                "scale=360:-1",
                str(frames_dir / f"{index:02d}.jpg"),
            ]
        )
    sheet = OUT_DIR / "qa_snapchat_caption_sheet.jpg"
    run(
        [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-framerate",
            "1",
            "-i",
            str(frames_dir / "%02d.jpg"),
            "-vf",
            "tile=4x4",
            "-frames:v",
            "1",
            str(sheet),
        ]
    )
    return sheet


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    caption_dir = OUT_DIR / "caption_text"
    caption_dir.mkdir(exist_ok=True)
    items: list[dict] = []

    for index, src in enumerate(sorted(SOURCE_DIR.glob("*.mp4")), 1):
        caption = CAPTIONS[src.name]
        dest = OUT_DIR / f"{index:02d}_{src.stem}_snapchat_caption.mp4"
        item = burn_one(src, dest, caption, caption_dir / f"{index:02d}.txt")
        item["index"] = index
        items.append(item)

    sheet = build_qa_sheet(items)
    manifest = {
        "label": "2026-06-01 16 crying selfie hooks with Snapchat-style burned captions",
        "source_dir": str(SOURCE_DIR),
        "output_dir": str(OUT_DIR),
        "count": len(items),
        "caption_style": {
            "placement": "upper-middle black translucent Snapchat-style strip, moved below TikTok top UI labels",
            "font": FONT,
            "drawbox_y": int(1280 * 0.44 - 62 / 2),
            "drawbox_h": 62,
            "fontsize": 29,
        },
        "all_720x1280": all(item["width"] == 720 and item["height"] == 1280 for item in items),
        "duration_range": [min(item["duration"] for item in items), max(item["duration"] for item in items)],
        "qa_sheet": str(sheet),
        "items": items,
    }
    (OUT_DIR / "snapchat_caption_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"count": len(items), "output_dir": str(OUT_DIR), "qa_sheet": str(sheet)}, indent=2))


if __name__ == "__main__":
    main()
