"""Moteur de rendu "glow" : fond noir étoilé, personnages lumineux, lignes qui se dessinent,
sous-titres en haut (MAJUSCULES + un mot en *italique serif*), voix off Kokoro, musique ambient.

Une vidéo = une liste de scènes. Chaque scène = des "chunks" de narration + une fonction de dessin
draw(c, T) appelée à chaque image, où T donne le temps local et le moment où chaque chunk/mot démarre.
"""
import math, os, random, subprocess, multiprocessing as mp
import numpy as np
import skia
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.environ.get("ASSETS", os.path.join(ROOT, "assets"))
FONTS = os.path.join(ASSETS, "fonts")

W, H, FPS, SR = 1920, 1080, 30, 24000
WHITE = (242, 245, 250)
BLUEGLOW = (150, 175, 255)

TF_BOLD = skia.Typeface.MakeFromFile(os.path.join(FONTS, "Inter-ExtraBold.otf"))
TF_SEMI = skia.Typeface.MakeFromFile(os.path.join(FONTS, "Inter-SemiBold.otf"))
TF_ITAL = skia.Typeface.MakeFromFile(os.path.join(FONTS, "InstrumentSerif-Italic.ttf"))


# ------------------------------------------------------------------ easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease(x):  # easeInOutCubic
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def eout(x):  # easeOutCubic
    x = clamp(x)
    return 1 - (1 - x) ** 3


def eback(x, s=1.6):
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def lerp(a, b, k):
    return a + (b - a) * k


def col(rgb, a=1.0):
    return skia.Color4f(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, clamp(a))


# ------------------------------------------------------------------ paints
def paint(rgb=WHITE, a=1.0, stroke=0, blur=0, cap=True):
    p = skia.Paint(AntiAlias=True, Color4f=col(rgb, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        if cap:
            p.setStrokeCap(skia.Paint.kRound_Cap)
            p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


def glowdraw(fn, a=1.0, rgb=WHITE, glow=1.0, stroke=0, gcol=None):
    """fn(paint) dessine la forme ; on la dessine en halo flou puis nette."""
    if glow > 0 and a > 0:
        g = gcol or rgb
        fn(paint(g, a * 0.55 * glow, stroke * 2.2 if stroke else 0, blur=14))
        fn(paint(g, a * 0.5 * glow, stroke * 1.4 if stroke else 0, blur=4))
    if a > 0:
        fn(paint(rgb, a, stroke))


# ------------------------------------------------------------------ texte
_fonts = {}


def F(tf, size):
    k = (id(tf), round(size, 1))
    if k not in _fonts:
        f = skia.Font(tf, size)
        f.setSubpixel(True)
        f.setEdging(skia.Font.Edging.kAntiAlias)
        _fonts[k] = f
    return _fonts[k]


def text_w(t, tf, size, spacing=0):
    f = F(tf, size)
    return f.measureText(t) + spacing * max(0, len(t) - 1)


def draw_text(c, t, x, y, size, tf=None, a=1.0, rgb=WHITE, align="center", spacing=0, glow=0.5, blur=0):
    tf = tf or TF_BOLD
    if a <= 0.01:
        return
    f = F(tf, size)
    w = text_w(t, tf, size, spacing)
    x0 = x - w / 2 if align == "center" else (x - w if align == "right" else x)

    def go(p):
        if spacing:
            xx = x0
            for ch in t:
                c.drawString(ch, xx, y, f, p)
                xx += f.measureText(ch) + spacing
        else:
            c.drawString(t, x0, y, f, p)
    if blur > 0.3:
        go(paint(rgb, a, blur=blur))
        return
    if glow:
        go(paint(rgb, a * 0.35 * glow, blur=10))
    go(paint(rgb, a))


# ------------------------------------------------------------------ primitives
def circle(c, x, y, r, a=1, stroke=0, glow=1, rgb=WHITE):
    glowdraw(lambda p: c.drawCircle(x, y, r, p), a, rgb, glow, stroke)


def rrect(c, x, y, w, h, r, a=1, stroke=0, glow=1, rgb=WHITE, fill=None):
    rect = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h), r, r)
    if fill is not None and a > 0:
        c.drawRRect(rect, paint(fill, a))
    glowdraw(lambda p: c.drawRRect(rect, p), a, rgb, glow, stroke)


