from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path("/Users/kk/Desktop/auto video")
BASE = ROOT / "figpad_gallery_carousels"
MANIFEST = BASE / "gallery_manifest.json"
OUT = BASE / "posts"
W, H = 1080, 1350

WHITE = (255, 255, 255)
BLACK = (10, 10, 10)
INK = (10, 38, 82)
MUTED = (58, 63, 74)
SOFT = (246, 249, 252)
BORDER = (220, 226, 235)
GREEN = (19, 141, 109)
AMBER = (202, 122, 0)
PURPLE = (102, 70, 210)


FEATURE_RULES = {
    "process-flow-diagram": ("Text-to-Figure", "Generate from a clean research workflow prompt.", "generateFigure", "Editable Export", "Export SVG or PPTX for downstream edits.", "svgConverter"),
    "mechanism-diagram": ("Text-to-Figure", "Describe the pathway. FigPad turns it into a figure.", "generateFigure", "SVG Editor", "Keep labels and layout editable.", "svgEditor"),
    "graphical-abstract-template": ("Image-to-Figure", "Recreate a polished graphical abstract style.", "imageToFigure", "Vectorizer", "Turn the result into editable SVG.", "vectorizer"),
    "journal-cover": ("Image-to-Figure", "Use references to explore cover-style visuals.", "imageToFigure", "Vectorizer", "Convert visual drafts into editable assets.", "vectorizer"),
    "lab-equipment-diagram": ("Image-to-Figure", "Upload a reference instrument and redraw it cleanly.", "imageToFigure", "SVG Converter", "Convert apparatus diagrams into SVG.", "svgConverter"),
    "microstructure-diagram": ("SVG Editor", "Edit labels, colors, and structure after generation.", "svgEditor", "Vectorizer", "Keep micro-structure details scalable.", "vectorizer"),
    "network-diagram": ("Text-to-Figure", "Generate networks from architecture or biology prompts.", "generateFigure", "SVG Editor", "Move nodes, labels, and arrows after generation.", "svgEditor"),
    "cross-section": ("SVG Editor", "Tune labels and layered anatomy after generation.", "svgEditor", "Editable Export", "Export SVG or PPTX for slides and papers.", "svgConverter"),
    "ecology-diagram": ("Text-to-Figure", "Prompt complex ecological systems in one canvas.", "generateFigure", "Vectorizer", "Keep maps and flows editable.", "vectorizer"),
}

TOOL_MENU_RULES = {
    "process-flow-diagram": ["Text to Figure", "Edit Text", "SVG Editor", "PPTX Export"],
    "mechanism-diagram": ["Text to Figure", "Edit Text", "SVG Editor", "PPTX Export"],
    "graphical-abstract-template": ["Image to Figure", "Text to Figure", "Vectorizer", "SVG Export"],
    "journal-cover": ["Image to Figure", "Reference Image", "Vectorizer", "PNG Export"],
    "lab-equipment-diagram": ["Image to Figure", "SVG Converter", "SVG Editor", "PPTX Export"],
    "microstructure-diagram": ["Text to Figure", "SVG Editor", "Vectorizer", "SVG Export"],
    "network-diagram": ["Text to Figure", "Edit Text", "SVG Editor", "PPTX Export"],
    "cross-section": ["Image to Figure", "Edit Text", "SVG Editor", "PPTX Export"],
    "ecology-diagram": ["Text to Figure", "Image to Figure", "Vectorizer", "PPTX Export"],
}

CTA_LINES = [
    "We'll DM you the FigPad link and prompt.",
    "Comment \"prompt\" for the exact FigPad setup.",
    "Save this for your next paper figure.",
    "Want the editable SVG workflow? Comment below.",
]


