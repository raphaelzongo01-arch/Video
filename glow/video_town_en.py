"""Video 6 (EN) — « In this town, everybody sleeps until noon. Except me. » (3D blocs, vertical)."""
import math, os
import numpy as np
import skia
import engine
from engine import ROOT, clamp, ease, eout, eback, lerp
from town3d import *

engine.LANG = "en"
SEED = 61
SPEED = 1.0
VOICE = "el_liam"
CACHE = os.path.join(ROOT, "out", "tts_town_en")

# ------------------------------------------------------------------ personnages
MILO = dict(skin=(176, 118, 80), top=(255, 132, 36), pants=(54, 66, 120), shoes=(70, 225, 130),
            headphones=True, hair=(38, 28, 24))
LEO = dict(skin=(244, 200, 160), top=(110, 200, 150), pants=(110, 200, 150), shoes=(240, 240, 240),
           hat="nightcap", hat_col=(110, 200, 150), hair=(200, 140, 60))
ROSA = dict(skin=(214, 160, 120), top=(250, 150, 190), pants=(250, 150, 190), shoes=(255, 255, 255),
            hair=(60, 35, 30), mask=True)
BOB = dict(skin=(240, 196, 160), top=(150, 120, 200), pants=(150, 120, 200), shoes=(120, 80, 60),
           hat="nightcap", hat_col=(150, 120, 200), hair=(220, 220, 220))
PJ = [dict(top=(140, 180, 250), pants=(140, 180, 250), hat="nightcap", hat_col=(140, 180, 250), skin=(240, 200, 165)),
      dict(top=(250, 210, 110), pants=(250, 210, 110), mask=True, skin=(190, 135, 95), hair=(30, 25, 20)),
      dict(top=(190, 150, 240), pants=(190, 150, 240), hat="nightcap", hat_col=(190, 150, 240), skin=(150, 100, 70)),
      dict(top=(250, 160, 160), pants=(250, 160, 160), mask=True, skin=(245, 210, 180), hair=(230, 190, 90)),
      dict(top=(150, 220, 220), pants=(150, 220, 220), hat="nightcap", hat_col=(150, 220, 220), skin=(225, 170, 125)),
      LEO, ROSA, BOB]
SPORT = [dict(top=c, pants=(50, 55, 70), shoes=(250, 250, 250), skin=s, hair=h)
         for c, s, h in [((230, 60, 70), (240, 200, 165), (90, 60, 30)), ((60, 140, 240), (150, 100, 70), (20, 20, 20)),
                         ((250, 200, 40), (225, 170, 125), (200, 150, 60)), ((120, 210, 110), (190, 135, 95), (30, 25, 20)),
                         ((200, 120, 240), (245, 210, 180), (230, 190, 90))]]


