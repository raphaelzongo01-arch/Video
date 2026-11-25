"""Video 8 (EN) — "Chapter 1 vs chapter 20"."""
import math, os
import engine
from engine import *
from extras import *

engine.LANG = "en"
SEED = 81
SPEED = 1.0
VOICE = "el_jessica"
CACHE = os.path.join(ROOT, "out", "tts_v8")
MUSIC = {}

PATH = [(300, 900), (520, 880), (700, 820), (860, 760), (1020, 680), (1180, 600), (1340, 520), (1500, 450), (1640, 400)]


def book(c, x, y, a, label):
    rrect(c, x, y, 150, 190, 8, a, stroke=3, glow=0.8, fill=(8, 9, 13))
    line(c, [(x - 60, y - 95), (x - 60, y + 95)], a * 0.6, 2, 0)
    tag(c, "CHAPTER", x + 8, y - 20, a * 0.7, 13, 4)
    draw_text(c, label, x + 8, y + 40, 52, TF_BOLD, a=a, glow=0.7)


# 1 — ne compare pas ton chapitre 1 à leur chapitre 20
def s1(c, T):
    book(c, 700, 600, T.pc(0, 0.5, f=eback), "1")
    book(c, 1220, 600, T.pc(1, 0.5, f=eback), "20")
    draw_text(c, "≠", 960, 620, 70, TF_SEMI, a=T.pc(1, 0.4, delay=0.3) * 0.7)


# 2 — tu vois leurs résultats, pas les années
def s2(c, T):
    k = T.pc(1, 2.0, f=ease)
    line(c, PATH, 0.25 + 0.7 * k, 3, 0.4 + 0.7 * k, smooth=True)
    x, y = PATH[-1]
    light_bloom(c, x, y - 40, 260, 0.6)
    figure(c, x, y, 1.0, 1, lit=1, arms="up")
    p = make_path(PATH, True)
    for i in range(1, 8):
        q = i / 8
        if k > q:
            px, py = point_on(p, q)
            circle(c, px, py, 6, clamp((k - q) * 8), glow=0.8)
    tag(c, "RESULTS", x - 170, y - 40, T.pc(0, 0.5) * 0.8, 15, 5)
    tag(c, "YEARS", 640, 950, T.pc(1, 0.5) * 0.8, 15, 5)


# 3 — les échecs, le doute, les nuits que personne n'a vues
def s3(c, T):
    line(c, PATH, 0.9, 3, 1.0, smooth=True)
    p = make_path(PATH, True)
    for j, (lab, q) in enumerate([("FAILURES", 0.2), ("DOUBT", 0.45), ("NIGHTS", 0.7)]):
        k = T.pc(j, 0.45, f=eback)
        x, y = point_on(p, q)
        check(c, x, y, 15 * k, k, ok=False)
        tag(c, lab, x, y + 50, k * 0.85, 14, 5)
    figure(c, PATH[-1][0], PATH[-1][1], 1.0, 1, lit=0.8)


# 4 — ils ont commencé exactement où tu es
def s4(c, T):
    line(c, PATH, 0.5, 3, 0.5, smooth=True)
    figure(c, PATH[0][0] + 20, PATH[0][1], 1.0, 1, lit=0.6)
    k = T.pc(1, 1.0, f=ease)
    gx = lerp(PATH[-1][0], PATH[0][0] + 110, k); gy = lerp(PATH[-1][1], PATH[0][1], k)
    figure(c, gx, gy, 1.0, 0.45 + 0.2 * k, dim=0.3)
    ring(c, PATH[0][0] + 70, PATH[0][1] - 50, 130, 0.5 * T.pc(1, 0.5, delay=1.0))


# 5 — ta seule compétition : toi hier
def s5(c, T):
    figure(c, 760, 800, 1.3, 1, dim=0.55)
    tag(c, "YESTERDAY", 760, 880, T.pc(0, 0.5) * 0.7, 15, 5)
    k = T.pc(1, 0.6)
    figure(c, 1160, 800, 1.3, k, lit=0.9)
    tag(c, "YOU", 1160, 880, k * 0.9, 15, 5)
    line(c, [(850, 700), (1060, 700)], k * 0.7, 3, 0.7, progress=max(0.001, k))
    line(c, [(1040, 685), (1062, 700), (1040, 715)], k * 0.7, 3, 0.7)


# 6 — reste dans ta voie, continue d'écrire
def s6(c, T):
    for lx in (560, 960, 1360):
        line(c, [(lx, 960), (lx, 380)], 0.15, 1.5, 0)
    k = T.pc(0, 2.4, f=ease)
    y = lerp(920, 470, k)
    line(c, [(960, 960), (960, y)], 0.9, 3, 1.0)
    figure(c, 960, y, 1.0, 1, lit=0.9)
    for lx, kk in ((560, 0.4), (1360, 0.7)):
        figure(c, lx, lerp(920, 470, kk), 0.8, 0.6, dim=0.5)


# 7 — CTA
def s7(c, T):
    k = T.pc(0, 0.6)
    figure(c, 860, 800, 1.2, k, dim=0.5)
    figure(c, 1060, 800, 1.2, k, lit=T.pc(0, 1.0, delay=0.5))
    kk = T.pc(1, 0.5, f=eback)
    c.save(); c.translate(960, 920); c.scale(kk, kk)
    rrect(c, 0, 0, 380, 64, 32, kk, stroke=2.5, glow=0.9, fill=(10, 12, 18))
    draw_text(c, "SHARE  →", 0, 8, 22, a=kk, spacing=5)
    c.restore()


SCENES = [
    dict(say=["Stop comparing your *chapter one*", "to someone's *chapter twenty*."], draw=s1),
    dict(say=["You see their *results*.", "You don't see the *years*."], draw=s2),
    dict(say=["The failures.", "The doubt.", "The nights *nobody* saw."], draw=s3),
    dict(say=["They started", "exactly where you are *now*."], draw=s4),
    dict(say=["Your only competition", "is who you were *yesterday*."], draw=s5),
    dict(say=["Stay in your *lane*.", "Keep *writing*."], draw=s6),
    dict(say=["Send this to someone", "who needs to *hear* it."], draw=s7),
]
