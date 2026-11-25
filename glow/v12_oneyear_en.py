"""Video 12 (EN) — "One year from now"."""
import math, os
import engine
from engine import *
from extras import *

engine.LANG = "en"
SEED = 121
SPEED = 1.0
VOICE = "el_jessica"
CACHE = os.path.join(ROOT, "out", "tts_v12")
MUSIC = {}


def cta(c, T):
    k = T.pc(0, 0.6)
    figure(c, 860, 800, 1.2, k, dim=0.5)
    figure(c, 1060, 800, 1.2, k, lit=T.pc(0, 1.0, delay=0.5))
    kk = T.pc(1, 0.5, f=eback)
    c.save(); c.translate(960, 920); c.scale(kk, kk)
    rrect(c, 0, 0, 380, 64, 32, kk, stroke=2.5, glow=0.9, fill=(10, 12, 18))
    draw_text(c, "SHARE  →", 0, 8, 22, a=kk, spacing=5)
    c.restore()


# 1 — dans un an, tu vas souhaiter avoir commencé aujourd'hui
def s1(c, T):
    calendar(c, 960, 520, 150, T.pc(0, 0.5), big="+365", small="DAYS")
    figure(c, 960, 860, 1.1, T.pc(1, 0.6), dim=0.3)


# 2 — l'année va passer quoi qu'il arrive
def s2(c, T):
    k = T.pc(0, T.dur - 0.3, f=ease)
    dot_grid(c, 960, 600, 365, 1, k_lit=k)
    draw_text(c, f"{int(365 * k)}", 960, 880, 60, TF_BOLD, a=0.9, glow=0.8)


# 3 — la question : où tu veux être quand elle se termine
def s3(c, T):
    figure(c, 620, 820, 1.2, 1, dim=0.5)
    tag(c, "SAME PLACE", 620, 900, T.pc(1, 0.5) * 0.8, 15, 5)
    figure(c, 1300, 680, 1.2, T.pc(1, 0.6, delay=0.4), lit=0.9)
    tag(c, "NEW LIFE", 1300, 760, T.pc(1, 0.5, delay=0.4) * 0.8, 15, 5)
    draw_text(c, "?", 960, 600, 90, TF_BOLD, a=T.pc(0, 0.5), glow=0.8)


# 4 — 365 petites décisions
def s4(c, T):
    for i in range(12):
        k = T.pc(0, 0.25, delay=i * 0.12)
        x = 440 + i * 95
        y = 800 - i * 30
        check(c, x, y, 14, k)
        if i:
            line(c, [(x - 95, y + 30), (x, y)], 0.4 * k, 2, 0)
    tag(c, "365 CHOICES", 960, 420, T.pc(1, 0.5) * 0.85, 18, 6)


# 5 — commence aujourd'hui, même mal
def s5(c, T):
    k = T.pc(1, 0.6, f=eback)
    light_bloom(c, 960, 640, 400, 0.6 * T.pc(1, 0.8))
    figure(c, 960, 820, 1.3, 1, lit=0.4 + 0.6 * T.pc(1, 0.8))
    c.save(); c.translate(960, 470); c.scale(k, k)
    boxed(c, "DAY 1", 0, 0, k, 24, 6, 26)
    c.restore()


def s6(c, T):
    cta(c, T)


SCENES = [
    dict(say=["One year from now,", "you'll wish you started *today*."], draw=s1),
    dict(say=["That year is going to pass", "*anyway*."], draw=s2),
    dict(say=["The only question is", "where you'll be when it *ends*."], draw=s3),
    dict(say=["It's three hundred sixty-five small choices.", "*One* at a time."], draw=s4),
    dict(say=["So start today.", "Even if it's *messy*."], draw=s5),
    dict(say=["Send this to someone", "who keeps saying *tomorrow*."], draw=s6),
]
