#!/usr/bin/env python3
"""Thin SNAP blit. Does not own the timeline.

Reads SNAP v1 blocks from a Soft export and writes PPM frames plus a wav
whose frequency is the SNAP TONE field (0 = silence). No copyrighted
assets, no diffusion, no beat table of its own.
"""
from __future__ import annotations

import math
import struct
import sys
import wave
from pathlib import Path

W, H = 960, 540

# Original 5x7 glyphs, row-major, low 5 bits. Not a redistributed font file.
def _g(*rows: int) -> tuple[int, ...]:
    return rows

FONT: dict[str, tuple[int, ...]] = {
    "A": _g(0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "B": _g(0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110),
    "C": _g(0b01111, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b01111),
    "D": _g(0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110),
    "E": _g(0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    "F": _g(0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000),
    "G": _g(0b01111, 0b10000, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111),
    "H": _g(0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "I": _g(0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b11111),
    "J": _g(0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100),
    "K": _g(0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    "L": _g(0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111),
    "M": _g(0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001),
    "N": _g(0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001),
    "O": _g(0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "P": _g(0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000),
    "Q": _g(0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101),
    "R": _g(0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001),
    "S": _g(0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110),
    "T": _g(0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    "U": _g(0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "V": _g(0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "W": _g(0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b10101, 0b01010),
    "X": _g(0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001),
    "Y": _g(0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100),
    "Z": _g(0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
    "0": _g(0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110),
    "1": _g(0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "2": _g(0b01110, 0b10001, 0b00001, 0b00010, 0b00100, 0b01000, 0b11111),
    "3": _g(0b11110, 0b00001, 0b00001, 0b01110, 0b00001, 0b00001, 0b11110),
    "4": _g(0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010),
    "5": _g(0b11111, 0b10000, 0b10000, 0b11110, 0b00001, 0b00001, 0b11110),
    "6": _g(0b01110, 0b10000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110),
    "7": _g(0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000),
    "8": _g(0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110),
    "9": _g(0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00001, 0b01110),
    "-": _g(0b00000, 0b00000, 0b00000, 0b11111, 0b00000, 0b00000, 0b00000),
    ".": _g(0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b01100, 0b01100),
    ":": _g(0b00000, 0b01100, 0b01100, 0b00000, 0b01100, 0b01100, 0b00000),
    " ": _g(0, 0, 0, 0, 0, 0, 0),
}


def parse_snaps(text: str) -> list[dict[str, str]]:
    blocks: list[dict[str, str]] = []
    cur: dict[str, str] | None = None
    for raw in text.splitlines():
        line = raw.rstrip("\n")
        if line == "SNAP v1":
            cur = {}
            continue
        if line == "END":
            if cur is not None:
                blocks.append(cur)
            cur = None
            continue
        if cur is None or not line:
            continue
        if " " in line:
            k, v = line.split(" ", 1)
            cur[k] = v
        else:
            cur[line] = ""
    return blocks


class Frame:
    def __init__(self) -> None:
        self.buf = bytearray(W * H * 3)

    def put(self, x: int, y: int, c: tuple[int, int, int]) -> None:
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.buf[i] = c[0]
            self.buf[i + 1] = c[1]
            self.buf[i + 2] = c[2]

    def fill(self, c: tuple[int, int, int]) -> None:
        pix = bytes(c)
        self.buf[:] = pix * (W * H)

    def line(self, x0: int, y0: int, x1: int, y1: int, c: tuple[int, int, int]) -> None:
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.put(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx: int, cy: int, r: int, c: tuple[int, int, int]) -> None:
        r2 = r * r
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r2:
                    self.put(x, y, c)

    def ring(self, cx: int, cy: int, r: int, c: tuple[int, int, int], thick: int = 2) -> None:
        r0 = max(0, r - thick)
        r2 = r * r
        r02 = r0 * r0
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                d = (x - cx) * (x - cx) + (y - cy) * (y - cy)
                if r02 <= d <= r2:
                    self.put(x, y, c)

    def rect(self, x: int, y: int, w: int, h: int, c: tuple[int, int, int]) -> None:
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.put(xx, yy, c)

    def text(self, s: str, x: int, y: int, scale: int, c: tuple[int, int, int]) -> None:
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT.get(" "))
            if glyph is None:
                cx += 6 * scale
                continue
            for row, bits in enumerate(glyph):
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        for sy in range(scale):
                            for sx in range(scale):
                                self.put(cx + col * scale + sx, y + row * scale + sy, c)
            cx += 6 * scale

    def text_center(self, s: str, y: int, scale: int, c: tuple[int, int, int]) -> None:
        width = len(s) * 6 * scale
        self.text(s, max(8, (W - width) // 2), y, scale, c)


def _i(snap: dict[str, str], key: str, default: int = 0) -> int:
    try:
        return int(snap.get(key, str(default)))
    except ValueError:
        return default


def draw_glyph(fr: Frame, kind: str, frame_i: int) -> None:
    x, y = 760, 210
    ink = (220, 210, 190)
    if kind == "hand":
        fr.disc(x, y + 20, 36, (90, 62, 40))
        fr.disc(x, y + 20, 28, (196, 140, 90))
        for i, dx in enumerate((-18, -6, 6, 18)):
            fr.rect(x + dx - 4, y - 28 - (i % 2) * 6, 8, 28, (176, 120, 74))
        fr.disc(x + 8, y + 8, 6, (120, 70, 40))
    elif kind == "paper":
        fr.rect(x - 40, y - 46, 80, 100, (232, 224, 200))
        for i in range(6):
            fr.rect(x - 28, y - 30 + i * 12, 56, 2, (40, 40, 40))
    elif kind == "rail":
        fr.line(x - 50, y + 40, x + 10, y - 30, ink)
        fr.line(x + 50, y + 40, x - 10, y - 30, ink)
        for i in range(5):
            yy = y + 30 - i * 14
            half = 46 - i * 8
            fr.line(x - half, yy, x + half, yy, (180, 170, 150))
    elif kind == "terminal":
        fr.rect(x - 46, y - 36, 92, 64, (8, 28, 12))
        fr.rect(x - 50, y - 40, 100, 72, (20, 40, 24))
        fr.rect(x - 46, y - 36, 92, 64, (6, 24, 10))
        for i in range(5):
            w = 20 + ((frame_i * 17 + i * 13) % 50)
            fr.rect(x - 36, y - 24 + i * 10, w, 3, (80, 255, 120))
    elif kind == "sphere":
        fr.ring(x, y, 40, (140, 210, 230), 2)
        fr.line(x - 40, y, x + 40, y, (140, 210, 230))
        fr.line(x, y - 40, x, y + 40, (140, 210, 230))
        fr.ring(x, y, 20, (140, 210, 230), 1)
        fr.ring(x, y, 8, (220, 240, 255), 2)
    else:
        for i in range(9):
            dx = ((i * 37 + frame_i) % 80) - 40
            dy = ((i * 19) % 70) - 30
            fr.disc(x + dx, y + dy, 2, (120, 120, 130))


def draw_snap(snap: dict[str, str]) -> Frame:
    fr = Frame()
    fr.fill((10, 12, 18))
    for x in range(0, W, 48):
        fr.line(x, 0, x, H, (18, 20, 28))
    for y in range(0, H, 48):
        fr.line(0, y, W, y, (18, 20, 28))

    clock = snap.get("CLOCK", "00:00:00.000")
    caption = snap.get("CAPTION", "")
    show = _i(snap, "SHOW_CAPTION", 1)
    if show and caption:
        fr.text_center(caption, 36, 3, (236, 232, 220))
    fr.text_center(clock, 78, 3, (180, 190, 210))

    cx, cy, radius = 430, 300, 150
    fr.ring(cx, cy, radius, (230, 230, 230), 3)
    for i in range(24):
        ang = -math.pi / 2 + (i / 24.0) * math.tau
        inner = radius - (16 if i % 6 == 0 else 8)
        fr.line(
            int(cx + math.cos(ang) * inner),
            int(cy + math.sin(ang) * inner),
            int(cx + math.cos(ang) * (radius - 2)),
            int(cy + math.sin(ang) * (radius - 2)),
            (230, 230, 230),
        )
    h = _i(snap, "H")
    m = _i(snap, "M")
    s = _i(snap, "S")
    sub = _i(snap, "SUBMS")
    frac = (h * 3600000 + m * 60000 + s * 1000 + sub) / 86400000.0
    ang = -math.pi / 2 + frac * math.tau
    fr.line(cx, cy, int(cx + math.cos(ang) * 110), int(cy + math.sin(ang) * 110), (245, 245, 245))
    fr.disc(cx, cy, 4, (245, 245, 245))

    kind = snap.get("GLYPH", snap.get("SCENE", "wild"))
    draw_glyph(fr, kind, _i(snap, "FRAME"))

    ppm = max(0, min(1000000, _i(snap, "PROGRESS")))
    fr.rect(80, 490, 800, 8, (40, 42, 52))
    fr.rect(80, 490, max(1, 800 * ppm // 1000000), 8, (232, 186, 92))
    beat = snap.get("BEAT", "")
    year = snap.get("YEAR", "")
    meta = f"BEAT {beat}  YEAR {year}".upper()
    fr.text(meta, 80, 504, 2, (150, 156, 170))
    if _i(snap, "AT_NOW") == 1:
        fr.text("AT NOW", 760, 504, 2, (140, 210, 230))
    return fr


def write_ppm(path: Path, fr: Frame) -> None:
    header = f"P6\n{W} {H}\n255\n".encode("ascii")
    path.write_bytes(header + bytes(fr.buf))


def write_wav(path: Path, snaps: list[dict[str, str]], hold_s: float = 0.5) -> None:
    sr = 22050
    n_hold = int(sr * hold_s)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        for snap in snaps:
            freq = _i(snap, "TONE", 0)
            frames = bytearray()
            for i in range(n_hold):
                if freq <= 0:
                    sample = 0
                else:
                    env = 1.0
                    a = int(sr * 0.02)
                    rel = int(sr * 0.05)
                    if i < a:
                        env = i / a
                    elif i > n_hold - rel:
                        env = max(0.0, (n_hold - i) / rel)
                    sample = int(9000 * env * math.sin(2 * math.pi * freq * i / sr))
                frames += struct.pack("<h", sample)
            wf.writeframes(frames)


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: blit_snap.py SNAP.txt FRAMES_DIR WAV", file=sys.stderr)
        return 2
    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    out = Path(sys.argv[2])
    wav = Path(sys.argv[3])
    snaps = parse_snaps(text)
    if not snaps:
        print("blit: no SNAP blocks", file=sys.stderr)
        return 1
    out.mkdir(parents=True, exist_ok=True)
    for i, snap in enumerate(snaps):
        fr = draw_snap(snap)
        write_ppm(out / f"f{i:03d}.ppm", fr)
    write_wav(wav, snaps)
    print(f"blit: frames={len(snaps)} dir={out} wav={wav}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
