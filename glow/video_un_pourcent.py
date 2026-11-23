"""Vidéo 2 — « 1 % par jour »."""
import math, os
from engine import *

SEED = 23
SPEED = 1.1
VOICE = "el_jessica"
CACHE = os.path.join(ROOT, "out", "tts_pourcent")
MUSIC = dict(beat=True, beat_bpm=88, seed=9, bpm=70, gain=1.0, prog=[[50, 53, 57], [46, 50, 53], [53, 57, 60], [48, 52, 55]],
             hit_scenes=[7, 10, 12])

DIM = (120, 125, 135)


def fr(v, d=2):
    return f"{v:.{d}f}".replace(".", ",")


# ---------------------------------------------------------------- graphe
OX, OY, GW = 380, 850, 1180


def graph_pts(days, S, n=120, rate=0.01):
    pts_a, pts_b = [], []
    for i in range(n + 1):
        d = days * i / n
        x = OX + GW * i / n
        pts_a.append((x, OY - 0))
        pts_b.append((x, OY - ((1 + rate) ** d - 1) * S))
    return pts_a, pts_b


def axes(c, a, label="JOURS", maxd="30"):
    line(c, [(OX, OY + 30), (OX, 330)], a * 0.35, 1.6, 0)
    line(c, [(OX - 20, OY + 30), (OX + GW + 40, OY + 30)], a * 0.35, 1.6, 0)
    tag(c, label, OX + GW / 2, OY + 68, a * 0.5, 13, 6)
    tag(c, "0", OX, OY + 68, a * 0.5, 13, 4)
    tag(c, maxd, OX + GW, OY + 68, a * 0.5, 13, 4)


def curves(c, days, S, prog=1.0, a=1.0, fig=True, labels=None, lit_b=1.0):
    A, B = graph_pts(days, S)
    line(c, A, a * 0.55, 3, 0.4, rgb=DIM, progress=max(prog, 0.001))
    line(c, B, a, 3.5, 1.1, progress=max(prog, 0.001), smooth=True)
    if fig and prog > 0:
        pa = make_path(A); pb = make_path(B, True)
        xa, ya = point_on(pa, prog); xb, yb = point_on(pb, prog)
        figure(c, xa, ya, 0.7, a, dim=0.55)
        figure(c, xb, yb, 0.7, a, lit=0.7 * lit_b)
        return (xa, ya), (xb, yb)
    return None, None


# 1 — deux personnes, même endroit
def s1(c, T):
    k = T.pc(0, 2.0, f=ease)
    line(c, [(260, 760), (lerp(260, 1660, k), 760)], 0.6, 2.5, 0.6)
    for i, x in enumerate((870, 1050)):
        kk = T.pc(0, 0.7, delay=0.2 + 0.25 * i)
        figure(c, x, 760 - (1 - kk) * 25, 1.15, kk)
    kk = T.pc(2, 0.6)
    circle(c, 960, 760, 9, kk, glow=1)
    tag(c, "DÉPART", 960, 815, kk * 0.8, 15, 5)
    ring(c, 960, 700, 170 + 5 * math.sin(T.t * 2), 0.45 * kk)


# 2 — même âge, même boulot, même salaire
def s2(c, T):
    figure(c, 830, 780, 1.4, 1)
    figure(c, 1090, 780, 1.4, 1)
    draw_text(c, "=", 960, 735, 60, TF_SEMI, a=T.pc(0, 0.5) * 0.7)
    items = [("25 ANS", 640), ("MÊME TAF", 960), ("1 800 €", 1280)]
    for i, (lab, x) in enumerate(items):
        k = T.pc(i, 0.5, f=eback)
        if k > 0:
            c.save(); c.translate(x, 450); c.scale(k, k)
            boxed(c, lab, 0, 0, k, 17, 5, 22)
            c.restore()
            dashed(c, [(x, 485), (lerp(x, 960, 0.5), 600)], 0.25 * k, 1.4, progress=k)


LA, LB = 560, 820  # deux couloirs


def lanes(c, T, ka=1.0, kb=1.0, pa=0.0, pb=0.0, lit_a=0.0, lit_b=0.0, dim_a=0.0, dim_b=0.0):
    line(c, [(300, LA), (lerp(300, 1620, ka), LA)], 0.55, 2.2, 0.5, rgb=DIM if dim_a else WHITE)
    if kb > 0:
        pts = [(300 + 1320 * kb * i / 40, LB - 120 * (kb * i / 40) ** 2) for i in range(41)]
        line(c, pts, 0.85, 2.8, 0.9)
    xa = lerp(330, 1500, pa)
    figure(c, xa, LA, 0.9, 1, lit=lit_a, dim=dim_a)
    xb = lerp(330, 1500, pb)
    yb = LB - 120 * ((xb - 300) / 1320) ** 2 if pb > 0 else LB
    figure(c, xb, yb, 0.9, 1, lit=lit_b, dim=dim_b)
    tag(c, "A", 270, LA - 30, 0.6, 16, 0)
    tag(c, "B", 270, LB - 30, 0.6, 16, 0)
    return (xa, LA), (xb, yb)


