"""Mini moteur 3D « blocs » (rendu skia) : boîtes ombrées, caméra perspective, ciel, brouillard,
ombres portées simples et décors dessinés sur les faces (visages, panneaux)."""
import math
import numpy as np
import skia

W, H = 1080, 1920


# ------------------------------------------------------------------ matrices
def T(x, y, z):
    m = np.eye(4); m[:3, 3] = (x, y, z); return m


def RX(a):
    c, s = math.cos(a), math.sin(a)
    m = np.eye(4); m[1, 1] = c; m[1, 2] = -s; m[2, 1] = s; m[2, 2] = c; return m


def RY(a):
    c, s = math.cos(a), math.sin(a)
    m = np.eye(4); m[0, 0] = c; m[0, 2] = s; m[2, 0] = -s; m[2, 2] = c; return m


def RZ(a):
    c, s = math.cos(a), math.sin(a)
    m = np.eye(4); m[0, 0] = c; m[0, 1] = -s; m[1, 0] = s; m[1, 1] = c; return m


def S(x, y, z):
    m = np.eye(4); m[0, 0] = x; m[1, 1] = y; m[2, 2] = z; return m


# cube unité centré : 8 sommets, 6 faces (indices, normale)
CV = np.array([[x, y, z, 1] for x in (-.5, .5) for y in (-.5, .5) for z in (-.5, .5)], float)
FACES = [((1, 3, 7, 5), (0, 0, 1, 0)) if False else None]
FACES = [
    ((4, 6, 7, 5), (1, 0, 0)),   # +x
    ((0, 1, 3, 2), (-1, 0, 0)),  # -x
    ((2, 3, 7, 6), (0, 1, 0)),   # +y
    ((0, 4, 5, 1), (0, -1, 0)),  # -y
    ((1, 5, 7, 3), (0, 0, 1)),   # +z (avant)
    ((0, 2, 6, 4), (0, 0, -1)),  # -z
]


class Scene:
    def __init__(self):
        self.boxes = []      # (matrice monde, couleur, decals{face: fn}, outline)
        self.shadows = []    # (x, z, rx, rz, alpha)
        self.flats = []      # quads au sol / murs : (4 pts monde, couleur)

    def box(self, M, color, decals=None, outline=True):
        self.boxes.append((M, color, decals or {}, outline))

    def cube(self, x, y, z, sx, sy, sz, color, ry=0.0, decals=None, outline=True):
        self.box(T(x, y, z) @ RY(ry) @ S(sx, sy, sz), color, decals, outline)

    def shadow(self, x, z, r=0.6, a=0.35):
        self.shadows.append((x, z, r, r * 0.8, a))


class Camera:
    def __init__(self, pos, target, fov=55):
        self.pos = np.array(pos, float)
        f = np.array(target, float) - self.pos
        f /= np.linalg.norm(f)
        r = np.cross(f, [0, 1, 0]); r /= np.linalg.norm(r)
        u = np.cross(r, f)
        self.R = np.stack([r, u, f])          # lignes : droite, haut, avant
        self.f = (H / 2) / math.tan(math.radians(fov) / 2)

    def to_cam(self, P):
        return (P - self.pos) @ self.R.T

    def proj(self, C):
        return np.stack([W / 2 + self.f * C[:, 0] / C[:, 2], H / 2 - self.f * C[:, 1] / C[:, 2]], 1)


def clip_near(C, near=0.15):
    out = []
    n = len(C)
    for i in range(n):
        a, b = C[i], C[(i + 1) % n]
        ia, ib = a[2] >= near, b[2] >= near
        if ia:
            out.append(a)
        if ia != ib:
            t = (near - a[2]) / (b[2] - a[2])
            out.append(a + (b - a) * t)
    return np.array(out) if len(out) >= 3 else None


def mix(c1, c2, k):
    return tuple(c1[i] * (1 - k) + c2[i] * k for i in range(3))


class Light:
    def __init__(self, sky_top, sky_bot, ambient, sun_dir, sun_col, fog_col, fog_start=25, fog_end=90, amb_col=(1, 1, 1)):
        self.sky_top, self.sky_bot = sky_top, sky_bot
        self.ambient, self.amb_col = ambient, amb_col
        d = np.array(sun_dir, float); self.sun_dir = d / np.linalg.norm(d)
        self.sun_col = sun_col
        self.fog_col, self.fog_start, self.fog_end = fog_col, fog_start, fog_end