def F(size):
    f = skia.Font(skia.Typeface.MakeFromFile(os.path.join(engine.FONTS, "LilitaOne-Regular.ttf")), size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


_fc = {}


def font(size):
    if size not in _fc:
        _fc[size] = F(size)
    return _fc[size]


def text_dec(txt, fg=(255, 255, 255), bg=None, size=46, aspect=1.0):
    """aspect = largeur/hauteur de la face, pour garder des lettres non déformées."""
    def d(c, sh, fog):
        if bg:
            c.drawRect(skia.Rect.MakeLTRB(0, 0, 100, 100), skia.Paint(Color4f=col4(bg)))
        c.save(); c.scale(1 / aspect, 1.0)
        f = font(62)
        w = f.measureText(txt)
        k = min(1.0, 92 * aspect / max(w, 1))
        c.translate(50 * aspect, 50); c.scale(k, k)
        c.drawString(txt, -w / 2, 22, f, skia.Paint(AntiAlias=True, Color4f=col4(fg)))
        c.restore()
    return d


def window_dec(lit):
    def d(c, sh, fog):
        c.drawRect(skia.Rect.MakeLTRB(0, 0, 100, 100), skia.Paint(Color4f=col4((255, 220, 120) if lit else (60, 80, 120))))
        p = skia.Paint(Color4f=col4((250, 250, 250)), Style=skia.Paint.kStroke_Style, StrokeWidth=8)
        c.drawRect(skia.Rect.MakeLTRB(4, 4, 96, 96), p); c.drawLine(50, 0, 50, 100, p); c.drawLine(0, 50, 100, 50, p)
    return d


# ------------------------------------------------------------------ décor
HOUSES = [((235, 205, 170), (170, 70, 60)), ((170, 205, 235), (70, 90, 140)), ((240, 170, 170), (120, 60, 70)),
          ((200, 230, 180), (90, 110, 70)), ((250, 230, 150), (160, 90, 50)), ((215, 190, 240), (90, 70, 130))]


def ground(sc, z0=-140, z1=40, road=True):
    sc.flats.append(([(-60, 0, z0), (60, 0, z0), (60, 0, z1), (-60, 0, z1)], (110, 175, 90)))
    if road:
        sc.flats.append(([(-3.2, 0.01, z0), (3.2, 0.01, z0), (3.2, 0.01, z1), (-3.2, 0.01, z1)], (75, 78, 88)))
        for sgn in (-1, 1):
            x0, x1 = sorted((3.2 * sgn, 5.2 * sgn))
            sc.flats.append(([(x0, 0.02, z0), (x1, 0.02, z0), (x1, 0.02, z1), (x0, 0.02, z1)], (200, 200, 205)))
        for z in range(z0, z1, 6):
            sc.flats.append(([(-0.12, 0.03, z), (0.12, 0.03, z), (0.12, 0.03, z + 3), (-0.12, 0.03, z + 3)], (250, 220, 80)))


def house(sc, x, z, idx=0, lit=False, sign=None, w=6.0, d=6.5, h=4.0):
    wall, roof = HOUSES[idx % len(HOUSES)]
    sgn = 1 if x > 0 else -1   # porte côté route
    sc.cube(x, h / 2, z, w, h, d, wall)
    ang = 0.6
    for s2 in (-1, 1):
        sc.box(T(x + s2 * w * 0.24, h + 0.85, z) @ RZ(-s2 * ang) @ S(w * 0.62, 0.3, d + 0.7), roof)
    sc.box(T(x, h + 0.2, z) @ S(w * 0.98, 0.4, d), wall)
    fx = x - sgn * (w / 2 + 0.03)
    sc.box(T(fx, 1.1, z) @ RY(-sgn * math.pi / 2) @ S(1.2, 2.2, 0.08), (120, 80, 60))
    for dz in (-2.0, 2.0):
        sc.box(T(fx, 2.3, z + dz) @ RY(-sgn * math.pi / 2) @ S(1.2, 1.1, 0.06), (255, 255, 255),
               {4: window_dec(lit)}, outline=False)
    if sign:
        sc.box(T(fx - sgn * 0.3, 3.4, z) @ RY(-sgn * math.pi / 2) @ S(3.6, 0.9, 0.12), (255, 255, 255),
               {4: text_dec(sign, (255, 255, 255), (200, 70, 60), 40, aspect=4.0)})
        sc.box(T(fx - sgn * 0.9, 2.95, z) @ RZ(sgn * 0.35) @ S(1.5, 0.12, 4.2), (230, 80, 70))


def tree(sc, x, z, k=1.0):
    sc.cube(x, 0.9 * k, z, 0.45 * k, 1.8 * k, 0.45 * k, (120, 85, 55))
    sc.cube(x, 2.4 * k, z, 2.2 * k, 1.6 * k, 2.2 * k, (80, 170, 80))
    sc.cube(x, 3.4 * k, z, 1.4 * k, 1.0 * k, 1.4 * k, (95, 190, 90))


def lamp(sc, x, z):
    sc.cube(x, 2.0, z, 0.18, 4.0, 0.18, (60, 60, 70))
    sc.cube(x - 0.5 * np.sign(x), 4.0, z, 1.1, 0.16, 0.25, (60, 60, 70))
    sc.cube(x - 0.9 * np.sign(x), 3.85, z, 0.4, 0.2, 0.4, (255, 235, 160), outline=False)


def town(sc, lit=False, bakery=True, park=True):
    ground(sc)
    for i, z in enumerate(range(-130, 30, 11)):
        for s2 in (-1, 1):
            zz = z + (4 if s2 > 0 else 0)
            if park and s2 < 0 and -60 < zz < -38:
                continue
            house(sc, 10.5 * s2, zz, i * 2 + (s2 > 0), lit and (i % 3 == 0),
                  sign="BAKERY" if (bakery and s2 > 0 and i == 7) else None)
        lamp(sc, 5.6 * (1 if i % 2 else -1), z + 5)
    if park:
        for (tx, tz) in [(-9, -56), (-13, -50), (-8, -45), (-14, -41), (-11, -59)]:
            tree(sc, tx, tz, 1.1)
        sc.cube(-7, 0.5, -49, 0.6, 0.16, 2.4, (150, 100, 60))
        sc.cube(-7.2, 0.8, -49, 0.12, 0.6, 2.4, (150, 100, 60))
        sc.box(T(-6.3, 1.6, -52) @ RY(math.pi / 2) @ S(2.6, 0.8, 0.12), (255, 255, 255),
               {4: text_dec("PARK", (255, 255, 255), (80, 150, 80), 44, aspect=3.25)})
        sc.cube(-6.3, 0.6, -52, 0.15, 1.2, 0.15, (120, 85, 55))


# ------------------------------------------------------------------ superpositions 2D
def project(cam, p):
    C = cam.to_cam(np.array([p], float))
    if C[0, 2] < 0.2:
        return None
    return cam.proj(C)[0]


def zzz(c, cam, p, t, a=1.0, size=60):
    q = project(cam, p)
    if q is None:
        return
    for i in range(3):
        ph = (t * 0.6 + i / 3) % 1
        x = q[0] + 20 + ph * 60 + i * 8
        y = q[1] - ph * 120
        al = a * math.sin(ph * math.pi)
        fs = font(int(size * (0.6 + 0.5 * ph)))
        stroke = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=6, Color4f=col4((30, 30, 60), al))
        c.drawString("Z", x, y, fs, stroke)
        c.drawString("Z", x, y, fs, skia.Paint(AntiAlias=True, Color4f=col4((255, 255, 255), al)))