# 3 — la première ne change rien
def s3(c, T):
    walk = T.pc(1, 3.0, f=ease) * 0.25
    (xa, ya), _ = lanes(c, T, ka=T.pc(0, 1.5, f=ease), kb=0.0, pa=walk, lit_a=0.4, dim_b=0.6)
    k = T.pc(1, 0.6, delay=0.4)
    boxed(c, "0 %", xa + 150, LA - 50, k, 18, 4, 18)


# 4 — la deuxième s'améliore de 1 %, chaque jour
def s4(c, T):
    kb = T.pc(1, 2.5, f=ease)
    walk = 0.25 * T.pc(1, 3.5, f=ease)
    _, (xb, yb) = lanes(c, T, ka=1, kb=kb, pa=0.25, pb=walk, lit_b=0.8, dim_a=0.6)
    k = T.pc(1, 0.6, delay=0.3)
    boxed(c, "+1 %", xb + 150, yb - 50, k, 18, 4, 18)
    # jours qui défilent
    for i in range(10):
        q = T.pc(2, 0.3, delay=i * 0.12)
        x = 360 + i * 125
        circle(c, x, LB + 50, 4, q * 0.6, glow=0.5)
    tag(c, "CHAQUE JOUR", 960, LB + 100, T.pc(2, 0.6) * 0.6, 14, 6)


# 5 — 1 %, c'est rien : 10 pages, 20 min, 1 €
def book(c, x, y, a):
    p = skia.Path()
    p.moveTo(x - 70, y - 40); p.quadTo(x - 35, y - 55, x, y - 40); p.lineTo(x, y + 40)
    p.quadTo(x - 35, y + 25, x - 70, y + 40); p.close()
    p2 = skia.Path()
    p2.moveTo(x + 70, y - 40); p2.quadTo(x + 35, y - 55, x, y - 40); p2.lineTo(x, y + 40)
    p2.quadTo(x + 35, y + 25, x + 70, y + 40); p2.close()
    for q in (p, p2):
        glowdraw(lambda pp: c.drawPath(q, pp), a, WHITE, 0.8, 3)
    for i in range(3):
        line(c, [(x - 55, y - 20 + i * 18), (x - 15, y - 25 + i * 18)], a * 0.5, 2, 0)
        line(c, [(x + 15, y - 25 + i * 18), (x + 55, y - 20 + i * 18)], a * 0.5, 2, 0)


def coin(c, x, y, a):
    circle(c, x, y, 52, a, stroke=3, glow=0.9)
    circle(c, x, y, 40, a * 0.5, stroke=1.6, glow=0)
    draw_text(c, "€", x, y + 16, 46, TF_BOLD, a=a, glow=0.4)


def s5(c, T):
    k0 = T.pc(0, 0.6)
    draw_text(c, "1 %", 960, 560, 130, TF_BOLD, a=k0 * (1 - T.pc(2, 0.5)), glow=0.8)
    xs = [600, 960, 1320]
    for i, x in enumerate(xs):
        k = T.pc(2 + i, 0.55, f=eback)
        if k <= 0:
            continue
        c.save(); c.translate(x, 560); c.scale(k, k)
        if i == 0:
            book(c, 0, 0, k)
        elif i == 1:
            clock(c, 0, 0, 55, k, ang=T.t * 3)
        else:
            coin(c, 0, 0, k)
        c.restore()
        tag(c, ["10 PAGES", "20 MIN", "1 € DE CÔTÉ"][i], x, 680, k * 0.85, 16, 5)
    figure(c, 960, 900, 0.9, T.pc(2, 0.6), lit=0.4)


# 6 — au début, personne ne voit la différence
def s6(c, T):
    a = T.pc(0, 0.6)
    axes(c, a, maxd="30")
    prog = T.pc(0, T.dur - 0.6, f=ease, delay=0.3)
    curves(c, 30, 150, prog, a)


# 7 — après un mois, à peine devant
def s7(c, T):
    z = lerp(1.0, 1.45, T.pc(0, 2.5, f=ease))
    camera(c, z, lerp(960, OX + GW - 120, T.pc(0, 2.5, f=ease)), lerp(600, OY - 60, T.pc(0, 2.5, f=ease)))
    axes(c, 1, maxd="30")
    (xa, ya), (xb, yb) = curves(c, 30, 150, 1.0, 1)
    k = T.pc(1, 0.6)
    tag(c, "×1,00", xa + 90, ya + 8, k * 0.6, 16, 3)
    tag(c, "×1,35", xb + 90, yb + 8, k, 16, 3)
    line(c, [(xb + 40, ya - 2), (xb + 40, yb + 2)], k * 0.6, 2, 0.4)
    boxed(c, "JOUR 30", xb - 40, ya - 150, T.pc(0, 0.6, delay=0.5), 15, 5, 18)