def font(size: int, bold: bool = False, serif: bool = False):
    candidates = []
    if serif:
        candidates.extend([
            "/System/Library/Fonts/Supplemental/Georgia Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Georgia.ttf",
            "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        ])
    candidates.extend([
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
    ])
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def text_width(draw: ImageDraw.ImageDraw, text: str, fnt) -> int:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def text_height(draw: ImageDraw.ImageDraw, text: str, fnt) -> int:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[3] - box[1]


def wrap_text(text: str, width: int) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    return textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False)


def clean_prompt(prompt: str) -> str:
    prompt = re.sub(r"\(\d+\)\s*", "", prompt)
    prompt = re.sub(r"\s*;\s*", ". ", prompt)
    prompt = re.sub(r"\s+", " ", prompt).strip()
    return prompt


def cover_fit(img: Image.Image, box_w: int, box_h: int, bg=WHITE) -> Image.Image:
    img = img.convert("RGBA")
    scale = min(box_w / img.width, box_h / img.height)
    resized = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (box_w, box_h), bg + (255,))
    canvas.alpha_composite(resized, ((box_w - resized.width) // 2, (box_h - resized.height) // 2))
    return canvas


def crop_fill(img: Image.Image, box_w: int, box_h: int, focus_y: float = 0.5) -> Image.Image:
    img = img.convert("RGBA")
    scale = max(box_w / img.width, box_h / img.height)
    resized = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.Resampling.LANCZOS)
    left = max(0, (resized.width - box_w) // 2)
    top = int(max(0, min(resized.height - box_h, (resized.height - box_h) * focus_y)))
    return resized.crop((left, top, left + box_w, top + box_h))


def rounded(img: Image.Image, radius: int = 32, outline: bool = True) -> Image.Image:
    img = img.convert("RGBA")
    mask = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, img.width, img.height), radius=radius, fill=255)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.alpha_composite(img)
    out.putalpha(mask)
    if outline:
        d = ImageDraw.Draw(out)
        d.rounded_rectangle((1, 1, img.width - 2, img.height - 2), radius=radius, outline=BORDER, width=2)
    return out


def shadow(size: tuple[int, int], radius: int = 42, opacity: int = 28, blur: int = 18) -> Image.Image:
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((blur, blur, size[0] - blur, size[1] - blur), radius=radius, fill=(0, 0, 0, opacity))
    return img.filter(ImageFilter.GaussianBlur(blur))


def brand(base: Image.Image, logo_path: Path, x: int = 52, y: int = 34, dark: bool = False):
    d = ImageDraw.Draw(base)
    logo = Image.open(logo_path).convert("RGBA").resize((40, 40), Image.Resampling.LANCZOS)
    if dark:
        logo = Image.eval(logo, lambda v: 255 if v > 0 else v)
    base.alpha_composite(logo, (x, y + 4))
    d.text((x + 54, y), "FigPad", font=font(38, bold=True, serif=True), fill=WHITE if dark else INK)


def center_text(draw: ImageDraw.ImageDraw, text: str, y: int, fnt, fill=BLACK):
    draw.text(((W - text_width(draw, text, fnt)) / 2, y), text, font=fnt, fill=fill)


def save(base: Image.Image, out_dir: Path, name: str) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / name
    base.convert("RGB").save(path, quality=95)
    return str(path)


def draw_chips(d: ImageDraw.ImageDraw, labels: list[str], y: int):
    x = 84
    for label in labels:
        w = max(210, text_width(d, label, font(25, bold=True)) + 54)
        d.rounded_rectangle((x, y, x + w, y + 58), radius=29, fill=SOFT, outline=BORDER, width=2)
        d.text((x + (w - text_width(d, label, font(25, bold=True))) / 2, y + 15), label, font=font(25, bold=True), fill=INK)
        x += w + 26


def tool_labels_for(item) -> list[str]:
    return TOOL_MENU_RULES.get(item["categorySlug"], ["Text to Figure", "Image to Figure", "SVG Editor", "PPTX Export"])