def line(c, pts, a=1, w=3, glow=1, rgb=WHITE, progress=1.0, smooth=False):
    if a <= 0 or progress <= 0:
        return
    path = make_path(pts, smooth)
    if progress < 1:
        path = sub_path(path, 0, progress)
    glowdraw(lambda p: c.drawPath(path, p), a, rgb, glow, w)
    return path


def make_path(pts, smooth=False):
    p = skia.Path()
    p.moveTo(*pts[0])
    if not smooth or len(pts) < 3:
        for q in pts[1:]:
            p.lineTo(*q)
        return p
    P = [pts[0]] + list(pts) + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        p.cubicTo(*c1, *c2, *p2)
    return p


def sub_path(path, k0, k1):
    m = skia.PathMeasure(path, False)
    L = m.getLength()
    out = skia.Path()
    m.getSegment(L * k0, L * k1, out, True)
    return out


def point_on(path, k):
    m = skia.PathMeasure(path, False)
    pos, tan = m.getPosTan(m.getLength() * clamp(k))
    return pos.x(), pos.y()


def dashed(c, pts, a=0.5, w=2, dash=(6, 10), progress=1.0):
    path = make_path(pts)
    if progress < 1:
        path = sub_path(path, 0, progress)
    p = paint(WHITE, a, w)
    p.setPathEffect(skia.DashPathEffect.Make(list(dash), 0))
    c.drawPath(path, p)


# ------------------------------------------------------------------ personnage
def figure(c, x, y, s=1.0, a=1.0, lit=0.0, arms="down", dim=0.0, halo=1.0):
    """Personnage lumineux, (x, y) = base. lit = 0..1 surbrillance, dim = 0..1 éteint."""
    if a <= 0.01:
        return
    rgbv = tuple(int(lerp(v, 95, dim)) for v in WHITE)
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    # halo au sol
    if halo > 0:
        hp = paint(BLUEGLOW, a * (0.35 + 0.5 * lit) * halo * (1 - dim * 0.8), blur=9)
        c.drawOval(skia.Rect.MakeLTRB(-40, -8, 40, 8), hp)
    body = skia.Path()
    body.moveTo(-31, 0)
    body.lineTo(-31, -24)
    body.cubicTo(-31, -46, -18, -54, 0, -54)
    body.cubicTo(18, -54, 31, -46, 31, -24)
    body.lineTo(31, 0)
    body.close()
    arm_pts = {"down": None,
               "open": [((-24, -44), (-52, -30)), ((24, -44), (52, -30))],
               "up": [((-22, -46), (-40, -86)), ((22, -46), (40, -86))],
               "wave": [((-24, -44), (-40, -14)), ((22, -46), (42, -88))],
               "point": [((-24, -44), (-40, -14)), ((24, -44), (66, -46))]}[arms]
    glow = 0.45 + 1.1 * lit

    def draw_all(p):
        c.drawPath(body, p)
        c.drawCircle(0, -73, 16.5, p)
    glowdraw(draw_all, a, rgbv, glow * (1 - dim))
    if arm_pts:
        for (p0, p1) in arm_pts:
            pa = make_path([p0, p1])
            glowdraw(lambda p: c.drawPath(pa, p), a, rgbv, glow * (1 - dim), stroke=10)
    if lit > 0.05:  # coeur de lumière
        c.drawCircle(0, -40, 60, paint(WHITE, a * 0.18 * lit, blur=40))
    c.restore()


def ring(c, x, y, r, a=1, w=2.5):
    circle(c, x, y, r, a, stroke=w, glow=0.8)


def bubble(c, x, y, txt, a=1, size=20):
    if a <= 0.01:
        return
    tw = text_w(txt, TF_BOLD, size) + 30
    rrect(c, x, y, tw, size + 22, (size + 22) / 2, a, fill=(10, 12, 18), stroke=2.2, glow=0.6)
    tail = make_path([(x - 10, y + (size + 22) / 2 - 1), (x - 18, y + (size + 22) / 2 + 12),
                      (x + 2, y + (size + 22) / 2 - 1)])
    glowdraw(lambda p: c.drawPath(tail, p), a, WHITE, 0.4, 2.2)
    draw_text(c, txt, x, y + size * 0.36, size, a=a, glow=0.2)


def tag(c, txt, x, y, a=1, size=17, spacing=5):
    draw_text(c, txt, x, y, size, TF_SEMI, a=a * 0.85, spacing=spacing, glow=0.2)


