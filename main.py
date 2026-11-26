#!/usr/bin/env python3
"""
make.fun news-image-20261125 — V6 stdlib tactical bitmap.
Python 3.13 stdlib only: 5x7 bitmap font scaled 2x/3x/4x, PNG writer.
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
    " ": ["00000","00000","00000","00000","00000","00000","00000"],
    "!": ["00100","00100","00100","00100","00100","00000","00100"],
    "?": ["01110","10001","00001","00010","00100","00000","00100"],
}

# V6 Color palette (R,G,B)
NAVY      = (10, 15, 30)      # #0A0F1E
CARD_BG   = (18, 26, 46)      # #121A2E
GRID_LINE = (22, 32, 55)      # thin separators
TEXT      = (232, 237, 245)   # #E8EDF5
ACCENT_Y  = (255, 179, 0)     # #FFB300
ACCENT_R  = (255, 68, 68)     # #FF4444
ACCENT_G  = (0, 230, 118)     # #00E676

# Story data with V6 specs
STORIES = [
    {"region": "WJAVA", "headline": "MINE FLOOD",       "badge": "9",      "icon": "v",   "accent": ACCENT_R},
    {"region": "CAIRO", "headline": "TANKER FIRE",      "badge": "30+",    "icon": "^",   "accent": ACCENT_R},
    {"region": "USA",   "headline": "TARIFFS 14 ECON",  "badge": "20%",    "icon": "v",   "accent": ACCENT_Y},
    {"region": "ASIA",  "headline": "CHIPS PLUNGE",     "badge": "6.2%",   "icon": "]",   "accent": ACCENT_G},
    {"region": "PAK",   "headline": "ASTRONAUT DOCKS",  "badge": "1",      "icon": "^",   "accent": ACCENT_G},
    {"region": "UK",    "headline": "ENERGY CAP +26%",  "badge": "26%",    "icon": "]",   "accent": ACCENT_Y},
]

CARD_W, CARD_H = 320, 200
CARD_GAP = 16
GRID_X0 = 32
GRID_Y0 = 110

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

    def outline_rect(self, x, y, w, h, color, t=1):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

def draw_glyph(c, x, y, ch, color, scale):
    """Draw a 5x7 glyph at given scale."""
    pattern = FONT5.get(ch.upper(), FONT5["?"])
    for row, bits in enumerate(pattern):
        for col, bit in enumerate(bits):
            if bit == "1":
                c.rect(x + col*scale, y + row*scale, scale, scale, color)

def glyph_w(scale):
    return 5*scale + 1  # glyph width including 1px spacing

def text_width(text, scale):
    return sum(glyph_w(scale) if ch != " " else 3*scale for ch in text.upper()) - (1 if text else 0)

def draw_text(c, x, y, text, color, scale, center=False):
    text = text.upper()
    if center:
        x = (W - text_width(text, scale)) // 2
    ox = x
    for ch in text:
        draw_glyph(c, ox, y, ch, color, scale)
        ox += glyph_w(scale) if ch != " " else 3*scale

def draw_header(c):
    # Header bar - navy bg
    c.rect(0, 0, W, 90, NAVY)
    # Header text at 3x scale (15x21)
    draw_text(c, 0, 20, "25 NOV 2026  —  WORLD BRIEFING", ACCENT_Y, 3, center=True)

def draw_card(c, idx, story):
    row = idx // 3
    col = idx % 3
    x = GRID_X0 + col * (CARD_W + CARD_GAP)
    y = GRID_Y0 + row * (CARD_H + CARD_GAP)
    accent = story["accent"]

    # Card background
    c.rect(x, y, CARD_W, CARD_H, CARD_BG)
    # Thin grid line separator (1px)
    c.outline_rect(x, y, CARD_W, CARD_H, GRID_LINE, 1)

    # Region tag at 2x (10x14)
    draw_text(c, x + 16, y + 12, story["region"], TEXT, 2)

    # Minimal 1px icon glyph (5x7 at 1x = 5x7)
    icon_x = x + CARD_W - 30
    icon_y = y + 16
    draw_glyph(c, icon_x, icon_y, story["icon"], accent, 1)

    # Headline at 2x
    draw_text(c, x + 16, y + 48, story["headline"], TEXT, 2)

    # HUGE badge number at 4x (20x28) - centered in lower card area
    badge_y = y + CARD_H - 60
    bw = text_width(story["badge"], 4)
    bx = x + (CARD_W - bw) // 2
    draw_text(c, bx, badge_y, story["badge"], accent, 4)

def draw_footer(c):
    # Footer at 2x scale
    draw_text(c, 0, H - 22, "MAKE.FUN  •  1N20PV53", ACCENT_Y, 2, center=True)

def render():
    c = Canvas(W, H)
    # Full navy background
    c.rect(0, 0, W, H, NAVY)
    draw_header(c)
    for i, s in enumerate(STORIES):
        draw_card(c, i, s)
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