def page_1(item, logo_path: Path, out_dir: Path):
    img = Image.open(item["imagePath"])
    is_cover = item["categorySlug"] == "journal-cover"
    base = Image.new("RGBA", (W, H), WHITE + (255,))
    d = ImageDraw.Draw(base)
    brand(base, logo_path)
    d.text((56, 92), item["category"].split("&")[0].strip(), font=font(34), fill=BLACK)
    d.text((682, 92), "Figure", font=font(38), fill=BLACK)
    d.text((56, 150), "Prompt", font=font(158, bold=True), fill=BLACK)
    title_lines = wrap_text(item["title"], 42)[:2]
    y = 320
    for line in title_lines:
        d.text((62, y), line, font=font(30, bold=True), fill=INK)
        y += 38
    visual_h = 720 if not is_cover else 700
    visual = cover_fit(img, 960, visual_h, WHITE if not is_cover else (248, 250, 252))
    visual_y = 405 if not is_cover else max(410, y + 16)
    base.alpha_composite(visual, (60, visual_y))
    base.alpha_composite(shadow((920, 110), 48, 34, 18), (80, 1196))
    d.rounded_rectangle((94, 1184, 986, 1286), radius=50, fill=(250, 251, 253), outline=BORDER, width=2)
    logo = Image.open(logo_path).convert("RGBA").resize((56, 56), Image.Resampling.LANCZOS)
    base.alpha_composite(logo, (164, 1207))
    d.text((242, 1206), "FigPad", font=font(52, bold=True), fill=BLACK)
    d.text((466, 1214), "x", font=font(44), fill=BLACK)
    d.text((536, 1209), "Scientific Figure AI", font=font(40, bold=True), fill=BLACK)
    return save(base, out_dir, "01_cover.png")


def page_2(item, logo_path: Path, out_dir: Path):
    base = Image.new("RGBA", (W, H), WHITE + (255,))
    d = ImageDraw.Draw(base)
    brand(base, logo_path, 52, 42)
    d.text((86, 158), "The Prompt", font=font(94, bold=True), fill=BLACK)
    d.text((92, 258), "From FigPad Gallery", font=font(34, bold=True), fill=INK)
    card = (104, 350, 976, 1018)
    base.alpha_composite(shadow((930, 725), 52, 32, 24), (72, 322))
    d.rounded_rectangle(card, radius=48, fill=WHITE, outline=(218, 222, 228), width=4)
    prompt = clean_prompt(item["prompt"])
    lines = wrap_text(prompt, 43)
    y = 410
    for i, line in enumerate(lines[:8]):
        if i == 7 and len(lines) > 8:
            line = line.rstrip(".,") + "..."
        d.text((154, y), line, font=font(34), fill=MUTED)
        y += 54
    d.rounded_rectangle((154, 874, 178, 928), radius=11, outline=INK, width=3)
    d.line((166, 890, 166, 918), fill=INK, width=3)
    menu = (558, 828, 996, 1160)
    base.alpha_composite(shadow((482, 380), 34, 28, 16), (536, 810))
    d.rounded_rectangle(menu, radius=34, fill=WHITE, outline=BORDER, width=2)
    d.text((612, 850), "Tools", font=font(36, bold=True), fill=BLACK)
    for row, label in enumerate(tool_labels_for(item)):
        y0 = 918 + row * 55
        d.rounded_rectangle((606, y0, 948, y0 + 45), radius=23, fill=SOFT, outline=None)
        d.text((630, y0 + 9), label, font=font(25), fill=BLACK)
    center_text(d, item["detailUrl"].replace("https://", ""), 1272, font(25), MUTED)
    return save(base, out_dir, "02_prompt.png")