# 8 — tout le monde abandonne
def s8(c, T):
    axes(c, 1, maxd="30")
    A, B = graph_pts(30, 150)
    line(c, A, 0.4, 3, 0.3, rgb=DIM)
    pb = make_path(B, True)
    line(c, B, 1, 3.5, 1.0, smooth=True)
    n = 9
    for i in range(n):
        q = 0.1 + 0.8 * i / (n - 1)
        x, y = point_on(pb, q)
        t0 = T.c(2) - 0.6 + i * 0.22
        f = T.p(t0, 1.1, f=lambda v: clamp(v) ** 2)
        figure(c, x + f * 30, y + f * 260, 0.55, (1 - f) * 0.9, dim=0.2 + 0.5 * f, halo=0.6)
        if 0 < f < 1:
            pass
    x, y = point_on(pb, 1.0)
    figure(c, x, y, 0.7, 1, lit=0.8)
    k = T.pc(2, 0.6)
    boxed(c, "ABANDON", 900, 470, k, 18, 6, 22)
    dashed(c, [(900, 505), (900, 700)], 0.3 * k, 1.4, progress=k)


# 9 — le cerveau veut des résultats tout de suite
def s9(c, T):
    figure(c, 640, 820, 1.3, 1, lit=0.2)
    k = T.pc(1, 0.6)
    rrect(c, 1120, 560, 620, 54, 27, k, stroke=2.5, glow=0.7)
    fill = 0.04 + 0.02 * math.sin(T.t * 3)
    if k > 0:
        rr = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(1120 - 300, 560 - 18, 600 * fill * k + 4, 36), 18, 18)
        c.drawRRect(rr, paint(WHITE, k * 0.9))
    tag(c, "RÉSULTATS", 1120, 630, k * 0.7, 15, 6)
    tag(c, "3 %", 1450, 520, k * 0.6, 15, 3)
    msgs = [("ça marche pas", 0.0), ("toujours rien", 0.5), ("j'arrête", 1.0)]
    for i, (m, d) in enumerate(msgs):
        kk = T.pc(2, 0.45, delay=d, f=eback)
        if kk > 0:
            c.save(); c.translate(560 + i * 90, 600 - i * 70); c.scale(kk, kk)
            bubble(c, 0, 0, m, kk, 18)
            c.restore()


# 10 — mais les maths ne mentent pas
def s10(c, T):
    k = T.pc(0, 0.8)
    draw_text(c, "1,01", 920, 640, 170, TF_BOLD, a=k, glow=0.9)
    kk = T.pc(1, 0.6, f=eback)
    c.save(); c.translate(1150, 520); c.scale(kk, kk)
    draw_text(c, "365", 0, 0, 80, TF_BOLD, a=kk, glow=0.9)
    c.restore()
    k3 = T.pc(2, 0.8)
    draw_text(c, "= 37,8", 960, 820, 70, TF_ITAL, a=k3, glow=0.8)
    light_bloom(c, 960, 600, 500, 0.5 * k)


# 11 — un an plus tard : 37 fois mieux
def s11(c, T):
    m = T.p(0.2, T.c(3) + 0.5, f=ease)
    days = lerp(30, 365, m)
    S = lerp(150, 420 / ((1.01 ** 365) - 1), m)
    S = min(S, 420 / ((1.01 ** days) - 1))
    S2 = S * 1.0
    a = 1
    axes(c, a, maxd=str(int(days)))
    A, B = graph_pts(days, S2)
    line(c, A, 0.5, 3, 0.4, rgb=DIM)
    line(c, B, 1, 3.8, 1.3, smooth=True)
    xa, ya = A[-1]; xb, yb = B[-1]
    light_bloom(c, xb, yb - 30, 260, 0.6 * m)
    figure(c, xa, ya, 0.7, 1, dim=0.55)
    figure(c, xb, yb, 0.8, 1, lit=0.9, arms="up" if m > 0.95 else "down")
    v = 1.01 ** days
    draw_text(c, "×" + fr(v, 1 if v >= 10 else 2), xb - 150, yb + 10, 44, TF_BOLD, a=1, glow=0.8)
    boxed(c, f"JOUR {int(days)}", xb - 150, yb + 75, 1, 15, 5, 18)


