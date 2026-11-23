"""Video 5 (EN) — "Motivation vs discipline"."""
import math, os
import engine
from engine import *
from extras import *

engine.LANG = "en"
SEED = 53
SPEED = 1.0
VOICE = "el_jessica"
CACHE = os.path.join(ROOT, "out", "tts_discipline_en")
MUSIC = {}

X0, X1, YM = 300, 1620, 600          # vague de la motivation
YD = 820                              # ligne de la discipline


def mot_wave(prog=1.0, a=1.0, c=None, amp=150, periods=2.2):
    pts = wave_pts(X0, X1, YM, amp, periods)
    line(c, pts, a, 3.2, 1.0, progress=max(prog, 0.001), smooth=True)
    return make_path(pts, True)


def disc_line(c, prog=1.0, a=1.0, rise=180):
    pts = [(X0, YD), (X1, YD - rise)]
    line(c, pts, a, 3.2, 1.0, progress=max(prog, 0.001))
    return make_path(pts)


# 1 — la motivation est une émotion
def s1(c, T):
    k = T.pc(0, 2.4, f=ease)
    p = mot_wave(k, 1, c)
    x, y = point_on(p, k)
    figure(c, x, y, 0.8, T.pc(0, 0.5), lit=0.5)
    tag(c, "MOTIVATION", X0 + 160, YM - 190, T.pc(0, 0.6) * 0.8, 16, 6)


# 2 — elle arrive, puis disparaît
def s2(c, T):
    p = mot_wave(1, 1, c)
    q = 0.12 + 0.24 * T.pc(0, 1.2, f=ease) + 0.12 * T.pc(1, 1.0, f=ease)
    x, y = point_on(p, q)
    figure(c, x, y, 0.8, 1, lit=0.8 * (1 - T.pc(1, 0.8)), dim=0.4 * T.pc(1, 0.8))


# 3 — lundi en feu, mercredi fatigué, vendredi fini
def s3(c, T):
    p = mot_wave(1, 1, c)
    qs = [0.11, 0.33, 0.56]
    k = 0 if T.t < T.c(1) else (1 if T.t < T.c(2) else 2)
    for j, (q, d) in enumerate(zip(qs, ["MON", "WED", "FRI"])):
        x, y = point_on(p, q)
        kk = T.pc(j, 0.4)
        tag(c, d, x, y + 60 + (j > 0) * 0, kk * (1 if j == k else 0.45), 15, 5)
        circle(c, x, y, 6, kk * 0.7, glow=0.6)
    x, y = point_on(p, lerp(qs[max(0, k - 1)], qs[k], T.p([0, T.c(1), T.c(2)][k], 0.5, ease)))
    figure(c, x, y, 0.8, 1, lit=[1.0, 0.3, 0][k], dim=[0, 0.3, 0.6][k])


# 4 — la discipline, c'est différent
def s4(c, T):
    mot_wave(1, 0.35, c)
    k = T.pc(0, 1.6, f=ease)
    disc_line(c, k)
    tag(c, "DISCIPLINE", X0 + 160, YD + 50, T.pc(0, 0.6) * 0.8, 16, 6)
    figure(c, lerp(X0, X1, 0.05), YD - 9, 0.8, T.pc(0, 0.5), lit=0.6)


# 5 — elle se fiche de ce que tu ressens
def s5(c, T):
    mot_wave(1, 0.35, c)
    p = disc_line(c, 1)
    q = 0.05 + 0.1 * T.pc(0, T.dur, f=lambda v: v)
    x, y = point_on(p, q)
    figure(c, x, y, 0.8, 1, lit=0.7)


# 6 — fatigué ? tu y vas. ennuyé ? tu y vas.
def s6(c, T):
    mot_wave(1, 0.35, c)
    p = disc_line(c, 1)
    q = 0.15 + 0.25 * T.pc(0, T.dur, f=lambda v: v)
    x, y = point_on(p, q)
    figure(c, x, y, 0.8, 1, lit=0.7)
    for j, (lab, ci) in enumerate([("TIRED", 0), ("BORED", 2)]):
        k = T.pc(ci, 0.4, f=eback)
        cx = 700 + j * 420
        if k > 0:
            c.save(); c.translate(cx, 400); c.scale(k, k)
            boxed(c, lab, 0, 0, k, 16, 5, 18)
            c.restore()
        ok = T.pc(ci + 1, 0.4, f=eback)
        if ok > 0:
            check(c, cx, 470, 16 * ok, ok)


# 7 — au début, la motivation a l'air plus forte
def s7(c, T):
    z = lerp(1.0, 1.25, T.pc(0, 2.5, f=ease))
    camera(c, z, 650, 650)
    mot_wave(1, 1, c)
    disc_line(c, 1, 0.8)
    k = T.pc(1, 0.6)
    line(c, [(560, YM - 150), (560, YD - 30)], 0.5 * k, 2, 0.4)
    tag(c, "MOTIVATION > DISCIPLINE", 560, YM - 190, k * 0.8, 14, 4)