def lerp_light(a, b, k):
    f = lambda x, y: tuple(np.array(x) * (1 - k) + np.array(y) * k) if isinstance(x, tuple) else x * (1 - k) + y * k
    return Light(f(a.sky_top, b.sky_top), f(a.sky_bot, b.sky_bot), f(a.ambient, b.ambient),
                 tuple(a.sun_dir * (1 - k) + b.sun_dir * k), f(a.sun_col, b.sun_col), f(a.fog_col, b.fog_col),
                 f(a.fog_start, b.fog_start), f(a.fog_end, b.fog_end), f(a.amb_col, b.amb_col))


NIGHT = Light((14, 20, 48), (40, 52, 98), 0.66, (0.3, 0.8, 0.4), (0.55, 0.62, 0.9), (34, 44, 86), 20, 80,
              (0.62, 0.7, 1.0))
DAWN = Light((70, 90, 170), (250, 170, 130), 0.84, (-0.5, 0.45, 0.6), (1.05, 0.82, 0.65), (230, 170, 150), 25, 95,
             (0.85, 0.82, 0.95))
DAY = Light((90, 160, 235), (190, 225, 250), 0.86, (0.4, 0.85, 0.35), (1.0, 0.97, 0.9), (190, 220, 245), 35, 120)


def col4(rgb, a=1.0):
    return skia.Color4f(min(1, rgb[0] / 255), min(1, rgb[1] / 255), min(1, rgb[2] / 255), a)


def draw_sky(c, L, t=0.0, moon=None, sun=None, stars=0.0):
    sh = skia.GradientShader.MakeLinear([(0, 0), (0, H * 0.62)], [col4(L.sky_top).toColor(), col4(L.sky_bot).toColor()])
    c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Shader=sh))
    if stars > 0:
        rng = np.random.default_rng(7)
        for i in range(120):
            x, y = rng.uniform(0, W), rng.uniform(0, H * 0.45)
            a = stars * (0.4 + 0.4 * math.sin(t * 2 + i))
            c.drawCircle(x, y, rng.uniform(1, 2.6), skia.Paint(AntiAlias=True, Color4f=col4((255, 255, 255), a)))
    if moon:
        x, y, r = moon
        c.drawCircle(x, y, r * 2.2, skia.Paint(AntiAlias=True, Color4f=col4((200, 210, 255), 0.12),
                                               MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 30)))
        c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Color4f=col4((250, 250, 240))))
    if sun:
        x, y, r = sun
        c.drawCircle(x, y, r * 3, skia.Paint(AntiAlias=True, Color4f=col4((255, 200, 120), 0.35),
                                             MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 60)))
        c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Color4f=col4((255, 235, 170))))


def render(c, scene, cam, L):
    polys = []
    # sol / quads plats
    for pts, color in scene.flats:
        P = np.array(pts, float)
        C = cam.to_cam(P)
        Cc = clip_near(C)
        if Cc is None:
            continue
        n = np.cross(P[1] - P[0], P[2] - P[0]); n /= (np.linalg.norm(n) + 1e-9)
        polys.append((Cc[:, 2].mean() + 0.5, Cc, color, n, None, "flat", None))
    # boîtes
    for (M, color, decals, outline) in scene.boxes:
        V = (CV @ M.T)[:, :3]
        Cv = cam.to_cam(V)
        if np.all(Cv[:, 2] < 0.15):
            continue
        for fi, (idx, nrm) in enumerate(FACES):
            n = M[:3, :3] @ np.array(nrm, float)
            n /= np.linalg.norm(n)
            center = V[list(idx)].mean(0)
            if np.dot(n, cam.pos - center) <= 0:
                continue
            Cf = Cv[list(idx)]
            Cc = Cf if np.all(Cf[:, 2] >= 0.15) else clip_near(Cf)
            if Cc is None:
                continue
            dec = decals.get(fi)
            # les dessus (tables, lits, gradins) passent avant ce qui est posé dessus
            key = Cc[:, 2].max() + 0.05 if n[1] > 0.7 else Cc[:, 2].mean()
            polys.append((key, Cc, color, n, dec, outline, Cv[[1, 3, 7, 5]] if dec else None))
    flats = sorted([p for p in polys if p[4] is None and p[5] == "flat"], key=lambda p: -p[0])
    boxes = sorted([p for p in polys if not (p[4] is None and p[5] == "flat")], key=lambda p: -p[0])
    polys = flats + [None] + boxes
    for item in polys:
        if item is None:
            draw_shadows(c, scene, cam)
            continue
        depth, Cc, color, n, dec, outline, Cf = item
        sh = L.ambient + max(0.0, float(np.dot(n, L.sun_dir))) * (1 - L.ambient) * 1.15
        d = max(0.0, float(np.dot(n, L.sun_dir)))
        rgb = tuple(color[i] * (L.ambient * L.amb_col[i] + d * L.sun_col[i] * 0.42) for i in range(3))
        fog = min(1.0, max(0.0, (depth - L.fog_start) / (L.fog_end - L.fog_start)))
        rgb = mix(rgb, L.fog_col, fog * 0.85)
        pts = cam.proj(Cc)
        path = skia.Path()
        path.addPoly([skia.Point(float(x), float(y)) for x, y in pts], True)
        c.drawPath(path, skia.Paint(AntiAlias=True, Color4f=col4(rgb)))
        if outline is True:
            c.drawPath(path, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=1.6,
                                        Color4f=col4(mix(rgb, (0, 0, 0), 0.35), 0.55)))
        if dec is not None and Cf is not None and np.all(Cf[:, 2] > 0.15):
            q = cam.proj(Cf)
            m = skia.Matrix()
            ok = m.setPolyToPoly([skia.Point(0, 100), skia.Point(0, 0), skia.Point(100, 0), skia.Point(100, 100)],
                                 [skia.Point(float(x), float(y)) for x, y in q])
            c.save(); c.concat(m)
            dec(c, sh, fog)
            c.restore()