def label(c, txt, x, y, size, fg=(255, 255, 255), a=1.0, stroke=10, scale=1.0, align="center"):
    if a <= 0.01 or scale <= 0.01:
        return
    f = font(size)
    w = f.measureText(txt)
    c.save(); c.translate(x, y); c.scale(scale, scale)
    x0 = -w / 2 if align == "center" else 0
    c.drawString(txt, x0, size * 0.35, f, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=stroke,
                                                     StrokeJoin=skia.Paint.kRound_Join, Color4f=col4((20, 20, 30), a)))
    c.drawString(txt, x0, size * 0.35, f, skia.Paint(AntiAlias=True, Color4f=col4(fg, a)))
    c.restore()


def panel(c, x, y, w, h, a=1.0, scale=1.0):
    c.save(); c.translate(x, y); c.scale(scale, scale)
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), 26, 26)
    c.drawRRect(r, skia.Paint(AntiAlias=True, Color4f=col4((25, 25, 40), 0.88 * a)))
    c.drawRRect(r, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=6, Color4f=col4((255, 210, 60), a)))
    c.restore()


# ------------------------------------------------------------------ plans
def shot_town(Tm):
    sc = Scene(); town(sc, lit=False)
    k = Tm.p(0, Tm.dur, ease)
    for i, z in enumerate(range(-90, 30, 22)):
        pass
    cam = Camera((lerp(1.5, 0.5, k), lerp(12, 8.5, k), lerp(22, 14, k)), (0, 1.5, -40), 58)
    L = lerp_light(NIGHT, DAWN, 0.35)

    def ov(c):
        for j, z in enumerate((-8, -19, -30, -41)):
            zzz(c, cam, (10.5 * (1 if j % 2 else -1), 6.2, z + (4 if j % 2 else 0)), Tm.t + j * 0.3, 1.0, 64)
    return sc, cam, L, dict(stars=0.6, moon=(820, 300, 46)), ov


def shot_except(Tm):
    sc = Scene(); town(sc, lit=False)
    character(sc, 5.0, 6.0, -math.pi / 2 + 0.3, MILO, face="smile" if Tm.t < Tm.c(0) + 0.5 else "happy")
    k = Tm.p(0, Tm.dur, ease)
    cam = Camera((lerp(0.6, 1.4, k), 2.3, lerp(8.6, 7.6, k)), (5.0, 1.85, 6.0), 42)
    return sc, cam, lerp_light(NIGHT, DAWN, 0.45), dict(stars=0.4, moon=(840, 260, 40)), None


def run_x(t):
    return 1.6


def shot_run_start(Tm):
    sc = Scene(); town(sc, lit=False)
    sp = 4.2
    z = 9.5 - sp * max(0, Tm.t - 0.8)
    x = lerp(3.8, 1.6, clamp((Tm.t - 0.8) / 1.0))
    run = clamp((Tm.t - 0.6) / 0.4)
    character(sc, x, z, math.pi if Tm.t > 0.8 else -0.35, MILO, run=run, phase=Tm.t * 9, face="focus")
    cam = Camera((x - 2.6, 2.6, z + 6.5), (x, 1.6, z - 2), 50)

    def ov(c):
        k = Tm.pc(0, 0.4, f=eback)
        panel(c, W / 2, 330, 420, 170, k, k)
        label(c, "5:00 AM", W / 2, 330, 96, (255, 220, 80), k, scale=k)
    return sc, cam, lerp_light(NIGHT, DAWN, 0.55), dict(stars=0.3, moon=(860, 250, 40)), ov


