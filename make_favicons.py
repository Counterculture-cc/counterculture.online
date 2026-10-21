#!/usr/bin/env python3
"""
Generate favicon files from the OFFICIAL COUNTER CULTURE logo.
Nothing is redrawn: the white artwork is recolored solid black (same shapes, same
alpha), trimmed of empty margins, scaled proportionally, and centered on a
TRANSPARENT square. Only the Apple touch icon gets a white background, because
iOS does not support transparency.

Usage:  python3 make_favicons.py logo.png [output_dir] [--no-tagline]
  --no-tagline  crop off the small tagline line under the wordmark (a crop of
                the official artwork, not a redesign) so the wordmark stays legible.
Needs:  pip install pillow numpy
Output: favicon.ico (16/32/48), favicon-48x48.png, favicon-96x96.png, apple-touch-icon.png (180x180)
"""
import sys
import numpy as np
from PIL import Image

args = [a for a in sys.argv[1:] if not a.startswith("--")]
no_tagline = "--no-tagline" in sys.argv
src = args[0] if args else "logo.png"
out = args[1] if len(args) > 1 else "."
BG = (0, 0, 0, 0)            # transparent background
APPLE_BG = (255, 255, 255, 255)  # iOS needs an opaque background

logo = Image.open(src).convert("RGBA")
alpha = np.array(logo)[..., 3]
# Recolor artwork to solid black, keeping the exact shape/antialiasing (alpha) untouched
_px = np.array(logo); _px[..., :3] = 0
logo = Image.fromarray(_px, "RGBA")

def trim(img, a):
    ys, xs = np.where(a > 10)
    return img.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))

if no_tagline:
    # Split at the widest empty horizontal band between the wordmark and the tagline.
    rows = (alpha > 10).any(axis=1)
    ys = np.where(rows)[0]
    gaps = [(ys[i + 1] - ys[i], ys[i], ys[i + 1]) for i in range(len(ys) - 1) if ys[i + 1] - ys[i] > 1]
    if gaps:
        _, top_end, _ = max(gaps)
        logo = logo.crop((0, 0, logo.width, top_end + 1))
        alpha = np.array(logo)[..., 3]

logo = trim(logo, alpha)
print(f"Artwork used: {logo.width}x{logo.height}px ({'wordmark only' if no_tagline else 'full logo'})")

def square(img, size, pad_pct=0.05, bg=BG):
    canvas = Image.new("RGBA", (size, size), bg)
    inner = size * (1 - 2 * pad_pct)
    ratio = min(inner / img.width, inner / img.height)
    r = img.resize((max(1, round(img.width * ratio)), max(1, round(img.height * ratio))), Image.LANCZOS)
    canvas.alpha_composite(r, ((size - r.width) // 2, (size - r.height) // 2))
    return canvas

square(logo, 48).save(f"{out}/favicon-48x48.png")
square(logo, 96).save(f"{out}/favicon-96x96.png")
square(logo, 256).save(f"{out}/favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
square(logo, 180, pad_pct=0.10, bg=APPLE_BG).convert("RGB").save(f"{out}/apple-touch-icon.png")
print("Done. Review each file visually before deploying.")
