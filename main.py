#!/usr/bin/env python3
"""
make.fun news-image-20261125 — V5 stdlib tactical situation-room board.
Python 3.13 standard library only: 2x scaled 5x7 bitmap font, PNG writer.
Output: 1024x704 PNG.
"""

import os
import struct
import zlib
import sys

W, H = 1024, 704

# 5x7 bitmap font (uppercase + digits + symbols)
FONT5 = {
    "A": ["01110","10001","10001","11111","10001","10001","10001"],
    "B": ["11110","10001","10001","11110","10001","10001","11110"],
    "C": ["01111","10000","10000","10000","10000","10000","01111"],
    "D": ["11110","10001","10001","10001","10001","10001","11110"],
    "E": ["11111","10000","10000","11110","10000","10000","11111"],
    "F": ["11111","10000","10000","11110","10000","10000","10000"],
    "G": ["01111","10000","10000","10111","10001","10001","01110"],
    "H": ["10001","10001","10001","11111","10001","10001","10001"],
    "I": ["11111","00100","00100","00100","00100","00100","11111"],
    "J": ["00111","00010","00010","00010","10010","10010","01100"],
    "K": ["10001","10010","10100","11000","10100","10010","10001"],
    "L": ["10000","10000","10000","10000","10000","10000","11111"],
    "M": ["10001","11011","10101","10101","10001","10001","10001"],
    "N": ["10001","11001","10101","10011","10001","10001","10001"],
    "O": ["01110","10001","10001","10001","10001","10001","01110"],
    "P": ["11110","10001","10001","11110","10000","10000","10000"],
    "Q": ["01110","10001","10001","10001","10101","10010","01101"],
    "R": ["11110","10001","10001","11110","10100","10010","10001"],
    "S": ["01111","10000","10000","01110","00001","00001","11110"],
    "T": ["11111","00100","00100","00100","00100","00100","00100"],
    "U": ["10001","10001","10001","10001","10001","10001","01110"],
    "V": ["10001","10001","10001","10001","10001","01010","00100"],
    "W": ["10001","10001","10001","10101","10101","10101","01010"],
    "X": ["10001","10001","01010","00100","01010","10001","10001"],
    "Y": ["10001","10001","01010","00100","00100","00100","00100"],
    "Z": ["11111","00001","00010","00100","01000","10000","11111"],
    "0": ["01110","10001","10011","10101","11001","10001","01110"],
    "1": ["00100","01100","00100","00100","00100","00100","01110"],
    "2": ["01110","10001","00001","00010","00100","01000","11111"],
    "3": ["11110","00001","00001","01110","00001","00001","11110"],
    "4": ["00010","00110","01010","10010","11111","00010","00010"],
    "5": ["11111","10000","10000","11110","00001","00001","11110"],
    "6": ["01111","10000","10000","11110","10001","10001","01110"],
    "7": ["11111","00001","00010","00100","01000","01000","01000"],
    "8": ["01110","10001","10001","01110","10001","10001","01110"],
    "9": ["01110","10001","10001","01111","00001","00001","11110"],
    "-": ["00000","00000","00000","11111","00000","00000","00000"],
    "/": ["00001","00010","00010","00100","01000","01000","10000"],
    ":": ["00000","00100","00100","00000","00100","00100","00000"],
    ".": ["00000","00000","00000","00000","00000","01100","01100"],
    ",": ["00000","00000","00000","00000","01100","00100","01000"],
    "•": ["00000","00000","00000","00000","00000","01100","01100"],
    "—": ["00000","00000","11111","11111","11111","00000","00000"],
    "|": ["00100","00100","00100","00100","00100","00100","00100"],
    "+": ["00000","00100","00100","11111","00100","00100","00000"],
    "%": ["11001","11010","00010","00100","01000","01011","10011"],
    "K": ["10001","10010","10100","11000","10100","10010","10001"],
    "G": ["01111","10000","10000","10111","10001","10001","01110"],
    "B": ["11110","10001","10001","11110","10001","10001","11110"],
    "T": ["11111","00100","00100","00100","00100","00100","00100"],
    "P": ["11110","10001","10001","11110","10000","10000","10000"],
    " ": ["00000","00000","00000","00000","00000","00000","00000"],
    "!": ["00100","00100","00100","00100","00100","00000","00100"],
    "?": ["01110","10001","00001","00010","00100","00000","00100"],
}

# Colors (R,G,B)
NAVY      = (8, 12, 26)
NAVY_DARK = (4, 8, 18)
CARD_BG   = (18, 28, 52)
CARD_EDGE = (40, 60, 100)
WHITE     = (250, 252, 255)
CYAN      = (0, 220, 255)
YELLOW    = (255, 215, 30)
RED       = (255, 60, 50)
ORANGE    = (255, 145, 30)
GREEN     = (60, 220, 100)
BLUE      = (60, 130, 255)
MAGENTA   = (220, 60, 200)
TEAL      = (30, 200, 180)
MUTED     = (110, 125, 155)

