"""Video 4 (EN) — "Your 5 people"."""
import math, os
import engine
from engine import *
from extras import *

engine.LANG = "en"
SEED = 41
SPEED = 1.0
VOICE = "el_jessica"
CACHE = os.path.join(ROOT, "out", "tts_cercle_en")
MUSIC = {}

CX, CY, R = 960, 640, 250


def pos(i, rot=0.0):
    a = -math.pi / 2 + i * 2 * math.pi / 5 + rot
    return CX + R * math.cos(a), CY + 30 + R * 0.78 * math.sin(a)


def circle_of_five(c, T, a=1.0, dim=0.0, hero_dim=0.0, hero_lit=0.3, links=1.0, alt=0.0, rot=0.0):
    """alt = 0 → ancien cercle (gris), 1 → nouveau cercle (lumineux)."""
    for i in range(5):
        x, y = pos(i, rot)
        dashed(c, [(CX, CY + 10), (x, y - 40)], 0.25 * a * links, 1.4)
    for i in range(5):
        x, y = pos(i, rot)
        bob = math.sin(T.t * 1.5 + i) * 2
        figure(c, x, y + bob, 0.9, a, dim=dim * (1 - alt), lit=0.5 * alt)
    figure(c, CX, CY + 40, 1.15, a, lit=hero_lit, dim=hero_dim)


# 1 — tu deviens les 5 personnes
def s1(c, T):
    for i in range(5):
        x, y = pos(i)
        k = T.pc(1, 0.5, delay=i * 0.12)
        dashed(c, [(CX, CY + 10), (x, y - 40)], 0.25 * k, 1.4, progress=k)
        figure(c, x, y + (1 - k) * 20, 0.9, k)
    figure(c, CX, CY + 40, 1.15, T.pc(0, 0.6), lit=0.4)
    ring(c, CX, CY + 10, 330, 0.3 * T.pc(2, 0.8), w=1.6)


# 2 — habitudes, mentalité, limites
def s2(c, T):
    circle_of_five(c, T)
    labs = ["HABITS", "MINDSET", "LIMITS"]
    for j, lab in enumerate(labs):
        k = T.pc(j, 0.45, f=eback)
        if k <= 0:
            continue
        x, y = pos([1, 4, 0][j])
        mx, my = (CX + x) / 2, (CY + y) / 2 - 30
        c.save(); c.translate(mx, my); c.scale(k, k)
        boxed(c, lab, 0, 0, k, 15, 5, 16)
        c.restore()


# 3 — s'ils se plaignent
def s3(c, T):
    circle_of_five(c, T, dim=0.4 * T.pc(0, 1.0))
    msgs = [(0, "ugh"), (1, "so tired"), (3, "not fair"), (4, "why me")]
    for n, (i, m) in enumerate(msgs):
        k = T.pc(0, 0.4, delay=0.3 + n * 0.25, f=eback)
        if k > 0:
            x, y = pos(i)
            c.save(); c.translate(x + 30, y - 135); c.scale(k, k)
            bubble(c, 0, 0, m, k, 17)
            c.restore()


# 4 — s'ils gaspillent leurs week-ends
def s4(c, T):
    circle_of_five(c, T, dim=0.5, hero_dim=0.25 * T.pc(1, 0.8))
    k = T.pc(0, 0.5)
    for j, d in enumerate(["SAT", "SUN"]):
        calendar(c, CX - 80 + j * 160, 325, 92, k, big=d, small="WASTED")


# 5 — s'ils rient de tes rêves
def s5(c, T):
    circle_of_five(c, T, dim=0.5, hero_dim=0.55 * T.pc(1, 1.2), hero_lit=0.3 * (1 - T.pc(1, 0.8)))
    for n, i in enumerate([0, 2, 4]):
        k = T.pc(0, 0.4, delay=0.4 + n * 0.2, f=eback)
        if k > 0:
            x, y = pos(i)
            c.save(); c.translate(x + 30, y - 135); c.scale(k, k)
            bubble(c, 0, 0, "lol", k, 18)
            c.restore()
    star4(c, CX, CY - 150, 16, 1 - T.pc(1, 1.0))


# 6 — ce n'est pas leur faute, c'est comme ça
def s6(c, T):
    circle_of_five(c, T, dim=0.5, hero_dim=0.4)
    k = T.pc(1, 1.2, f=ease)
    for i in range(5):  # l'influence descend vers le centre
        x, y = pos(i)
        line(c, [(x, y - 40), (lerp(x, CX, k), lerp(y - 40, CY - 20, k))], 0.5 * T.pc(1, 0.3), 2.5, 0.8)


