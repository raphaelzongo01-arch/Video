"""Vidéo 1 — « Le bon moment n'existe pas »."""
import math, os
from engine import *

SEED = 11
SPEED = 1.1
VOICE = "siwis"
CACHE = os.path.join(ROOT, "out", "tts_attente")
MUSIC = dict(seed=4, bpm=66, gain=1.0, hit_scenes=[4, 10, 11])

GY = 700  # sol de la rangée
ROW = [W / 2 + (i - 4) * 152 for i in range(9)]
HERO = 4


def row(c, T, dim=0.0, a=1.0, hero_lit=0.0, skip_hero=False, sway=True):
    for i, x in enumerate(ROW):
        if skip_hero and i == HERO:
            continue
        bob = math.sin(T.t * 1.6 + i * 1.3) * 2 if sway else 0
        figure(c, x, GY + bob, 1.0, a, lit=hero_lit if i == HERO else 0, dim=dim)


# 1 — Tout le monde attend le bon moment
def s1(c, T):
    camera(c, lerp(1.12, 1.0, T.p(0, 4, ease)), W / 2, lerp(560, H / 2, T.p(0, 4, ease)))
    for i, x in enumerate(ROW):
        k = T.p(0.05 * i, 0.7)
        figure(c, x, GY + (1 - k) * 30, 1.0, k)
    k = T.pw(0, 3, 0.8)
    clock(c, W / 2, 420, 62, k, ang=T.t * 2.4)
    for i, x in enumerate(ROW):  # regards vers l'horloge
        dashed(c, [(x, GY - 95), (W / 2 + (x - W / 2) * 0.15, 490)], 0.18 * T.pw(1, 0, 0.8), 1.5,
               progress=T.pw(1, 0, 1.0))