def draw_shadows(c, scene, cam):
    for (x, z, rx, rz, a) in scene.shadows:
        pts = []
        for k in range(16):
            t = k * 2 * math.pi / 16
            pts.append((x + rx * math.cos(t), 0.02, z + rz * math.sin(t)))
        C = cam.to_cam(np.array(pts))
        if np.any(C[:, 2] < 0.2):
            continue
        P = cam.proj(C)
        path = skia.Path(); path.addPoly([skia.Point(float(px), float(py)) for px, py in P], True)
        c.drawPath(path, skia.Paint(AntiAlias=True, Color4f=col4((0, 0, 20), a),
                                    MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 4)))


# ------------------------------------------------------------------ personnages
def character(sc, x, z, ry=0.0, style=None, run=0.0, phase=0.0, face="smile", arms=None, scale=1.0, y0=0.0,
              sleeping=False, lie=False):
    """Personnage en blocs. run = amplitude de course (0..1), phase = position dans le cycle."""
    st = dict(skin=(232, 190, 150), top=(240, 120, 40), pants=(60, 70, 110), shoes=(250, 250, 250),
              hat=None, hat_col=(250, 250, 250), headphones=False, hair=(60, 40, 30), mask=False, glasses=False)
    st.update(style or {})
    sw = math.sin(phase) * 0.75 * run
    bob = abs(math.sin(phase)) * 0.08 * run
    base = T(x, y0, z) @ RY(ry) @ S(scale, scale, scale)
    if lie:
        base = base @ T(0, 0.35, 0) @ RX(-math.pi / 2) @ T(0, -0.35, 0)
    lean = RX(0.18 * run)
    root = base @ T(0, bob, 0)
    # jambes
    for sgn, a in ((-1, sw), (1, -sw)):
        leg = root @ T(0.17 * sgn, 0.72, 0) @ RX(a) @ T(0, -0.36, 0)
        sc.box(leg @ S(0.3, 0.72, 0.32), st["pants"])
        sc.box(leg @ T(0, -0.36, 0.05) @ S(0.32, 0.14, 0.42), st["shoes"])
    body = root @ T(0, 0.72, 0) @ lean
    sc.box(body @ T(0, 0.4, 0) @ S(0.68, 0.8, 0.4), st["top"])
    # bras
    for sgn, a in ((-1, -sw), (1, sw)):
        ang = a if arms is None else arms[0 if sgn < 0 else 1]
        arm = body @ T(0.45 * sgn, 0.74, 0) @ RX(ang) @ RZ(-0.08 * sgn) @ T(0, -0.33, 0)
        sc.box(arm @ S(0.24, 0.7, 0.28), st["top"])
        sc.box(arm @ T(0, -0.4, 0) @ S(0.22, 0.14, 0.24), st["skin"])
    head = body @ T(0, 0.8 + 0.42, 0)
    expr = face

    def face_dec(c, sh, fog, expr=expr, st=st):
        draw_face(c, expr, st, sleeping)
    sc.box(head @ S(0.84, 0.8, 0.8), st["skin"], {4: face_dec})
    if st["hair"] is not None and st["hat"] is None:
        sc.box(head @ T(0, 0.36, -0.04) @ S(0.88, 0.16, 0.86), st["hair"])
    if st["hat"] == "beanie":
        sc.box(head @ T(0, 0.38, 0) @ S(0.9, 0.24, 0.86), st["hat_col"])
        sc.box(head @ T(0, 0.56, 0) @ S(0.22, 0.14, 0.22), st["hat_col"])
    elif st["hat"] == "nightcap":
        sc.box(head @ T(0, 0.42, 0) @ S(0.88, 0.2, 0.86), st["hat_col"])
        sc.box(head @ T(0.12, 0.62, -0.08) @ RZ(-0.5) @ S(0.4, 0.34, 0.4), st["hat_col"])
        sc.box(head @ T(0.38, 0.78, -0.12) @ S(0.16, 0.16, 0.16), (250, 250, 250))
    elif st["hat"] == "hood":
        sc.box(head @ T(0, 0.12, -0.1) @ S(0.98, 0.96, 0.82), st["top"])
    if st["headphones"]:
        for sgn in (-1, 1):
            sc.box(head @ T(0.47 * sgn, 0.0, 0) @ S(0.14, 0.34, 0.34), (245, 245, 245))
        sc.box(head @ T(0, 0.46, 0) @ S(1.02, 0.08, 0.12), (245, 245, 245))
    if st["mask"]:
        sc.box(head @ T(0, 0.1, 0.405) @ S(0.8, 0.18, 0.02), (90, 120, 230), outline=False)
    sc.shadow(x, z, 0.55 * scale)


