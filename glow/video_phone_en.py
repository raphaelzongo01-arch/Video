"""Video 3 (EN) — "4 hours a day" (le téléphone)."""
import math, os
import engine
from engine import *
from extras import *

engine.LANG = "en"
SEED = 31
SPEED = 1.0
VOICE = "el_jessica"
CACHE = os.path.join(ROOT, "out", "tts_phone_en")
MUSIC = {}


# 1 — 96 fois par jour
def s1(c, T):
    k = T.pc(0, 0.6)
    figure(c, 760, 820, 1.4, k, lit=0.3)
    phone(c, 1130, 640, 220, T.pc(0, 0.6, delay=0.3), glow_screen=0.4 + 0.3 * math.sin(T.t * 6) ** 2)
    v = 96 * T.pc(1, 1.4, f=ease)
    counter(c, 1130, 450, v, 90, a=T.pc(1, 0.3), suffix="×")
    for i in range(6):  # notifications qui vibrent
        kk = T.p(T.c(1) + i * 0.2, 0.3)
        if 0 < kk:
            dy = -80 - i * 12
            circle(c, 1130 + 95 + (i % 2) * 18, 640 + dy + 160 - i * 30, 6, kk * (1 - T.pc(1, 0.4, delay=2.0)), glow=1)


# 2 — 4 heures, chaque jour
def s2(c, T):
    k = T.pc(0, 0.5)
    clock_arc(c, 960, 600, 170, 4, k, k=T.pc(0, 1.4, f=ease, delay=0.2))
    draw_text(c, "4H", 960, 628, 80, TF_BOLD, a=T.pc(0, 0.6, delay=0.4), glow=0.8)
    tag(c, "EVERY DAY", 960, 840, T.pc(1, 0.5) * 0.8, 17, 6)


# 3 — 60 jours par an
def s3(c, T):
    k = T.pc(0, 0.5)
    dot_grid(c, 960, 620, 60, k, k_lit=T.pc(0, 1.6, f=ease, delay=0.3))
    kk = T.pc(1, 0.5, f=eback)
    c.save(); c.translate(960, 870); c.scale(kk, kk)
    boxed(c, "60 DAYS / YEAR", 0, 0, kk, 20, 5, 24)
    c.restore()


# 4 — à regarder la vie des autres
def s4(c, T):
    feed(c, 1080, 620, 380, T.pc(0, 0.5), T.t)
    figure(c, 720, 860, 1.3, 1, lit=0.15 + 0.25 * T.pc(0, 0.5))
    dashed(c, [(760, 760), (930, 650)], 0.3 * T.pc(1, 0.5), 1.5, progress=T.pc(1, 0.6))


# 5 — « je n'ai pas le temps »
def s5(c, T):
    figure(c, 960, 850, 1.4, 1, lit=0.2)
    k = T.pc(1, 0.45, f=eback)
    c.save(); c.translate(1080, 640); c.scale(k, k)
    bubble(c, 0, 0, "I don't have time", k, 24)
    c.restore()
    phone(c, 820, 760, 120, 0.8 * T.pc(0, 0.5), glow_screen=0.5, rot=-12)


# 6 — tu l'as, il est dans ta poche
def s6(c, T):
    z = lerp(1.0, 1.35, T.pc(0, 2.5, f=ease))
    camera(c, z, 960, 620)
    phone(c, 960, 620, 300, 1, glow_screen=0.4 + 0.6 * T.pc(1, 0.8))
    clock(c, 960, 610, 58, T.pc(1, 0.6), ang=T.t * 2)


# 7 — reprendre 1 heure
def s7(c, T):
    k = T.pc(0, 0.5)
    clock_arc(c, 960, 600, 170, 4, k * 0.35, k=1)
    clock_arc(c, 960, 600, 170, 1, k, k=T.pc(1, 1.0, f=ease))
    draw_text(c, "1H", 960, 628, 80, TF_BOLD, a=T.pc(1, 0.6), glow=0.9)
    tag(c, "TAKE IT BACK", 960, 840, T.pc(1, 0.5, delay=0.3) * 0.8, 17, 6)