def boxed(c, txt, x, y, a=1, size=22, spacing=5, pad=26):
    tw = text_w(txt, TF_BOLD, size, spacing)
    rrect(c, x, y, tw + pad * 2, size + 34, 8, a, stroke=3, glow=0.8, fill=(8, 9, 13))
    draw_text(c, txt, x, y + size * 0.36, size, a=a, spacing=spacing, glow=0.3)


def check(c, x, y, r=16, a=1, ok=True):
    circle(c, x, y, r, a, glow=0.8)
    if ok:
        line(c, [(x - r * 0.42, y), (x - r * 0.1, y + r * 0.32), (x + r * 0.45, y - r * 0.35)], a, 3.2, 0, (15, 17, 24))
    else:
        line(c, [(x - r * 0.35, y - r * 0.35), (x + r * 0.35, y + r * 0.35)], a, 3.2, 0, (15, 17, 24))
        line(c, [(x + r * 0.35, y - r * 0.35), (x - r * 0.35, y + r * 0.35)], a, 3.2, 0, (15, 17, 24))


def clock(c, x, y, r, a=1, ang=0.0):
    circle(c, x, y, r, a, stroke=3, glow=0.9)
    for i in range(12):
        t = i * math.pi / 6
        line(c, [(x + r * 0.78 * math.cos(t), y + r * 0.78 * math.sin(t)),
                 (x + r * 0.88 * math.cos(t), y + r * 0.88 * math.sin(t))], a * 0.7, 2, 0)
    line(c, [(x, y), (x + r * 0.45 * math.sin(ang / 12), y - r * 0.45 * math.cos(ang / 12))], a, 4, 0.6)
    line(c, [(x, y), (x + r * 0.7 * math.sin(ang), y - r * 0.7 * math.cos(ang))], a, 3, 0.6)
    circle(c, x, y, 4, a, glow=0.4)


def calendar(c, x, y, w, a=1, big="", small=""):
    h = w * 1.05
    rrect(c, x, y, w, h, 12, a, stroke=3, glow=0.8, fill=(8, 9, 13))
    top = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w, h * 0.24), 12, 12)
    c.drawRRect(top, paint(WHITE, a * 0.9))
    for dx in (-w * 0.25, w * 0.25):
        line(c, [(x + dx, y - h / 2 - 10), (x + dx, y - h / 2 + 10)], a, 5, 0.3)
    if small:
        draw_text(c, small, x, y - h / 2 + h * 0.12 + 7, w * 0.11, a=a, rgb=(12, 14, 20), glow=0, spacing=2)
    if big:
        size = w * (0.42 if len(big) <= 2 else 0.24 if len(big) <= 5 else 0.15)
        draw_text(c, big, x, y + h * 0.12 + size * 0.36, size, a=a, glow=0.5)


def hourglass(c, x, y, s, a=1, k=0.0):
    w, h = 34 * s, 50 * s
    line(c, [(x - w, y - h), (x + w, y - h)], a, 4, 0.7)
    line(c, [(x - w, y + h), (x + w, y + h)], a, 4, 0.7)
    line(c, [(x - w * 0.8, y - h), (x, y), (x - w * 0.8, y + h)], a, 3, 0.7)
    line(c, [(x + w * 0.8, y - h), (x, y), (x + w * 0.8, y + h)], a, 3, 0.7)
    # sable
    top = (1 - k)
    p = skia.Path()
    yy = y - h * 0.15 - h * 0.7 * top
    p.moveTo(x - w * 0.8 * (y - yy) / h, yy); p.lineTo(x + w * 0.8 * (y - yy) / h, yy); p.lineTo(x, y - 3); p.close()
    c.drawPath(p, paint(WHITE, a * 0.8))
    p2 = skia.Path()
    hb = h * 0.8 * k
    p2.moveTo(x - w * 0.75, y + h - 2); p2.lineTo(x + w * 0.75, y + h - 2); p2.lineTo(x, y + h - 2 - hb); p2.close()
    c.drawPath(p2, paint(WHITE, a * 0.8))


def star4(c, x, y, r, a=1):
    p = skia.Path()
    p.moveTo(x, y - r); p.quadTo(x, y, x + r, y); p.quadTo(x, y, x, y + r); p.quadTo(x, y, x - r, y)
    p.quadTo(x, y, x, y - r); p.close()
    glowdraw(lambda q: c.drawPath(p, q), a, WHITE, 1.2)