# Region accent colors
ACCENTS = {
    "ASIA":    YELLOW,
    "AFRICA":  RED,
    "TRADE":   ORANGE,
    "MARKETS": GREEN,
    "SPACE":   BLUE,
    "UK":      TEAL,
}

# 2x scaled glyph size
GLYPH_W, GLYPH_H = 10, 14  # 5x7 * 2
GLYPH_SPACE = 2

class Canvas:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.p = bytearray(w * h * 3)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.p[i] = color[0]
            self.p[i+1] = color[1]
            self.p[i+2] = color[2]

    def rect(self, x, y, w, h, color):
        x0 = max(0, int(x)); y0 = max(0, int(y))
        x1 = min(self.w, int(x + w)); y1 = min(self.h, int(y + h))
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            start = (yy * self.w + x0) * 3
            self.p[start:start+len(row)] = row

    def rect_alpha(self, x, y, w, h, color, alpha):
        x0 = max(0, int(x)); y0 = max(0, int(y))
        x1 = min(self.w, int(x + w)); y1 = min(self.h, int(y + h))
        for yy in range(y0, y1):
            for xx in range(x0, x1):
                i = (yy * self.w + xx) * 3
                inv = 1.0 - alpha
                self.p[i]   = int(self.p[i]   * inv + color[0] * alpha)
                self.p[i+1] = int(self.p[i+1] * inv + color[1] * alpha)
                self.p[i+2] = int(self.p[i+2] * inv + color[2] * alpha)

    def outline_rect(self, x, y, w, h, color, t=2):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

def draw_glyph2x(c, x, y, ch, color, scale=2):
    """Draw a 5x7 glyph at 2x scale (10x14)."""
    pattern = FONT5.get(ch.upper(), FONT5["?"])
    for row, bits in enumerate(pattern):
        for col, bit in enumerate(bits):
            if bit == "1":
                c.rect(x + col*scale, y + row*scale, scale, scale, color)