# 8 — 365 heures : un skill, un corps, un business
def s8(c, T):
    k = T.pc(0, 0.6)
    counter(c, 960, 470, 365 * T.pc(0, 1.2, f=ease), 110, a=k)
    tag(c, "HOURS / YEAR", 960, 530, k * 0.7, 16, 6)
    xs = [640, 960, 1280]
    for i, x in enumerate(xs):
        kk = T.pc(1 + i, 0.5, f=eback)
        if kk <= 0:
            continue
        c.save(); c.translate(x, 720); c.scale(kk, kk)
        if i == 0:
            from video_un_pourcent import book
            book(c, 0, 0, kk)
        elif i == 1:
            dumbbell(c, 0, 0, 1.0, kk)
        else:
            briefcase(c, 0, 0, 1.0, kk)
        c.restore()
        tag(c, ["A SKILL", "A BODY", "A BUSINESS"][i], x, 820, kk * 0.85, 16, 6)


# 9 — une heure, c'est tout
def s9(c, T):
    k = T.pc(0, 0.6)
    light_bloom(c, 960, 600, 420, 0.6 * k)
    draw_text(c, "1H", 960, 650, 180, TF_BOLD, a=k, glow=1.0)
    ring(c, 960, 590, 190 + 6 * math.sin(T.t * 2), 0.5 * T.pc(1, 0.6))


# 10 — pose le téléphone et commence
def s10(c, T):
    drop = T.pc(1, 0.8, f=ease)
    figure(c, 760, 850, 1.3, 1, lit=0.3 + 0.7 * T.pc(2, 0.8))
    phone(c, lerp(900, 1000, drop), lerp(700, 860, drop), 120, 1 - 0.6 * drop, glow_screen=0.6 * (1 - drop),
          rot=lerp(-12, -90, drop))
    k = T.pc(2, 1.6, f=ease)
    line(c, [(760, 850), (1100, 820), (1400, 720), (1650, 600)], 0.9, 3, 1.0, progress=max(0.001, k), smooth=True)


# 11 — CTA
def s11(c, T):
    k = T.pc(0, 0.6)
    figure(c, 860, 800, 1.2, k, dim=0.5)
    figure(c, 1060, 800, 1.2, k, lit=T.pc(0, 1.0, delay=0.5))
    phone(c, 930, 700, 70, k * 0.6, glow_screen=0.6, rot=-15)
    kk = T.pc(1, 0.5, f=eback)
    c.save(); c.translate(960, 920); c.scale(kk, kk)
    rrect(c, 0, 0, 380, 64, 32, kk, stroke=2.5, glow=0.9, fill=(10, 12, 18))
    draw_text(c, "SHARE  →", 0, 8, 22, a=kk, spacing=5)
    c.restore()


SCENES = [
    dict(say=["You check your phone", ("*96* times a day.", "ninety-six times a day.")], draw=s1),
    dict(say=["Four hours.", "Every single *day*."], draw=s2),
    dict(say=[("That's 60 days a year.", "That's sixty days a year."), "Two full *months*."], draw=s3),
    dict(say=["Scrolling.", "Watching other people", "live *their* lives."], draw=s4),
    dict(say=["And then you say", "“I don't have *time*.”"], draw=s5),
    dict(say=["You do.", "It's just *in your pocket*."], draw=s6),
    dict(say=["Now imagine taking back", "just *one* hour a day."], draw=s7),
    dict(say=[("That's 365 hours a year.", "That's three hundred sixty-five hours a year."),
              "Enough to learn a *skill*,", "build a *body*,", "or start a *business*."], draw=s8),
    dict(say=["One hour.", "That's all it *takes*."], draw=s9),
    dict(say=["So tonight,", "put the phone *down*.", "And start."], draw=s10),
    dict(say=["Send this to someone", "who needs to *hear* it."], draw=s11),
]
