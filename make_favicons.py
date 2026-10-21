#!/usr/bin/env python3
"""
Generate favicon files from the OFFICIAL COUNTER CULTURE logo.
Nothing is redesigned: the logo is only scaled and centered on a transparent
square canvas (no cropping, no distortion, no recoloring).

Usage:  python3 make_favicons.py path/to/logo.png [output_dir]
Needs:  pip install pillow
Output: favicon.ico (16/32/48), favicon-48x48.png, favicon-96x96.png,
        apple-touch-icon.png (180x180, solid background)
"""
import sys
from PIL import Image

src = sys.argv[1] if len(sys.argv) > 1 else "logo.png"
out = sys.argv[2] if len(sys.argv) > 2 else "."

logo = Image.open(src).convert("RGBA")
w, h = logo.size
print(f"Source: {src} ({w}x{h})")
if min(w, h) < 96:
    print("WARNING: source is smaller than 96px; use a larger original for crisp icons.")

def square(img, size, pad_pct=0.06, bg=(0, 0, 0, 0)):
    """Fit img inside a size x size square, preserving aspect ratio."""
    canvas = Image.new("RGBA", (size, size), bg)
    inner = int(size * (1 - 2 * pad_pct))
    ratio = min(inner / img.width, inner / img.height)
    r = img.resize((max(1, round(img.width * ratio)), max(1, round(img.height * ratio))), Image.LANCZOS)
    canvas.paste(r, ((size - r.width) // 2, (size - r.height) // 2), r)
    return canvas

square(logo, 48).save(f"{out}/favicon-48x48.png")
square(logo, 96).save(f"{out}/favicon-96x96.png")
# favicon.ico: multi-size, built from a large master so small sizes stay sharp
square(logo, 256).save(f"{out}/favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

# Apple touch icons can't be transparent. Pick the logo's own background if it has
# one; otherwise change APPLE_BG to your brand background color.
APPLE_BG = (255, 255, 255, 255)
square(logo, 180, pad_pct=0.10, bg=APPLE_BG).convert("RGB").save(f"{out}/apple-touch-icon.png")
print("Done. Review each file visually before deploying.")
