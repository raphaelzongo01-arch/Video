"""Video 9 (EN) — "Comfort zone"."""
import math, os
import engine
from engine import *
from extras import *

engine.LANG = "en"
SEED = 91
SPEED = 1.0
VOICE = "el_jessica"
CACHE = os.path.join(ROOT, "out", "tts_v9")
MUSIC = {}
CX, CY = 960, 660
ICONS = [(-1, 650, 500, "GOALS"), (0, 1270, 500, "BODY"), (1, 650, 830, "MONEY"), (2, 1270, 830, "CONFIDENCE")]


def zone(c, r, a=1.0, wobble=0.0):
    c.drawCircle(CX, CY, r, paint((150, 175, 255), 0.07 * a))
    circle(c, CX, CY + wobble, r, a * 0.9, stroke=3, glow=1.0)


def icon(c, i, x, y, k):
    if k <= 0:
        return
    c.save(); c.translate(x, y); c.scale(k, k)
    if i == -1:
        star4(c, 0, 0, 34, k)
    elif i == 0:
        dumbbell(c, 0, 0, 0.8, k)
    elif i == 1:
        circle(c, 0, 0, 36, k, stroke=3, glow=0.8); draw_text(c, "$", 0, 14, 40, TF_BOLD, a=k, glow=0.4)
    else:
        figure(c, 0, 30, 0.6, k, lit=0.6, arms="up")
    c.restore()


# 1 — ceci est ta zone de confort
def s1(c, T):
    zone(c, 170 * T.pc(0, 0.8, f=eback) + 1, T.pc(0, 0.5))
    figure(c, CX, CY + 60, 1.1, 1, lit=0.3)


# 2 — c'est chaud, c'est sûr, rien n'y pousse
def s2(c, T):
    zone(c, 170)
    figure(c, CX, CY + 60, 1.1, 1, lit=0.3, dim=0.35 * T.pc(2, 0.8))
    for j, lab in enumerate(["WARM", "SAFE"]):
        tag(c, lab, CX + (j * 2 - 1) * 330, CY - 10, T.pc(j, 0.4) * 0.8, 16, 6)
    k = T.pc(2, 0.5)
    tag(c, "NO GROWTH", CX, CY + 250, k, 16, 6)


# 3 — tout ce que tu veux est dehors
def s3(c, T):
    zone(c, 170)
    figure(c, CX, CY + 60, 1.1, 1, lit=0.3)
    for n, (i, x, y, lab) in enumerate(ICONS):
        k = T.pc(1, 0.45, delay=n * 0.15, f=eback)
        icon(c, i, x, y, k)
        tag(c, lab, x, y + 70, k * 0.8, 13, 5)


# 4 — le premier pas dehors fait mal
def s4(c, T):
    shake = math.sin(T.t * 40) * 3 * T.pc(1, 0.2) * (1 - T.pc(1, 1.2, delay=0.4))
    zone(c, 170, wobble=shake)
    for n, (i, x, y, lab) in enumerate(ICONS):
        icon(c, i, x, y, 0.6)
    k = T.pc(0, 1.2, f=ease)
    figure(c, CX + 210 * k + shake, CY + 60, 1.1, 1, lit=0.4)


# 5 — mais personne ne te dit ça
def s5(c, T):
    zone(c, 170)
    for n, (i, x, y, lab) in enumerate(ICONS):
        icon(c, i, x, y, 0.6)
    figure(c, CX + 210, CY + 60, 1.1, 1, lit=0.5)


# 6 — à chaque pas dehors, le cercle grandit
def s6(c, T):
    k = T.pc(1, 2.0, f=ease)
    r = lerp(170, 380, k)
    zone(c, r)
    for n, (i, x, y, lab) in enumerate(ICONS):
        icon(c, i, x, y, 0.6 + 0.4 * clamp((r - 300) / 70))
    figure(c, CX + lerp(210, 300, k), CY + 60, 1.1, 1, lit=0.5 + 0.5 * k)


# 7 — jusqu'à ce que ce qui te faisait peur devienne normal
def s7(c, T):
    zone(c, 380)
    light_bloom(c, CX, CY, 500, 0.5 * T.pc(1, 0.8))
    for n, (i, x, y, lab) in enumerate(ICONS):
        icon(c, i, x, y, 1.0)
        tag(c, lab, x, y + 70, 0.8, 13, 5)
    figure(c, CX, CY + 60, 1.2, 1, lit=1, arms="up" if T.t > T.c(1) else "down")


# 8 — CTA
def s8(c, T):
    k = T.pc(0, 0.6)
    figure(c, 860, 800, 1.2, k, dim=0.5)
    figure(c, 1060, 800, 1.2, k, lit=T.pc(0, 1.0, delay=0.5))
    kk = T.pc(1, 0.5, f=eback)
    c.save(); c.translate(960, 920); c.scale(kk, kk)
    rrect(c, 0, 0, 380, 64, 32, kk, stroke=2.5, glow=0.9, fill=(10, 12, 18))
    draw_text(c, "SHARE  →", 0, 8, 22, a=kk, spacing=5)
    c.restore()


SCENES = [
    dict(say=["This is your comfort *zone*."], draw=s1),
    dict(say=["It's warm.", "It's safe.", "And *nothing* grows here."], draw=s2),
    dict(say=["Everything you want", "is *outside* this circle."], draw=s3),
    dict(say=["The first step out", "feels *terrible*."], draw=s4),
    dict(say=["But here's what nobody tells you."], draw=s5),
    dict(say=["Every time you step out,", "the circle gets *bigger*."], draw=s6, zoom=1.15),
    dict(say=["Until the things that scared you", "feel *normal*."], draw=s7, zoom=1.15),
    dict(say=["Send this to someone", "who needs a *push*."], draw=s8),
]
