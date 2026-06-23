from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import textwrap


ROOT = Path("/Users/kk/Desktop/auto video")
OUT = ROOT / "figpad_poster_assets"
OUT.mkdir(exist_ok=True)

LOGO = OUT / "figpad_logo.png"
FIGURE = OUT / "process_illumina.png"
WORKSPACE_SCREENSHOT = Path("/Users/kk/Desktop/截屏2026-06-03 18.47.54.png")
SVG_EDITOR_SCREENSHOT = OUT / "playwright_svg_editor_landing.png"
SVG_CONVERTER_SCREENSHOT = OUT / "playwright_svg_converter.png"
SVG_EDIT_FRAME = OUT / "raw_svg_editor_edit_frame.jpg"
EXPORT_FRAME = OUT / "raw_export_ppt_frame.jpg"

W, H = 1080, 1350
WHITE = (255, 255, 255)
BLACK = (12, 12, 12)
MUTED = (54, 58, 66)
SOFT = (244, 247, 250)
BLUE = (11, 44, 99)
BORDER = (222, 226, 232)

PROMPT = (
    "Create a publication-style workflow diagram for Illumina next-generation "
    "sequencing on a clean white background. Show genomic DNA extraction and "
    "fragmentation, library preparation, size selection, bridge amplification, "
    "sequencing-by-synthesis, base calling, FASTQ generation, and downstream "
    "bioinformatics analysis. Use equipment schematics, arrows, readable labels, "
    "molecular details, and a journal-ready scientific figure layout."
)


def font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def text_width(draw, text, fnt):
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0]


