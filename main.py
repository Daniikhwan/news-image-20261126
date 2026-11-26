#!/usr/bin/env python3
"""news-image-20261126 -- sum up Thursday 26 November 2026 in one image.

A deterministic, pure-stdlib Python program. It draws a newspaper-style
front page (1024x1024 PNG) and writes it to $MAKEFUN_OUTPUT_DIR/entry.png.

Six stories, all first reported on -- or happening on -- 26 November 2026:
  1. Taiwan says it will keep its 15% US tariff (Reuters, Taipei, 26 Nov)
  2. Thanksgiving Day in the United States (Thursday 26 Nov)
  3. World Chess Championship, Game 3, Geneva -- Gukesh v Sindarov, 1-1
  4. India: Constitution Day, and 18 years since the 26/11 Mumbai attacks
  5. Virgin Australia airport staff strike at four airports today
  6. EU leaders meet in Brussels over the next long-term budget

No network, no randomness, no external files, no fonts: every glyph is
drawn from the 5x7 bitmap font defined below, and the PNG is encoded
by hand (zlib + struct). Running it twice gives byte-identical output.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

# --- palette ---------------------------------------------------------------
PAPER = (250, 243, 227)
INK = (28, 28, 34)
NAVY = (20, 33, 61)
GOLD = (217, 164, 65)
RED = (179, 39, 30)
WHITE = (255, 255, 255)
TEAL = (14, 107, 107)
ORANGE = (217, 108, 44)
GREEN = (46, 107, 52)
SAFFRON = (255, 153, 51)
FLAG_GREEN = (19, 136, 8)
FLAG_NAVY = (0, 0, 128)
SKY = (62, 124, 177)
EU_BLUE = (31, 58, 147)
EU_GOLD = (255, 204, 0)
BROWN = (123, 74, 33)
CREAM = (245, 230, 200)

# --- 5x7 bitmap font (uppercase, digits, punctuation) ----------------------
# Each glyph is 7 rows of 5 bits, "#" = on, "." = off.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
}


class Canvas:
    """A plain RGB pixel buffer with tiny drawing primitives."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = color[0]
            self.buf[i + 1] = color[1]
            self.buf[i + 2] = color[2]

    def hline(self, x1, x2, y, color):
        if x2 < x1:
            x1, x2 = x2, x1
        for x in range(max(0, x1), min(self.w, x2 + 1)):
            self.px(x, y, color)

    def vline(self, x, y1, y2, color):
        if y2 < y1:
            y1, y2 = y2, y1
        for y in range(max(0, y1), min(self.h, y2 + 1)):
            self.px(x, y, color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            self.hline(x, x + w - 1, yy, color)

    def border(self, x, y, w, h, color, t=2):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def line(self, x1, y1, x2, y2, color):
        dx = abs(x2 - x1)
        dy = -abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx + dy
        x, y = x1, y1
        while True:
            self.px(x, y, color)
            if x == x2 and y == y2:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def thick_line(self, x1, y1, x2, y2, width, color):
        steps = max(abs(x2 - x1), abs(y2 - y1), 1)
        r = width // 2
        for i in range(steps + 1):
            x = x1 + (x2 - x1) * i // steps
            y = y1 + (y2 - y1) * i // steps
            self.circle(x, y, r, color)

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.hline(cx - dx, cx + dx, cy + dy, color)

    def ring(self, cx, cy, r, color, t=2):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            inner = int(math.sqrt(max(0, (r - t) * (r - t) - dy * dy))) if abs(dy) < r - t else 0
            self.hline(cx - dx, cx - inner, cy + dy, color)
            self.hline(cx + inner, cx + dx, cy + dy, color)

    def fill_polygon(self, pts, color):
        ys = [p[1] for p in pts]
        n = len(pts)
        for y in range(min(ys), max(ys) + 1):
            xs = []
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.hline(int(round(xs[i])), int(round(xs[i + 1])), y, color)

    def star(self, cx, cy, r, color):
        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            rr = r if i % 2 == 0 else r * 0.45
            pts.append((int(round(cx + rr * math.cos(ang))),
                        int(round(cy + rr * math.sin(ang)))))
        self.fill_polygon(pts, color)

    def text_width(self, s, scale):
        return len(s) * 6 * scale

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale

    def text_center(self, y, s, scale, color):
        x = (self.w - self.text_width(s, scale)) // 2
        self.text(x, y, s, scale, color)

# --- pictograms (each drawn inside a 150x188 tile at tx, ty) ----------------

def pic_ship(c, tx, ty):
    # Containers stacked on a hull, riding two waves.
    c.rect(tx + 30, ty + 34, 90, 26, GOLD)
    c.rect(tx + 42, ty + 60, 66, 26, WHITE)
    c.rect(tx + 54, ty + 86, 42, 26, (232, 196, 120))
    c.fill_polygon([(tx + 18, ty + 112), (tx + 132, ty + 112),
                    (tx + 118, ty + 140), (tx + 32, ty + 140)], NAVY)
    c.hline(tx + 14, tx + 136, ty + 152, WHITE)
    c.hline(tx + 26, tx + 124, ty + 164, WHITE)
    c.line(tx + 96, ty + 34, tx + 96, ty + 14, INK)
    c.fill_polygon([(tx + 96, ty + 14), (tx + 116, ty + 20),
                    (tx + 96, ty + 26)], RED)


def pic_turkey(c, tx, ty):
    # A Thanksgiving turkey: fanned tail, round body, small head.
    cx, cy = tx + 75, ty + 118
    for ang in (-160, -135, -110, -90, -70, -45, -20):
        rad = math.radians(ang)
        ex = int(cx + 66 * math.cos(rad))
        ey = int(cy + 66 * math.sin(rad))
        px, py = -math.sin(rad), math.cos(rad)
        c.fill_polygon([
            (int(cx + 8 * px), int(cy - 6 + 8 * py)),
            (int(cx - 8 * px), int(cy - 6 - 8 * py)),
            (ex, ey),
        ], CREAM)
    c.circle(cx, cy, 42, BROWN)
    c.circle(cx, cy - 52, 16, BROWN)
    c.fill_polygon([(cx + 12, cy - 56), (cx + 28, cy - 50),
                    (cx + 12, cy - 46)], ORANGE)
    c.circle(cx + 22, cy - 42, 4, RED)
    c.thick_line(cx - 12, cy + 40, cx - 12, cy + 56, 4, INK)
    c.thick_line(cx + 12, cy + 40, cx + 12, cy + 56, 4, INK)


def pic_chess(c, tx, ty):
    # A 4x4 board with a white king and a black pawn.
    bx, by, sq = tx + 11, ty + 28, 32
    for r in range(4):
        for col in range(4):
            colr = WHITE if (r + col) % 2 == 0 else INK
            c.rect(bx + col * sq, by + r * sq, sq, sq, colr)
    kx, ky = bx + sq + sq // 2, by + sq + sq // 2
    c.circle(kx, ky + 2, 11, WHITE)
    c.ring(kx, ky + 2, 11, INK, 2)
    c.rect(kx - 8, ky + 10, 16, 4, INK)
    c.thick_line(kx, ky - 14, kx, ky - 2, 4, INK)
    c.thick_line(kx - 5, ky - 10, kx + 5, ky - 10, 4, INK)
    px_, py = bx + 2 * sq + sq // 2, by + 2 * sq + sq // 2
    c.circle(px_, py, 9, INK)
    c.rect(px_ - 7, py + 8, 14, 4, INK)


def pic_india(c, tx, ty):
    # A flame of remembrance above the Indian tricolour.
    c.fill_polygon([(tx + 75, ty + 12), (tx + 89, ty + 42),
                    (tx + 75, ty + 52), (tx + 61, ty + 42)], (226, 88, 26))
    c.fill_polygon([(tx + 75, ty + 26), (tx + 83, ty + 44),
                    (tx + 75, ty + 50), (tx + 67, ty + 44)], GOLD)
    fx, fy = tx + 15, ty + 66
    c.rect(fx, fy, 120, 24, SAFFRON)
    c.rect(fx, fy + 24, 120, 24, WHITE)
    c.rect(fx, fy + 48, 120, 24, FLAG_GREEN)
    c.ring(fx + 60, fy + 36, 10, FLAG_NAVY, 2)
    for i in range(8):
        ang = i * math.pi / 4
        c.line(fx + 60, fy + 36,
               int(fx + 60 + 9 * math.cos(ang)),
               int(fy + 36 + 9 * math.sin(ang)), FLAG_NAVY)
    c.text(tx + 30, ty + 152, "26/11", 3, WHITE)


def pic_plane(c, tx, ty):
    # An airliner above a picket sign that reads STRIKE.
    c.thick_line(tx + 20, ty + 70, tx + 128, ty + 70, 14, WHITE)
    c.fill_polygon([(tx + 128, ty + 62), (tx + 146, ty + 70),
                    (tx + 128, ty + 78)], WHITE)
    c.fill_polygon([(tx + 58, ty + 70), (tx + 84, ty + 112),
                    (tx + 96, ty + 112), (tx + 80, ty + 70)], WHITE)
    c.fill_polygon([(tx + 118, ty + 70), (tx + 126, ty + 42),
                    (tx + 134, ty + 42), (tx + 130, ty + 70)], WHITE)
    for wx in (52, 66, 80):
        c.circle(tx + wx, ty + 66, 2, INK)
    c.rect(tx + 35, ty + 130, 80, 34, WHITE)
    c.border(tx + 35, ty + 130, 80, 34, INK, 2)
    c.text(tx + 39, ty + 140, "STRIKE", 2, INK)
    c.thick_line(tx + 75, ty + 164, tx + 75, ty + 184, 4, INK)


def pic_eu(c, tx, ty):
    # A ring of twelve gold stars around the letters EU.
    cx, cy = tx + 75, ty + 88
    for i in range(12):
        ang = -math.pi / 2 + i * math.pi / 6
        sx = int(cx + 62 * math.cos(ang))
        sy = int(cy + 62 * math.sin(ang))
        c.star(sx, sy, 9, EU_GOLD)
    c.text(tx + 39, ty + 68, "EU", 6, WHITE)


PICTOGRAMS = {
    "ship": pic_ship,
    "turkey": pic_turkey,
    "chess": pic_chess,
    "india": pic_india,
    "plane": pic_plane,
    "eu": pic_eu,
}

# --- the six stories ---------------------------------------------------------
# tag: small coloured label. headline: up to 3 short lines, scale 4.
# sub: up to 3 lines, scale 2. accent: panel top bar + tile colour.
STORIES = [
    {
        "tag": "TRADE - TAIPEI",
        "headline": ["TAIWAN", "KEEPS 15%", "TARIFF"],
        "sub": ["TAIPEI CONFIDENT AFTER",
                "TRUMP'S NEW TARIFF",
                "SALVO ON 14 PARTNERS"],
        "accent": TEAL,
        "pic": "ship",
    },
    {
        "tag": "USA - HOLIDAY",
        "headline": ["AMERICA", "GIVES", "THANKS"],
        "sub": ["THURSDAY IS THE US",
                "HOLIDAY. TABLES FULL,",
                "MARKETS SHUT."],
        "accent": ORANGE,
        "pic": "turkey",
    },
    {
        "tag": "SPORT - GENEVA",
        "headline": ["CHESS", "GAME 3", "IN GENEVA"],
        "sub": ["GUKESH V SINDAROV",
                "TIED 1-1 IN THE",
                "YOUNGEST TITLE MATCH"],
        "accent": GREEN,
        "pic": "chess",
    },
    {
        "tag": "INDIA - MUMBAI",
        "headline": ["INDIA", "REMEMBERS", "26/11"],
        "sub": ["CONSTITUTION DAY, 18",
                "YEARS AFTER THE",
                "MUMBAI ATTACKS"],
        "accent": GOLD,
        "pic": "india",
    },
    {
        "tag": "LABOUR - AUSTRALIA",
        "headline": ["VIRGIN", "WALKS OUT"],
        "sub": ["AIRPORT STRIKES HIT",
                "FOUR AUSTRALIAN",
                "AIRPORTS TODAY"],
        "accent": SKY,
        "pic": "plane",
    },
    {
        "tag": "POLITICS - BRUSSELS",
        "headline": ["EU LEADERS", "HAGGLE OVER", "BUDGET"],
        "sub": ["BRUSSELS TALKS ON",
                "THE NEXT LONG-TERM",
                "EU BUDGET"],
        "accent": EU_BLUE,
        "pic": "eu",
    },
]

# --- layout ------------------------------------------------------------------

def draw_panel(c, x0, y0, story):
    pw, ph = 480, 244
    c.rect(x0, y0, pw, ph, WHITE)
    c.border(x0, y0, pw, ph, INK, 2)
    c.rect(x0 + 2, y0 + 2, pw - 4, 12, story["accent"])
    # Pictogram tile.
    tx, ty = x0 + 16, y0 + 28
    c.rect(tx, ty, 150, 188, story["accent"])
    c.border(tx, ty, 150, 188, INK, 2)
    PICTOGRAMS[story["pic"]](c, tx, ty)
    # Text column.
    tx2 = x0 + 182
    c.text(tx2, y0 + 32, story["tag"], 2, story["accent"])
    y = y0 + 56
    for line in story["headline"]:
        c.text(tx2, y, line, 4, INK)
        y += 30
    y += 8
    for line in story["sub"]:
        c.text(tx2, y, line, 2, (70, 70, 78))
        y += 18


def draw_front_page():
    c = Canvas(W, H, PAPER)
    # Masthead.
    c.rect(24, 24, 976, 124, NAVY)
    c.rect(24, 148, 976, 4, GOLD)
    c.text_center(38, "THE WORLD IN ONE DAY", 3, GOLD)
    c.text_center(66, "26 NOVEMBER 2026", 9, WHITE)
    # Kicker.
    c.text_center(166, "THURSDAY - SIX STORIES FROM AROUND THE WORLD", 3, RED)
    # Six panels, 2 columns x 3 rows.
    for i, story in enumerate(STORIES):
        x0 = 24 + (i % 2) * 496
        y0 = 198 + (i // 2) * 258
        draw_panel(c, x0, y0, story)
    # Footer with sources.
    c.text_center(972, "SOURCES: REUTERS - BBC - FIDE - THE HINDU - ABC NEWS",
                 2, (90, 90, 96))
    return c


# --- PNG encoding (hand-rolled, stdlib only) ---------------------------------

def _chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def write_png(path, canvas):
    raw = b"".join(
        b"\x00" + bytes(canvas.buf[y * W * 3:(y + 1) * W * 3])
        for y in range(H)
    )
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n"
           + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", zlib.compress(raw, 9))
           + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    canvas = draw_front_page()
    write_png(os.path.join(out_dir, "entry.png"), canvas)


if __name__ == "__main__":
    main()
