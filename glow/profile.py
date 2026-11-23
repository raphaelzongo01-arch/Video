"""Photo de profil 1080×1080 dans le style des vidéos (lisible en rond)."""
import math, os, random, sys
import numpy as np
import skia
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import (figure, line, make_path, glowdraw, light_bloom, star4, paint, ring, WHITE)

S = 1080


def background(c):
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    d = np.sqrt(((xx - S / 2) / (S * 0.62)) ** 2 + ((yy - S * 0.46) / (S * 0.62)) ** 2)
    k = np.clip(d, 0, 1)[..., None] ** 1.2
    img = np.array([26, 30, 42], np.float32) * (1 - k) + np.array([4, 5, 8], np.float32) * k
    img += np.random.default_rng(3).normal(0, 1.3, (S, S))[..., None]
    arr = np.dstack([np.clip(img, 0, 255).astype(np.uint8), np.full((S, S), 255, np.uint8)])
    c.drawImage(skia.Image.fromarray(np.ascontiguousarray(arr), colorType=skia.kRGBA_8888_ColorType), 0, 0)
    r = random.Random(5)
    for _ in range(70):
        x, y = r.uniform(0, S), r.uniform(0, S * 0.7)
        c.drawCircle(x, y, r.uniform(0.7, 1.8), paint(WHITE, r.uniform(0.15, 0.55)))


def main(out):
    surf = skia.Surface(S, S)
    c = surf.getCanvas()
    background(c)
    top = (540, 600)
    light_bloom(c, 540, 560, 520, 1.0)
    hill_pts = [(-80, 1000), (220, 930), (420, 720), (540, 600), (660, 720), (860, 930), (1160, 1000)]
    hill = make_path(hill_pts, True)
    fill = skia.Path(hill); fill.lineTo(1160, 1200); fill.lineTo(-80, 1200); fill.close()
    c.drawPath(fill, paint((5, 6, 10), 1))
    glowdraw(lambda p: c.drawPath(hill, p), 1.0, WHITE, 1.4, 4)
    figure(c, top[0], top[1], 2.1, 1.0, lit=1.0, arms="up")
    ring(c, 540, 470, 215, 0.35, w=2)
    pts = [(300, 250), (410, 190), (540, 225), (670, 175), (790, 245)]
    line(c, pts, 0.35, 1.6, 0.4)
    for (x, y) in pts:
        star4(c, x, y, 13, 1.0)
    img = surf.makeImageSnapshot()
    img.save(out, skia.kPNG)
    # aperçu en rond
    from PIL import Image, ImageDraw
    im = Image.open(out).convert("RGBA")
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).ellipse([0, 0, S, S], fill=255)
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255)); bg.paste(im, (0, 0), m)
    bg.save(out.replace(".png", "_apercu_rond.png"))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../photo_profil.png")