def light_bloom(c, x, y, r, a=1, rgb=(170, 190, 255)):
    if a <= 0:
        return
    sh = skia.GradientShader.MakeRadial(skia.Point(x, y), r,
                                        [skia.Color4f(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, 0.55 * a).toColor(),
                                         skia.Color4f(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, 0.12 * a).toColor(),
                                         skia.Color4f(0, 0, 0, 0).toColor()], [0, 0.45, 1])
    p = skia.Paint(AntiAlias=True, Shader=sh)
    c.drawCircle(x, y, r, p)


def camera(c, zoom=1.0, cx=W / 2, cy=H / 2, rot=0.0):
    c.translate(W / 2, H / 2)
    c.scale(zoom, zoom)
    if rot:
        c.rotate(rot)
    c.translate(-cx, -cy)


# ------------------------------------------------------------------ fond
class Background:
    def __init__(self, seed=1):
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W * 0.5) / (W * 0.75)) ** 2 + ((yy - H * 0.42) / (H * 0.85)) ** 2)
        center = np.array([24, 27, 36], np.float32)
        edge = np.array([3, 4, 7], np.float32)
        k = np.clip(d, 0, 1)[..., None] ** 1.3
        img = center * (1 - k) + edge * k
        # grille de points très discrète
        grid = ((xx % 28 < 1.5) & (yy % 28 < 1.5)).astype(np.float32)[..., None] * 9 * (1 - k)
        img = img + grid
        rng = np.random.default_rng(seed)
        img += rng.normal(0, 1.4, img.shape[:2])[..., None]
        arr = np.dstack([np.clip(img, 0, 255).astype(np.uint8), np.full((H, W), 255, np.uint8)])
        self.image = skia.Image.fromarray(np.ascontiguousarray(arr), colorType=skia.kRGBA_8888_ColorType)
        r = random.Random(seed)
        self.stars = [(r.uniform(0, W), r.uniform(0, H), r.uniform(0.6, 1.8), r.uniform(0, 6.28), r.uniform(0.4, 1.6))
                      for _ in range(90)]

    def draw(self, c, t):
        c.drawImage(self.image, 0, 0)
        for (x, y, s, ph, sp) in self.stars:
            a = 0.25 + 0.35 * (0.5 + 0.5 * math.sin(t * sp + ph))
            c.drawCircle(x + math.sin(t * 0.05 + ph) * 6, y, s, paint(WHITE, a * 0.6))


# ------------------------------------------------------------------ sous-titres
def parse_caption(cap):
    """'TOUT LE MONDE attend le *bon* moment' -> [(mot, italique)]"""
    out = []
    for w in cap.split():
        it = w.startswith("*") or w.endswith("*") or "*" in w
        out.append((w.replace("*", ""), it))
    # fusion des signes isolés
    merged = []
    for w, it in out:
        if merged and w.rstrip(".,") in ("?", "!", ":", "%", "€", "»", ";"):
            merged[-1] = (merged[-1][0] + " " + w, merged[-1][1])
        elif merged and merged[-1][0] in ("«",):
            merged[-1] = ("« " + w, it)
        else:
            merged.append((w, it))
    return merged


CAP_SIZE, ITAL_SIZE = 50, 66


def word_img_w(w, it):
    return text_w(w, TF_ITAL, ITAL_SIZE) if it else text_w(w.upper(), TF_BOLD, CAP_SIZE, 1)


def layout_caption(words, maxw=1250):
    lines, cur, cw = [], [], 0
    sp = 16
    for i, (w, it) in enumerate(words):
        ww = word_img_w(w, it)
        if cur and cw + sp + ww > maxw:
            lines.append(cur); cur, cw = [], 0
        cur.append((i, w, it, ww)); cw += (sp if len(cur) > 1 else 0) + ww
    if cur:
        lines.append(cur)
    # équilibre 2 lignes
    if len(lines) == 2 and len(lines[0]) - len(lines[1]) >= 3:
        lines[1].insert(0, lines[0].pop())
    return lines


