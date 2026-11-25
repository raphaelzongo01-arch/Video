"""Video 13 (EN) — "Excuses"."""
import math, os
import engine
from engine import *
from extras import *
from v12_oneyear_en import cta

engine.LANG = "en"
SEED = 131
SPEED = 1.0
VOICE = "el_jessica"
CACHE = os.path.join(ROOT, "out", "tts_v13")
MUSIC = {}
EX = ["TOO TIRED", "TOO BUSY", "NOT READY", "NO MONEY", "TOMORROW", "BAD DAY"]
WX = 1150


def wall(c, k=1.0, broken=0.0, a=1.0):
    for i, lab in enumerate(EX):
        kk = clamp(k * len(EX) - i)
        if kk <= 0:
            continue
        y = 900 - i * 82
        dx = (1 if i % 2 else -1) * 260 * broken * (0.6 + 0.1 * i)
        dy = -80 * broken * math.sin(i)
        c.save(); c.translate(WX + dx, y + dy); c.rotate(25 * broken * (1 if i % 2 else -1)); c.scale(kk, kk)
        boxed(c, lab, 0, 0, kk * a * (1 - 0.7 * broken), 16, 5, 30)
        c.restore()


# 1 — tu n'as pas un problème de temps, tu as un problème d'excuses
def s1(c, T):
    figure(c, 640, 900, 1.2, 1, lit=0.3)
    clock(c, 960, 520, 70, T.pc(0, 0.5) * (1 - T.pc(1, 0.4)), ang=T.t * 2)
    k = T.pc(1, 0.4, f=eback)
    if k > 0:
        c.save(); c.translate(960, 520); c.scale(k, k)
        boxed(c, "EXCUSES", 0, 0, k, 22, 6, 26)
        c.restore()


# 2 — trop fatigué, trop occupé, pas prêt…
def s2(c, T):
    figure(c, 640, 900, 1.2, 1, lit=0.3)
    wall(c, T.pc(0, T.dur - 0.4, f=lambda v: clamp(v)))


# 3 — chaque excuse est une brique, et tu construis un mur
def s3(c, T):
    figure(c, 640, 900, 1.2, 1, dim=0.3 * T.pc(1, 0.8))
    wall(c, 1)


# 4 — le seul moyen, c'est de passer à travers
def s4(c, T):
    run = T.pc(1, 0.7, f=lambda v: clamp(v) ** 2)
    x = lerp(640, 1500, run)
    wall(c, 1, broken=clamp((x - WX + 120) / 300))
    figure(c, x, 900, 1.2, 1, lit=0.6 + 0.4 * run)
    if run >= 1:
        light_bloom(c, 1500, 820, 380, 0.7)


# 5 — de l'autre côté : les résultats
def s5(c, T):
    light_bloom(c, 1300, 760, 460, 0.8)
    figure(c, 1300, 900, 1.3, 1, lit=1, arms="up" if T.t > T.c(1) else "down")
    k = T.pc(1, 0.5, f=eback)
    c.save(); c.translate(1300, 520); c.scale(k, k)
    boxed(c, "RESULTS", 0, 0, k, 22, 6, 26)
    c.restore()
    wall(c, 1, broken=1, a=0.5)


def s6(c, T):
    cta(c, T)


SCENES = [
    dict(say=["You don't have a time problem.", "You have an *excuse* problem."], draw=s1),
    dict(say=["Too tired.", "Too busy.", "Not ready.", "*Tomorrow*."], draw=s2),
    dict(say=["Every excuse is a brick.", "And you're building a *wall*."], draw=s3),
    dict(say=["The only way out", "is *through*."], draw=s4),
    dict(say=["And on the other side?", "*Results*."], draw=s5),
    dict(say=["Send this to someone", "full of *excuses*."], draw=s6),
]
