"""Video 15 (EN) — "Consistency beats intensity"."""
import math, os
import engine
from engine import *
from extras import *
from v12_oneyear_en import cta

engine.LANG = "en"
SEED = 151
SPEED = 1.0
VOICE = "el_jessica"
CACHE = os.path.join(ROOT, "out", "tts_v15")
MUSIC = {}
X0, X1 = 360, 1580
LA, LB = 600, 860


def lanes(c):
    line(c, [(X0, LA), (X1, LA)], 0.35, 2, 0.3)
    line(c, [(X0, LB), (X1, LB)], 0.35, 2, 0.3)
    tag(c, "INTENSITY", X0 + 70, LA + 40, 0.6, 13, 5)
    tag(c, "CONSISTENCY", X0 + 80, LB + 40, 0.6, 13, 5)


# 1 — deux personnes commencent le même jour
def s1(c, T):
    lanes(c)
    figure(c, X0 + 20, LA, 0.9, T.pc(0, 0.5), lit=0.4)
    figure(c, X0 + 20, LB, 0.9, T.pc(0, 0.5, delay=0.2), lit=0.4)


# 2 — la première fonce à fond
def s2(c, T):
    lanes(c)
    k = T.pc(0, 1.0, f=eout)
    xa = lerp(X0 + 20, 1050, k)
    line(c, [(X0, LA), (xa, LA)], 0.9, 3, 1.0)
    figure(c, xa, LA, 0.9, 1, lit=0.8)
    figure(c, X0 + 20, LB, 0.9, 1, lit=0.4)


# 3 — puis elle s'arrête, épuisée
def s3(c, T):
    lanes(c)
    line(c, [(X0, LA), (1050, LA)], 0.6, 3, 0.4)
    figure(c, 1050, LA, 0.9, 1, dim=0.6 * T.pc(0, 0.8))
    tag(c, "BURNED OUT", 1050, LA - 110, T.pc(1, 0.4) * 0.8, 14, 5)
    figure(c, X0 + 20, LB, 0.9, 1, lit=0.4)


# 4 — la deuxième avance un peu chaque jour
def s4(c, T):
    lanes(c)
    line(c, [(X0, LA), (1050, LA)], 0.4, 3, 0.2)
    figure(c, 1050, LA, 0.9, 1, dim=0.6)
    k = T.pc(0, T.dur - 0.3, f=lambda v: clamp(v))
    xb = lerp(X0 + 20, 1000, k)
    for i in range(int((xb - X0) / 60)):
        circle(c, X0 + 40 + i * 60, LB + 1, 4, 0.8, glow=0.6)
    figure(c, xb, LB, 0.9, 1, lit=0.7)


# 5 — et elle la dépasse, sans jamais forcer
def s5(c, T):
    lanes(c)
    line(c, [(X0, LA), (1050, LA)], 0.4, 3, 0.2)
    figure(c, 1050, LA, 0.9, 1, dim=0.6)
    k = T.pc(0, T.dur - 0.3, f=ease)
    xb = lerp(1000, X1 - 40, k)
    line(c, [(X0, LB), (xb, LB)], 0.9, 3, 1.0)
    figure(c, xb, LB, 0.9, 1, lit=0.9)
    if xb > 1060:
        light_bloom(c, xb, LB - 40, 260, 0.6 * clamp((xb - 1060) / 200))


# 6 — la constance bat l'intensité
def s6(c, T):
    k = T.pc(1, 0.5, f=eback)
    c.save(); c.translate(960, 640); c.scale(k, k)
    boxed(c, "CONSISTENCY > INTENSITY", 0, 0, k, 20, 5, 26)
    c.restore()
    figure(c, 960, 860, 1.2, T.pc(0, 0.5), lit=0.8)


def s7(c, T):
    cta(c, T)


SCENES = [
    dict(say=["Two people start on the same day."], draw=s1),
    dict(say=["The first one goes *all in*."], draw=s2),
    dict(say=["Two weeks later,", "*burned out*."], draw=s3),
    dict(say=["The second one does a little.", "Every. Single. *Day*."], draw=s4),
    dict(say=["And without ever rushing,", "*passes* them."], draw=s5),
    dict(say=["Consistency", "beats *intensity*."], draw=s6),
    dict(say=["Send this to someone", "who needs to *hear* it."], draw=s7),
]