# 12 — la première est restée au même endroit
def s12(c, T):
    m = T.pc(0, 3.0, f=ease)
    camera(c, lerp(1.0, 1.45, m), lerp(960, OX + GW - 200, m), lerp(600, OY - 20, m))
    axes(c, 1, maxd="365")
    S = 420 / ((1.01 ** 365) - 1)
    A, B = graph_pts(365, S)
    line(c, A, 0.6, 3, 0.4, rgb=DIM)
    line(c, B, 1, 3.8, 1.3, smooth=True)
    xa, ya = A[-1]
    figure(c, xa, ya, 0.7, 1, dim=0.4, lit=0)
    k = T.pc(1, 0.6)
    tag(c, "×1", xa - 90, ya - 25, k * 0.8, 18, 3)
    ring(c, xa, ya - 32, 60, 0.4 * T.pc(2, 0.6))


# 13 — juste 1 %, aujourd'hui
def s13(c, T):
    k = T.pc(0, 3, f=ease)
    light_bloom(c, 960, 520, 560, 0.7 * T.pc(0, 1.5))
    hill = make_path([(200, 1000), (600, 900), (860, 640), (960, 560), (1060, 640), (1320, 900), (1720, 1000)], True)
    fp = skia.Path(hill); fp.lineTo(1720, 1300); fp.lineTo(200, 1300); fp.close()
    c.drawPath(fp, paint((5, 6, 10), 1))
    glowdraw(lambda p: c.drawPath(hill, p), 0.95, WHITE, 1.2, 3.2)
    figure(c, 960, 560, 1.0, 1, lit=1, arms="up" if T.t > T.c(3) else "down")
    pts = [(640, 380), (760, 310), (880, 350), (1040, 300), (1170, 360), (1280, 320)]
    kk = T.pc(1, 2.0, f=ease)
    for i, (px, py) in enumerate(pts):
        star4(c, px, py, 9, clamp(kk * 5 - i))
    line(c, pts, 0.3, 1.2, 0.3, progress=max(0.001, kk))
    k2 = T.pc(2, 0.5, f=eback)
    c.save(); c.translate(1150, 500); c.scale(k2, k2)
    boxed(c, "+1 %", 0, 0, k2, 22, 4, 22)
    c.restore()


# 14 — CTA
def s14(c, T):
    k = T.pc(0, 0.6)
    figure(c, 860, 780, 1.2, k, dim=0.5)
    figure(c, 1060, 780, 1.2, k, lit=T.pc(0, 1.0, delay=0.5))
    dashed(c, [(900, 650), (960, 600), (1020, 650)], 0.4 * T.pc(0, 0.8, delay=0.5), 1.6,
           progress=T.pc(0, 0.8, delay=0.5))
    kk = T.pc(1, 0.5, f=eback)
    c.save(); c.translate(960, 900); c.scale(kk, kk)
    rrect(c, 0, 0, 380, 64, 32, kk, stroke=2.5, glow=0.9, fill=(10, 12, 18))
    draw_text(c, "PARTAGE  →", 0, 8, 22, a=kk, spacing=5)
    c.restore()


SCENES = [
    dict(say=["Imagine deux potes.", "Ils partent exactement", "du même *endroit*."], draw=s1),
    dict(say=["Même âge.", "Même taf.", "Même *salaire*."], draw=s2),
    dict(say=["Le premier", "change *rien*."], draw=s3),
    dict(say=["Le deuxième", ("progresse de 1 %.", "progresse de un pour cent."), "*Chaque* jour."], draw=s4),
    dict(say=[("1 %,", "Un pour cent,"), "c'est rien, hein ?", "Dix pages de lecture.", "Vingt minutes de sport.",
              ("Un euro mis de *côté*.", "Un euro mis de côté.")], draw=s5),
    dict(say=["Au début,", "tu vois *aucune* différence."], draw=s6, zoom=1.15),
    dict(say=["Au bout d'un mois,", "il est à peine *devant*."], draw=s7, zoom=1.15),
    dict(say=["Et c'est là", "que quasiment tout le monde", "*lâche*."], draw=s8, zoom=1.15),
    dict(say=["Parce que ton cerveau", "veut des résultats", "*tout de suite*."], draw=s9, zoom=1.15),
    dict(say=["Mais les maths,", "elles,", "mentent *pas*."], draw=s10),
    dict(say=[("1 % par jour,", "Un pour cent par jour,"), "pendant un an,", "ça fait",
              ("37 fois *mieux*.", "trente-sept fois mieux.")], draw=s11, zoom=1.15, pause=0.6),
    dict(say=["Et le premier ?", "Il est resté", "au même *endroit*."], draw=s12, zoom=1.15),
    dict(say=["T'as pas besoin", "d'un énorme changement.", ("Juste 1 %.", "Juste un pour cent."),
              "*Aujourd'hui*."], draw=s13),
    dict(say=["Envoie ça au pote", "qui doit l'*entendre*."], draw=s14),
]