def feature_page(item, logo_path: Path, out_dir: Path, manifest, index: int):
    rule = FEATURE_RULES[item["categorySlug"]]
    title, subtitle, shot_key = rule[0], rule[1], rule[2]
    if index == 4:
        title, subtitle, shot_key = rule[3], rule[4], rule[5]
    shot = Image.open(manifest["functionScreenshots"][shot_key])
    base = Image.new("RGBA", (W, H), WHITE + (255,))
    d = ImageDraw.Draw(base)
    brand(base, logo_path)
    title_lines = wrap_text(title, 16)
    y = 130
    for line in title_lines[:2]:
        d.text((58, y), line, font=font(90, bold=True), fill=BLACK)
        y += 96
    for line in wrap_text(subtitle, 48)[:2]:
        d.text((64, y + 6), line, font=font(30), fill=MUTED)
        y += 38
    crop = crop_fill(shot, 890, 590, 0.34 if shot_key in {"generateFigure", "imageToFigure"} else 0.16)
    base.alpha_composite(shadow((950, 650), 40, 30, 20), (66, 434))
    base.alpha_composite(rounded(crop, 34), (95, 464))
    if index == 3:
        chips = ["Real website", "No video frames", "FigPad workflow"]
    else:
        chips = ["SVG", "PPTX", "PNG export"]
    draw_chips(d, chips, 1132)
    footer = "Feature proof from figpad.ai"
    if index == 4:
        footer = "Generated figures stay editable"
    center_text(d, footer, 1258, font(34, bold=True), INK)
    return save(base, out_dir, f"0{index}_feature.png")


def page_5(item, logo_path: Path, out_dir: Path, idx: int):
    base = Image.new("RGBA", (W, H), WHITE + (255,))
    d = ImageDraw.Draw(base)
    d.text((56, 86), "Comment+", font=font(118, bold=True), fill=BLACK)
    d.text((56, 250), "Follow+", font=font(118, bold=True), fill=BLACK)
    d.text((56, 414), "Like", font=font(118, bold=True), fill=BLACK)
    cta = CTA_LINES[idx % len(CTA_LINES)]
    y = 690
    for line in wrap_text(cta, 27)[:3]:
        d.text((58, y), line, font=font(52, bold=True), fill=BLACK)
        y += 68
    logo = Image.open(logo_path).convert("RGBA").resize((66, 66), Image.Resampling.LANCZOS)
    base.alpha_composite(logo, (600, 1188))
    d.text((680, 1191), "FigPad", font=font(62, bold=True), fill=BLACK)
    return save(base, out_dir, "05_cta.png")


def caption_for(item) -> str:
    hooks = {
        "journal-cover": "Journal-cover style, but built from a prompt.",
        "graphical-abstract-template": "A graphical abstract prompt worth saving.",
        "process-flow-diagram": "This is the workflow prompt behind the figure.",
        "mechanism-diagram": "A pathway figure generated from one structured prompt.",
    }
    hook = hooks.get(item["categorySlug"], "Scientific figure prompt you can reuse.")
    return (
        f"{hook} FigPad helps turn scientific ideas into editable figures with SVG/PPTX export. "
        f"Comment 'prompt' if you want the link and exact prompt."
    )


def build():
    manifest = json.loads(MANIFEST.read_text())
    logo_path = Path(manifest["logoPath"])
    records = []
    for idx, item in enumerate(manifest["items"]):
        out_dir = OUT / item["categorySlug"] / f"{idx + 1:03d}-{item['slug']}"
        files = [
            page_1(item, logo_path, out_dir),
            page_2(item, logo_path, out_dir),
            feature_page(item, logo_path, out_dir, manifest, 3),
            feature_page(item, logo_path, out_dir, manifest, 4),
            page_5(item, logo_path, out_dir, idx),
        ]
        records.append({
            "id": item["id"],
            "title": item["title"],
            "category": item["category"],
            "detailUrl": item["detailUrl"],
            "prompt": clean_prompt(item["prompt"]),
            "caption": caption_for(item),
            "files": files,
        })
        print(f"[{idx + 1}/{len(manifest['items'])}] {item['title']}")
    (BASE / "posting_manifest.json").write_text(json.dumps(records, indent=2, ensure_ascii=False))
    print(f"Saved {len(records)} post sets to {OUT}")


if __name__ == "__main__":
    build()