def shot_run_past(Tm):
    sc = Scene(); town(sc, lit=False)
    sp = 5.2
    z = -12 - sp * Tm.t
    character(sc, 1.6, z, math.pi, MILO, run=1, phase=Tm.t * 10, face="focus")
    # M. Bob endormi sur sa chaise de porche
    bz = -70
    sc.cube(-6.2, 0.45, bz, 1.2, 0.9, 1.2, (170, 110, 70))
    sc.cube(-6.8, 1.2, bz, 0.2, 1.6, 1.2, (170, 110, 70))
    character(sc, -6.0, bz, math.pi / 2, BOB, face="sleep", scale=0.95, y0=0.5, sleeping=True,
              arms=(-0.3, -0.3))
    cam = Camera((4.8, 2.5, z + 5.0), (0.6, 1.5, z - 5), 52)

    def ov(c):
        zzz(c, cam, (-6.0, 2.9, bz), Tm.t, 1.0, 56)
    return sc, cam, lerp_light(NIGHT, DAWN, 0.65), dict(stars=0.2), ov


def bedroom(sc, wall=(170, 200, 240), floor=(200, 160, 120), blanket=(240, 110, 110)):
    sc.flats.append(([(-4, 0, -4), (4, 0, -4), (4, 0, 4), (-4, 0, 4)], floor))
    sc.flats.append(([(-4, 0, -4), (4, 0, -4), (4, 5, -4), (-4, 5, -4)], wall))
    sc.flats.append(([(-4, 0, -4), (-4, 0, 4), (-4, 5, 4), (-4, 5, -4)], tuple(v * 0.9 for v in wall)))
    sc.box(T(1.5, 2.8, -3.83) @ S(1.6, 1.4, 0.06), (255, 255, 255), {4: window_dec(False)}, outline=False)
    sc.cube(-1.2, 0.35, -1.4, 2.4, 0.7, 4.2, (150, 100, 70))
    sc.cube(-1.2, 0.82, -1.4, 2.2, 0.24, 4.0, (250, 250, 250))
    sc.cube(-1.2, 1.0, -3.0, 1.4, 0.3, 0.7, (255, 255, 255))
    sc.cube(-1.2, 1.0, -0.6, 2.25, 0.3, 2.6, blanket)
    sc.cube(2.6, 0.5, -3.2, 1.0, 1.0, 1.0, (180, 130, 90))


def sleeper(sc, x, y, z, st):
    """Tête posée sur l'oreiller, couchée sur le côté, visage tourné vers +x (vers la caméra)."""
    def face_dec(c, sh, fog):
        draw_face(c, "sleep", st, True)
    head = T(x, y, z) @ RY(math.pi / 2) @ RZ(0.0)
    sc.box(head @ S(0.84, 0.8, 0.8), st.get("skin", (232, 190, 150)), {4: face_dec})
    if st.get("hat") == "nightcap":
        sc.box(head @ T(0, 0.42, 0) @ S(0.88, 0.22, 0.86), st["hat_col"])
        sc.box(head @ T(0.1, 0.62, -0.1) @ RZ(-0.5) @ S(0.4, 0.34, 0.4), st["hat_col"])
        sc.box(head @ T(0.36, 0.78, -0.14) @ S(0.16, 0.16, 0.16), (255, 255, 255))
    else:
        sc.box(head @ T(0, 0.38, -0.05) @ S(0.9, 0.18, 0.86), st.get("hair", (60, 40, 30)))
        sc.box(head @ T(0, 0.0, -0.45) @ S(0.9, 0.84, 0.14), st.get("hair", (60, 40, 30)))
    if st.get("mask"):
        sc.box(head @ T(0, 0.08, 0.41) @ S(0.84, 0.16, 0.03), (90, 120, 230), outline=False)