def text_width_2x(text):
    return sum(GLYPH_W if ch != " " else GLYPH_W//2 for ch in text.upper()) + (len(text)-1)*GLYPH_SPACE

def draw_text_2x(c, x, y, text, color, center=False):
    text = text.upper()
    if center:
        x = (W - text_width_2x(text)) // 2
    ox = x
    for ch in text:
        draw_glyph2x(c, ox, y, ch, color)
        ox += GLYPH_W if ch != " " else GLYPH_W//2
        ox += GLYPH_SPACE

# Story data
STORIES = [
    {"region": "ASIA",    "headline": "WEST JAVA MINE FLOOD", "badge": "9 DEAD  17 TRAPPED",   "icon": "mine"},
    {"region": "AFRICA",  "headline": "CAIRO TANKER FIRE",    "badge": "30+ KILLED",          "icon": "fire"},
    {"region": "TRADE",   "headline": "US TARIFFS 14 ECON",   "badge": "UP TO 20%",           "icon": "tariff"},
    {"region": "MARKETS", "headline": "ASIAN CHIPS PLUNGE",   "badge": "KOSPI -6.2%",         "icon": "chip"},
    {"region": "SPACE",   "headline": "PAK ASTRONAUT TIANGONG","badge": "SHENZHOU-24",        "icon": "rocket"},
    {"region": "UK",      "headline": "ENERGY CAP JAN +26%",  "badge": "GBP 2166",            "icon": "bolt"},
]

# 2x3 grid layout
CARD_W, CARD_H = 320, 200
CARD_GAP = 16
GRID_X0 = 32
GRID_Y0 = 110

def draw_icon(c, kind, cx, cy, accent):
    """Tiny 2x icons."""
    if kind == "mine":
        # mountain + water
        c.rect(cx-12, cy+2, 24, 16, (60,45,35))
        c.rect(cx-8, cy+10, 16, 14, (10,30,60))
        c.rect(cx-2, cy-6, 4, 8, YELLOW)
    elif kind == "fire":
        c.rect(cx-14, cy+4, 28, 14, (30,30,40))
        for dx, dy, sz, col in [(0,-8,10,RED),( -8,-2,7,ORANGE),(8,-2,7,ORANGE),(0,-14,5,YELLOW)]:
            c.rect(cx+dx-sz//2, cy+dy-sz//2, sz, sz, col)
    elif kind == "tariff":
        c.rect(cx-16, cy-8, 32, 24, (18,36,67))
        c.outline_rect(cx-16, cy-8, 32, 24, accent, 2)
        draw_text_2x(c, cx-12, cy-4, "20%", YELLOW)
    elif kind == "chip":
        c.rect(cx-14, cy-10, 28, 20, (18,70,40))
        c.outline_rect(cx-14, cy-10, 28, 20, (40,120,70), 2)
        draw_text_2x(c, cx-8, cy-6, "AI", GREEN)
        c.rect(cx-2, cy+6, 4, 10, RED)
    elif kind == "rocket":
        c.rect(cx-4, cy-14, 8, 22, (100,180,255))
        c.rect(cx-10, cy-2, 20, 8, (60,100,180))
        c.rect(cx-2, cy-18, 4, 4, RED)
    elif kind == "bolt":
        # lightning
        pts = [(cx,cy-16),(cx-6,cy-2),(cx,cy-2),(cx-4,cy+12),(cx+6,cy-4),(cx,cy-4)]
        for i in range(len(pts)-1):
            x0,y0=pts[i]; x1,y1=pts[i+1]
            steps=max(abs(x1-x0),abs(y1-y0))
            for s in range(steps+1):
                t=s/max(1,steps)
                xx=int(x0+(x1-x0)*t); yy=int(y0+(y1-y0)*t)
                c.rect(xx,yy,2,2,YELLOW)

def draw_card(c, idx, story):
    row = idx // 3
    col = idx % 3
    x = GRID_X0 + col * (CARD_W + CARD_GAP)
    y = GRID_Y0 + row * (CARD_H + CARD_GAP)
    accent = ACCENTS[story["region"]]

    # Card background
    c.rect(x, y, CARD_W, CARD_H, CARD_BG)
    c.outline_rect(x, y, CARD_W, CARD_H, CARD_EDGE, 2)
    # Accent top bar
    c.rect(x, y, CARD_W, 6, accent)
    # Region tag
    draw_text_2x(c, x+10, y+8, story["region"], WHITE)

    # Icon
    draw_icon(c, story["icon"], x+24, y+70, accent)

    # Headline (left of icon area)
    draw_text_2x(c, x+52, y+40, story["headline"], WHITE)

    # BIG badge number at bottom
    badge_y = y + CARD_H - 38
    c.rect(x+12, badge_y, CARD_W-24, 30, NAVY_DARK)
    c.outline_rect(x+12, badge_y, CARD_W-24, 30, accent, 2)
    draw_text_2x(c, x+20, badge_y+4, story["badge"], accent, center=False)

def draw_header(c):
    # Header bar
    c.rect(0, 0, W, 90, NAVY_DARK)
    c.rect(0, 90, W, 4, CYAN)
    draw_text_2x(c, 0, 20, "25 NOV 2026  —  WORLD BRIEFING", CYAN, center=True)
    # Live dot
    c.rect(W-120, 26, 8, 8, RED)
    draw_text_2x(c, W-110, 22, "LIVE", RED)

def draw_ticker(c):
    y = H - 40
    c.rect(0, y, W, 40, NAVY_DARK)
    c.rect(0, y, W, 2, CYAN)
    draw_text_2x(c, 0, y+6, "DOW 50K+  |  ZAPORIZHZHIA BLACKOUT  |  HORMUZ CLAIM LABELLED", MUTED, center=True)

def draw_footer(c):
    y = H - 18
    draw_text_2x(c, 0, y, "MAKE.FUN  •  1N20PV53", YELLOW, center=True)

def render():
    c = Canvas(W, H)
    # Full navy background
    c.rect(0, 0, W, H, NAVY)
    # Subtle grid lines
    for gx in range(0, W, 64):
        c.rect(gx, 0, 1, H, (16,22,40))
    for gy in range(0, H, 64):
        c.rect(0, gy, W, 1, (16,22,40))
    draw_header(c)
    for i, s in enumerate(STORIES):
        draw_card(c, i, s)
    draw_ticker(c)
    draw_footer(c)
    return c

def png_bytes(canvas):
    raw_rows = []
    stride = W * 3
    for y in range(H):
        start = y * stride
        raw_rows.append(b"\x00" + bytes(canvas.p[start:start+stride]))
    raw = b"".join(raw_rows)
    comp = zlib.compress(raw, 9)

    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    out = [b"\x89PNG\r\n\x1a\n"]
    out.append(chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)))
    out.append(chunk(b"IDAT", comp))
    out.append(chunk(b"IEND", b""))
    return b"".join(out)

def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    canvas = render()
    data = png_bytes(canvas)
    with open(path, "wb") as f:
        f.write(data)
    print(f"{path}  {W}x{H}  {len(data)} bytes")
    return 0

if __name__ == "__main__":
    sys.exit(main())