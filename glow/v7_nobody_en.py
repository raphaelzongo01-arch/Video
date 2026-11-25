"""Video 7 (EN) — "Nobody's coming"."""
import math, os
import engine
from engine import *
from extras import *

engine.LANG = "en"
SEED = 71
SPEED = 1.0
VOICE = "el_jessica"
CACHE = os.path.join(ROOT, "out", "tts_v7")
MUSIC = {}
HX, HY = 960, 760


def crossed(c, txt, x, y, k, kx):
    if k <= 0:
        return
    c.save(); c.translate(x, y); c.scale(k, k)
    boxed(c, txt, 0, 0, k * (1 - 0.5 * kx), 17, 5, 20)
    c.restore()
    w = text_w(txt, TF_BOLD, 17, 5) / 2 + 36
    line(c, [(x - w, y + 14), (x + w, y - 14)], kx, 3.5, 0.8, progress=max(0.001, kx))


# 1 — personne ne viendra te sauver
def s1(c, T):
    figure(c, HX, HY, 1.3, 1, lit=0.3)
    for i in range(6):
        ang = i * math.pi / 3 + 0.3
        k = T.pc(1, 1.4, f=ease, delay=0.1 * i)
        r = 240 + 420 * k
        figure(c, HX + r * math.cos(ang), HY + 0.45 * r * math.sin(ang), 0.9, 1 - k, dim=0.4)


# 2 — pas ton boss, pas tes potes, pas la chance
def s2(c, T):
    figure(c, HX, HY, 1.3, 1, lit=0.3)
    for j, (lab, x) in enumerate([("BOSS", 620), ("FRIENDS", 960), ("LUCK", 1300)]):
        crossed(c, lab, x, 450, T.pc(j, 0.45, f=eback), T.pc(j, 0.35, delay=0.35))


# 3 — tu attends que quelqu'un remarque
def s3(c, T):
    figure(c, HX - 200, HY, 1.3, 1, lit=0.2)
    rrect(c, HX + 260, 620, 170, 300, 10, 0.8, stroke=3, glow=0.6, fill=(8, 9, 13))   # porte fermée
    circle(c, HX + 320, 630, 6, 0.8, glow=0.5)
    dashed(c, [(HX - 150, HY - 110), (HX + 170, 620)], 0.35 * T.pc(1, 0.6), 1.6, progress=T.pc(1, 0.8))
    draw_text(c, "?", HX - 200, 560 - 6 * math.sin(T.t * 3), 60, TF_BOLD, a=T.pc(1, 0.5), glow=0.7)


# 4 — les jours passent, rien ne change
def s4(c, T):
    figure(c, HX, HY, 1.3, 1, dim=0.5 * T.pc(1, 1.0))
    d = 1 + int(120 * T.pc(0, 1.6, f=lambda v: clamp(v)))
    calendar(c, HX, 450, 130, T.pc(0, 0.4), big=str(d), small="DAY")


# 5 — la personne que tu attends, c'est toi
def s5(c, T):
    k = T.pc(2, 0.9, f=ease)
    light_bloom(c, HX, HY - 60, 520 * k + 1, k)
    figure(c, HX, HY, 1.3 + 0.2 * k, 1, lit=k, dim=0.5 * (1 - T.pc(1, 0.6)) * (1 - k))
    ring(c, HX, HY - 60, 150 + 10 * math.sin(T.t * 2), 0.7 * k)
    dashed(c, [(HX, 380), (HX, HY - 170)], 0.4 * T.pc(1, 0.6) * (1 - k), 1.6)


# 6 — dès que tu arrêtes d'attendre, tout bouge
def s6(c, T):
    pts = [(560, 820), (800, 790), (1000, 700), (1200, 640), (1420, 520), (1620, 450)]
    k = T.pc(1, 1.8, f=ease)
    line(c, pts, 0.9, 3.2, 1.1, progress=max(0.001, 0.05 + 0.95 * k), smooth=True)
    x, y = point_on(make_path(pts, True), 0.05 + 0.95 * k)
    figure(c, x, y, 1.0, 1, lit=0.9)


# 7 — personne ne viendra, alors vas-y
def s7(c, T):
    light_bloom(c, 960, 520, 560, 0.7 * T.pc(0, 1.2))
    hill = make_path([(200, 1000), (600, 900), (860, 640), (960, 560), (1060, 640), (1320, 900), (1720, 1000)], True)
    fp = skia.Path(hill); fp.lineTo(1720, 1300); fp.lineTo(200, 1300); fp.close()
    c.drawPath(fp, paint((5, 6, 10), 1))
    glowdraw(lambda p: c.drawPath(hill, p), 0.95, WHITE, 1.2, 3.2)
    figure(c, 960, 560, 1.0, 1, lit=1, arms="up" if T.t > T.c(1) else "down")


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
    dict(say=["Nobody is coming", "to *save* you."], draw=s1),
    dict(say=["Not your boss.", "Not your friends.", "Not *luck*."], draw=s2),
    dict(say=["You keep waiting", "for someone to *notice*."], draw=s3),
    dict(say=["Days pass.", "*Nothing* changes."], draw=s4),
    dict(say=["Here's the truth.", "The person you're waiting for", "is *you*."], draw=s5),
    dict(say=["The moment you stop waiting,", "*everything* starts moving."], draw=s6),
    dict(say=["Nobody's coming.", "So *go*."], draw=s7),
    dict(say=["Send this to someone", "who's still *waiting*."], draw=s8),
]
