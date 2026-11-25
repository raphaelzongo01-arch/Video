"""Video 17 (EN) — "$5 a day" (argent) : animations renforcées + écran final Follow."""
import math, os, random
import engine
from engine import *
from extras import *

engine.LANG = "en"
import voice as _V
_V.EL_TAG = "[confident]"      # indication courte : économise les crédits
SEED = 171
SPEED = 1.0
VOICE = "el_jessica"
CACHE = os.path.join(ROOT, "out", "tts_v17")
MUSIC = {}
GOLD = (255, 214, 110)


# ------------------------------------------------------------------ effets
def punch(c, T, strength=0.06):
    """Petit zoom « coup de poing » sur chaque mot en italique."""
    z = 1.0
    for ch in T.s["chunks"]:
        for (w, it), tw in zip(ch["words"], ch["times"]):
            if it:
                d = T.t - (tw - T.s["start"])
                if 0 <= d < 0.45:
                    z += strength * math.sin(math.pi * d / 0.45) * (1 - d / 0.45)
    c.translate(W / 2, H * 0.56); c.scale(z, z); c.translate(-W / 2, -H * 0.56)


def sparks(c, t, x, y, n=24, spread=320, seed=1, a=1.0, rgb=WHITE):
    r = random.Random(seed)
    for i in range(n):
        ang = r.uniform(0, 2 * math.pi); sp = r.uniform(0.3, 1.0)
        d = spread * sp * eout(clamp(t / 0.9))
        al = a * (1 - clamp(t / 1.1))
        if al > 0:
            c.drawCircle(x + d * math.cos(ang), y + d * math.sin(ang) * 0.7, r.uniform(2, 4.5), paint(rgb, al, blur=1))


def dust(c, t, a=0.5):
    r = random.Random(9)
    for i in range(40):
        x = (r.uniform(0, W) + t * r.uniform(8, 25)) % W
        y = (r.uniform(0, H) - t * r.uniform(10, 40)) % H
        c.drawCircle(x, y, r.uniform(1, 2.4), paint(WHITE, a * r.uniform(0.2, 0.6)))


