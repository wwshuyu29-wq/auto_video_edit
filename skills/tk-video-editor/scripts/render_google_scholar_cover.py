#!/usr/bin/env python3
"""Render Google Scholar style cover images with small style variations."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


W, H = 1080, 1920
FONT_PATHS = [
    Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    Path("/System/Library/Fonts/Supplemental/Arial Black.ttf"),
    Path("/System/Library/Fonts/Helvetica.ttc"),
]

STYLE_PRESETS = {
    "reference": {
        "line_gap": 9,
        "y_ratio": 0.415,
        "highlight": ["phd/master"],
        "highlight_fill": (255, 235, 112, 255),
        "band_alpha": 10,
    },
    "pain": {
        "line_gap": 14,
        "y_ratio": 0.420,
        "highlight": ["google", "scholar"],
        "highlight_fill": (160, 215, 255, 255),
        "band_alpha": 12,
    },
    "workflow": {
        "line_gap": 7,
        "y_ratio": 0.415,
        "highlight": ["50", "tabs"],
        "highlight_fill": (255, 232, 105, 255),
        "band_alpha": 10,
    },
}


def get_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_PATHS:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def word_key(word: str) -> str:
    return re.sub(r"(^[^a-zA-Z0-9]+|[^a-zA-Z0-9/]+$)", "", word).lower()


def word_width(draw: ImageDraw.ImageDraw, word: str, font: ImageFont.FreeTypeFont, stroke: int) -> int:
    bbox = draw.textbbox((0, 0), word, font=font, stroke_width=stroke)
    return bbox[2] - bbox[0]


def style_color(value: object, fallback: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    if isinstance(value, list) and len(value) in {3, 4}:
        rgb = [max(0, min(255, int(v))) for v in value]
        if len(rgb) == 3:
            rgb.append(255)
        return tuple(rgb)  # type: ignore[return-value]
    if isinstance(value, tuple) and len(value) == 4:
        return value
    return fallback


def wrap_words(draw: ImageDraw.ImageDraw, words: list[str], font: ImageFont.FreeTypeFont, max_width: int, stroke: int) -> list[list[str]]:
    lines: list[list[str]] = []
    current: list[str] = []
    for word in words:
        candidate = [*current, word]
        text = " ".join(candidate)
        if word_width(draw, text, font, stroke) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = [word]
    if current:
        lines.append(current)
    return lines


def fit_lines(draw: ImageDraw.ImageDraw, text: str, max_width: int, max_height: int, line_gap: int) -> tuple[ImageFont.FreeTypeFont, list[list[str]], int]:
    words = text.split()
    for size in range(70, 40, -2):
        font = get_font(size)
        lines = wrap_words(draw, words, font, max_width, 8)
        line_h = size + line_gap
        if lines and len(lines) * line_h <= max_height:
            return font, lines, line_h
    font = get_font(40)
    return font, wrap_words(draw, words, font, max_width, 8), 40 + line_gap


def forced_lines(text: str, style: dict) -> list[list[str]] | None:
    value = style.get("lines")
    if isinstance(value, list) and value and all(isinstance(item, str) for item in value):
        return [str(item).split() for item in value]
    if "\n" in text:
        return [line.split() for line in text.splitlines() if line.strip()]
    return None


def fit_lines_for_style(draw: ImageDraw.ImageDraw, text: str, style: dict) -> tuple[ImageFont.FreeTypeFont, list[list[str]], int]:
    max_width = int(style.get("max_width", 900))
    max_height = int(style.get("max_height", 390))
    line_gap = int(style.get("line_gap", 9))
    start_size = int(style.get("font_size", 70))
    manual = forced_lines(text, style)
    for size in range(start_size, 40, -2):
        font = get_font(size)
        lines = manual or wrap_words(draw, text.split(), font, max_width, 8)
        line_h = size + line_gap
        if lines and len(lines) * line_h <= max_height:
            return font, lines, line_h
    font = get_font(40)
    return font, manual or wrap_words(draw, text.split(), font, max_width, 8), 40 + line_gap


def draw_centered_line(
    draw: ImageDraw.ImageDraw,
    words: list[str],
    x_center: int,
    y: int,
    font: ImageFont.FreeTypeFont,
    highlight: set[str],
    highlight_fill: tuple[int, int, int, int],
) -> None:
    stroke = 8
    space_w = word_width(draw, " ", font, 0)
    widths = [word_width(draw, word, font, stroke) for word in words]
    total_w = sum(widths) + space_w * (len(words) - 1)
    x = x_center - total_w // 2
    for word, width in zip(words, widths):
        fill = highlight_fill if word_key(word) in highlight else (255, 255, 255, 255)
        draw.text(
            (x, y),
            word,
            font=font,
            fill=fill,
            stroke_width=stroke,
            stroke_fill=(0, 0, 0, 245),
        )
        x += width + space_w


def render_cover(base_image: Path, text: str, out: Path, preset: str, custom_style: dict | None = None) -> None:
    style = {**STYLE_PRESETS.get(preset, STYLE_PRESETS["reference"])}
    if custom_style:
        style.update(custom_style)
    image = Image.open(base_image).convert("RGB").resize((W, H)).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rectangle((0, 560, W, 980), fill=(0, 0, 0, int(style["band_alpha"])))
    image = Image.alpha_composite(image, overlay)
    draw = ImageDraw.Draw(image)

    font, lines, line_h = fit_lines_for_style(draw, text, style)
    y = int(H * float(style["y_ratio"]) - (len(lines) * line_h) / 2)
    highlight = {str(item).lower() for item in style["highlight"]}
    highlight_fill = style_color(style.get("highlight_fill"), (255, 235, 112, 255))
    for line in lines:
        draw_centered_line(draw, line, W // 2, y, font, highlight, highlight_fill)
        y += line_h

    out.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(out, quality=94)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-image", type=Path, required=True)
    parser.add_argument("--variants", type=Path, required=True, help="JSON object mapping variant id to exact caption text")
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    variants = json.loads(args.variants.read_text(encoding="utf-8"))
    rendered: list[Path] = []
    for variant_id, value in variants.items():
        if isinstance(value, dict):
            text = str(value.get("text", ""))
            custom_style = value.get("style") if isinstance(value.get("style"), dict) else {}
        else:
            text = str(value)
            custom_style = {}
        if "problem" in variant_id:
            preset = "pain"
        elif "workflow" in variant_id:
            preset = "workflow"
        else:
            preset = "reference"
        out = args.out_dir / f"cover_style_{variant_id}.jpg"
        render_cover(args.base_image, str(text), out, preset, custom_style)
        rendered.append(out)

    thumbs = [Image.open(path).convert("RGB").resize((270, 480)) for path in rendered]
    sheet = Image.new("RGB", (270 * len(thumbs), 480), (0, 0, 0))
    for idx, thumb in enumerate(thumbs):
        sheet.paste(thumb, (270 * idx, 0))
    sheet.save(args.out_dir / "cover_style_contact_sheet.jpg", quality=94)

    print(json.dumps({"covers": [str(path) for path in rendered], "sheet": str(args.out_dir / "cover_style_contact_sheet.jpg")}, indent=2))


if __name__ == "__main__":
    main()