# 2 — projets en attente
def s2(c, T):
    row(c, T)
    clock(c, W / 2, 420, 62, 1 - T.pc(0, 0.4), ang=T.t * 2.4 + 8)
    labels = [(1, "PROJET"), (3, "BUSINESS"), (5, "SPORT"), (7, "VOYAGE"), (2, "LIVRE"), (6, "DÉMÉNAGER")]
    for n, (i, lab) in enumerate(labels):
        k = T.p(T.c(min(n // 2, 2)) + (n % 2) * 0.35, 0.5, eback)
        if k <= 0:
            continue
        y = GY - 175 - (n % 2) * 70
        dashed(c, [(ROW[i], GY - 98), (ROW[i], y + 18)], 0.35 * k, 1.5)
        c.save(); c.translate(ROW[i], y); c.scale(k, k)
        boxed(c, lab, 0, 0, k, size=15, spacing=4, pad=16)
        c.restore()


# 3 — lundi, le mois prochain, l'année prochaine
def s3(c, T):
    row(c, T, dim=0.25 * T.pc(1, 2))
    k = T.pc(0, 0.6, delay=0.2)
    labs = [("LUNDI", "BIENTÔT"), ("MOIS +1", "PLUS TARD"), ("2027", "UN JOUR")]
    idx = 0 if T.t < T.c(2) - 0.05 else 1 if T.t < T.c(3) - 0.05 else 2
    flip = 1 - abs(math.sin(clamp((T.t - [0, T.c(2), T.c(3)][idx]) / 0.25) * math.pi)) * 0.25
    calendar(c, W / 2, 430, 130 * flip * k, k, big=labs[idx][0], small=labs[idx][1])
    for j in range(3):
        kk = T.pc(j + 1, 0.4)
        tag(c, ["LUNDI", "LE MOIS PROCHAIN", "L'ANNÉE PROCHAINE"][j], W / 2 + (j - 1) * 470, 540, kk * 0.6)
        line(c, [(W / 2 + (j - 1) * 470 - 60, 556), (W / 2 + (j - 1) * 470 + 60, 556)], kk * 0.25, 1.5, 0)


# 4 — le temps n'attend personne
def s4(c, T):
    fade = T.pc(1, 3, f=ease)
    row(c, T, dim=0.25 + 0.45 * fade, a=1 - 0.35 * fade)
    # ligne du temps qui défile sous la rangée
    k = T.pc(0, 1.2, f=ease)
    line(c, [(0, GY + 60), (W * k, GY + 60)], 0.6, 2, 0.6)
    off = (T.t * 160) % 120
    for i in range(18):
        x = W - (i * 120 + off)
        if x < W * (1 - k):
            continue
        line(c, [(x, GY + 52), (x, GY + 68)], 0.5, 2, 0)
    hourglass(c, W / 2, 440, 1.2, T.pc(1, 0.7), k=clamp((T.t - T.c(1)) / 5))
    draw_text(c, "→", W - 90, GY + 105, 40, TF_SEMI, a=0.5 * k)


# 5 — un jour, l'un d'eux décide d'avancer
def s5(c, T):
    zk = T.p(T.c(1), 3, ease)
    camera(c, lerp(1.0, 1.18, zk), W / 2, lerp(H / 2, 600, zk))
    step = T.pc(1, 1.6, delay=0.4, f=ease)
    for i, x in enumerate(ROW):
        if i == HERO:
            continue
        figure(c, x, GY, 1.0, 0.85, dim=0.6)
    lit = T.pc(0, 0.8)
    hy = GY + step * 130
    hx = ROW[HERO]
    bob = abs(math.sin(step * math.pi * 3)) * -8 if 0 < step < 1 else 0
    figure(c, hx, hy + bob, 1.0 + 0.1 * step, 1, lit=lit, arms="down")
    ring(c, hx, hy - 50, 95 + 6 * math.sin(T.t * 2), 0.7 * T.pc(0, 0.6) * (1 - T.pc(2, 0.6)))
    k = T.pc(2, 0.6)
    tag(c, "PAS PRÊT", hx + 150, hy - 55, k * 0.9)
    line(c, [(hx + 75, hy - 60), (hx + 92, hy - 60)], k * 0.5, 2, 0)


# 6 — les autres le regardent, ils jugent
def s6(c, T):
    camera(c, 1.18, W / 2, 600)
    hx, hy = ROW[HERO], GY + 130
    for i, x in enumerate(ROW):
        if i == HERO:
            continue
        turn = T.pc(0, 0.6)
        figure(c, x, GY, 1.0, 0.9, dim=0.45 - 0.15 * turn)
    figure(c, hx, hy, 1.1, 1, lit=0.6)
    msgs = [(1, "lol", 0), (3, "jamais", 1), (5, "t'es sûr ?", 0), (7, "...", 1), (2, "pfff", 2), (6, "il rêve", 2)]
    for n, (i, m, ch) in enumerate(msgs):
        k = T.p(T.c(min(ch, 2)) + 0.15 * (n % 3), 0.45, eback)
        if k > 0:
            c.save(); c.translate(ROW[i] + 20, GY - 150 - (n % 2) * 45); c.scale(k, k)
            bubble(c, 0, 0, m, k, 19)
            c.restore()


# 7 — premiers pas maladroits
PATH7 = [(260, 760), (420, 740), (520, 780), (640, 700), (760, 760), (900, 650), (1040, 700), (1200, 580),
         (1360, 620), (1520, 480), (1700, 430)]


def s7(c, T):
    k = 0.12 + 0.88 * T.pc(0, T.dur - 0.3, f=ease)
    p = make_path(PATH7, True)
    fx, fy = point_on(p, k * 0.45)
    camera(c, 1.35, fx + 120, fy - 60)
    path = line(c, PATH7, 0.85, 3, 0.9, progress=max(0.001, k * 0.45), smooth=True)
    p = make_path(PATH7, True)
    x, y = point_on(p, k * 0.45)
    wob = math.sin(T.t * 9) * 4 * (1 - T.pc(0, 3))
    c.save(); c.translate(x, y); c.rotate(wob); c.translate(-x, -y)
    figure(c, x, y, 0.85, 1, lit=0.5)
    c.restore()


# 8 — les heures, les échecs, les recommencements
def s8(c, T):
    cam = T.pc(0, T.dur - 0.2, f=ease)
    p = make_path(PATH7, True)
    k = 0.45 + 0.35 * T.pc(0, T.dur - 0.4, f=ease)
    fx, fy = point_on(p, k)
    z = lerp(1.35, 0.95, cam)
    camera(c, z, lerp(fx + 120, W / 2 + 150, cam), lerp(fy - 60, 640, cam))
    line(c, PATH7, 0.85, 3, 0.9, progress=k, smooth=True)
    nodes = [(0.12, "ESSAI", True), (0.24, "ÉCHEC", False), (0.36, "RECOMMENCE", True), (0.5, "ÉCHEC", False),
             (0.62, "100 H", True), (0.74, "ENCORE", True)]
    for n, (q, lab, ok) in enumerate(nodes):
        if k < q:
            continue
        kk = clamp((k - q) / 0.04)
        x, y = point_on(p, q)
        check(c, x, y, 14 * eback(kk), kk, ok)
        tag(c, lab, x, y + 48, kk * 0.75, size=14, spacing=4)
    x, y = point_on(p, k)
    figure(c, x, y - 4, 0.85, 1, lit=0.6)


# 9 — chaque jour un peu plus loin (dézoom, colline)
HILL = [(-200, 900), (300, 880), (700, 820), (1050, 640), (1300, 470), (1500, 370), (1650, 330), (1800, 345),
        (2100, 520), (2500, 820), (2900, 1000)]


def s9(c, T):
    z = lerp(1.25, 0.95, T.p(0, T.dur, ease))
    camera(c, z, lerp(700, 1050, T.p(0, T.dur, ease)), 600)
    # colline pleine
    hill = make_path(HILL, True)
    fillp = skia.Path(hill); fillp.lineTo(2900, 1600); fillp.lineTo(-200, 1600); fillp.close()
    c.drawPath(fillp, paint((6, 7, 11), 1))
    line(c, HILL, 0.25, 2, 0.4, smooth=True)
    k = T.pc(0, T.dur - 0.3, f=ease)
    line(c, HILL[:7], 0.95, 3.5, 1.2, progress=max(0.001, 0.25 + 0.6 * k), smooth=True)
    hp = make_path(HILL[:7], True)
    x, y = point_on(hp, 0.25 + 0.6 * k)
    figure(c, x, y - 2, 0.85, 1, lit=0.8)
    # la foule, minuscule, au pied
    for j in range(8):
        figure(c, 120 + j * 34, 885, 0.32, 0.8, dim=0.6, halo=0.3)
    tag(c, "EUX", 240, 960, T.pc(1, 0.6) * 0.6, 13, 4)


# 10 — un an plus tard, ils attendent toujours
def s10(c, T):
    row(c, T, dim=0.55, skip_hero=True)
    k = T.pc(0, 0.7)
    calendar(c, W / 2, 430, 130, k, big="+365", small="JOURS")
    clock(c, W / 2 + 200, 430, 44, 0.6 * T.pc(1, 0.6), ang=T.t * 2.4)
    # la place vide du héros
    dashed(c, [(ROW[HERO] - 32, GY), (ROW[HERO] - 32, GY - 54), (ROW[HERO] + 32, GY - 54), (ROW[HERO] + 32, GY)],
           0.35 * T.pc(2, 0.6), 1.5, (5, 7))
    for i, x in enumerate(ROW):
        if i != HERO and T.pc(2, 0.1) > 0:
            tag(c, "...", x, GY - 120 - 6 * math.sin(T.t * 2 + i), 0.5 * T.pc(2, 0.6), 20, 6)


# 11 — lui, il est ailleurs
def s11(c, T):
    z = lerp(0.9, 1.08, T.p(0, 6, ease))
    camera(c, z, 1500, 520)
    hill = make_path(HILL, True)
    fillp = skia.Path(hill); fillp.lineTo(2900, 1600); fillp.lineTo(-200, 1600); fillp.close()
    light_bloom(c, 1650, 300, 520, 0.9 * T.pc(0, 2))
    c.drawPath(fillp, paint((5, 6, 10), 1))
    line(c, HILL, 0.95, 3.5, 1.2, smooth=True)
    x, y = point_on(make_path(HILL[:7], True), 1.0)
    figure(c, x, y - 2, 1.0, 1, lit=1, arms="up" if T.t > T.c(1) + 0.3 else "down")
    # constellation
    pts = [(1360, 170), (1460, 120), (1580, 150), (1700, 90), (1820, 140), (1910, 110)]
    kk = T.pc(1, 2.0, f=ease)
    for i, (px, py) in enumerate(pts):
        star4(c, px, py, 10, clamp(kk * 6 - i))
    line(c, pts, 0.35, 1.2, 0.3, progress=max(0.001, kk))


# 12 — le bon moment n'arrive jamais, il se crée
def s12(c, T):
    k = T.pc(0, 0.7)
    clock(c, W / 2, 470, 120, k * (1 - T.pc(1, 0.8)), ang=T.t * 0.4)
    cross = T.pc(0, 0.5, delay=1.2)
    line(c, [(W / 2 - 150, 620), (W / 2 + 150, 320)], cross * (1 - T.pc(1, 0.8)), 4, 0.8, progress=cross)
    kk = T.pc(1, 0.9, f=ease)
    light_bloom(c, W / 2, 560, 420 * kk + 1, kk)
    figure(c, W / 2, 680, 1.5, kk, lit=kk, arms="open")
    ring(c, W / 2, 600, 140 + 10 * math.sin(T.t * 2), 0.6 * kk)


# 13 — commence aujourd'hui
def s13(c, T):
    line(c, [(260, 640), (1660, 640)], 0.7, 2.5, 0.7, progress=T.pc(0, 1.5, f=ease))
    days = ["JOUR 1", "JOUR 2", "JOUR 3", "JOUR 30", "JOUR 365"]
    for i, d in enumerate(days):
        x = 360 + i * 300
        k = T.pc(1, 0.4, delay=i * 0.18)
        done = i == 0 and T.pc(1, 0.3, delay=0.8) > 0
        if done:
            check(c, x, 640, 16 * eback(T.pc(1, 0.4, delay=0.8)), k)
        elif k > 0:
            circle(c, x, 640, 16, k * 0.9, glow=0.4, rgb=(15, 17, 24))
            circle(c, x, 640, 16, k * 0.9, stroke=2.5, glow=0.5)
        tag(c, d, x, 700, k * (1 if i == 0 else 0.5), 15, 5)
    k = T.pc(1, 1.0, delay=0.3)
    figure(c, 360, 620, 0.9, k, lit=0.9)
    kk = T.pc(2, 0.6)
    boxed(c, "AUJOURD'HUI", 360, 790, kk, 18, 5)


# 14 — CTA
def s14(c, T):
    k = T.pc(0, 0.6)
    for i, x in enumerate(ROW):
        figure(c, x, GY, 1.0, 0.8 * k, dim=0.55, lit=0)
    figure(c, ROW[HERO], GY, 1.05, k, lit=1 * T.pc(0, 1.0, delay=0.6))
    ring(c, ROW[HERO], GY - 50, 95, 0.6 * T.pc(0, 0.8, delay=0.6))
    kk = T.pc(1, 0.5, f=eback)
    c.save(); c.translate(W / 2, 880); c.scale(kk, kk)
    rrect(c, 0, 0, 380, 64, 32, kk, stroke=2.5, glow=0.9, fill=(10, 12, 18))
    draw_text(c, "PARTAGE  →", 0, 8, 22, a=kk, spacing=5)
    c.restore()


SCENES = [
    dict(say=["Tout le monde attend le bon moment.", "Et toi aussi, *franchement*."], draw=s1),
    dict(say=["Le bon moment pour lancer ton *business*,", "pour te remettre au sport,", "pour enfin *te lancer*."],
         draw=s2),
    dict(say=["Alors tu repousses.", "Lundi.", "Le mois prochain.", "L'année *prochaine*."], draw=s3),
    dict(say=["Mais écoute-moi bien.", "Le temps, lui,", "il t'attend *pas*."], draw=s4),
    dict(say=["Un jour,", "y en a un qui décide d'y aller.", "Sans être *prêt*."], draw=s5),
    dict(say=["Et là, tout le monde le regarde.", "Ils le *jugent*.", "« Pour qui il se prend ? »"], draw=s6),
    dict(say=["Ses premiers pas sont *nuls*.", "Et c'est normal."], draw=s7, zoom=1.0),
    dict(say=["Personne voit les heures,", "les *échecs*,", "les fois où il recommence."], draw=s8, zoom=1.0),
    dict(say=["Mais chaque jour,", "il avance. Un peu plus *loin*."], draw=s9),
    dict(say=["Un an plus tard,", "ceux qui attendaient", "attendent *toujours*."], draw=s10),
    dict(say=["Lui ?", "Il est *ailleurs*."], draw=s11, pause=0.3),
    dict(say=["Le bon moment n'arrive jamais, mon pote.", "Tu le *crées*."], draw=s12),
    dict(say=["Alors arrête d'attendre.", "Commence *aujourd'hui*.", "Même petit. Même mal."], draw=s13, zoom=1.05),
    dict(say=["Envoie ça au pote", "qui attend *encore*."], draw=s14),
]