def shot_bed(Tm, who, blanket):
    sc = Scene()
    bedroom(sc, blanket=blanket)
    sleeper(sc, -1.2, 1.5, -2.85, who)
    k = Tm.p(0, Tm.dur, ease)
    cam = Camera((lerp(2.3, 1.7, k), lerp(2.6, 2.4, k), lerp(-1.2, -1.6, k)), (-1.1, 1.3, -2.7), 46)
    L = Light((30, 40, 80), (60, 70, 120), 0.8, (0.3, 0.8, 0.5), (0.7, 0.75, 1.0), (40, 50, 90), 30, 90, (0.8, 0.85, 1.0))

    def ov(c):
        zzz(c, cam, (-1.0, 2.1, -3.1), Tm.t, 1.0, 80)
    return sc, cam, L, dict(), ov


def dog(sc, x, z, ry=0.0, sleeping=True, run=0.0, phase=0.0):
    base = T(x, 0, z) @ RY(ry)
    col = (220, 170, 110)
    sw = math.sin(phase) * 0.6 * run
    for dx, dz, a in ((-0.25, 0.4, sw), (0.25, 0.4, -sw), (-0.25, -0.4, -sw), (0.25, -0.4, sw)):
        sc.box(base @ T(dx, 0.35, dz) @ RX(a) @ T(0, -0.15, 0) @ S(0.2, 0.4 if not sleeping else 0.2, 0.2), col)
    by = 0.62 if not sleeping else 0.32
    sc.box(base @ T(0, by, 0) @ S(0.7, 0.5, 1.2), col)

    def face_dec(c, sh, fog):
        draw_face(c, "sleep" if sleeping else "happy", {}, sleeping)
        c.drawOval(skia.Rect.MakeLTRB(40, 58, 60, 70), skia.Paint(AntiAlias=True, Color4f=col4((40, 30, 30))))
    head = base @ T(0, by + 0.25, 0.75)
    sc.box(head @ S(0.62, 0.58, 0.55), col, {4: face_dec})
    for s2 in (-1, 1):
        sc.box(head @ T(0.3 * s2, 0.12, -0.05) @ S(0.14, 0.42, 0.3), (160, 110, 70))
    sc.box(base @ T(0, by + 0.15, -0.7) @ RX(0.7 + 0.3 * math.sin(phase * 2)) @ S(0.12, 0.12, 0.5), col)
    sc.shadow(x, z, 0.7)


def shot_dog(Tm):
    sc = Scene()
    sc.flats.append(([(-4, 0, -4), (4, 0, -4), (4, 0, 4), (-4, 0, 4)], (200, 160, 120)))
    sc.flats.append(([(-4, 0, -2), (4, 0, -2), (4, 5, -2), (-4, 5, -2)], (240, 210, 170)))
    sc.cube(0, 0.08, 0, 2.4, 0.16, 2.0, (230, 90, 90))
    dog(sc, 0, 0, 0.0, True)
    k = Tm.p(0, Tm.dur, ease)
    cam = Camera((lerp(1.6, 1.2, k), 1.6, lerp(3.4, 2.8, k)), (0, 0.5, 0.2), 46)
    L = Light((30, 40, 80), (60, 70, 120), 0.82, (0.3, 0.8, 0.5), (0.7, 0.75, 1.0), (40, 50, 90), 30, 90, (0.8, 0.85, 1.0))

    def ov(c):
        zzz(c, cam, (0, 1.0, 0.8), Tm.t, 1.0, 56)
    return sc, cam, L, dict(), ov


def shot_montage(Tm):
    sc = Scene(); town(sc)
    day = 1 + int(299 * clamp(Tm.t / Tm.dur) ** 1.6)
    sky_k = (Tm.t * 0.9) % 1.0
    z = -20 - 6 * Tm.t
    character(sc, 1.6, z, math.pi, MILO, run=1, phase=Tm.t * 11, face="focus")
    cam = Camera((-1.6, 1.4, z - 4.5), (1.6, 1.9, z), 50)
    L = lerp_light(DAWN, DAY, 0.3 + 0.5 * math.sin(sky_k * math.pi))

    def ov(c):
        panel(c, W / 2, 330, 440, 160, 1, 1)
        label(c, f"DAY {day}", W / 2, 330, 92, (255, 220, 80))
    return sc, cam, L, dict(sun=(300 + 300 * sky_k, 700 - 300 * math.sin(sky_k * math.pi), 50)), ov


