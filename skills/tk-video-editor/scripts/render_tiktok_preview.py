#!/usr/bin/env python3
"""Render a captioned TikTok preview from a shot_matching_plan.json.

This preview path does not require FFmpeg drawtext/libass support. It renders
TikTok-style caption overlays as transparent PNGs with Pillow, then composites
them over 1080x1920 vertical video segments.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


W, H = 1080, 1920
FPS = 30
FONT_PATHS = [
    Path("/System/Library/Fonts/AppleSDGothicNeo.ttc"),
    Path("/System/Library/Fonts/Supplemental/AppleGothic.ttf"),
    Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    Path("/System/Library/Fonts/Supplemental/Arial Black.ttf"),
    Path("/System/Library/Fonts/Helvetica.ttc"),
]
DEFAULT_HIGHLIGHT = (255, 235, 112, 255)
EMOJI_TOKENS = {"😭", "👀", "😳", "🤯", "✅"}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def parse_time_range(value: str, fallback_index: int, fallback_duration: float = 3.0) -> tuple[float, float]:
    match = re.search(r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)", value or "")
    if match:
        start = float(match.group(1))
        end = float(match.group(2))
        return start, max(end, start + 0.5)
    start = fallback_index * fallback_duration
    return start, start + fallback_duration


def srt_time(seconds: float) -> str:
    ms_total = int(round(seconds * 1000))
    h, rem = divmod(ms_total, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_srt(segments: list[dict], out_path: Path) -> None:
    lines: list[str] = []
    for idx, seg in enumerate(segments, start=1):
        lines.extend([
            str(idx),
            f"{srt_time(seg['start'])} --> {srt_time(seg['end'])}",
            seg["text"],
            "",
        ])
    out_path.write_text("\n".join(lines), encoding="utf-8")


def font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_PATHS:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def emoji_kind(token: str) -> str | None:
    for item in EMOJI_TOKENS:
        if item in token:
            return item
    return None


def emoji_size_for(fnt: ImageFont.FreeTypeFont) -> int:
    return max(36, int(getattr(fnt, "size", 58) * 0.92))


def draw_emoji_marker(draw: ImageDraw.ImageDraw, token: str, x: int, y: int, size: int) -> None:
    kind = emoji_kind(token)
    if not kind:
        return

    if kind == "👀":
        eye_w = int(size * 0.44)
        eye_h = int(size * 0.58)
        gap = int(size * 0.08)
        for idx in range(2):
            ex = x + idx * (eye_w + gap)
            ey = y + int(size * 0.12)
            draw.ellipse((ex, ey, ex + eye_w, ey + eye_h), fill=(255, 255, 255, 255), outline=(0, 0, 0, 245), width=max(2, size // 14))
            draw.ellipse((ex + int(eye_w * 0.48), ey + int(eye_h * 0.28), ex + int(eye_w * 0.78), ey + int(eye_h * 0.58)), fill=(30, 30, 35, 255))
        return

    if kind == "✅":
        draw.rounded_rectangle((x, y + size * 0.08, x + size, y + size * 0.92), radius=size // 5, fill=(54, 164, 91, 255), outline=(0, 0, 0, 245), width=max(2, size // 14))
        draw.line((x + size * 0.24, y + size * 0.52, x + size * 0.42, y + size * 0.70, x + size * 0.76, y + size * 0.34), fill=(255, 255, 255, 255), width=max(4, size // 10), joint="curve")
        return

    # Rounded yellow face markers for emotional reactions.
    draw.ellipse((x, y, x + size, y + size), fill=(255, 204, 64, 255), outline=(0, 0, 0, 245), width=max(2, size // 16))
    eye_y = y + int(size * 0.34)
    left_x = x + int(size * 0.30)
    right_x = x + int(size * 0.66)

    if kind == "😭":
        draw.ellipse((left_x - size * 0.045, eye_y, left_x + size * 0.045, eye_y + size * 0.09), fill=(30, 30, 35, 255))
        draw.ellipse((right_x - size * 0.045, eye_y, right_x + size * 0.045, eye_y + size * 0.09), fill=(30, 30, 35, 255))
        draw.arc((x + size * 0.32, y + size * 0.58, x + size * 0.70, y + size * 0.86), 200, 340, fill=(30, 30, 35, 255), width=max(3, size // 14))
        draw.polygon([(x + size * 0.22, y + size * 0.48), (x + size * 0.13, y + size * 0.72), (x + size * 0.31, y + size * 0.72)], fill=(80, 172, 255, 255))
        draw.polygon([(x + size * 0.78, y + size * 0.48), (x + size * 0.69, y + size * 0.72), (x + size * 0.87, y + size * 0.72)], fill=(80, 172, 255, 255))
    elif kind == "😳":
        draw.ellipse((left_x - size * 0.07, eye_y, left_x + size * 0.07, eye_y + size * 0.14), fill=(30, 30, 35, 255))
        draw.ellipse((right_x - size * 0.07, eye_y, right_x + size * 0.07, eye_y + size * 0.14), fill=(30, 30, 35, 255))
        draw.ellipse((x + size * 0.16, y + size * 0.52, x + size * 0.36, y + size * 0.64), fill=(255, 130, 150, 150))
        draw.ellipse((x + size * 0.64, y + size * 0.52, x + size * 0.84, y + size * 0.64), fill=(255, 130, 150, 150))
        draw.line((x + size * 0.42, y + size * 0.70, x + size * 0.58, y + size * 0.70), fill=(30, 30, 35, 255), width=max(3, size // 14))
    elif kind == "🤯":
        draw.rectangle((x + size * 0.22, y - size * 0.03, x + size * 0.78, y + size * 0.18), fill=(255, 116, 92, 255), outline=(0, 0, 0, 245), width=max(2, size // 18))
        draw.ellipse((left_x - size * 0.055, eye_y, left_x + size * 0.055, eye_y + size * 0.11), fill=(30, 30, 35, 255))
        draw.ellipse((right_x - size * 0.055, eye_y, right_x + size * 0.055, eye_y + size * 0.11), fill=(30, 30, 35, 255))
        draw.ellipse((x + size * 0.43, y + size * 0.61, x + size * 0.57, y + size * 0.78), fill=(30, 30, 35, 255))


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return []

    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if draw.textbbox((0, 0), candidate, font=fnt, stroke_width=6)[2] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def text_width(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont, stroke_width: int = 7) -> int:
    if any(item in text for item in EMOJI_TOKENS):
        words = text.split()
        if not words:
            return 0
        space_w = draw.textbbox((0, 0), " ", font=fnt, stroke_width=0)[2]
        total = 0
        for word in words:
            if emoji_kind(word):
                total += emoji_size_for(fnt)
            else:
                bbox = draw.textbbox((0, 0), word, font=fnt, stroke_width=stroke_width)
                total += bbox[2] - bbox[0]
        return total + space_w * (len(words) - 1)
    bbox = draw.textbbox((0, 0), text, font=fnt, stroke_width=stroke_width)
    return bbox[2] - bbox[0]


def word_key(word: str) -> str:
    return re.sub(r"(^[^a-zA-Z0-9]+|[^a-zA-Z0-9/.-]+$)", "", word).lower()


def style_color(value: object, fallback: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    if isinstance(value, list) and len(value) in {3, 4}:
        rgb = [max(0, min(255, int(v))) for v in value]
        if len(rgb) == 3:
            rgb.append(255)
        return tuple(rgb)  # type: ignore[return-value]
    return fallback


def forced_lines(text: str, style: dict) -> list[str] | None:
    value = style.get("lines")
    if isinstance(value, list) and value and all(isinstance(item, str) for item in value):
        return [str(item) for item in value]
    if "\n" in text:
        return [line for line in text.splitlines() if line.strip()]
    return None


def fit_caption(
    draw: ImageDraw.ImageDraw,
    text: str,
    priority: str,
    style: dict | None = None,
) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    style = style or {}
    max_width = int(style.get("max_width", 900))
    start_size = int(style.get("font_size", 70 if priority != "large" else 66))
    min_size = int(style.get("min_font_size", 42))
    line_gap = int(style.get("line_gap", 8))
    max_height = int(style.get("max_height", 390))
    manual_lines = forced_lines(text, style)
    for size in range(start_size, min_size - 1, -2):
        fnt = font(size)
        lines = manual_lines or wrap_text(draw, text, fnt, max_width)
        line_h = size + line_gap
        if lines and len(lines) * line_h <= max_height and all(text_width(draw, line, fnt) <= max_width for line in lines):
            return fnt, lines, line_h
    fnt = font(min_size)
    return fnt, manual_lines or wrap_text(draw, text, fnt, max_width), min_size + line_gap


def caption_y(lines: list[str], line_h: int, beat: str, style: dict | None = None) -> int:
    style = style or {}
    block_h = len(lines) * line_h
    if "y_ratio" in style:
        return int(H * float(style["y_ratio"]) - block_h / 2)
    if beat == "hook":
        return int(H * 0.40 - block_h / 2)
    return int(H * 0.43 - block_h / 2)


def draw_caption_line(
    draw: ImageDraw.ImageDraw,
    line: str,
    x_center: int,
    y: int,
    fnt: ImageFont.FreeTypeFont,
    style: dict,
) -> None:
    stroke_width = int(style.get("stroke_width", 7))
    stroke_fill = style_color(style.get("stroke_fill"), (0, 0, 0, 235))
    fill = style_color(style.get("fill"), (255, 255, 255, 255))
    highlight_fill = style_color(style.get("highlight_fill"), DEFAULT_HIGHLIGHT)
    highlight_terms = {
        str(item).lower()
        for item in style.get("highlight_terms", [])
        if isinstance(item, str)
    }
    word_spacing = int(style.get("word_spacing", 0))
    words = line.split()
    if not words:
        return

    space_w = text_width(draw, " ", fnt, 0) + word_spacing
    widths = [emoji_size_for(fnt) if emoji_kind(word) else text_width(draw, word, fnt, stroke_width) for word in words]
    total_w = sum(widths) + space_w * (len(words) - 1)
    x = int(x_center - total_w / 2)
    for word, width in zip(words, widths):
        if emoji_kind(word):
            draw_emoji_marker(draw, word, x, y + max(0, int(getattr(fnt, "size", 58) * 0.05)), emoji_size_for(fnt))
            x += width + space_w
            continue
        key = word_key(word)
        is_highlighted = key in highlight_terms or any(term in key for term in highlight_terms if len(term) > 3)
        draw.text(
            (x, y),
            word,
            font=fnt,
            fill=highlight_fill if is_highlighted else fill,
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )
        x += width + space_w


def render_overlay(text: str, beat: str, priority: str, out_path: Path, style: dict | None = None) -> None:
    style = style or {}
    if any(item in text for item in EMOJI_TOKENS):
        native_script = Path(__file__).with_name("render_native_caption_overlay.swift")
        spec = {
            "text": text,
            "beat": beat,
            "priority": priority,
            "width": W,
            "height": H,
            "output": str(out_path),
            "style": style,
        }
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(spec, f, ensure_ascii=False)
            spec_path = Path(f.name)
        try:
            run(["swift", str(native_script), str(spec_path)])
        finally:
            spec_path.unlink(missing_ok=True)
        return

    out_path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    fnt, lines, line_h = fit_caption(draw, text, priority, style)
    y = caption_y(lines, line_h, beat, style)

    for line in lines:
        draw_caption_line(draw, line, W // 2, y, fnt, style)
        y += line_h

    image.save(out_path)


def build_segments(plan: dict) -> list[dict]:
    segments = []
    for idx, item in enumerate(plan.get("edit_plan") or []):
        start, end = parse_time_range(str(item.get("time", "")), idx)
        text = item.get("on_screen_text") or item.get("voiceover") or ""
        segments.append({
            "index": idx,
            "start": start,
            "end": end,
            "duration": max(0.5, end - start),
            "text": text,
            "beat": item.get("beat", ""),
            "clip_id": item.get("clip_id", ""),
            "clip_start": float(item.get("clip_start", 0) or 0),
            "clip_end": float(item["clip_end"]) if item.get("clip_end") is not None else None,
            "playback_speed": float(item.get("playback_speed", 1.0) or 1.0),
            "subtitle_priority": item.get("subtitle_priority", "normal"),
            "caption_style": item.get("caption_style") if isinstance(item.get("caption_style"), dict) else {},
        })
    return segments


def render_segment(
    src: Path,
    overlay: Path,
    clip_start: float,
    clip_end: float | None,
    duration: float,
    speed: float,
    out_path: Path,
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    frames = max(1, int(math.ceil(duration * FPS)))
    speed = max(0.25, speed)
    if clip_end is None:
        source_duration = duration * speed
    else:
        source_duration = max(0.1, min(duration * speed, clip_end - clip_start))
    filter_complex = (
        f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},setsar=1,setpts=PTS/{speed:.4f},"
        f"tpad=stop_mode=clone:stop_duration={duration:.3f},"
        f"trim=duration={duration:.3f},fps={FPS}[v];"
        "[v][1:v]overlay=0:0:shortest=1,format=yuv420p[vout]"
    )
    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-ss",
        f"{clip_start:.3f}",
        "-t",
        f"{source_duration:.3f}",
        "-i",
        str(src),
        "-loop",
        "1",
        "-t",
        f"{duration:.3f}",
        "-i",
        str(overlay),
        "-filter_complex",
        filter_complex,
        "-map",
        "[vout]",
        "-an",
        "-r",
        str(FPS),
        "-frames:v",
        str(frames),
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "22",
        "-movflags",
        "+faststart",
        str(out_path),
    ]
    run(cmd)


def concat_segments(segment_paths: list[Path], out_path: Path, workdir: Path) -> None:
    concat_file = workdir / "concat.txt"
    concat_file.write_text("".join(f"file '{path.resolve()}'\n" for path in segment_paths), encoding="utf-8")
    run([
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_file),
        "-c",
        "copy",
        "-movflags",
        "+faststart",
        str(out_path),
    ])


def probe(path: Path) -> dict:
    proc = subprocess.run([
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration,size:stream=width,height",
        "-of",
        "json",
        str(path),
    ], check=True, capture_output=True, text=True)
    return json.loads(proc.stdout)


def make_contact_sheet(video: Path, out_path: Path) -> None:
    run([
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(video),
        "-vf",
        "fps=1/3.5,scale=270:-1,tile=5x2",
        "-frames:v",
        "1",
        str(out_path),
    ])


def make_midpoint_sheet(video: Path, segments: list[dict], out_path: Path, workdir: Path) -> None:
    frames_dir = workdir / "qa_frames"
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True, exist_ok=True)

    frame_paths: list[Path] = []
    for seg in segments:
        midpoint = float(seg["start"]) + float(seg["duration"]) / 2
        frame_path = frames_dir / f"frame_{int(seg['index']):02d}.jpg"
        run([
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            f"{midpoint:.3f}",
            "-i",
            str(video),
            "-frames:v",
            "1",
            str(frame_path),
        ])
        frame_paths.append(frame_path)

    thumbs: list[Image.Image] = []
    for frame_path in frame_paths:
        img = Image.open(frame_path).convert("RGB")
        thumb_h = 480
        thumb_w = int(img.width * (thumb_h / img.height))
        thumbs.append(img.resize((thumb_w, thumb_h)))

    cols = 5
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * 270, rows * 480), (0, 0, 0))
    for idx, thumb in enumerate(thumbs):
        thumb = thumb.resize((270, 480))
        x = (idx % cols) * 270
        y = (idx // cols) * 480
        sheet.paste(thumb, (x, y))
    sheet.save(out_path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shot-plan", type=Path, required=True)
    parser.add_argument("--asset-library", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--workdir", type=Path, default=None)
    parser.add_argument("--report-out", type=Path, default=None)
    args = parser.parse_args()

    plan = load_json(args.shot_plan)
    assets = load_json(args.asset_library)
    if isinstance(assets, dict) and "asset_library" in assets:
        assets = assets["asset_library"]
    elif isinstance(assets, dict) and "assets" in assets:
        assets = assets["assets"]
    asset_by_id = {item.get("clip_id") or Path(item.get("file_path", "")).stem: item for item in assets}

    workdir = args.workdir or args.out.parent / "preview_render"
    overlays_dir = workdir / "overlays"
    segments_dir = workdir / "segments"
    if segments_dir.exists():
        shutil.rmtree(segments_dir)
    segments_dir.mkdir(parents=True, exist_ok=True)
    overlays_dir.mkdir(parents=True, exist_ok=True)

    segments = build_segments(plan)
    write_json(workdir / "render_plan.json", {"segments": segments})
    write_json(args.out.parent / "captions.json", {"segments": segments})
    build_srt(segments, args.out.parent / "master.srt")

    rendered_segments: list[Path] = []
    for seg in segments:
        asset = asset_by_id.get(seg["clip_id"])
        if not asset:
            raise SystemExit(f"missing asset for clip_id={seg['clip_id']}")
        src = Path(asset["file_path"]).expanduser()
        if not src.is_absolute():
            src = (args.asset_library.parent / src).resolve()
        overlay = overlays_dir / f"overlay_{seg['index']:02d}.png"
        render_overlay(seg["text"], seg["beat"], seg["subtitle_priority"], overlay, seg.get("caption_style") or {})
        out_seg = segments_dir / f"seg_{seg['index']:02d}.mp4"
        print(f"[{seg['index']:02d}] {seg['clip_id']} {seg['duration']:.2f}s")
        render_segment(
            src,
            overlay,
            seg["clip_start"],
            seg["clip_end"],
            seg["duration"],
            seg["playback_speed"],
            out_seg,
        )
        rendered_segments.append(out_seg)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    concat_segments(rendered_segments, args.out, workdir)
    sheet = args.out.with_name(f"{args.out.stem}_sheet.jpg")
    make_contact_sheet(args.out, sheet)
    midpoint_sheet = args.out.with_name(f"{args.out.stem}_midpoint_sheet.jpg")
    make_midpoint_sheet(args.out, segments, midpoint_sheet, workdir)

    report_path = args.report_out or args.out.parent / "render_report.json"
    metadata = probe(args.out)
    write_json(report_path, {
        "status": "rendered_preview",
        "inputs": {
            "shot_matching_plan": str(args.shot_plan),
            "asset_library": str(args.asset_library),
        },
        "outputs": {
            "preview_video": str(args.out),
            "preview_sheet": str(sheet),
            "preview_midpoint_sheet": str(midpoint_sheet),
            "captions": str(args.out.parent / "captions.json"),
            "srt": str(args.out.parent / "master.srt"),
            "render_report": str(report_path),
        },
        "video_metadata": metadata,
        "notes": [
            "Preview uses PNG caption overlays to avoid depending on FFmpeg drawtext/libass.",
            "Final VO/music is not added in this preview pass.",
        ],
    })
    print(f"preview: {args.out}")
    print(f"sheet: {sheet}")
    print(f"midpoint sheet: {midpoint_sheet}")


if __name__ == "__main__":
    main()