def draw_face(c, expr, st, sleeping=False):
    """Visage dessiné dans un carré 0..100 (face avant de la tête)."""
    ink = skia.Paint(AntiAlias=True, Color4f=col4((30, 25, 30)))
    white = skia.Paint(AntiAlias=True, Color4f=col4((255, 255, 255)))
    blush = skia.Paint(AntiAlias=True, Color4f=col4((240, 120, 120), 0.45))
    c.drawOval(skia.Rect.MakeLTRB(12, 60, 30, 70), blush)
    c.drawOval(skia.Rect.MakeLTRB(70, 60, 88, 70), blush)
    stroke = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=4.5, StrokeCap=skia.Paint.kRound_Cap,
                        Color4f=col4((30, 25, 30)))
    if sleeping or expr == "sleep":
        for ex in (33, 67):
            p = skia.Path(); p.moveTo(ex - 9, 46); p.quadTo(ex, 52, ex + 9, 46); c.drawPath(p, stroke)
        c.drawOval(skia.Rect.MakeLTRB(44, 70, 56, 78), ink)
        return
    if expr in ("smile", "happy", "talk", "focus", "proud"):
        for ex in (33, 67):
            c.drawOval(skia.Rect.MakeLTRB(ex - 7, 36, ex + 7, 54), ink)
            c.drawCircle(ex + 2.5, 41, 2.6, white)
    elif expr == "wide":
        for ex in (33, 67):
            c.drawCircle(ex, 44, 11, white); c.drawCircle(ex, 44, 11, stroke); c.drawCircle(ex, 45, 5, ink)
    elif expr == "laugh":
        for ex in (33, 67):
            p = skia.Path(); p.moveTo(ex - 9, 48); p.quadTo(ex, 36, ex + 9, 48); c.drawPath(p, stroke)
    if expr == "focus":
        c.drawLine(24, 30, 40, 34, stroke); c.drawLine(76, 30, 60, 34, stroke)
    if expr in ("smile", "focus"):
        p = skia.Path(); p.moveTo(40, 68); p.quadTo(50, 76, 60, 68); c.drawPath(p, stroke)
    elif expr in ("happy", "laugh", "proud"):
        p = skia.Path(); p.moveTo(36, 64); p.lineTo(64, 64); p.quadTo(62, 84, 50, 84); p.quadTo(38, 84, 36, 64); p.close()
        c.drawPath(p, skia.Paint(AntiAlias=True, Color4f=col4((130, 30, 40))))
        c.drawRect(skia.Rect.MakeLTRB(40, 64, 60, 68), white)
    elif expr == "wide":
        c.drawOval(skia.Rect.MakeLTRB(44, 66, 56, 80), skia.Paint(AntiAlias=True, Color4f=col4((130, 30, 40))))
    elif expr == "talk":
        c.drawOval(skia.Rect.MakeLTRB(42, 66, 58, 76), skia.Paint(AntiAlias=True, Color4f=col4((130, 30, 40))))