def draw_caption(c, words, times, t, fade_out=1.0, y0=118):
    lines = layout_caption(words)
    lh = 66
    for li, ln in enumerate(lines):
        tot = sum(x[3] for x in ln) + 16 * (len(ln) - 1)
        x = W / 2 - tot / 2
        y = y0 + li * lh
        for (i, w, it, ww) in ln:
            st = times[i]
            k = clamp((t - st) / 0.28)
            if k > 0:
                e = eout(k)
                a = e * fade_out
                blur = (1 - e) * 9
                dy = (1 - e) * 10
                if it:
                    draw_text(c, w, x, y + dy + 2, ITAL_SIZE, TF_ITAL, a=a, align="left", glow=0.6, blur=blur)
                else:
                    draw_text(c, w.upper(), x, y + dy, CAP_SIZE, TF_BOLD, a=a, align="left", spacing=1, glow=0.45,
                              blur=blur)
            x += ww + 16


# ------------------------------------------------------------------ voix
def tts(chunks, cache_dir, speed=1.0, voice="miro"):
    import hashlib, voice as V
    os.makedirs(cache_dir, exist_ok=True)
    out = []
    for cap, say in chunks:
        key = hashlib.md5(repr((say, speed, voice, V.VOICES[voice], V.FX[V.VOICES[voice][5]])).encode()).hexdigest()
        fn = os.path.join(cache_dir, key + ".wav")
        if not os.path.exists(fn):
            sf.write(fn, V.say(say, voice, speed), SR)
        s, _ = sf.read(fn, dtype="float32")
        out.append(s)
    return out


def word_times(words, start, dur):
    def wt(w):
        return 2 + len(w) + 5 * sum(ch.isdigit() for ch in w) + (4 if w[-1] in ".,?!:»" else 0)
    ws = [wt(w) for w, _ in words]
    tot = sum(ws)
    t, out = start, []
    for x in ws:
        out.append(t); t += dur * x / tot
    return out


# ------------------------------------------------------------------ timeline
class T:
    def __init__(self, scene, t):
        self.s = scene
        self.t = t - scene["start"]          # temps local
        self.dur = scene["end"] - scene["start"]

    def c(self, k):  # début du chunk k (temps local)
        k = min(k, len(self.s["chunks"]) - 1)
        return self.s["chunks"][k]["start"] - self.s["start"]

    def w(self, k, j):  # début du mot j du chunk k
        ch = self.s["chunks"][min(k, len(self.s["chunks"]) - 1)]
        return ch["times"][min(j, len(ch["times"]) - 1)] - self.s["start"]

    def p(self, t0, d=0.6, f=eout):  # progression 0..1 à partir de t0 (local)
        return f((self.t - t0) / d) if d > 0 else float(self.t >= t0)

    def pc(self, k, d=0.6, delay=0.0, f=eout):
        return self.p(self.c(k) + delay, d, f)

    def pw(self, k, j, d=0.5, delay=0.0, f=eout):
        return self.p(self.w(k, j) + delay, d, f)


def build(scenes, cache_dir, speed=1.0, voice="miro", gap=0.14, scene_gap=0.38, lead=0.6, tail=2.2):
    all_chunks = []
    for sc in scenes:
        for ch in sc["say"]:
            cap, say = (ch if isinstance(ch, tuple) else (ch, ch.replace("*", "")))
            all_chunks.append((cap, say))
    clips = tts(all_chunks, cache_dir, speed, voice)
    t = lead
    ci = 0
    for si, sc in enumerate(scenes):
        sc["chunks"] = []
        for ch in sc["say"]:
            cap, say = all_chunks[ci]
            clip = clips[ci]; ci += 1
            d = len(clip) / SR
            words = parse_caption(cap)
            sc["chunks"].append(dict(cap=cap, words=words, start=t, end=t + d,
                                     times=word_times(words, t, d), clip=clip))
            t += d + gap
        t += scene_gap + sc.get("pause", 0)
    for si, sc in enumerate(scenes):
        sc["start"] = (sc["chunks"][0]["start"] - 0.35) if si else 0.0
    for si, sc in enumerate(scenes):
        sc["end"] = scenes[si + 1]["start"] if si + 1 < len(scenes) else t + tail
    return scenes, scenes[-1]["end"]


# ------------------------------------------------------------------ rendu image
_G = {}