# --- course
def race_world(sc, crowd_run=0.0, t=0.0, milo_z=None, finish=False, crowd_face="laugh", milo_face="smile",
               crowd_z_shift=0.0):
    sc.flats.append(([(-60, 0, -150), (60, 0, -150), (60, 0, 40), (-60, 0, 40)], (110, 175, 90)))
    sc.flats.append(([(-5, 0.01, -150), (5, 0.01, -150), (5, 0.01, 40), (-5, 0.01, 40)], (215, 95, 70)))
    for lx in (-3, -1, 1, 3):
        sc.flats.append(([(lx - 0.06, 0.02, -150), (lx + 0.06, 0.02, -150), (lx + 0.06, 0.02, 40), (lx - 0.06, 0.02, 40)],
                         (250, 250, 250)))
    sc.flats.append(([(-5, 0.03, -0.2), (5, 0.03, -0.2), (5, 0.03, 0.2), (-5, 0.03, 0.2)], (250, 250, 250)))
    for zz, txt, cc in ((0, "SUNRISE RACE", (250, 140, 40)), (-110, "FINISH", (60, 160, 90))):
        for s2 in (-1, 1):
            sc.cube(5.6 * s2, 2.6, zz, 0.3, 5.2, 0.3, (240, 240, 240))
        sc.box(T(0, 5.0, zz) @ S(11.4, 1.4, 0.25), (255, 255, 255), {4: text_dec(txt, (255, 255, 255), cc, 34, aspect=11.4 / 1.4)})
        for i in range(14):
            sc.cube(-5.2 + i * 0.8, 4.05, zz + 0.05, 0.4, 0.45, 0.05,
                    [(240, 80, 80), (250, 200, 60), (80, 170, 240), (120, 210, 110)][i % 4], outline=False)
    # gradins + spectateurs
    for row in range(4):
        sc.cube(10 + row * 1.2, 0.4 + row * 0.6, -14, 1.2, 0.8 + row * 1.2, 26, (180, 185, 195))
        for i in range(9):
            st = PJ[(i + row * 3) % len(PJ)]
            character(sc, 10 + row * 1.2, -24 + i * 2.4, -math.pi / 2, st, face=crowd_face, y0=0.8 + row * 1.2,
                      scale=0.85, arms=(-2.6 + 0.4 * math.sin(t * 6 + i), -2.6 + 0.4 * math.cos(t * 6 + i))
                      if crowd_face in ("laugh", "happy") and (i + row) % 3 == 0 else None)
    # coureurs en pyjama
    for i in range(6):
        st = PJ[i % len(PJ)]
        x = -4 + i * 1.6
        zz = -1.2 - (i % 2) * 1.2 - crowd_run * (2.2 + 0.4 * (i % 3)) * max(0, t) + crowd_z_shift
        character(sc, x, zz, math.pi if crowd_run > 0 else 0.0, st, run=0.6 * crowd_run, phase=t * 6 + i,
                  face=crowd_face, scale=0.95)
    if milo_z is not None:
        pass


def shot_race_intro(Tm):
    sc = Scene(); race_world(sc, t=Tm.t, crowd_face="happy")
    k = Tm.p(0, Tm.dur, ease)
    cam = Camera((lerp(-2, 2, k), lerp(9, 6, k), lerp(16, 11, k)), (0, 3.2, -2), 55)
    return sc, cam, DAY, dict(sun=(820, 360, 55)), None


def shot_laugh(Tm):
    sc = Scene(); race_world(sc, t=Tm.t, crowd_face="laugh" if Tm.t > Tm.c(1) else "happy")
    walk = Tm.p(Tm.c(1) - 0.2, 1.6, ease)
    character(sc, lerp(-7, -0.4, walk), lerp(4, 0.6, walk), math.pi * 0.85 if walk < 1 else math.pi, MILO,
              run=0.5 if 0 < walk < 1 else 0, phase=Tm.t * 7, face="smile")
    if Tm.t < Tm.c(2) - 0.1:
        cam = Camera((-6, 3.0, 9), (-0.5, 1.5, -1), 52)
    else:  # gros plan sur un rieur
        cam = Camera((-3.5, 1.9, 1.6), (-4, 1.7, -1.2), 40)

    def ov(c):
        if Tm.t > Tm.c(2) - 0.1:
            q = project(cam, (-4, 2.9, -1.2))
            if q is not None:
                label(c, "HA HA!", q[0] + 160, q[1] - 160, 80, (255, 230, 90), Tm.pc(2, 0.3), scale=eback(Tm.pc(2, 0.3)))
    return sc, cam, DAY, dict(sun=(820, 360, 55)), ov


