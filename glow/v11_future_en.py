"""Video 11 (EN) — "Your future self"."""
import math, os
import engine
from engine import *
from extras import *

engine.LANG = "en"
SEED = 111
SPEED = 1.0
VOICE = "el_jessica"
CACHE = os.path.join(ROOT, "out", "tts_v11")
MUSIC = {}
YOU = (480, 800)
FUT = (1440, 800)


def future(c, a=1.0, glow=1.0):
    light_bloom(c, FUT[0], FUT[1] - 60, 300, 0.6 * a * glow)
    figure(c, FUT[0], FUT[1], 1.2, a, lit=glow)
    tag(c, "FUTURE YOU", FUT[0], FUT[1] + 80, a * 0.8, 14, 5)


def you(c, x, a=1.0, lit=0.3, dim=0.0):
    figure(c, x, YOU[1], 1.2, a, lit=lit, dim=dim)
    tag(c, "YOU", x, YOU[1] + 80, a * 0.8, 14, 5)


# 1 — quelque part dans le futur, une version de toi qui a réussi
def s1(c, T):
    future(c, T.pc(1, 0.8), T.pc(2, 0.8))
    you(c, YOU[0], T.pc(0, 0.6))


# 2 — chaque choix te rapproche…
def s2(c, T):
    future(c)
    you(c, YOU[0])
    k = T.pc(1, 0.8, f=ease)
    line(c, [(YOU[0] + 80, 740), (lerp(YOU[0] + 80, FUT[0] - 80, k), 740)], 0.8, 3, 0.9, progress=max(0.001, k))


# 3 — …ou t'éloigne
def s3(c, T):
    future(c, 1, 1 - 0.5 * T.pc(0, 0.6))
    you(c, YOU[0] - 90 * T.pc(0, 0.8, f=ease), dim=0.3 * T.pc(0, 0.6))
    line(c, [(YOU[0] + 80, 740), (FUT[0] - 80, 740)], 0.3, 3, 0.2)


def step(c, T, d, label, ok):
    future(c)
    k = T.pc(1, 0.8, f=ease)
    x = YOU[0] + 260 + d * 160 * k
    you(c, x, lit=0.6 if ok else 0.1, dim=0 if ok else 0.4 * k)
    kk = T.pc(0, 0.4, f=eback)
    c.save(); c.translate(x, 470); c.scale(kk, kk)
    boxed(c, label, 0, 0, kk, 16, 5, 18)
    c.restore()
    if T.pc(1, 0.2) > 0:
        check(c, x, 540, 16 * T.pc(1, 0.4, f=eback), T.pc(1, 0.3), ok=ok)


# 4 — sauter la salle : un pas en arrière
def s4(c, T):
    step(c, T, -1, "SKIP THE GYM", False)


# 5 — lire 10 pages : un pas plus près
def s5(c, T):
    step(c, T, +1, "READ 10 PAGES", True)


# 6 — ils te regardent, ils attendent que tu te pointes
def s6(c, T):
    future(c, 1, 1)
    you(c, YOU[0] + 420)
    k = T.pc(0, 0.8)
    dashed(c, [(FUT[0] - 60, FUT[1] - 120), (YOU[0] + 480, YOU[1] - 120)], 0.4 * k, 1.6, progress=k)


# 7 — alors aujourd'hui, rends-les fiers
def s7(c, T):
    k = T.pc(1, 1.4, f=ease)
    mx = lerp(YOU[0] + 420, FUT[0] - 120, k)
    light_bloom(c, FUT[0] - 60, 700, 520 * k + 1, 0.8 * k)
    future(c)
    figure(c, mx, YOU[1], 1.2, 1, lit=0.4 + 0.6 * k, arms="up" if k >= 1 else "down")


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
    dict(say=["Somewhere in the future,", "there's a version of you", "who *made it*."], draw=s1),
    dict(say=["Every choice you make today", "moves you *toward* them,"], draw=s2),
    dict(say=["or *away*."], draw=s3),
    dict(say=["Skipping the gym?", "One step *back*."], draw=s4),
    dict(say=["Reading ten pages?", "One step *closer*."], draw=s5),
    dict(say=["They're watching.", "Waiting for you to *show up*."], draw=s6),
    dict(say=["So today,", "make them *proud*."], draw=s7),
    dict(say=["Send this to someone", "who needs to *hear* it."], draw=s8),
]
