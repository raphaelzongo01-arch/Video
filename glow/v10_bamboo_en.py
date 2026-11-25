"""Video 10 (EN) — "The bamboo"."""
import math, os
import engine
from engine import *
from extras import *

engine.LANG = "en"
SEED = 101
SPEED = 1.0
VOICE = "el_jessica"
CACHE = os.path.join(ROOT, "out", "tts_v10")
MUSIC = {}
GY = 760     # niveau du sol
SX = 960     # position de la graine


def soil(c, a=1.0):
    c.drawRect(skia.Rect.MakeLTRB(0, GY, W, H), paint((7, 8, 12), a))
    line(c, [(150, GY), (1770, GY)], 0.8 * a, 2.5, 0.8)


def seed(c, a=1.0):
    c.drawOval(skia.Rect.MakeXYWH(SX - 12, GY + 40, 24, 16), paint(WHITE, a))
    c.drawCircle(SX, GY + 48, 30, paint(WHITE, 0.25 * a, blur=14))


def roots(c, k, a=1.0):
    import random
    r = random.Random(3)
    for i in range(14):
        ang = math.pi / 2 + r.uniform(-1.2, 1.2)
        L = r.uniform(90, 220)
        pts = [(SX, GY + 48)]
        x, y = SX, GY + 48
        for j in range(5):
            x += math.cos(ang) * L / 5 + r.uniform(-12, 12)
            y += math.sin(ang) * L / 5
            pts.append((x, y))
        line(c, pts, a * 0.8, 2, 0.9, progress=max(0.001, k), smooth=True)


def year_box(c, txt, k):
    if k > 0:
        c.save(); c.translate(SX, 440); c.scale(k, k)
        boxed(c, txt, 0, 0, k, 22, 6, 24)
        c.restore()


# 1 — une graine de bambou va dans le sol
def s1(c, T):
    soil(c)
    k = T.pc(0, 1.2, f=ease)
    c.drawCircle(SX, lerp(500, GY + 48, k), 8, paint(WHITE, 1))
    if k >= 1:
        seed(c)


def years(c, T, labels, flat=True):
    soil(c); seed(c)
    for j, lab in enumerate(labels):
        if T.t >= T.c(j) - 0.05 and (j + 1 >= len(labels) or T.t < T.c(j + 1) - 0.05):
            year_box(c, lab, eback(T.pc(j, 0.35)))
    line(c, [(SX - 30, GY - 2), (SX + 30, GY - 2)], 0.3, 2, 0)


# 2-4 — année 1, 2, 3, 4 : rien
def s2(c, T):
    years(c, T, ["YEAR 1", "YEAR 1"])
    draw_text(c, "0 FT", SX, 620, 40, TF_BOLD, a=T.pc(1, 0.4) * 0.7, glow=0.4)


def s3(c, T):
    years(c, T, ["YEAR 2", "YEAR 2"])
    draw_text(c, "0 FT", SX, 620, 40, TF_BOLD, a=0.7, glow=0.4)


def s4(c, T):
    years(c, T, ["YEAR 3", "YEAR 4", "YEAR 4"])
    draw_text(c, "0 FT", SX, 620, 40, TF_BOLD, a=0.7, glow=0.4)


# 5 — la plupart auraient abandonné
def s5(c, T):
    soil(c); seed(c)
    k = T.pc(0, 2.0, f=ease)
    figure(c, lerp(SX - 220, 300, k), GY, 1.0, 1 - 0.7 * k, dim=0.5 * k)


# 6 — mais sous terre, les racines poussaient
def s6(c, T):
    z = lerp(1.0, 1.25, T.pc(0, 2.5, f=ease))
    camera(c, z, SX, lerp(600, 820, T.pc(0, 2.5, f=ease)))
    soil(c); seed(c)
    roots(c, T.pc(1, 2.2, f=ease))


# 7 — puis en année 5 : 27 mètres en six semaines
def s7(c, T):
    soil(c)
    roots(c, 1, 0.5)
    k = T.pc(1, 2.2, f=ease)
    top = lerp(GY, 300, k)
    line(c, [(SX, GY), (SX, top)], 1, 9, 1.4)
    for j in range(int((GY - top) / 70)):
        yy = GY - 70 * (j + 1)
        line(c, [(SX - 14, yy), (SX + 14, yy)], 0.8, 3, 0.3)
        lf = (-1) ** j
        line(c, [(SX, yy), (SX + lf * 60, yy - 30)], 0.7, 2.5, 0.6)
    year_box(c, "YEAR 5", eback(T.pc(0, 0.35)))
    draw_text(c, f"{int(90 * k)} FT", SX + 230, lerp(GY, 360, k), 64, TF_BOLD, a=T.pc(1, 0.4), glow=0.9)
    tag(c, "IN 6 WEEKS", SX + 230, lerp(GY, 360, k) + 50, T.pc(2, 0.4) * 0.8, 15, 5)


# 8 — tu n'es pas bloqué, tu construis des racines
def s8(c, T):
    soil(c)
    roots(c, 1, 0.9)
    seed(c)
    figure(c, SX, GY, 1.1, 1, lit=0.8)
    light_bloom(c, SX, GY + 80, 360, 0.5 * T.pc(1, 0.8))


# 9 — CTA
def s9(c, T):
    k = T.pc(0, 0.6)
    figure(c, 860, 800, 1.2, k, dim=0.5)
    figure(c, 1060, 800, 1.2, k, lit=T.pc(0, 1.0, delay=0.5))
    kk = T.pc(1, 0.5, f=eback)
    c.save(); c.translate(960, 920); c.scale(kk, kk)
    rrect(c, 0, 0, 380, 64, 32, kk, stroke=2.5, glow=0.9, fill=(10, 12, 18))
    draw_text(c, "SHARE  →", 0, 8, 22, a=kk, spacing=5)
    c.restore()


SCENES = [
    dict(say=["A bamboo seed", "goes into the *ground*."], draw=s1),
    dict(say=["Year one.", "*Nothing*."], draw=s2),
    dict(say=["Year two.", "Nothing."], draw=s3),
    dict(say=["Year three.", "Year four.", "Still *nothing*."], draw=s4),
    dict(say=["Most people would have *quit*."], draw=s5),
    dict(say=["But underground,", "the roots were *growing*."], draw=s6),
    dict(say=["Then in year five,", ("it grows *90 feet*", "it grows ninety feet"), "in six *weeks*."], draw=s7),
    dict(say=["You're not stuck.", "You're building *roots*."], draw=s8),
    dict(say=["Send this to someone", "who feels *stuck*."], draw=s9),
]