def shot_horn(Tm):
    sc = Scene(); race_world(sc, t=Tm.t, crowd_face="wide")
    character(sc, -0.4, 0.6, math.pi, MILO, face="focus")
    cam = Camera((0.8, 1.6, 4.6), (-0.4, 1.75, 0.6), 38)

    def ov(c):
        st = Tm.t - (Tm.s["chunks"][-1]["end"] - Tm.s["start"])
        if st > 0.05:
            k = clamp(st / 0.18)
            c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Color4f=col4((255, 255, 255), 0.35 * (1 - clamp(st / 0.4)))))
            label(c, "BWAAAP!", W / 2, 760, 150, (255, 255, 255), 1, scale=eback(k), stroke=14)
    return sc, cam, DAY, dict(sun=(820, 360, 55)), ov


def shot_sprint(Tm):
    sc = Scene()
    t = Tm.t
    race_world(sc, crowd_run=1, t=t * 0.6, crowd_face="wide")
    mz = -6.0 - 9.0 * t
    character(sc, -0.4, mz, math.pi, MILO, run=1.0, phase=t * 14, face="focus")
    cam = Camera((-2.4, 1.7, mz - 4.6), (-0.3, 1.7, mz + 1.5), 56)

    def ov(c):
        for i, (tt, lab) in enumerate(Tm.s.get("sfx_items", [])):
            k = (Tm.t - tt)
            if 0 < k < 0.55:
                label(c, "ZOOM!", W / 2 + (i % 2 * 2 - 1) * 120, 700 + i * 60, 140, (255, 255, 255), 1 - clamp((k - 0.4) / 0.15),
                      scale=eback(clamp(k / 0.15)), stroke=14)
    return sc, cam, DAY, dict(sun=(820, 360, 55)), ov


def shot_finish(Tm):
    sc = Scene()
    race_world(sc, crowd_run=0, t=Tm.t, crowd_face="wide", crowd_z_shift=-80)
    k = Tm.p(0, 1.0, ease)
    mz = lerp(-104, -114, k)
    character(sc, -0.4, mz, math.pi, MILO, run=1 - k, phase=Tm.t * 12,
              face="happy", arms=(-2.8, -2.8) if k >= 1 else None)
    cam = Camera((2.0, 2.4, -121), (-0.4, 2.2, -110), 52)

    def ov(c):
        kk = Tm.pc(0, 0.45, f=eback, delay=0.2)
        panel(c, W / 2, 360, 620, 300, min(1, kk), kk)
        label(c, "1ST", W / 2, 320, 150, (255, 210, 60), min(1, kk), scale=kk)
        label(c, "+1:00", W / 2, 440, 70, (255, 255, 255), Tm.pc(1, 0.3), scale=kk)
    return sc, cam, DAY, dict(sun=(820, 360, 55)), ov


def shot_silence(Tm):
    sc = Scene()
    race_world(sc, crowd_run=0, t=0, crowd_face="wide", crowd_z_shift=-104)
    walk = Tm.p(Tm.c(1) - 0.3, 1.4, ease)
    character(sc, lerp(3.5, 1.0, walk), lerp(-104, -112.5, walk), math.pi * (1 - 0.1 * walk), LEO,
              run=0.5 if 0 < walk < 1 else 0, phase=Tm.t * 7, face="talk" if Tm.t > Tm.c(2) else "wide")
    character(sc, -0.4, -114, 0.25, MILO, face="smile")
    if Tm.t < Tm.c(1) - 0.3:
        cam = Camera((0, 6, -96), (2, 1.5, -106), 50)
    else:
        cam = Camera((4.2, 2.3, -109.2), (0.2, 1.8, -113.4), 46)
    return sc, cam, DAY, dict(sun=(820, 360, 55)), None


def shot_truth(Tm):
    sc = Scene()
    race_world(sc, crowd_run=0, t=0, crowd_face="wide", crowd_z_shift=-104)
    character(sc, 1.0, -112.5, math.pi * 0.9, LEO, face="wide")
    character(sc, -0.4, -114, 0.25, MILO, face="proud" if Tm.t > Tm.c(1) else "smile")
    k = Tm.p(0, Tm.dur, ease)
    cam = Camera((lerp(0.8, 0.4, k), 2.25, lerp(-110.3, -111.2, k)), (-0.4, 2.15, -114), 40)
    return sc, cam, DAY, dict(sun=(820, 360, 55)), None


DOOR = (7.47, 6.0)


