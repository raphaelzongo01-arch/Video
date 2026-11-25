"""Video 16 (EN) — "What if it works?"."""
import math, os
import engine
from engine import *
from extras import *
from v12_oneyear_en import cta

engine.LANG = "en"
SEED = 161
SPEED = 1.0
VOICE = "el_jessica"
CACHE = os.path.join(ROOT, "out", "tts_v16")
MUSIC = {}
LX, RX, GY = 700, 1300, 760


def cliffs(c, a=1.0):
    for (x0, x1) in ((150, LX), (RX, 1770)):
        p = skia.Path(); p.moveTo(x0, GY); p.lineTo(x1, GY); p.lineTo(x1 + (-30 if x1 == LX else 0), 1100)
        p.lineTo(x0, 1100); p.close()
        c.drawPath(p, paint((7, 8, 12), a))
    line(c, [(150, GY), (LX, GY), (LX - 30, 1100)], a * 0.9, 3, 0.9)
    line(c, [(1770, GY), (RX, GY), (RX + 30, 1100)], a * 0.9, 3, 0.9)


def planks(c, n, a=1.0):
    w = (RX - LX) / 8
    for i in range(n):
        x = LX + w * i + w / 2
        rrect(c, x, GY + 6, w - 10, 14, 4, a, stroke=2.5, glow=0.8, fill=(10, 12, 18))


# 1 — tu as peur que ça rate
def s1(c, T):
    cliffs(c)
    figure(c, LX - 120, GY, 1.1, 1, lit=0.3)
    draw_text(c, "?", RX + 150, 560, 70, TF_BOLD, a=T.pc(0, 0.5) * 0.7, glow=0.6)


# 2 — mais si ça marchait ?
def s2(c, T):
    cliffs(c)
    k = T.pc(0, 0.8)
    light_bloom(c, RX + 220, GY - 120, 380, 0.7 * k)
    figure(c, RX + 220, GY, 1.1, k, lit=1, arms="up")
    figure(c, LX - 120, GY, 1.1, 1, lit=0.3 + 0.4 * k)


# 3 — tu ne verras jamais tout le pont
def s3(c, T):
    cliffs(c)
    dashed(c, [(LX, GY), (RX, GY)], 0.35 * T.pc(0, 0.5), 2, (8, 10))
    figure(c, LX - 120, GY, 1.1, 1, lit=0.4)
    light_bloom(c, RX + 220, GY - 120, 300, 0.4)


# 4 — chaque pas construit la planche suivante
def s4(c, T):
    cliffs(c)
    k = T.pc(0, T.dur - 0.3, f=lambda v: clamp(v))
    n = int(1 + 7 * k)
    planks(c, n)
    w = (RX - LX) / 8
    x = lerp(LX - 120, LX + w * (n - 1) + w / 2, clamp(k * 1.05))
    figure(c, x, GY, 1.1, 1, lit=0.6)


# 5 — de l'autre côté
def s5(c, T):
    cliffs(c)
    planks(c, 8)
    k = T.pc(0, 1.2, f=ease)
    light_bloom(c, RX + 220, GY - 120, 420, 0.8)
    figure(c, lerp(RX - 40, RX + 220, k), GY, 1.2, 1, lit=1, arms="up" if k >= 1 else "down")


def s6(c, T):
    cta(c, T)


SCENES = [
    dict(say=["You're scared it won't work."], draw=s1),
    dict(say=["But what if it *does*?"], draw=s2),
    dict(say=["You'll never see the whole bridge", "before you *start*."], draw=s3),
    dict(say=["Every step you take", "builds the *next* one."], draw=s4),
    dict(say=["Just take the *first* step."], draw=s5),
    dict(say=["Send this to someone", "who's *scared* to start."], draw=s6),
]
