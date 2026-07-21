"""Genera los iconos PNG de la PWA (app instalable en Android).

Uso: OUTPUT_DIR=. python3 scripts/build_icons.py
"""
import math
import os

from PIL import Image, ImageDraw

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", ".")
NAVY = (9, 40, 59)
GREEN = (8, 112, 71)
LIME = (199, 243, 107)
INK = (16, 35, 58)


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_background(draw, size):
    for y in range(size):
        draw.line([(0, y), (size, y)], fill=lerp(NAVY, GREEN, y / size))


def draw_ball(draw, cx, cy, radius):
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(255, 255, 255))
    pent = radius * 0.42
    points = [
        (cx + pent * math.sin(math.tau * i / 5), cy - pent * math.cos(math.tau * i / 5))
        for i in range(5)
    ]
    draw.polygon(points, fill=INK)
    for px, py in points:
        dx, dy = px - cx, py - cy
        norm = math.hypot(dx, dy)
        end = (cx + dx / norm * radius * 0.97, cy + dy / norm * radius * 0.97)
        draw.line([(px, py), end], fill=INK, width=max(2, round(radius * 0.07)))


def build_icon(size, maskable=False):
    scale = 4
    canvas = size * scale
    image = Image.new("RGB", (canvas, canvas))
    draw = ImageDraw.Draw(image)
    draw_background(draw, canvas)
    # Zona segura del 80 % para iconos maskable.
    radius = canvas * (0.26 if maskable else 0.32)
    cx = cy = canvas / 2
    draw_ball(draw, cx, cy, radius)
    accent = canvas * (0.045 if maskable else 0.055)
    draw.ellipse(
        [cx + radius * 0.85, cy - radius * 1.25 - accent, cx + radius * 0.85 + accent * 2, cy - radius * 1.25 + accent],
        fill=LIME,
    )
    if not maskable:
        rounded = Image.new("L", (canvas, canvas), 0)
        ImageDraw.Draw(rounded).rounded_rectangle([0, 0, canvas, canvas], radius=canvas * 0.22, fill=255)
        image.putalpha(rounded)
    return image.resize((size, size), Image.LANCZOS)


def main():
    targets = [
        ("icon-192.png", 192, False),
        ("icon-512.png", 512, False),
        ("icon-maskable-512.png", 512, True),
        ("apple-touch-icon.png", 180, True),
    ]
    for name, size, maskable in targets:
        path = os.path.join(OUTPUT_DIR, name)
        build_icon(size, maskable).save(path)
        print("✔", path)


if __name__ == "__main__":
    main()
