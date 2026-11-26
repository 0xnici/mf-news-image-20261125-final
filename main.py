#!/usr/bin/env python3
"""Deterministic make.fun news image for 2026-11-25.

Standard-library only: a tiny raster engine, bitmap font, and PNG writer.
The final artifact is intentionally a single high-contrast editorial image.
"""

import math
import os
import struct
import zlib

W = 1600
H = 1100

# Five-by-seven block font authored for this entry. Kept uppercase on purpose:
# bold news-wall labels beat small typography in a five-second pairwise judge.
FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01111", "10000", "10000", "10111", "10001", "10001", "01110"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00010", "00010", "00010", "10010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "10000", "11110", "00001", "00001", "11110"],
    "6": ["01111", "10000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00001", "11110"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    ":": ["00000", "00100", "00100", "00000", "00100", "00100", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ",": ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    "#": ["01010", "11111", "01010", "01010", "11111", "01010", "01010"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    "&": ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    "+": ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    "%": ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "?": ["01110", "10001", "00001", "00010", "00100", "00000", "00100"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
}

PALETTE = {
    "ink": (8, 12, 24),
    "navy": (12, 23, 48),
    "panel": (20, 33, 67),
    "card": (245, 247, 252),
    "paper": (231, 238, 248),
    "muted": (110, 124, 150),
    "cyan": (74, 221, 255),
    "blue": (58, 128, 255),
    "yellow": (255, 210, 67),
    "green": (96, 255, 132),
    "red": (255, 75, 91),
    "orange": (255, 151, 71),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
}


def clamp(v):
    return 0 if v < 0 else 255 if v > 255 else int(v)


def lerp(a, b, t):
    return int(a + (b - a) * t)


def mix(c1, c2, t):
    return (lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t), lerp(c1[2], c2[2], t))


class Canvas:
    def __init__(self, width, height):
        self.w = width
        self.h = height
        self.p = bytearray(width * height * 3)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.p[i] = color[0]
            self.p[i + 1] = color[1]
            self.p[i + 2] = color[2]

    def blend(self, x, y, color, alpha):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            inv = 1.0 - alpha
            self.p[i] = clamp(self.p[i] * inv + color[0] * alpha)
            self.p[i + 1] = clamp(self.p[i + 1] * inv + color[1] * alpha)
            self.p[i + 2] = clamp(self.p[i + 2] * inv + color[2] * alpha)

    def rect(self, x, y, w, h, color):
        x0 = max(0, int(x)); y0 = max(0, int(y))
        x1 = min(self.w, int(x + w)); y1 = min(self.h, int(y + h))
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            start = (yy * self.w + x0) * 3
            self.p[start:start + len(row)] = row

    def rect_alpha(self, x, y, w, h, color, alpha):
        x0 = max(0, int(x)); y0 = max(0, int(y))
        x1 = min(self.w, int(x + w)); y1 = min(self.h, int(y + h))
        for yy in range(y0, y1):
            for xx in range(x0, x1):
                self.blend(xx, yy, color, alpha)

    def outline_rect(self, x, y, w, h, color, t=2):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def gradient(self):
        top = (5, 9, 22)
        mid = (15, 28, 61)
        bot = (2, 7, 18)
        cx, cy = self.w * 0.55, self.h * 0.42
        maxd = math.hypot(cx, cy)
        for y in range(self.h):
            ty = y / max(1, self.h - 1)
            base = mix(top, mid, min(1, ty * 1.55)) if ty < 0.65 else mix(mid, bot, (ty - 0.65) / 0.35)
            for x in range(self.w):
                d = math.hypot(x - cx, y - cy) / maxd
                glow = max(0.0, 1.0 - d * 2.1)
                c = mix(base, (26, 74, 116), glow * 0.45)
                i = (y * self.w + x) * 3
                self.p[i] = c[0]
                self.p[i + 1] = c[1]
                self.p[i + 2] = c[2]

    def line(self, x0, y0, x1, y1, color, t=1):
        x0 = int(x0); y0 = int(y0); x1 = int(x1); y1 = int(y1)
        dx = abs(x1 - x0); sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0); sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            half = t // 2
            self.rect(x0 - half, y0 - half, t, t, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy; x0 += sx
            if e2 <= dx:
                err += dx; y0 += sy

    def circle(self, cx, cy, r, color, fill=True, alpha=1.0):
        cx = int(cx); cy = int(cy); r = int(r)
        r2 = r * r
        inner = max(0, r - 3)
        inner2 = inner * inner
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if fill:
                    if d2 <= r2:
                        self.blend(xx, yy, color, alpha) if alpha < 1 else self.set(xx, yy, color)
                elif inner2 <= d2 <= r2:
                    self.blend(xx, yy, color, alpha) if alpha < 1 else self.set(xx, yy, color)

    def ellipse_outline(self, cx, cy, rx, ry, color, alpha=1.0, steps=420, thick=2):
        last = None
        for k in range(steps + 1):
            a = 2.0 * math.pi * k / steps
            x = cx + math.cos(a) * rx
            y = cy + math.sin(a) * ry
            if last:
                if alpha < 1:
                    self.line_alpha(last[0], last[1], x, y, color, alpha, thick)
                else:
                    self.line(last[0], last[1], x, y, color, thick)
            last = (x, y)

    def line_alpha(self, x0, y0, x1, y1, color, alpha, t=1):
        x0 = int(x0); y0 = int(y0); x1 = int(x1); y1 = int(y1)
        dx = abs(x1 - x0); sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0); sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            half = t // 2
            for yy in range(y0 - half, y0 - half + t):
                for xx in range(x0 - half, x0 - half + t):
                    self.blend(xx, yy, color, alpha)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy; x0 += sx
            if e2 <= dx:
                err += dx; y0 += sy

    def poly(self, pts, color):
        ys = [p[1] for p in pts]
        y0 = max(0, int(min(ys))); y1 = min(self.h - 1, int(max(ys)))
        for y in range(y0, y1 + 1):
            xs = []
            for i in range(len(pts)):
                xA, yA = pts[i]
                xB, yB = pts[(i + 1) % len(pts)]
                if (yA <= y < yB) or (yB <= y < yA):
                    x = xA + (y - yA) * (xB - xA) / (yB - yA)
                    xs.append(x)
            xs.sort()
            for a, b in zip(xs[0::2], xs[1::2]):
                self.rect(int(a), y, int(b - a) + 1, 1, color)


def char_width(ch, scale):
    return 6 * scale if ch != " " else 4 * scale


def text_width(s, scale):
    return sum(char_width(ch, scale) for ch in s.upper())


def draw_text(c, x, y, text, scale, color, shadow=None):
    text = text.upper()
    ox = int(x)
    for ch in text:
        pattern = FONT.get(ch, FONT["?"])
        if shadow:
            for row, bits in enumerate(pattern):
                for col, bit in enumerate(bits):
                    if bit == "1":
                        c.rect(ox + col * scale + scale // 3, y + row * scale + scale // 3, scale, scale, shadow)
        for row, bits in enumerate(pattern):
            for col, bit in enumerate(bits):
                if bit == "1":
                    c.rect(ox + col * scale, y + row * scale, scale, scale, color)
        ox += char_width(ch, scale)


def centered(c, y, text, scale, color, shadow=None):
    draw_text(c, (W - text_width(text, scale)) // 2, y, text, scale, color, shadow)


def wrap_words(text, max_width, scale):
    words = text.upper().split()
    lines = []
    current = ""
    for word in words:
        candidate = word if not current else current + " " + word
        if text_width(candidate, scale) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def label(c, x, y, text, scale, color, max_width=None, leading=None):
    if max_width is None:
        draw_text(c, x, y, text, scale, color)
        return y + 8 * scale
    leading = leading or 9 * scale
    yy = y
    for line in wrap_words(text, max_width, scale):
        draw_text(c, x, yy, line, scale, color)
        yy += leading
    return yy


def draw_shadow_card(c, x, y, w, h, accent):
    for s, a in [(18, 0.10), (10, 0.12), (5, 0.18)]:
        c.rect_alpha(x + s, y + s, w, h, (0, 0, 0), a)
    c.rect(x, y, w, h, PALETTE["card"])
    c.rect(x, y, w, 14, accent)
    c.rect(x, y + 14, w, 4, mix(accent, PALETTE["white"], 0.25))
    c.outline_rect(x, y, w, h, mix(accent, PALETTE["black"], 0.18), 4)


def draw_background(c):
    c.gradient()
    # Command-center grid.
    for x in range(0, W, 80):
        a = 0.13 if x % 240 == 0 else 0.06
        c.line_alpha(x, 0, x, H, PALETTE["cyan"], a, 1)
    for y in range(0, H, 80):
        a = 0.13 if y % 240 == 0 else 0.06
        c.line_alpha(0, y, W, y, PALETTE["cyan"], a, 1)
    # Orbital globe motif behind the cards.
    cx, cy, r = 800, 515, 360
    c.circle(cx, cy, r, (8, 33, 62), True, 0.34)
    c.circle(cx, cy, r, PALETTE["cyan"], False, 0.42)
    for rr in [120, 210, 300]:
        c.ellipse_outline(cx, cy, rr, r * 0.92, PALETTE["cyan"], 0.14, thick=2)
        c.ellipse_outline(cx, cy, r * 0.95, rr * 0.55, PALETTE["cyan"], 0.13, thick=2)
    for a in range(-60, 80, 30):
        x1 = cx + math.cos(math.radians(a)) * r
        y1 = cy + math.sin(math.radians(a)) * r
        x2 = cx - math.cos(math.radians(a)) * r
        y2 = cy - math.sin(math.radians(a)) * r
        c.line_alpha(x1, y1, x2, y2, PALETTE["cyan"], 0.10, 2)
    # Simple continent-like shards, deliberately abstract to avoid false map precision.
    blobs = [
        [(640, 420), (695, 386), (756, 408), (732, 463), (662, 468)],
        [(790, 358), (874, 376), (905, 432), (855, 475), (775, 446)],
        [(705, 535), (772, 520), (812, 575), (760, 635), (690, 604)],
        [(925, 540), (1015, 565), (1045, 635), (970, 684), (905, 623)],
    ]
    for b in blobs:
        c.poly(b, (24, 68, 92))


def draw_header(c):
    c.rect_alpha(0, 0, W, 185, (0, 0, 0), 0.25)
    c.rect(0, 0, W, 10, PALETTE["cyan"])
    centered(c, 32, "WORLD NEWS COMMAND WALL", 11, PALETTE["white"], (0, 0, 0))
    centered(c, 118, "WEDNESDAY 25 NOVEMBER 2026", 8, PALETTE["yellow"], (0, 0, 0))
    draw_text(c, 48, 42, "GLOBAL", 4, PALETTE["cyan"])
    draw_text(c, 48, 76, "4 STORY SNAPSHOT", 3, PALETTE["paper"])
    draw_text(c, 1330, 42, "INSTANT READ", 4, PALETTE["cyan"])
    draw_text(c, 1330, 76, "NOISE -> SIGNAL", 3, PALETTE["paper"])
    # A small stamped dateline helps the date survive thumbnail views.
    c.rect(626, 182, 348, 18, PALETTE["red"])
    draw_text(c, 650, 177, "25 NOV NEWS WALL", 4, PALETTE["white"], (0, 0, 0))


def draw_ukraine(c, x, y):
    draw_shadow_card(c, x, y, 690, 350, PALETTE["blue"])
    draw_text(c, x + 32, y + 34, "UKRAINE PEACE TALKS", 5, PALETTE["ink"])
    label(c, x + 34, y + 96, "NATO coordination and Poland AWACS watch frame the diplomacy track.", 4, PALETTE["navy"], 600, 42)
    # Ukrainian flag + negotiation table.
    c.rect(x + 38, y + 235, 190, 42, (0, 91, 187))
    c.rect(x + 38, y + 277, 190, 42, (255, 213, 0))
    c.outline_rect(x + 38, y + 235, 190, 84, PALETTE["ink"], 3)
    c.rect(x + 284, y + 250, 190, 40, PALETTE["navy"])
    c.circle(x + 318, y + 230, 18, PALETTE["blue"], True)
    c.circle(x + 440, y + 230, 18, PALETTE["yellow"], True)
    c.line(x + 338, y + 242, x + 370, y + 250, PALETTE["ink"], 5)
    c.line(x + 420, y + 242, x + 388, y + 250, PALETTE["ink"], 5)
    draw_text(c, x + 304, y + 302, "TALKS", 4, PALETTE["ink"])
    # AWACS plane over Poland.
    c.line(x + 535, y + 255, x + 640, y + 230, PALETTE["ink"], 7)
    c.poly([(565, y + 248), (520, y + 225), (602, y + 239)], PALETTE["ink"])
    c.poly([(590, y + 242), (550, y + 285), (620, y + 249)], PALETTE["ink"])
    c.circle(x + 610, y + 216, 23, PALETTE["cyan"], False)
    draw_text(c, x + 512, y + 298, "POLAND AWACS", 3, PALETTE["red"])


def draw_nvidia(c, x, y):
    draw_shadow_card(c, x, y, 690, 350, PALETTE["green"])
    draw_text(c, x + 32, y + 34, "NVIDIA HUANG RETURNS", 5, PALETTE["ink"])
    label(c, x + 34, y + 96, "CEO Jensen Huang back in focus as markets track the AI chip leader.", 4, PALETTE["navy"], 600, 42)
    # Chip board.
    c.rect(x + 50, y + 222, 212, 98, (31, 125, 57))
    c.outline_rect(x + 50, y + 222, 212, 98, PALETTE["ink"], 4)
    c.rect(x + 92, y + 244, 128, 54, (5, 42, 24))
    draw_text(c, x + 110, y + 258, "AI", 7, PALETTE["green"])
    for pin in range(8):
        c.rect(x + 32 + pin * 28, y + 207, 12, 20, PALETTE["yellow"])
        c.rect(x + 32 + pin * 28, y + 318, 12, 20, PALETTE["yellow"])
    # Stylized CEO portrait: glasses + leather-jacket silhouette.
    c.circle(x + 402, y + 244, 54, (238, 193, 154), True)
    c.rect(x + 345, y + 292, 118, 42, PALETTE["ink"])
    c.circle(x + 380, y + 245, 15, PALETTE["ink"], False)
    c.circle(x + 426, y + 245, 15, PALETTE["ink"], False)
    c.line(x + 395, y + 245, x + 411, y + 245, PALETTE["ink"], 3)
    c.line(x + 500, y + 238, x + 628, y + 238, PALETTE["green"], 8)
    c.poly([(630, y + 238), (600, y + 218), (600, y + 258)], PALETTE["green"])
    draw_text(c, x + 500, y + 276, "CEO RETURN", 4, PALETTE["ink"])


def draw_riyadh(c, x, y):
    draw_shadow_card(c, x, y, 690, 350, PALETTE["red"])
    draw_text(c, x + 32, y + 34, "RIYADH STRIKE ALERT", 5, PALETTE["ink"])
    label(c, x + 34, y + 96, "Saudi skyline shaken after reported Houthi strike on tallest-tower target.", 4, PALETTE["navy"], 600, 42)
    # Night skyline with tallest tower and impact marker.
    base = y + 320
    c.rect(x + 45, y + 255, 88, 65, (23, 27, 45))
    c.rect(x + 145, y + 225, 70, 95, (23, 27, 45))
    c.rect(x + 238, y + 165, 64, 155, (23, 27, 45))
    c.poly([(270, y + 105), (238, y + 165), (302, y + 165)], (23, 27, 45))
    c.rect(x + 322, y + 245, 78, 75, (23, 27, 45))
    for wx in range(x + 60, x + 390, 30):
        for wy in range(y + 245, base - 10, 26):
            if (wx + wy) % 3:
                c.rect(wx, wy, 9, 12, PALETTE["yellow"])
    c.circle(x + 270, y + 142, 34, PALETTE["red"], False)
    c.circle(x + 270, y + 142, 12, PALETTE["orange"], True)
    c.line(x + 530, y + 182, x + 306, y + 142, PALETTE["red"], 5)
    c.line(x + 520, y + 197, x + 306, y + 142, PALETTE["orange"], 3)
    # Defense shield.
    c.poly([(520, y + 235), (592, y + 255), (578, y + 316), (520, y + 338), (462, y + 316), (448, y + 255)], (15, 61, 95))
    c.outline_rect(x + 460, y + 250, 120, 82, PALETTE["cyan"], 4)
    draw_text(c, x + 474, y + 278, "AIR", 5, PALETTE["cyan"])
    draw_text(c, x + 462, y + 317, "DEFENSE", 3, PALETTE["cyan"])


def draw_markets(c, x, y):
    draw_shadow_card(c, x, y, 690, 350, PALETTE["yellow"])
    draw_text(c, x + 32, y + 34, "GLOBAL MARKETS WATCH", 5, PALETTE["ink"])
    label(c, x + 34, y + 96, "Finance desks price geopolitics, oil risk and the AI trade in one tape.", 4, PALETTE["navy"], 600, 42)
    # Terminal panel.
    c.rect(x + 45, y + 205, 600, 115, (9, 22, 35))
    c.outline_rect(x + 45, y + 205, 600, 115, PALETTE["ink"], 3)
    values = [28, 42, 36, 56, 48, 72, 62, 82, 70, 93, 76, 88]
    last = None
    for i, v in enumerate(values):
        px = x + 80 + i * 45
        py = y + 300 - v
        c.line(px, y + 300 - max(8, v - 18), px, y + 300 - min(105, v + 16), PALETTE["paper"], 2)
        col = PALETTE["green"] if i % 3 != 1 else PALETTE["red"]
        c.rect(px - 9, py - 13, 18, 26, col)
        if last:
            c.line(last[0], last[1], px, py, PALETTE["cyan"], 3)
        last = (px, py)
    draw_text(c, x + 70, y + 225, "AI", 4, PALETTE["green"])
    draw_text(c, x + 170, y + 225, "OIL", 4, PALETTE["yellow"])
    draw_text(c, x + 300, y + 225, "FX", 4, PALETTE["cyan"])
    draw_text(c, x + 430, y + 225, "RISK", 4, PALETTE["red"])
    draw_text(c, x + 70, y + 330, "GLOBAL FINANCE PANEL", 3, PALETTE["ink"])


def draw_footer(c):
    c.rect_alpha(0, H - 96, W, 96, (0, 0, 0), 0.42)
    draw_text(c, 50, H - 56, "FOUR ANCHORS. ONE DATE. GLOBAL BREADTH.", 3, PALETTE["paper"])
    draw_text(c, 1010, H - 78, "MAKE.FUN /", 4, PALETTE["yellow"])
    draw_text(c, 1010, H - 42, "1N20PV53", 5, PALETTE["yellow"], (0, 0, 0))
    c.rect(0, H - 8, W, 8, PALETTE["cyan"])


def png_bytes(width, height, rgb):
    raw_rows = []
    stride = width * 3
    for y in range(height):
        start = y * stride
        raw_rows.append(b"\x00" + bytes(rgb[start:start + stride]))
    raw = b"".join(raw_rows)
    comp = zlib.compress(raw, 9)

    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    out = [b"\x89PNG\r\n\x1a\n"]
    out.append(chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)))
    out.append(chunk(b"IDAT", comp))
    out.append(chunk(b"IEND", b""))
    return b"".join(out)


def render():
    c = Canvas(W, H)
    draw_background(c)
    draw_header(c)
    draw_ukraine(c, 70, 205)
    draw_nvidia(c, 840, 205)
    draw_riyadh(c, 70, 600)
    draw_markets(c, 840, 600)
    draw_footer(c)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    canvas = render()
    data = png_bytes(canvas.w, canvas.h, canvas.p)
    with open(path, "wb") as f:
        f.write(data)
    print(path)


if __name__ == "__main__":
    main()