# 7 — imagine un autre cercle
def s7(c, T):
    sw = T.pc(1, 1.4, f=ease)
    for i in range(5):
        x, y = pos(i)
        figure(c, x - 120 * sw * math.cos(i), y + 60 * sw, 0.9, 1 - sw, dim=0.5)
    for i in range(5):
        x, y = pos(i, 0.0)
        figure(c, x, y + (1 - sw) * 30, 0.9, sw, lit=0.6)
        dashed(c, [(CX, CY + 10), (x, y - 40)], 0.3 * sw, 1.4)
    figure(c, CX, CY + 40, 1.15, 1, lit=0.4 + 0.4 * sw)


# 8 — des gens qui s'entraînent, construisent, te poussent
def s8(c, T):
    circle_of_five(c, T, alt=1, hero_lit=0.8)
    labs = ["TRAIN", "BUILD", "PUSH YOU"]
    for j, lab in enumerate(labs):
        k = T.pc(j, 0.45, f=eback)
        if k <= 0:
            continue
        x, y = pos([1, 4, 0][j])
        mx, my = (CX + x) / 2, (CY + y) / 2 - 30
        c.save(); c.translate(mx, my); c.scale(k, k)
        boxed(c, lab, 0, 0, k, 15, 5, 16)
        c.restore()


# 9 — ta normalité change
def s9(c, T):
    k = T.pc(1, 1.0, f=ease)
    light_bloom(c, CX, CY, 520 * k + 1, 0.7 * k)
    circle_of_five(c, T, alt=1, hero_lit=1.0)
    ring(c, CX, CY - 10, lerp(100, 360, k), 0.6 * (1 - k * 0.6))


# 10 — pas besoin de couper tout le monde, mais choisis
def s10(c, T):
    k = T.pc(1, 0.8, f=ease)
    for i in range(5):
        x, y = pos(i)
        figure(c, x, y, 0.9, 1, dim=0.5 * (1 - k) if i % 2 else 0, lit=0.6 * k if i % 2 == 0 else 0)
    figure(c, CX, CY + 40, 1.15, 1, lit=0.7)
    kk = T.pc(1, 0.5, f=eback)
    c.save(); c.translate(CX, 340); c.scale(kk, kk)
    boxed(c, "CHOOSE", 0, 0, kk, 22, 6, 24)
    c.restore()


# 11 — regarde tes 5
def s11(c, T):
    for i in range(5):
        x, y = pos(i)
        k = T.pc(0, 0.4, delay=i * 0.12)
        ring(c, x, y - 40, 44, 0.6 * k, w=2)
        draw_text(c, "?", x, y - 26, 44, TF_BOLD, a=k, glow=0.6)
    figure(c, CX, CY + 40, 1.15, 1, lit=0.5 + 0.3 * T.pc(1, 0.8))


# 12 — CTA
def s12(c, T):
    circle_of_five(c, T, alt=1, hero_lit=0.8, a=T.pc(0, 0.5))
    kk = T.pc(1, 0.5, f=eback)
    c.save(); c.translate(CX, 990); c.scale(kk, kk)
    rrect(c, 0, 0, 380, 64, 32, kk, stroke=2.5, glow=0.9, fill=(10, 12, 18))
    draw_text(c, "SHARE  →", 0, 8, 22, a=kk, spacing=5)
    c.restore()


SCENES = [
    dict(say=["You become", "the five people", "you spend the most time *with*."], draw=s1),
    dict(say=["Their habits.", "Their mindset.", "Their *limits*."], draw=s2),
    dict(say=["If they complain all day,", "you'll *complain*."], draw=s3),
    dict(say=["If they waste their weekends,", "you'll *waste* yours."], draw=s4),
    dict(say=["If they laugh at your dreams,", "you'll stop *dreaming*."], draw=s5),
    dict(say=["It's not their *fault*.", "It's just how it works."], draw=s6),
    dict(say=["Now imagine", "a different *circle*."], draw=s7),
    dict(say=["People who train.", "Who build.", "Who *push* you."], draw=s8),
    dict(say=["Suddenly,", "your normal *changes*."], draw=s9),
    dict(say=["You don't have to cut everyone off.", "But you have to *choose*."], draw=s10),
    dict(say=["Look at your five.", "Be *honest*."], draw=s11),
    dict(say=["Send this to someone", "in your *five*."], draw=s12, zoom=1.15),
]