def cover_fit(img, box_w, box_h, bg=WHITE):
    img = img.convert("RGBA")
    scale = min(box_w / img.width, box_h / img.height)
    resized = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (box_w, box_h), bg + (255,))
    canvas.alpha_composite(resized, ((box_w - resized.width) // 2, (box_h - resized.height) // 2))
    return canvas


def crop_fill(img, box_w, box_h):
    img = img.convert("RGBA")
    scale = max(box_w / img.width, box_h / img.height)
    resized = img.resize((int(img.width * scale), int(img.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - box_w) // 2
    top = (resized.height - box_h) // 2
    return resized.crop((left, top, left + box_w, top + box_h))


def rounded_image(img, radius=36, outline=True):
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


def shadow(size, radius=40, opacity=28, blur=20):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((blur, blur, size[0] - blur, size[1] - blur), radius=radius, fill=(0, 0, 0, opacity))
    return img.filter(ImageFilter.GaussianBlur(blur))


def paste_logo(base, x, y, size):
    logo = Image.open(LOGO).convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
    base.alpha_composite(logo, (x, y))


def brand_lockup(base, x=52, y=36, logo_size=42, text_size=38, fill=BLUE):
    d = ImageDraw.Draw(base)
    paste_logo(base, x, y + 2, logo_size)
    d.text((x + logo_size + 14, y), "FigPad", font=font(text_size, bold=True), fill=fill)


def center_text(draw, text, y, fnt, fill=BLACK):
    draw.text(((W - text_width(draw, text, fnt)) / 2, y), text, font=fnt, fill=fill)


def pill(base, xy, radius=48, fill=(250, 251, 252), outline=(232, 235, 238)):
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=2)


def attachment_icon(draw, x, y, color=BLUE):
    draw.rounded_rectangle((x, y, x + 20, y + 40), radius=9, outline=color, width=3)
    draw.line((x + 10, y + 12, x + 10, y + 33), fill=color, width=3)


def save_page(base, name):
    out = OUT / name
    base.convert("RGB").save(out, quality=95)
    return out


def page_1():
    base = Image.new("RGBA", (W, H), WHITE + (255,))
    d = ImageDraw.Draw(base)
    brand_lockup(base, 52, 32, 42, 38)

    d.text((56, 92), "Scientific", font=font(40), fill=BLACK)
    d.text((690, 92), "Figure", font=font(40), fill=BLACK)
    d.text((56, 150), "Prompt", font=font(162, bold=True), fill=BLACK)

    fig = cover_fit(Image.open(FIGURE), 980, 720, WHITE)
    base.alpha_composite(fig, (50, 360))

    base.alpha_composite(shadow((940, 112), 48, 36, 18), (70, 1191))
    pill(base, (82, 1180, 998, 1284))
    paste_logo(base, 158, 1204, 58)
    d.text((238, 1204), "FigPad", font=font(52, bold=True), fill=BLACK)
    d.text((468, 1213), "x", font=font(44), fill=(34, 34, 34))
    d.text((540, 1207), "Scientific Figure AI", font=font(42, bold=True), fill=BLACK)
    return save_page(base, "figpad_scientific_figure_prompt_01.png")


def page_2():
    base = Image.new("RGBA", (W, H), WHITE + (255,))
    d = ImageDraw.Draw(base)

    card = (108, 212, 972, 910)
    base.alpha_composite(shadow((card[2] - card[0] + 70, card[3] - card[1] + 70), 54, 32, 24), (card[0] - 35, card[1] - 25))
    d.rounded_rectangle(card, radius=48, fill=WHITE, outline=(218, 221, 225), width=5)

    lines = textwrap.wrap(PROMPT, width=39)
    y = 282
    prompt_font = font(35)
    for i, line in enumerate(lines[:10]):
        if i == 9 and len(lines) > 10:
            line = line.rstrip(".,") + "..."
        d.text((160, y), line, font=prompt_font, fill=MUTED)
        y += 54
    attachment_icon(d, 160, 804)

    menu = (560, 814, 994, 1128)
    base.alpha_composite(shadow((menu[2] - menu[0] + 50, menu[3] - menu[1] + 50), 34, 30, 16), (menu[0] - 24, menu[1] - 18))
    d.rounded_rectangle(menu, radius=34, fill=WHITE, outline=(226, 228, 232), width=2)
    d.text((612, 830), "Tools", font=font(38, bold=True), fill=BLACK)
    d.rounded_rectangle((606, 905, 946, 970), radius=32, fill=SOFT)
    paste_logo(base, 636, 916, 38)
    d.text((692, 915), "FigPad", font=font(32), fill=BLACK)
    d.text((646, 1001), "Text to Figure", font=font(31), fill=BLACK)
    d.text((646, 1061), "Editable PPT export", font=font(31), fill=BLACK)

    center_text(d, "Prompt from FigPad Gallery", 1180, font(36, bold=True), BLUE)
    center_text(d, "figpad.ai/scientific-visualization", 1232, font(28), MUTED)
    return save_page(base, "figpad_scientific_figure_prompt_02.png")


def page_3():
    base = Image.new("RGBA", (W, H), WHITE + (255,))
    d = ImageDraw.Draw(base)
    brand_lockup(base, 52, 34, 40, 36)

    d.text((56, 122), "Editable", font=font(116, bold=True), fill=BLACK)
    d.text((60, 250), "SVG Canvas", font=font(78, bold=True), fill=BLACK)
    d.text((64, 344), "Change labels, colors, and layout after generation.", font=font(30), fill=MUTED)

    editor = Image.open(SVG_EDIT_FRAME)
    main = cover_fit(editor, 920, 595, (248, 251, 255))
    base.alpha_composite(shadow((970, 645), 38, 32, 22), (55, 425))
    base.alpha_composite(rounded_image(main, 34), (80, 455))

    shot = Image.open(SVG_EDITOR_SCREENSHOT)
    crop = shot.crop((120, 80, 1320, 650))
    live = cover_fit(crop, 440, 260, (248, 251, 255))
    base.alpha_composite(shadow((490, 310), 28, 24, 14), (560, 940))
    base.alpha_composite(rounded_image(live, 24), (585, 965))
    d.rounded_rectangle((92, 980, 505, 1130), radius=34, fill=WHITE, outline=BORDER, width=2)
    d.text((125, 1006), "figpad.ai/svg-editor", font=font(30, bold=True), fill=BLUE)
    d.text((125, 1058), "Captured from the", font=font(26), fill=MUTED)
    d.text((125, 1092), "real product page", font=font(26), fill=MUTED)

    chips = [("Edit text", 100), ("Vector canvas", 405), ("Export SVG", 690)]
    for label, x in chips:
        d.rounded_rectangle((x, 1160, x + 250, 1220), radius=30, fill=SOFT, outline=BORDER, width=2)
        center_x = x + 125 - text_width(d, label, font(26, bold=True)) / 2
        d.text((center_x, 1174), label, font=font(26, bold=True), fill=BLUE)

    center_text(d, "Generated figure stays editable", 1260, font(34, bold=True), BLUE)
    return save_page(base, "figpad_scientific_figure_prompt_03.png")


def page_4():
    base = Image.new("RGBA", (W, H), WHITE + (255,))
    d = ImageDraw.Draw(base)
    brand_lockup(base, 52, 34, 40, 36)

    d.text((56, 122), "Export", font=font(116, bold=True), fill=BLACK)
    d.text((60, 250), "as SVG / PPTX", font=font(70, bold=True), fill=BLACK)
    d.text((64, 344), "Not just a screenshot. Keep editing downstream.", font=font(30), fill=MUTED)

    export = Image.open(EXPORT_FRAME)
    crop = export.crop((0, 180, 1080, 1450))
    framed = cover_fit(crop, 560, 720, (248, 251, 255))
    base.alpha_composite(shadow((610, 770), 38, 32, 22), (55, 430))
    base.alpha_composite(rounded_image(framed, 34), (80, 460))

    converter = Image.open(SVG_CONVERTER_SCREENSHOT)
    ccrop = converter.crop((40, 80, 980, 840))
    small = cover_fit(ccrop, 360, 315, (248, 251, 255))
    base.alpha_composite(shadow((410, 365), 28, 26, 16), (625, 520))
    base.alpha_composite(rounded_image(small, 24), (650, 545))

    d.rounded_rectangle((650, 910, 1010, 1045), radius=32, fill=SOFT, outline=BORDER, width=2)
    d.text((684, 932), "SVG Vector", font=font(30, bold=True), fill=BLUE)
    d.text((684, 986), "Editable PPTX", font=font(30, bold=True), fill=BLUE)

    d.rounded_rectangle((112, 1210, 968, 1284), radius=37, fill=SOFT, outline=BORDER, width=2)
    d.text((164, 1227), "Use the prompt, then export editable formats", font=font(30, bold=True), fill=BLUE)
    return save_page(base, "figpad_scientific_figure_prompt_04.png")


def page_5():
    base = Image.new("RGBA", (W, H), WHITE + (255,))
    d = ImageDraw.Draw(base)

    d.text((48, -18), "Comment+", font=font(135, bold=True), fill=BLACK)
    d.text((48, 178), "Follow+", font=font(135, bold=True), fill=BLACK)
    d.text((48, 374), "Like", font=font(135, bold=True), fill=BLACK)

    d.text((54, 670), "We'll DM you the", font=font(56, bold=True), fill=BLACK)
    d.text((54, 744), "FigPad link and prompt.", font=font(56, bold=True), fill=BLACK)

    paste_logo(base, 610, 1190, 66)
    d.text((690, 1191), "FigPad", font=font(62, bold=True), fill=BLACK)
    return save_page(base, "figpad_scientific_figure_prompt_05.png")


if __name__ == "__main__":
    for path in [page_1(), page_2(), page_3(), page_4(), page_5()]:
        print(path)