def _init(video_module_name):
    import importlib
    mod = importlib.import_module(video_module_name)
    scenes, total = build(mod.SCENES, mod.CACHE, mod.SPEED, getattr(mod, "VOICE", "miro"))
    _G.update(scenes=scenes, total=total, bg=Background(mod.SEED),
              surface=skia.Surface(W, H))


def scene_draw(c, sc, t):
    c.save()
    z = sc.get("zoom", 1.3)
    c.translate(W / 2, H * 0.56); c.scale(z, z); c.translate(-W / 2, -H * 0.56)
    sc["draw"](c, T(sc, t))
    c.restore()


def render_frame(fi):
    scenes, bg, surf = _G["scenes"], _G["bg"], _G["surface"]
    t = fi / FPS
    c = surf.getCanvas()
    c.clear(skia.ColorBLACK)
    bg.draw(c, t)
    si = max(i for i, s in enumerate(scenes) if s["start"] <= t + 1e-6)
    sc = scenes[si]
    XF = 0.4
    if si > 0 and t - sc["start"] < XF and not sc.get("cut"):
        k = ease((t - sc["start"]) / XF)
        prev = scenes[si - 1]
        c.saveLayerAlpha(None, int(255 * (1 - k)))
        scene_draw(c, prev, t)
        c.restore()
        c.saveLayerAlpha(None, int(255 * k))
        scene_draw(c, sc, t)
        c.restore()
    else:
        scene_draw(c, sc, t)
    # sous-titre : le chunk courant
    cur = None
    for s in scenes:
        for ch in s["chunks"]:
            if ch["start"] - 0.12 <= t:
                cur = (s, ch)
    if cur:
        s, ch = cur
        nxt_start = None
        flat = [x for ss in scenes for x in ss["chunks"]]
        i = flat.index(ch)
        nxt_start = flat[i + 1]["start"] - 0.12 if i + 1 < len(flat) else ch["end"] + 1.2
        hold_end = min(nxt_start, ch["end"] + 1.4)
        fo = 1 - clamp((t - hold_end + 0.25) / 0.25)
        if fo > 0:
            draw_caption(c, ch["words"], ch["times"], t, fo)
    # vignette + fondu d'entrée/sortie
    total = _G["total"]
    fade = min(clamp(t / 0.5), clamp((total - t) / 0.8))
    if fade < 1:
        c.drawRect(skia.Rect.MakeWH(W, H), paint((0, 0, 0), 1 - fade))
    arr = surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3]
    return np.ascontiguousarray(arr).tobytes()


def render_video(video_module_name, out_path, music_fn):
    import importlib
    mod = importlib.import_module(video_module_name)
    scenes, total = build(mod.SCENES, mod.CACHE, mod.SPEED, getattr(mod, "VOICE", "miro"))
    print(f"durée : {total:.1f}s")
    # audio
    n = int(total * SR)
    audio = np.zeros(n + SR)
    for s in scenes:
        for ch in s["chunks"]:
            a = int(ch["start"] * SR)
            audio[a:a + len(ch["clip"])] += ch["clip"] * 1.0
    bgm = music_fn(total, [s["start"] for s in scenes], getattr(mod, "MUSIC", {}))
    audio[:len(bgm)] += bgm
    audio = audio[:n]
    audio /= max(1.0, np.abs(audio).max() / 0.92)
    wav = out_path.replace(".mp4", ".wav")
    sf.write(wav, audio.astype(np.float32), SR)
    # vidéo
    nframes = int(total * FPS)
    tmp = out_path.replace(".mp4", "_v.mp4")
    proc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                             "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    with mp.get_context("fork").Pool(4, initializer=_init, initargs=(video_module_name,)) as pool:
        for i, buf in enumerate(pool.imap(render_frame, range(nframes), chunksize=8)):
            proc.stdin.write(buf)
            if i % 300 == 0:
                print(f"  {i}/{nframes}", flush=True)
    proc.stdin.close(); proc.wait()
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", out_path], check=True)
    os.remove(tmp)
    print("OK ->", out_path)


def preview(video_module_name, times, out_png):
    _init(video_module_name)
    from PIL import Image
    ims = []
    for t in times:
        buf = render_frame(int(t * FPS))
        ims.append(Image.frombytes("RGB", (W, H), buf).resize((640, 360)))
    cols = 3
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (640 * cols, 360 * rows))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % cols) * 640, (i // cols) * 360))
    sheet.save(out_png)
    return _G["scenes"], _G["total"]