def shot_door(Tm):
    sc = Scene(); town(sc)
    k = Tm.pc(1, 0.8, f=ease)
    dx, dz = DOOR
    sc.box(T(dx - 0.05, 1.1, dz) @ RY(math.pi / 2) @ S(1.2, 2.2, 0.06), (25, 20, 30), outline=False)
    sc.box(T(dx - 0.1, 1.1, dz - 0.6) @ RY(-k * 1.6) @ T(0, 0, 0.6) @ RY(math.pi / 2) @ S(1.2, 2.2, 0.1),
           (120, 80, 60))
    step = Tm.pc(1, 0.9, f=ease, delay=0.3)
    if step > 0:
        character(sc, lerp(dx + 0.2, dx - 1.4, step), dz, -math.pi / 2, MILO, run=0.4 * (step < 1), phase=Tm.t * 8,
                  face="smile")
    zz = Tm.p(0, Tm.dur, ease)
    cam = Camera((lerp(0.5, 1.5, zz), 2.0, lerp(10.5, 9.5, zz)), (dx, 1.5, dz), 50)
    return sc, cam, DAWN, dict(sun=(200, 900, 50)), None


def shot_crowd(Tm):
    sc = Scene(); town(sc)
    for i in range(14):
        st = SPORT[i % len(SPORT)] if i not in (3, 7, 10) else [LEO, ROSA, BOB][(3, 7, 10).index(i)]
        x = 3.2 - (i // 7) * 1.5
        z = 2.4 + (i % 7) * 1.25
        wave = (-2.8 + 0.4 * math.sin(Tm.t * 7 + i), -0.2) if (i % 3 == 0 and Tm.t > Tm.c(1)) else None
        character(sc, x, z, math.pi / 2 * 0.9, st, face="happy", arms=wave)
    dog(sc, 4.4, 4.0, math.pi / 2, sleeping=False, phase=Tm.t * 6)
    character(sc, DOOR[0] - 1.4, DOOR[1], -math.pi / 2, MILO, face="wide" if Tm.t < Tm.c(1) + 0.4 else "happy",
              arms=(-2.8, -2.8) if Tm.t > Tm.c(1) + 0.4 else None)
    k = Tm.p(0, Tm.dur, ease)
    cam = Camera((lerp(-1.5, -3.5, k), lerp(7.5, 9.0, k), lerp(6.5, 6.0, k)), (5.2, 1.4, 6.0), 52)
    return sc, cam, DAWN, dict(sun=(250, 900, 55)), None


SHOTS = {}
SCENES = [
    dict(say=["In this town, everybody sleeps until noon."], shot=shot_town),
    dict(say=["Except me."], shot=shot_except),
    dict(say=["Every morning at five, while the whole town is snoring, I go running."], shot=shot_run_start),
    dict(say=["Past the bakery.", "Past the park.", "Past Mister Bob, asleep on his porch."], shot=shot_run_past),
    dict(say=["My best friend Leo sleeps until noon."], shot=lambda Tm: shot_bed(Tm, LEO, (120, 200, 150))),
    dict(say=["My neighbor Rosa sleeps until noon."], shot=lambda Tm: shot_bed(Tm, ROSA, (250, 150, 190))),
    dict(say=["Even my dog sleeps until noon."], shot=shot_dog),
    dict(say=["But not me.", "Day after day."], shot=shot_montage, sfx=[("TAP!", 0.25), ("TAP!", 0.6), ("TAP!", 0.95)],
         pause=1.2),
    dict(say=["Then came the biggest day of the year.", "The Sunrise Race."], shot=shot_race_intro),
    dict(say=["Everybody showed up in pajamas.", "When I got to the start line, everybody laughed.",
              "“Who's the kid with the headphones?”"], shot=shot_laugh),
    dict(say=["Then the horn went off."], shot=shot_horn, sfx=[("BWAAAP!", 0.1)], pause=0.9),
    dict(say=[], shot=shot_sprint, sfx=[("ZOOM!", 0.1), ("ZOOM!", 0.7), ("ZOOM!", 1.3)], silent=2.0),
    dict(say=["First place.", "By a full minute."], shot=shot_finish),
    dict(say=["Everybody went silent.", "Leo walked up to me and asked,", "“When did you get so fast?”"],
         shot=shot_silence, no_music=True),
    dict(say=["I told him the truth.", "While you were sleeping."], shot=shot_truth, no_music=True, pause=0.4),
    dict(say=["The next morning, at five,", "I opened my door…"], shot=shot_door),
    dict(say=["and the whole town was outside.", "Waiting for me."], shot=shot_crowd, pause=1.0),
]