def bill(c, x, y, rot, a=1.0, s=1.0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    rrect(c, 0, 0, 150, 72, 8, a, stroke=2.5, glow=0.8, fill=(10, 14, 12), rgb=(170, 255, 190))
    circle(c, 0, 0, 22, a * 0.8, stroke=2, glow=0.4, rgb=(170, 255, 190))
    draw_text(c, "$", 0, 10, 28, TF_BOLD, a=a, rgb=(170, 255, 190), glow=0.5)
    c.restore()


def bill_rain(c, t, a=1.0, n=26, seed=3):
    r = random.Random(seed)
    for i in range(n):
        x = r.uniform(250, 1670); sp = r.uniform(260, 480); ph = r.uniform(0, 1)
        y = -100 + ((t * sp + ph * 1300) % 1300)
        bill(c, x + 40 * math.sin(t * 2 + i), y, r.uniform(-40, 40) + 60 * math.sin(t * 1.5 + i), a * 0.85, 0.7)


def coin(c, x, y, a=1.0, s=1.0, label="$"):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.drawCircle(0, 0, 60, paint(GOLD, 0.25 * a, blur=22))
    circle(c, 0, 0, 52, a, stroke=4, glow=1.0, rgb=GOLD)
    circle(c, 0, 0, 40, a * 0.6, stroke=2, glow=0, rgb=GOLD)
    draw_text(c, label, 0, 15, 40 if len(label) < 3 else 30, TF_BOLD, a=a, rgb=GOLD, glow=0.6)
    c.restore()


def money(v):
    return "$" + f"{int(v):,}"


# ------------------------------------------------------------------ scènes
# 1 — tu crois qu'il te faut plus d'argent
def s1(c, T):
    dust(c, T.t)
    punch(c, T)
    figure(c, 960, 860, 1.3, 1, lit=0.3)
    for i in range(7):
        k = T.p(0.15 * i, 1.6)
        x = 960 + (i - 3) * 110 + 30 * math.sin(T.t * 2 + i)
        y = 640 - 260 * k
        draw_text(c, "$", x, y, 70, TF_BOLD, a=(1 - k) * 0.9, rgb=(170, 255, 190), glow=0.8)
    rrect(c, 960, 960, 170, 90, 12, 0.8, stroke=3, glow=0.7, fill=(8, 9, 13))      # portefeuille vide
    draw_text(c, "EMPTY", 960, 968, 18, TF_SEMI, a=0.7, spacing=4)


# 2 — non, il te faut un système
def s2(c, T):
    dust(c, T.t)
    punch(c, T)
    nodes = [(560, 620, "INCOME"), (960, 620, "SAVE"), (1360, 620, "INVEST")]
    k = T.pc(1, 0.5, f=eback)
    for i, (x, y, lab) in enumerate(nodes):
        kk = T.pc(1, 0.4, delay=0.15 * i, f=eback)
        if kk > 0:
            c.save(); c.translate(x, y); c.scale(kk, kk)
            boxed(c, lab, 0, 0, kk, 18, 5, 22)
            c.restore()
        if i:
            px = nodes[i - 1][0] + 100; qx = x - 100
            line(c, [(px, y), (qx, y)], 0.5 * kk, 2, 0.4)
            for j in range(3):   # particules qui circulent
                f = (T.t * 0.8 + j / 3) % 1
                c.drawCircle(lerp(px, qx, f), y, 5, paint(GOLD, kk))
    figure(c, 960, 900, 1.1, T.pc(0, 0.5), lit=0.5)


# 3 — 5 $ par jour
def s3(c, T):
    dust(c, T.t)
    punch(c, T, 0.1)
    k = T.pc(0, 0.6, f=lambda v: 1 - abs(math.cos(clamp(v) * math.pi * 1.5)) * (1 - clamp(v)))
    y = lerp(250, 620, T.pc(0, 0.5, f=lambda v: clamp(v) ** 2))
    coin(c, 960, y, 1, 1.6 + 0.2 * math.sin(T.t * 3) * T.pc(0, 0.6), "$5")
    if T.pc(0, 0.5) >= 1:
        sparks(c, T.t - T.c(0) - 0.5, 960, 620, 30, 380, seed=4, rgb=GOLD)
    tag(c, "PER DAY", 960, 760, T.pc(0, 0.5, delay=0.4) * 0.9, 20, 8)


# 4 — investi, chaque jour, pendant 40 ans
def s4(c, T):
    dust(c, T.t)
    punch(c, T)
    k = T.pc(1, T.dur - T.c(1) - 0.2, f=lambda v: clamp(v))
    years = int(1 + 39 * k)
    n = 20
    for i in range(n):
        q = clamp(k * n - i)
        if q <= 0:
            continue
        h = 20 + 260 * (1.1 ** (i * 2) - 1) / (1.1 ** 40 - 1) * 4
        h = min(h, 360) * q
        x = 520 + i * 46
        rrect(c, x, 900 - h / 2, 32, h, 6, 0.9, stroke=2, glow=0.8, fill=(30, 26, 12), rgb=GOLD)
    calendar(c, 960, 420, 120, T.pc(0, 0.4), big=str(years), small="YEARS")


# 5 — presque un million de dollars
def s5(c, T):
    m = T.pc(0, 1.6, f=ease)
    bill_rain(c, T.t, a=T.pc(0, 0.6))
    punch(c, T, 0.08)
    light_bloom(c, 960, 560, 560 * m + 1, 0.8 * m)
    v = 1825 * ((1.1 ** (40 * m) - 1) / 0.1) if m > 0 else 0
    draw_text(c, money(v), 960, 640, 150, TF_BOLD, a=1, rgb=GOLD, glow=1.0)
    tag(c, "$5/DAY · 40 YEARS · ~10%/YEAR", 960, 720, 0.7 * T.pc(0, 0.6), 15, 4)
    if m >= 1:
        sparks(c, T.t - 1.6, 960, 600, 40, 520, seed=7, rgb=GOLD)
    figure(c, 960, 960, 1.0, 1, lit=1, arms="up" if m > 0.9 else "down")


# 6 — le café n'est pas le problème, attendre l'est
def s6(c, T):
    dust(c, T.t)
    punch(c, T, 0.08)
    k = T.pc(0, 0.5, f=eback)
    c.save(); c.translate(700, 600); c.scale(k, k)
    rrect(c, 0, 20, 110, 130, 14, k, stroke=3.5, glow=0.8, fill=(8, 9, 13))
    p = skia.Path(); p.addArc(skia.Rect.MakeXYWH(45, -10, 60, 60), -90, 180)
    glowdraw(lambda q: c.drawPath(p, q), k, WHITE, 0.6, 3.5)
    for j in range(3):
        f = (T.t * 0.7 + j / 3) % 1
        line(c, [(-25 + j * 25, -60 - f * 40), (-20 + j * 25, -80 - f * 40)], k * (1 - f) * 0.7, 3, 0.4)
    c.restore()
    check(c, 700, 790, 18 * T.pc(0, 0.4, delay=0.3, f=eback), T.pc(0, 0.3, delay=0.3))
    kk = T.pc(1, 0.5, f=eback)
    c.save(); c.translate(1240, 620); c.scale(kk, kk)
    hourglass(c, 0, 0, 1.4, kk, k=(T.t % 2) / 2)
    c.restore()
    check(c, 1240, 790, 18 * T.pc(1, 0.4, delay=0.3, f=eback), T.pc(1, 0.3, delay=0.3), ok=False)
    if T.pc(1, 0.1) > 0:
        sparks(c, T.t - T.c(1), 1240, 620, 22, 260, seed=2)


# 7 — abonne-toi, je te motive tous les jours
def s7(c, T):
    dust(c, T.t, 0.7)
    light_bloom(c, 960, 600, 520, 0.6 * T.pc(0, 0.8))
    figure(c, 960, 520, 1.2, T.pc(0, 0.5), lit=1)
    ring(c, 960, 460, 120 + 6 * math.sin(T.t * 3), 0.6 * T.pc(0, 0.6))
    # bouton Follow + main qui tape
    k = T.pc(0, 0.5, f=eback, delay=0.2)
    tap = T.p(T.c(0) + 1.0, 0.25)
    pressed = tap > 0.5
    s = k * (1 - 0.08 * math.sin(math.pi * clamp(tap)))
    c.save(); c.translate(960, 760); c.scale(s, s)
    if pressed:
        rrect(c, 0, 0, 420, 96, 48, 1, stroke=3, glow=0.6, fill=(14, 16, 22))
        draw_text(c, "FOLLOWING", -20, 12, 32, TF_BOLD, a=1, spacing=3, glow=0.4)
        check(c, 150, 0, 16, 1)
    else:
        rrect(c, 0, 0, 420, 96, 48, 1, stroke=0, glow=1.2, fill=(254, 44, 85), rgb=(254, 44, 85))
        draw_text(c, "FOLLOW", 0, 12, 36, TF_BOLD, a=1, spacing=4, glow=0.3)
    c.restore()
    if pressed:
        sparks(c, T.t - T.c(0) - 1.13, 960, 760, 30, 340, seed=11, rgb=(254, 44, 85))
    hx = lerp(1260, 1010, T.p(T.c(0) + 0.5, 0.5, ease)); hy = lerp(980, 790, T.p(T.c(0) + 0.5, 0.5, ease)) + 14 * clamp(tap)
    c.save(); c.translate(hx, hy); c.rotate(-20)
    rrect(c, 0, 0, 44, 70, 20, k, stroke=3, glow=0.6, fill=(8, 9, 13))
    rrect(c, 0, -60, 22, 60, 11, k, stroke=3, glow=0.6, fill=(8, 9, 13))
    c.restore()
    # cloche + « DAILY »
    kb = T.pc(1, 0.5, f=eback)
    c.save(); c.translate(1300, 460); c.rotate(14 * math.sin(T.t * 14) * (1 - T.pc(1, 1.2))); c.scale(kb, kb)
    p = skia.Path(); p.moveTo(-36, 30); p.quadTo(-36, -40, 0, -44); p.quadTo(36, -40, 36, 30); p.close()
    glowdraw(lambda q: c.drawPath(p, q), kb, WHITE, 0.9, 3.5)
    circle(c, 0, 42, 8, kb, glow=0.6)
    c.restore()
    tag(c, "DAILY MOTIVATION", 960, 880, T.pc(1, 0.5) * 0.9, 18, 6)


SCENES = [
    dict(say=["You think you need more *money*."], draw=s1),
    dict(say=["You don't.", "You need a *system*."], draw=s2),
    dict(say=[("*$5* a day.", "Five dollars a day.")], draw=s3),
    dict(say=["Invested.", "Every day.", "For forty *years*."], draw=s4),
    dict(say=[("That's almost *one million* dollars.", "That's almost one million dollars.")], draw=s5),
    dict(say=["Your coffee isn't the problem.", "*Waiting* is."], draw=s6),
    dict(say=["Follow me.", "I'll motivate you *every day*."], draw=s7, pause=1.0),
]
