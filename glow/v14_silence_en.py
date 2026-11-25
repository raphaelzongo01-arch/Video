"""Video 14 (EN) — "Work in silence"."""
import math, os
import engine
from engine import *
from extras import *
from v12_oneyear_en import cta

engine.LANG = "en"
SEED = 141
SPEED = 1.0
VOICE = "el_jessica"
CACHE = os.path.join(ROOT, "out", "tts_v14")
MUSIC = {}
CROWD = [(440, 860), (580, 880), (720, 860), (1240, 860), (1380, 880), (1520, 860)]


def crowd(c, T, talk=True, a=1.0, face_k=0.0):
    msgs = ["I'm gonna start", "next week", "big plans", "trust me", "soon", "watch me"]
    for i, (x, y) in enumerate(CROWD):
        figure(c, x, y, 0.9, a, dim=0.5)
        if talk:
            k = T.p(0.2 + i * 0.25, 0.4, eback)
            if k > 0:
                c.save(); c.translate(x + 30, y - 150 - (i % 2) * 40); c.scale(k, k)
                bubble(c, 0, 0, msgs[i], k * a, 17)
                c.restore()


# 1 — tout le monde parle de ses plans
def s1(c, T):
    crowd(c, T)
    figure(c, 960, 880, 1.1, 1, lit=0.3)


# 2 — lui ne dit rien, il bosse
def s2(c, T):
    crowd(c, T, talk=True, a=0.6)
    figure(c, 960, 880, 1.1, 1, lit=0.6)
    k = T.pc(1, T.dur - 0.5, f=ease)
    for i in range(int(8 * k) + 1):
        circle(c, 960 + (i - 4) * 34, 960, 6, 0.9, glow=0.8)
    tag(c, "WORK", 960, 1010, T.pc(1, 0.5) * 0.8, 15, 6)


# 3 — pas de posts, pas d'annonces, juste des heures
def s3(c, T):
    crowd(c, T, talk=False, a=0.45)
    figure(c, 960, 880, 1.1, 1, lit=0.7)
    for j, (lab, ok) in enumerate([("POSTS", False), ("ANNOUNCEMENTS", False), ("HOURS", True)]):
        k = T.pc(j, 0.4, f=eback)
        x = 640 + j * 320
        if k > 0:
            c.save(); c.translate(x, 470); c.scale(k, k)
            boxed(c, lab, 0, 0, k, 16, 5, 18)
            c.restore()
            check(c, x, 540, 15 * k, k, ok=ok)


# 4 — et un jour, les résultats font tout le bruit
def s4(c, T):
    k = T.pc(1, 0.8, f=ease)
    crowd(c, T, talk=False, a=1 - 0.4 * k)
    light_bloom(c, 960, 760, 560 * k + 1, k)
    for r in range(3):
        ring(c, 960, 800, (180 + r * 120) * k + 1, 0.5 * k * (1 - r * 0.25))
    figure(c, 960, 880, 1.2 + 0.2 * k, 1, lit=0.7 + 0.3 * k, arms="up" if k >= 1 else "down")


# 5 — travaille en silence
def s5(c, T):
    crowd(c, T, talk=False, a=0.5)
    light_bloom(c, 960, 760, 400, 0.6)
    figure(c, 960, 880, 1.3, 1, lit=1)


def s6(c, T):
    cta(c, T)


SCENES = [
    dict(say=["Everybody talks about their plans."], draw=s1),
    dict(say=["He doesn't say a word.", "He just *works*."], draw=s2),
    dict(say=["No posts.", "No announcements.", "Just *hours*."], draw=s3),
    dict(say=["And one day,", "the results make all the *noise*."], draw=s4),
    dict(say=["Work in *silence*."], draw=s5),
    dict(say=["Send this to someone", "who's building *quietly*."], draw=s6),
]
