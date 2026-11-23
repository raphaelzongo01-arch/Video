"""Éléments graphiques supplémentaires (téléphone, grille de jours, compteur, vague)."""
import math
from engine import *


def phone(c, x, y, h=200, a=1.0, glow_screen=0.0, rot=0.0):
    w = h * 0.52
    c.save(); c.translate(x, y); c.rotate(rot)
    if glow_screen > 0:
        c.drawCircle(0, 0, h * 0.9, paint((150, 175, 255), a * 0.25 * glow_screen, blur=50))
    rrect(c, 0, 0, w, h, w * 0.18, a, stroke=3.5, glow=0.9, fill=(8, 9, 13))
    if glow_screen > 0:
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2 + 8, -h / 2 + 18, w - 16, h - 36), 8, 8)
        c.drawRRect(rr, paint((170, 190, 255), a * 0.35 * glow_screen))
    line(c, [(-w * 0.12, -h / 2 + 9), (w * 0.12, -h / 2 + 9)], a, 3, 0)
    c.restore()


def feed(c, x, y, h, a, t):
    """Écran de téléphone avec des cartes qui défilent."""
    w = h * 0.52
    phone(c, x, y, h, a, glow_screen=0.25)
    c.save(); c.translate(x, y)
    c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2 + 8, -h / 2 + 18, w - 16, h - 36), 8, 8), True)
    off = (t * 90) % 70
    for i in range(-1, 6):
        yy = -h / 2 + 24 + i * 70 - off
        rrect(c, 0, yy + 26, w - 34, 56, 6, a * 0.7, stroke=1.6, glow=0.2)
        figure(c, -w / 2 + 34, yy + 46, 0.28, a * 0.8, halo=0)
        line(c, [(-w / 2 + 58, yy + 18), (w / 2 - 26, yy + 18)], a * 0.5, 2, 0)
        line(c, [(-w / 2 + 58, yy + 32), (w / 2 - 50, yy + 32)], a * 0.35, 2, 0)
    c.restore()


def dot_grid(c, x, y, n_lit, a=1.0, total=365, cols=29, sp=23, r=5.2, k_lit=1.0):
    rows = math.ceil(total / cols)
    x0 = x - (cols - 1) * sp / 2
    y0 = y - (rows - 1) * sp / 2
    lit_count = int(n_lit * k_lit)
    for i in range(total):
        px, py = x0 + (i % cols) * sp, y0 + (i // cols) * sp
        if i < lit_count:
            circle(c, px, py, r * 1.25, a, glow=1.6)
        else:
            circle(c, px, py, r * 0.8, a * 0.5, stroke=1.4, glow=0)


def counter(c, x, y, value, size=120, a=1.0, suffix="", tf=None):
    draw_text(c, f"{int(round(value))}{suffix}", x, y, size, tf or TF_BOLD, a=a, glow=0.9)


def clock_arc(c, x, y, r, hours, a=1.0, k=1.0):
    """Cadran avec un arc lumineux de `hours` heures (sur 24)."""
    circle(c, x, y, r, a, stroke=3, glow=0.8)
    for i in range(24):
        t = i * math.pi / 12 - math.pi / 2
        q = 0.86 if i % 6 else 0.78
        line(c, [(x + r * q * math.cos(t), y + r * q * math.sin(t)),
                 (x + r * 0.93 * math.cos(t), y + r * 0.93 * math.sin(t))], a * 0.6, 2, 0)
    if hours * k > 0:
        p = skia.Path()
        p.addArc(skia.Rect.MakeXYWH(x - r * 1.15, y - r * 1.15, r * 2.3, r * 2.3), -90, 360 * hours / 24 * k)
        glowdraw(lambda q: c.drawPath(p, q), a, WHITE, 1.3, 9)


def wave_pts(x0, x1, y, amp, periods, n=160, phase=0.0, drift=0.0):
    return [(x0 + (x1 - x0) * i / n,
             y - amp * math.sin(phase + 2 * math.pi * periods * i / n) - drift * i / n) for i in range(n + 1)]


def briefcase(c, x, y, s, a):
    rrect(c, x, y + 8 * s, 90 * s, 62 * s, 8 * s, a, stroke=3, glow=0.8)
    rrect(c, x, y - 28 * s, 36 * s, 18 * s, 5 * s, a, stroke=3, glow=0.6)
    line(c, [(x - 45 * s, y + 4 * s), (x + 45 * s, y + 4 * s)], a * 0.6, 2, 0)


def dumbbell(c, x, y, s, a):
    line(c, [(x - 40 * s, y), (x + 40 * s, y)], a, 6 * s, 0.6)
    for dx in (-40, 40):
        rrect(c, x + dx * s, y, 16 * s, 54 * s, 5 * s, a, stroke=3, glow=0.8, fill=(8, 9, 13))
    for dx in (-58, 58):
        rrect(c, x + dx * s, y, 12 * s, 34 * s, 4 * s, a, stroke=3, glow=0.8, fill=(8, 9, 13))
