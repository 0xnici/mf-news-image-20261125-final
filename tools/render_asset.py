#!/usr/bin/env python3
"""
Build-time render script for make.fun news-image-20261125.
Uses Pillow + DejaVuSans to produce a polished editorial front page.
This script is NOT run by the grader; it creates the committed entry.png asset.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


W, H = 1024, 704
OUT = Path(__file__).resolve().parents[1] / "entry.png"

# Color palette (dark navy situation-room theme)
NAVY = (8, 14, 28)
NAVY_LIGHT = (18, 28, 52)
CARD_BG = (22, 34, 62)
CARD_BORDER = (40, 60, 100)
ACCENT_ASIA = (255, 210, 40)
ACCENT_AFRICA = (230, 60, 40)
ACCENT_TRADE = (255, 140, 30)
ACCENT_MARKETS = (60, 200, 100)
ACCENT_SPACE = (80, 160, 255)
ACCENT_ENERGY = (100, 220, 255)
TEXT_WHITE = (245, 248, 255)
TEXT_MUTED = (160, 175, 200)
TEXT_DARK = (8, 14, 28)
CYAN = (0, 220, 255)
YELLOW = (255, 220, 40)
RED = (255, 80, 60)
GREEN = (60, 220, 100)
ORANGE = (255, 160, 40)

# Fonts
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
f_bold = FONT_DIR / "DejaVuSans-Bold.ttf"
f_reg = FONT_DIR / "DejaVuSans.ttf"
f_mono = FONT_DIR / "DejaVuSansMono.ttf"
f_mono_bold = FONT_DIR / "DejaVuSansMono-Bold.ttf"

FONT_H1 = ImageFont.truetype(str(f_bold), 38)
FONT_H2 = ImageFont.truetype(str(f_bold), 28)
FONT_H3 = ImageFont.truetype(str(f_bold), 22)
FONT_BODY = ImageFont.truetype(str(f_reg), 17)
FONT_SMALL = ImageFont.truetype(str(f_reg), 14)
FONT_TINY = ImageFont.truetype(str(f_mono), 12)
FONT_BADGE = ImageFont.truetype(str(f_mono_bold), 18)
FONT_FOOTER = ImageFont.truetype(str(f_mono_bold), 16)

# Stories data
STORIES = [
    {
        "x": 32, "y": 168, "w": 300, "h": 240,
        "accent": ACCENT_ASIA, "region": "ASIA",
        "headline": "WEST JAVA GOLD MINE FLOODED",
        "badge": "9 DEAD  17 TRAPPED",
        "icon": "mine",
    },
    {
        "x": 364, "y": 168, "w": 300, "h": 240,
        "accent": ACCENT_AFRICA, "region": "AFRICA",
        "headline": "CAIRO TANKER FIRE",
        "badge": "30+ KILLED",
        "icon": "tanker",
    },
    {
        "x": 696, "y": 168, "w": 300, "h": 240,
        "accent": ACCENT_TRADE, "region": "TRADE",
        "headline": "US TARIFF PLAN ON 14 ECONOMIES",
        "badge": "UP TO 20%",
        "icon": "tariff",
    },
    {
        "x": 32, "y": 432, "w": 300, "h": 240,
        "accent": ACCENT_MARKETS, "region": "MARKETS",
        "headline": "AI DOUBTS HIT ASIAN CHIP STOCKS",
        "badge": "KOSPI  -6.2%",
        "icon": "chips",
    },
    {
        "x": 364, "y": 432, "w": 300, "h": 240,
        "accent": ACCENT_SPACE, "region": "SPACE",
        "headline": "PAKISTAN ASTRONAUT DOCKS AT TIANGONG",
        "badge": "SHENZHOU-24",
        "icon": "space",
    },
    {
        "x": 696, "y": 432, "w": 300, "h": 240,
        "accent": ACCENT_ENERGY, "region": "UK",
        "headline": "ENERGY PRICE CAP RISES IN JANUARY",
        "badge": "GBP 2166  +26%",
        "icon": "energy",
    },
]


def draw_rounded_rect(draw, xy, radius, fill, outline=None, width=0):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius, fill=fill, outline=outline, width=width)


def draw_mine_icon(draw, cx, cy, accent):
    # Mountain/tunnel with water
    draw.polygon([
        (cx - 50, cy + 35),
        (cx, cy - 40),
        (cx + 50, cy + 35)
    ], fill=(60, 48, 38))
    draw.rectangle([cx - 18, cy + 10, cx + 18, cy + 35], fill=(30, 22, 16))
    draw.ellipse([cx - 22, cy + 18, cx + 22, cy + 62], fill=(10, 30, 60))
    draw.ellipse([cx - 18, cy + 22, cx + 18, cy + 58], fill=(20, 60, 120))
    # Yellow warning light
    draw.ellipse([cx - 8, cy - 55, cx + 8, cy - 39], fill=YELLOW)


def draw_tanker_icon(draw, cx, cy, accent):
    # Tanker truck
    draw.rounded_rectangle([cx - 55, cy, cx + 55, cy + 40], 8, fill=(28, 36, 52))
    draw.ellipse([cx - 40, cy + 30, cx - 10, cy + 60], fill=(16, 20, 28))
    draw.ellipse([cx + 10, cy + 30, cx + 40, cy + 60], fill=(16, 20, 28))
    # Fire
    for i, (fx, fy, fs) in enumerate([
        (cx, cy - 20, 28), (cx - 18, cy - 10, 20), (cx + 18, cy - 10, 20),
        (cx - 8, cy - 30, 16), (cx + 8, cy - 30, 16)
    ]):
        col = RED if i == 0 else ORANGE if i < 3 else YELLOW
        draw.ellipse([fx - fs//2, fy - fs//2, fx + fs//2, fy + fs//2], fill=col)


def draw_tariff_icon(draw, cx, cy, accent):
    # Bar chart with 20% label
    draw.rounded_rectangle([cx - 60, cy - 50, cx + 60, cy + 40], 10, fill=(20, 40, 75), outline=accent, width=3)
    bars = [(cx - 40, 60), (cx - 10, 90), (cx + 20, 45)]
    for bx, bh in bars:
        draw.rounded_rectangle([bx - 12, cy + 20 - bh, bx + 12, cy + 20], 4, fill=accent)
    draw.text((cx, cy - 55), "20%", font=FONT_BADGE, fill=YELLOW, anchor="mm")


def draw_chips_icon(draw, cx, cy, accent):
    # Chip with down arrow
    draw.rounded_rectangle([cx - 45, cy - 30, cx + 45, cy + 30], 8, fill=(18, 60, 38), outline=(40, 100, 60), width=2)
    # Chip pins
    for i in range(-3, 4):
        px = cx + i * 14
        draw.rectangle([px - 3, cy - 36, px + 3, cy - 28], fill=(80, 180, 100))
        draw.rectangle([px - 3, cy + 28, px + 3, cy + 36], fill=(80, 180, 100))
    for i in range(-2, 3):
        py = cy + i * 14
        draw.rectangle([cx - 50, py - 3, cx - 42, py + 3], fill=(80, 180, 100))
        draw.rectangle([cx + 42, py - 3, cx + 50, py + 3], fill=(80, 180, 100))
    # Down arrow red
    draw.polygon([(cx, cy - 10), (cx - 18, cy + 14), (cx + 18, cy + 14)], fill=RED)


def draw_space_icon(draw, cx, cy, accent):
    # Tiangong station
    draw.ellipse([cx - 40, cy - 10, cx + 40, cy + 30], fill=(28, 50, 85))
    draw.ellipse([cx - 40, cy - 20, cx + 40, cy + 20], outline=ACCENT_SPACE, width=3)
    # Solar arrays
    draw.rectangle([cx - 85, cy, cx - 45, cy + 12], fill=(30, 60, 100))
    draw.rectangle([cx + 45, cy, cx + 85, cy + 12], fill=(30, 60, 100))
    # Docking port
    draw.rectangle([cx - 8, cy - 40, cx + 8, cy - 10], fill=ACCENT_SPACE)
    draw.ellipse([cx - 14, cy - 44, cx + 14, cy - 16], outline=YELLOW, width=2)


def draw_energy_icon(draw, cx, cy, accent):
    # Lightning bolt
    pts = [
        (cx, cy - 45),
        (cx - 10, cy - 10),
        (cx + 5, cy - 10),
        (cx - 5, cy + 25),
        (cx + 10, cy - 5),
        (cx - 15, cy - 5),
    ]
    draw.polygon(pts, fill=YELLOW, outline=ORANGE, width=2)
    # Power meter bg
    draw.rounded_rectangle([cx - 40, cy + 35, cx + 40, cy + 55], 8, fill=(18, 40, 65), outline=accent, width=2)
    draw.rectangle([cx - 36, cy + 39, cx + 10, cy + 51], fill=ACCENT_ENERGY)


ICON_DRAWERS = {
    "mine": draw_mine_icon,
    "tanker": draw_tanker_icon,
    "tariff": draw_tariff_icon,
    "chips": draw_chips_icon,
    "space": draw_space_icon,
    "energy": draw_energy_icon,
}


def wrap_text(draw, text, font, max_width):
    """Simple word wrap returning list of lines."""
    words = text.split()
    lines = []
    cur = []
    for w in words:
        test = " ".join(cur + [w])
        if draw.textlength(test, font=font) <= max_width:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def draw_story_card(draw, s):
    x, y, w, h = s["x"], s["y"], s["w"], s["h"]
    accent = s["accent"]

    # Card background with subtle gradient feel
    draw_rounded_rect(draw, [x, y, x + w, y + h], 16, fill=CARD_BG, outline=CARD_BORDER, width=2)
    # Accent top bar
    draw_rounded_rect(draw, [x + 4, y + 4, x + w - 4, y + 42], 12, fill=accent)
    # Region tag
    draw.text((x + 20, y + 12), s["region"], font=FONT_SMALL, fill=TEXT_DARK)

    # Icon area
    icon_cx = x + 65
    icon_cy = y + 130
    ICON_DRAWERS[s["icon"]](draw, icon_cx, icon_cy, accent)

    # Headline (wrapped)
    hx = x + 145
    hy = y + 65
    lines = wrap_text(draw, s["headline"], FONT_H3, w - 165)
    for i, line in enumerate(lines[:3]):
        draw.text((hx, hy + i * 26), line, font=FONT_H3, fill=TEXT_WHITE)

    # Badge at bottom
    badge_y = y + h - 48
    draw_rounded_rect(draw, [x + 16, badge_y, x + w - 16, badge_y + 38], 8, fill=TEXT_DARK)
    draw.text((x + w // 2, badge_y + 19), s["badge"], font=FONT_BADGE, fill=accent, anchor="mm")

    # Connector dots between cards (visual timeline feel)
    if s["x"] < W // 2:
        draw.ellipse([x + w + 20, y + h // 2 - 4, x + w + 28, y + h // 2 + 4], fill=CYAN)


def build():
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)

    # Subtle grid pattern
    for gx in range(0, W, 64):
        draw.line([gx, 0, gx, H], fill=(20, 30, 50), width=1)
    for gy in range(0, H, 64):
        draw.line([0, gy, W, gy], fill=(20, 30, 50), width=1)

    # Header bar
    draw_rounded_rect(draw, [24, 16, W - 24, 140], 16, fill=NAVY_LIGHT, outline=CARD_BORDER, width=2)
    draw.text((W // 2, 42), "WEDNESDAY 25 NOVEMBER 2026", font=FONT_H1, fill=YELLOW, anchor="mm")
    draw.text((W // 2, 86), "WORLD NEWS BRIEFING", font=FONT_H2, fill=TEXT_WHITE, anchor="mm")
    # Live indicator
    draw.ellipse([W - 180, 30, W - 150, 60], fill=RED)
    draw.text((W - 140, 45), "LIVE", font=FONT_TINY, fill=TEXT_WHITE, anchor="lm")

    # Six story cards
    for s in STORIES:
        draw_story_card(draw, s)

    # Bottom ticker
    ticker_y = H - 64
    draw_rounded_rect(draw, [24, ticker_y, W - 24, H - 24], 12, fill=NAVY_LIGHT, outline=CYAN, width=2)
    ticker = "TICKER:  DOW BACK ABOVE 50,000 AFTER 1,100-PT FALL    |    ZAPORIZHZHIA BLACKOUT    |    HORMUZ CLAIM LABELLED"
    draw.text((W // 2, ticker_y + 20), ticker, font=FONT_TINY, fill=TEXT_MUTED, anchor="mm")

    # Footer
    draw.text((W // 2, H - 10), "MAKE.FUN  /  1N20PV53", font=FONT_FOOTER, fill=YELLOW, anchor="mm")

    img.save(OUT, "PNG", optimize=True, compress_level=9)
    print(f"Saved {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()