# 8 — après quelques mois, la discipline est loin devant
def s8(c, T):
    m = T.pc(0, 3.0, f=ease)
    camera(c, lerp(1.0, 0.82, m), 960, lerp(650, 560, m))
    rise = lerp(180, 620, m)
    mot_wave(1, 0.8, c)
    p = disc_line(c, 1, 1, rise)
    x, y = point_on(p, 1.0)
    figure(c, x, y, 0.9, 1, lit=1.0)
    light_bloom(c, x, y - 40, 260, 0.7 * m)
    k = T.pc(1, 0.6)
    line(c, [(X1 + 40, YM), (X1 + 40, y + 10)], 0.6 * k, 2.5, 0.6)
    tag(c, "MILES AHEAD", X1 - 190, (YM + y) / 2, k, 16, 5)


# 9 — les résultats ne viennent pas de tes meilleurs jours
def s9(c, T):
    p = mot_wave(1, 0.5, c)
    for q in (0.11, 0.56, 1.0):
        x, y = point_on(p, q)
        star4(c, x, y - 30, 12, T.pc(0, 0.5) * (1 - T.pc(1, 0.5)))
    for q in (0.11, 0.56):
        x, y = point_on(p, q)
        line(c, [(x - 22, y - 52), (x + 22, y - 8)], T.pc(1, 0.4), 3, 0.6)


# 10 — mais de tes jours moyens
def s10(c, T):
    k = T.pc(0, 1.6, f=ease)
    n = 14
    for i in range(n):
        q = clamp(k * n - i)
        x = 360 + i * 92
        y = 800 - i * 22
        circle(c, x, y, 8, q, glow=0.9)
        if i:
            line(c, [(x - 92, y + 22), (x, y)], q * 0.6, 2, 0.4)
    kk = T.pc(1, 0.5, f=eback)
    c.save(); c.translate(960, 420); c.scale(kk, kk)
    boxed(c, "AVERAGE DAYS", 0, 0, kk, 20, 6, 22)
    c.restore()
    figure(c, 360 + (n - 1) * 92 * k, 800 - (n - 1) * 22 * k, 0.8, 1, lit=0.8)


# 11 — n'attends pas d'être prêt, viens quand même
def s11(c, T):
    k = T.pc(0, 3, f=ease)
    light_bloom(c, 960, 520, 560, 0.7 * T.pc(0, 1.5))
    hill = make_path([(200, 1000), (600, 900), (860, 640), (960, 560), (1060, 640), (1320, 900), (1720, 1000)], True)
    fp = skia.Path(hill); fp.lineTo(1720, 1300); fp.lineTo(200, 1300); fp.close()
    c.drawPath(fp, paint((5, 6, 10), 1))
    glowdraw(lambda p: c.drawPath(hill, p), 0.95, WHITE, 1.2, 3.2)
    figure(c, 960, 560, 1.0, 1, lit=1, arms="up" if T.t > T.c(1) else "down")


# 12 — CTA
def s12(c, T):
    k = T.pc(0, 0.6)
    figure(c, 860, 800, 1.2, k, dim=0.5)
    figure(c, 1060, 800, 1.2, k, lit=T.pc(0, 1.0, delay=0.5))
    line(c, [(900, 660), (1020, 660)], 0.5 * T.pc(0, 0.6, delay=0.5), 2.5, 0.6)
    kk = T.pc(1, 0.5, f=eback)
    c.save(); c.translate(960, 920); c.scale(kk, kk)
    rrect(c, 0, 0, 380, 64, 32, kk, stroke=2.5, glow=0.9, fill=(10, 12, 18))
    draw_text(c, "SHARE  →", 0, 8, 22, a=kk, spacing=5)
    c.restore()


SCENES = [
    dict(say=["Motivation", "is a *feeling*."], draw=s1),
    dict(say=["It shows up.", "Then it *disappears*."], draw=s2),
    dict(say=["Monday, you're on fire.", "Wednesday, you're *tired*.", "Friday, you're *done*."], draw=s3),
    dict(say=["Discipline", "is *different*."], draw=s4),
    dict(say=["It doesn't care", "how you *feel*."], draw=s5),
    dict(say=["Tired?", "You still go.", "Bored?", "You still *go*."], draw=s6),
    dict(say=["At first,", "motivation looks *stronger*."], draw=s7),
    dict(say=["But after a few months,", "discipline is *miles* ahead."], draw=s8),
    dict(say=["Because results don't come", "from your *best* days."], draw=s9),
    dict(say=["They come", "from your *average* days."], draw=s10),
    dict(say=["Stop waiting to feel *ready*.", "Show up anyway."], draw=s11),
    dict(say=["Send this to someone", "who needs a *push*."], draw=s12),
]
