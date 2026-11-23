"""Génère une vidéo verticale "faceless" style cartoon (TikTok/Reels/Shorts).

Personnage : Léa (chignon roux, sweat jaune).
Histoire : revendre des vêtements vintage chinés à Emmaüs.

Usage : python3 make_video.py  -> out/video_lea_vintage.mp4
Dépendances : pillow, numpy, kokoro-onnx, soundfile, ffmpeg
(modèles Kokoro : kokoro-v1.0.onnx + voices-v1.0.bin dans ASSETS)
"""
import math, os, random, subprocess, sys
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.environ.get("ASSETS", os.path.join(HERE, "assets"))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

W, H, FPS = 1080, 1920, 30
GROUND = 1560
SR = 24000

CREAM = (251, 249, 242)
INK = (25, 25, 28)
ORANGE = (247, 147, 30)
YELLOW = (255, 210, 31)
GREEN = (61, 190, 61)
BLUE = (30, 150, 220)
PINK = (245, 160, 170)

FONT = os.path.join(ASSETS, "fonts", "Montserrat.ttf")
HAND = os.path.join(ASSETS, "fonts", "Caveat.ttf")
_fc = {}


def font(size, hand=False, weight=b"Black"):
    key = (size, hand, weight)
    if key not in _fc:
        f = ImageFont.truetype(HAND if hand else FONT, size)
        try:
            f.set_variation_by_name(b"Bold" if hand else weight)
        except Exception:
            pass
        _fc[key] = f
    return _fc[key]


# --------------------------------------------------------------------------
# SCRIPT : (texte lu, texte des sous-titres, fond, éléments, pose, expression)
# éléments : (mot_d'apparition, type, params)
# --------------------------------------------------------------------------
SCENES = [
    dict(say="Mille cinq cents balles par mois, avec des fringues que personne ne veut.",
         cap="1 500 balles par mois, avec des fringues que personne ne veut.",
         bg="plain", pose="head", face="money",
         els=[(0, "title", dict(t="1 500 BALLES", x=540, y=300, s=110, rot=-3)),
              (3, "hand", dict(t="par mois", x=760, y=410, s=60)),
              (6, "prop", dict(k="rack", x=700, y=1180, w=560))]),
    dict(say="Ouais. Des vieux vêtements, à deux euros.",
         cap="Ouais. Des vieux vêtements, à 2 €.",
         bg="blue", pose="point", face="smile",
         els=[(0, "prop", dict(k="shirt_pink", x=280, y=330, w=210, rot=-8)),
              (2, "prop", dict(k="shirt_yellow", x=800, y=300, w=210, rot=8)),
              (5, "price", dict(t="2 €", x=760, y=1000, s=130))]),
    dict(say="Aujourd'hui, je te montre exactement comment je fais.",
         cap="Aujourd'hui je te montre exactement comment je fais.",
         bg="burst", pose="wave", face="happy", center=True, els=[]),
    dict(say="Envoie ça à ta pote qui passe sa vie sur Vinted.",
         cap="Envoie ça à ta pote qui passe sa vie sur Vinted.",
         bg="plain", pose="phone", face="wink",
         els=[(0, "title", dict(t="ENVOIE À TA POTE", x=540, y=300, s=78, rot=0)),
              (2, "prop", dict(k="phone_send", x=520, y=1000, w=220, rot=12))]),
    dict(say="Étape un. Le samedi matin, direction Emmaüs.",
         cap="Étape 1. Le samedi matin, direction Emmaüs.",
         bg="sky", pose="point", face="smile",
         els=[(0, "title", dict(t="ÉTAPE 1", x=540, y=300, s=120, rot=-2)),
              (3, "hand", dict(t="samedi matin", x=560, y=430, s=70)),
              (5, "prop", dict(k="seller", x=820, y=1300, w=260))]),
    dict(say="Neuf heures pile. Les bacs viennent d'être remplis.",
         cap="9H00 pile. Les bacs viennent d'être remplis.",
         bg="sky", pose="head", face="star",
         els=[(0, "title", dict(t="9H00 PILE", x=540, y=300, s=110, rot=-3)),
              (0, "prop", dict(k="clock", x=830, y=470, w=150)),
              (3, "prop", dict(k="bin", x=720, y=1330, w=440))]),
    dict(say="Tout est entre un et cinq euros. Personne ne regarde vraiment.",
         cap="Tout est entre 1 € et 5 €. Personne ne regarde vraiment.",
         bg="sky", pose="point", face="smile",
         els=[(3, "price", dict(t="1 €", x=450, y=640, s=120)),
              (5, "price", dict(t="5 €", x=760, y=640, s=120)),
              (6, "prop", dict(k="seller_sleep", x=820, y=1300, w=260))]),
    dict(say="Étape deux. Tu cherches les bonnes étiquettes.",
         cap="Étape 2. Tu cherches les bonnes étiquettes.",
         bg="blue", pose="head", face="wide",
         els=[(0, "title", dict(t="ÉTAPE 2", x=540, y=300, s=120, rot=2)),
              (4, "prop", dict(k="tag", x=700, y=1050, w=330, rot=-6))]),
    dict(say="Fabriqué en Italie, cent pour cent laine. Ça, c'est de l'or.",
         cap="Made in Italy, 100 % laine. Ça, c'est de l'or.",
         bg="plain", pose="point", face="wide",
         els=[(0, "title", dict(t="100 % LAINE", x=540, y=300, s=110, rot=-2)),
              (0, "prop", dict(k="tag_zoom", x=720, y=1050, w=380)),
              (6, "hand", dict(t="= de l'or", x=760, y=760, s=80))]),
    dict(say="Tu vérifies le prix des ventes sur l'appli, en dix secondes.",
         cap="Tu vérifies le prix des ventes sur l'appli, en 10 secondes.",
         bg="plain", pose="point", face="smile",
         els=[(0, "hand", dict(t="prix déjà vendus", x=620, y=560, s=70)),
              (2, "prop", dict(k="phone_app", x=700, y=1100, w=280)),
              (8, "price", dict(t="10 s", x=870, y=760, s=90))]),
    dict(say="Étape trois. Photos à la lumière du jour, et tu postes le soir même.",
         cap="Étape 3. Photos à la lumière du jour, et tu postes le soir même.",
         bg="plain", pose="phone", face="smile",
         els=[(0, "title", dict(t="ÉTAPE 3", x=540, y=300, s=120, rot=-2)),
              (2, "prop", dict(k="sun", x=840, y=560, w=180)),
              (3, "prop", dict(k="camera", x=680, y=1100, w=260))]),
    dict(say="Et un jour, tu tombes sur une veste en jean à trois euros.",
         cap="Et un jour, tu tombes sur une veste en jean à 3 €.",
         bg="plain", pose="head", face="wide",
         els=[(7, "prop", dict(k="jacket", x=730, y=1100, w=360)),
              (11, "price", dict(t="3 €", x=730, y=780, s=120))]),
    dict(say="Revendue quatre-vingt-dix euros en deux jours. La pépite.",
         cap="Revendue 90 € en 2 jours. La pépite.",
         bg="plain", pose="point", face="star",
         els=[(0, "prop", dict(k="jacket", x=730, y=1100, w=360)),
              (1, "price", dict(t="3 € → 90 €", x=640, y=780, s=110)),
              (6, "title", dict(t="LA PÉPITE", x=600, y=320, s=120, rot=-4))]),
    dict(say="Résultat ce mois-ci : plus mille deux cents euros !",
         cap="Résultat ce mois-ci : +1 200 € !",
         bg="burst", pose="up", face="money", center=True, money=True,
         els=[(0, "title", dict(t="CE MOIS-CI", x=540, y=250, s=80, rot=-2)),
              (3, "price", dict(t="+1 200 €", x=540, y=400, s=150))]),
    dict(say="Avec seulement quatre sorties par mois, et deux heures de tri.",
         cap="Avec seulement 4 sorties par mois, et 2 heures de tri.",
         bg="plain", pose="head", face="smile",
         els=[(2, "counter", dict(label="SORTIES / MOIS", n="4", x=330, y=420)),
              (8, "counter", dict(label="HEURES DE TRI", n="2", x=760, y=420))]),
    dict(say="Tu penses que le vintage, c'est juste une mode ?",
         cap="Tu penses que le vintage, c'est juste une mode ?",
         bg="plain", pose="head", face="smile",
         els=[(7, "title", dict(t="MODE ?", x=300, y=320, s=100, rot=-4, col=BLUE)),
              (8, "hand", dict(t="pouf !", x=320, y=480, s=80))]),
    dict(say="Ou un vrai filon pour notre génération ?",
         cap="Ou un vrai filon pour notre génération ?",
         bg="plain", pose="point", face="wide",
         els=[(0, "title", dict(t="MODE ?", x=300, y=320, s=100, rot=-4, col=BLUE)),
              (3, "title", dict(t="FILON ?", x=780, y=320, s=100, rot=3)),
              (3, "prop", dict(k="gold", x=780, y=520, w=150))]),
    dict(say="Enregistre la vidéo, et abonne-toi pour la suite.",
         cap="Enregistre la vidéo, et abonne-toi pour la suite.",
         bg="burst", pose="phone", face="wink", center=True,
         els=[(0, "title", dict(t="ENREGISTRE", x=540, y=280, s=110, rot=-2)),
              (0, "prop", dict(k="bookmark", x=220, y=520, w=110)),
              (4, "prop", dict(k="subscribe", x=780, y=540, w=300, rot=-6))]),
]


# --------------------------------------------------------------------------
# AUDIO : voix off
# --------------------------------------------------------------------------
def tts():
    from kokoro_onnx import Kokoro
    k = Kokoro(os.path.join(ASSETS, "kokoro-v1.0.onnx"), os.path.join(ASSETS, "voices-v1.0.bin"))
    clips = []
    for sc in SCENES:
        s, sr = k.create(sc["say"], voice="ff_siwis", speed=1.12, lang="fr-fr")
        s = np.asarray(s, dtype=np.float32)
        env = np.abs(s) > 0.02
        idx = np.nonzero(env)[0]
        a = max(0, idx[0] - int(0.03 * sr)); b = min(len(s), idx[-1] + int(0.08 * sr))
        clips.append(s[a:b])
    return clips


def word_times(cap, start, dur):
    words = cap.split()
    # fusionne les signes isolés (€, %, :, ?, !, →) avec le mot précédent
    merged = []
    for w in words:
        if merged and w in ("€", "%", ":", "?", "!", "→", "€.", "€,", "€!", "%,", "s"):
            merged[-1] += " " + w
        else:
            merged.append(w)
    def weight(w):
        d = sum(c.isdigit() for c in w)
        return 1.5 + len(w) + 4 * d + (3 if w.endswith((".", ",", "?", "!", ":")) else 0)
    ws = [weight(w) for w in merged]
    tot = sum(ws)
    t = start; out = []
    for w, x in zip(merged, ws):
        d = dur * x / tot
        out.append((w, t, t + d)); t += d
    return out


# --------------------------------------------------------------------------
# DESSIN : utilitaires (supersampling x4 pour l'antialiasing)
# --------------------------------------------------------------------------
K = 4


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.im = Image.new("RGBA", (w * K, h * K), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def P(self, pts):
        return [(x * K, y * K) for x, y in pts]

    def ell(self, x0, y0, x1, y1, fill=None, ol=INK, w=6):
        self.d.ellipse([x0 * K, y0 * K, x1 * K, y1 * K], fill=fill, outline=ol, width=int(w * K) if ol else 0)

    def rect(self, x0, y0, x1, y1, fill=None, ol=INK, w=6, r=0):
        self.d.rounded_rectangle([x0 * K, y0 * K, x1 * K, y1 * K], radius=r * K, fill=fill,
                                 outline=ol, width=int(w * K) if ol else 0)

    def poly(self, pts, fill=None, ol=INK, w=6):
        self.d.polygon(self.P(pts), fill=fill)
        if ol:
            self.line(pts + [pts[0]], ol, w)

    def line(self, pts, col=INK, w=6):
        self.d.line(self.P(pts), fill=col, width=int(w * K), joint="curve")
        r = w * K / 2
        for x, y in self.P([pts[0], pts[-1]]):
            self.d.ellipse([x - r, y - r, x + r, y + r], fill=col)

    def arc(self, box, a0, a1, col=INK, w=6):
        self.d.arc([b * K for b in box], a0, a1, fill=col, width=int(w * K))

    def text(self, xy, t, size, fill=INK, hand=False, anchor="mm"):
        self.d.text((xy[0] * K, xy[1] * K), t, font=font(size * K, hand), fill=fill, anchor=anchor)

    def done(self):
        return self.im.resize((self.w, self.h), Image.LANCZOS)


def star(c, cx, cy, r, fill=YELLOW):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    c.poly(pts, fill=fill, w=3)


# --------------------------------------------------------------------------
# PERSONNAGE : Léa
# --------------------------------------------------------------------------
HAIR = (222, 98, 45)
HOODIE = (255, 196, 40)
JEANS = (70, 110, 190)
SKIN = (255, 255, 255)
CW, CH = 420, 600  # boîte du personnage ; pieds à y=585


def draw_char(pose="idle", face="smile", blink=False):
    c = Canvas(CW, CH)
    cx = 170
    # --- jambes
    c.rect(cx - 52, 430, cx - 8, 560, fill=JEANS, w=6, r=8)
    c.rect(cx + 8, 430, cx + 52, 560, fill=JEANS, w=6, r=8)
    # chaussures
    c.rect(cx - 70, 548, cx - 2, 585, fill=(255, 255, 255), w=6, r=14)
    c.rect(cx + 2, 548, cx + 74, 585, fill=(255, 255, 255), w=6, r=14)
    c.line([(cx - 66, 572), (cx - 6, 572)], (220, 60, 60), 4)
    c.line([(cx + 6, 572), (cx + 70, 572)], (220, 60, 60), 4)

    def arm(pts, hand_col=SKIN):
        c.line(pts, INK, 40)
        c.line(pts, HOODIE, 28)
        hx, hy = pts[-1]
        c.ell(hx - 17, hy - 17, hx + 17, hy + 17, fill=hand_col, w=5)

    L = (cx - 62, 270); R = (cx + 62, 270)
    # bras arrière selon pose
    left_arm = {"idle": [L, (cx - 88, 340), (cx - 84, 410)],
                "point": [L, (cx - 88, 340), (cx - 84, 410)],
                "head": [L, (cx - 88, 340), (cx - 84, 410)],
                "phone": [L, (cx - 88, 340), (cx - 84, 410)],
                "wave": [L, (cx - 88, 340), (cx - 84, 410)],
                "up": [L, (cx - 120, 200), (cx - 130, 110)]}[pose]
    right_arm = {"idle": [R, (cx + 88, 340), (cx + 84, 410)],
                 "point": [R, (cx + 130, 300), (cx + 185, 290)],
                 "head": [R, (cx + 115, 230), (cx + 82, 140)],
                 "phone": [R, (cx + 115, 320), (cx + 110, 250)],
                 "wave": [R, (cx + 130, 220), (cx + 140, 120)],
                 "up": [R, (cx + 120, 200), (cx + 130, 110)]}[pose]
    # --- corps (sweat à capuche)
    c.poly([(cx - 70, 250), (cx + 70, 250), (cx + 78, 440), (cx - 78, 440)], fill=HOODIE, w=6)
    c.rect(cx - 45, 360, cx + 45, 410, fill=(240, 175, 25), w=5, r=10)  # poche
    c.line([(cx - 20, 262), (cx - 16, 320)], INK, 4)
    c.line([(cx + 20, 262), (cx + 16, 320)], INK, 4)
    arm(left_arm)
    # --- tête
    hx0, hy0, hx1, hy1 = cx - 95, 55, cx + 95, 250
    # chignon
    c.ell(cx - 45, -2 + 10, cx + 45, 80, fill=HAIR, w=6)
    c.ell(hx0, hy0, hx1, hy1, fill=SKIN, w=6)
    # cheveux : calotte + mèche
    c.d.pieslice([hx0 * K, hy0 * K, hx1 * K, hy1 * K], 180, 360, fill=HAIR)
    c.poly([(hx0 + 3, 152), (cx - 20, 118), (cx + 40, 132), (hx1 - 3, 152), (hx1 - 3, 140), (hx0 + 3, 140)],
           fill=HAIR, ol=None)
    c.ell(hx0, hy0, hx1, hy1, fill=None, w=6)
    c.arc([hx0, hy0, hx1, hy1], 180, 360, INK, 6)
    c.line([(hx0 + 4, 150), (cx - 20, 118), (cx + 40, 132), (hx1 - 4, 150)], INK, 5)
    # mèches sur les côtés
    c.poly([(hx0 + 2, 150), (hx0 + 22, 150), (hx0 + 12, 205)], fill=HAIR, w=5)
    c.poly([(hx1 - 2, 150), (hx1 - 22, 150), (hx1 - 12, 205)], fill=HAIR, w=5)
    # joues
    c.ell(cx - 75, 195, cx - 45, 213, fill=PINK, ol=None)
    c.ell(cx + 45, 195, cx + 75, 213, fill=PINK, ol=None)
    # yeux
    ey = 178; exl, exr = cx - 38, cx + 38
    if blink and face in ("smile", "wide", "idle"):
        face_eyes = "closed"
    else:
        face_eyes = face
    if face_eyes in ("smile", "idle"):
        for ex in (exl, exr):
            c.ell(ex - 9, ey - 14, ex + 9, ey + 14, fill=INK, ol=None)
            c.ell(ex - 3, ey - 9, ex + 3, ey - 3, fill=(255, 255, 255), ol=None)
    elif face_eyes == "wide":
        for ex in (exl, exr):
            c.ell(ex - 22, ey - 22, ex + 22, ey + 22, fill=(255, 255, 255), w=5)
            c.ell(ex - 8, ey - 8, ex + 8, ey + 8, fill=INK, ol=None)
    elif face_eyes == "money":
        for ex in (exl, exr):
            c.ell(ex - 24, ey - 24, ex + 24, ey + 24, fill=GREEN, w=5)
            c.text((ex, ey + 1), "€", 32, fill=(255, 255, 255))
    elif face_eyes == "star":
        for ex in (exl, exr):
            star(c, ex, ey, 26)
    elif face_eyes in ("happy", "closed"):
        for ex in (exl, exr):
            if face_eyes == "happy":
                c.arc([ex - 18, ey - 10, ex + 18, ey + 22], 200, 340, INK, 6)
            else:
                c.line([(ex - 14, ey + 2), (ex + 14, ey + 2)], INK, 6)
    elif face_eyes == "wink":
        c.ell(exl - 9, ey - 14, exl + 9, ey + 14, fill=INK, ol=None)
        c.line([(exr - 16, ey - 8), (exr + 10, ey), (exr - 16, ey + 8)], INK, 6)
    # bouche
    my = 222
    if face in ("wide",):
        c.ell(cx - 11, my - 12, cx + 11, my + 12, fill=(120, 30, 40), w=5)
    elif face in ("money", "star", "happy"):
        c.d.chord([(cx - 26) * K, (my - 22) * K, (cx + 26) * K, (my + 18) * K], 0, 180, fill=(120, 30, 40),
                  outline=INK, width=5 * K)
    elif face == "wink":
        c.ell(cx - 14, my - 10, cx + 14, my + 14, fill=(120, 30, 40), w=5)
    else:
        c.arc([cx - 18, my - 18, cx + 18, my + 8], 20, 160, INK, 6)
    # bras avant
    arm(right_arm)
    if pose == "phone":
        x, y = right_arm[-1]
        c.rect(x - 22, y - 70, x + 22, y + 5, fill=(40, 40, 45), w=5, r=8)
        c.rect(x - 15, y - 62, x + 15, y - 6, fill=(120, 200, 255), ol=None, r=4)
        c.ell(x - 17, y - 17, x + 17, y + 17, fill=SKIN, w=5)
    return c.done()


_char_cache = {}


def char_img(pose, face, blink):
    key = (pose, face, blink)
    if key not in _char_cache:
        _char_cache[key] = draw_char(pose, face, blink)
    return _char_cache[key]


# --------------------------------------------------------------------------
# ACCESSOIRES
# --------------------------------------------------------------------------
def shirt(col):
    c = Canvas(300, 300)
    c.poly([(90, 40), (125, 30), (150, 55), (175, 30), (210, 40), (285, 95), (250, 150), (225, 130),
            (225, 280), (75, 280), (75, 130), (50, 150), (15, 95)], fill=col, w=7)
    c.line([(125, 30), (150, 55), (175, 30)], INK, 6)
    return c.done()


def prop_img(k):
    if k == "rack":
        c = Canvas(560, 560)
        c.line([(40, 60), (520, 60)], (120, 120, 130), 12)
        c.line([(60, 60), (60, 540)], (120, 120, 130), 12)
        c.line([(500, 60), (500, 540)], (120, 120, 130), 12)
        c.line([(20, 540), (100, 540)], (120, 120, 130), 12)
        c.line([(460, 540), (540, 540)], (120, 120, 130), 12)
        cols = [(230, 90, 90), (90, 160, 230), (120, 200, 120), (250, 200, 80), (190, 120, 210)]
        for i, col in enumerate(cols):
            x = 110 + i * 85
            c.arc([x - 14, 52, x + 14, 80], 180, 360, INK, 4)
            c.poly([(x - 40, 85), (x + 40, 85), (x + 48, 330), (x - 48, 330)], fill=col, w=5)
        return c.done()
    if k == "shirt_pink":
        return shirt((245, 160, 160))
    if k == "shirt_yellow":
        return shirt((250, 220, 120))
    if k == "phone_send":
        c = Canvas(220, 400)
        c.rect(10, 10, 210, 390, fill=(255, 255, 255), w=8, r=28)
        c.rect(30, 50, 190, 330, fill=(235, 240, 250), ol=None, r=8)
        c.poly([(60, 200), (160, 140), (125, 250), (110, 205)], fill=(255, 255, 255), w=6)
        c.line([(110, 205), (160, 140)], INK, 5)
        c.ell(95, 345, 125, 375, fill=None, w=5)
        return c.done()
    if k in ("seller", "seller_sleep"):
        c = Canvas(260, 420)
        c.rect(40, 300, 220, 420, fill=(150, 90, 50), w=6)  # table
        c.poly([(70, 170), (190, 170), (205, 310), (55, 310)], fill=(110, 70, 40), w=6)
        c.ell(70, 40, 190, 170, fill=SKIN, w=6)
        c.ell(65, 70, 85, 110, fill=(200, 200, 200), w=4)
        c.ell(175, 70, 195, 110, fill=(200, 200, 200), w=4)
        if k == "seller":
            c.ell(98, 92, 110, 108, fill=INK, ol=None); c.ell(150, 92, 162, 108, fill=INK, ol=None)
            c.arc([110, 110, 150, 140], 20, 160, INK, 5)
        else:
            c.line([(95, 102), (115, 102)], INK, 5); c.line([(145, 102), (165, 102)], INK, 5)
            c.ell(122, 125, 138, 141, fill=None, w=4)
            c.text((215, 50), "z", 40, fill=BLUE); c.text((240, 15), "z", 30, fill=BLUE)
        c.ell(90, 95, 120, 115, fill=None, w=4); c.ell(140, 95, 170, 115, fill=None, w=4)
        c.line([(120, 104), (140, 104)], INK, 4)
        return c.done()
    if k == "clock":
        c = Canvas(160, 160)
        c.ell(10, 10, 150, 150, fill=(255, 255, 255), w=7)
        c.line([(80, 80), (80, 35)], INK, 7); c.line([(80, 80), (110, 80)], INK, 7)
        c.text((80, 120), "9:00", 22, fill=(220, 60, 60))
        return c.done()
    if k == "bin":
        c = Canvas(440, 300)
        cols = [(230, 90, 90), (90, 160, 230), (120, 200, 120), (250, 200, 80), (190, 120, 210), (240, 140, 60)]
        for i, col in enumerate(cols):
            x = 40 + i * 62
            c.poly([(x, 120 - (i % 2) * 25), (x + 90, 100 - (i % 3) * 15), (x + 95, 170), (x + 5, 175)], fill=col, w=5)
        c.poly([(10, 140), (430, 140), (400, 290), (40, 290)], fill=(160, 110, 60), w=7)
        c.text((220, 215), "1 € – 5 €", 46, fill=(255, 255, 255))
        return c.done()
    if k in ("tag", "tag_zoom"):
        c = Canvas(380, 300)
        c.rect(20, 40, 360, 260, fill=(255, 255, 255), w=7, r=14)
        c.text((190, 100), "MADE IN", 42)
        c.text((190, 155), "ITALY", 54, fill=(200, 50, 50))
        c.text((190, 220), "100 % LAINE", 34, fill=(90, 90, 90))
        if k == "tag_zoom":
            c.ell(240, 120, 350, 230, fill=None, w=9)
            c.line([(335, 215), (372, 262)], INK, 16)
        return c.done()
    if k == "phone_app":
        c = Canvas(280, 500)
        c.rect(10, 10, 270, 490, fill=(40, 40, 50), w=7, r=34)
        c.rect(28, 50, 252, 450, fill=(255, 255, 255), ol=None, r=10)
        c.rect(28, 50, 252, 100, fill=(30, 170, 160), ol=None, r=10)
        c.text((140, 75), "VENDUS", 26, fill=(255, 255, 255))
        for i, (n, p) in enumerate([("Pull laine", "45 €"), ("Veste jean", "90 €"), ("Chemise", "28 €")]):
            y = 130 + i * 105
            c.rect(42, y, 238, y + 85, fill=(245, 245, 248), w=3, r=10)
            c.rect(52, y + 12, 108, y + 72, fill=[(230, 90, 90), (90, 160, 230), (120, 200, 120)][i], w=3, r=6)
            c.text((120, y + 30), n, 18, anchor="lm")
            c.text((120, y + 60), p, 24, fill=GREEN, anchor="lm")
        return c.done()
    if k == "sun":
        c = Canvas(200, 200)
        for i in range(12):
            a = i * math.pi / 6
            c.line([(100 + 62 * math.cos(a), 100 + 62 * math.sin(a)), (100 + 90 * math.cos(a), 100 + 90 * math.sin(a))], ORANGE, 9)
        c.ell(45, 45, 155, 155, fill=YELLOW, w=7)
        return c.done()
    if k == "camera":
        c = Canvas(280, 220)
        c.rect(70, 25, 150, 70, fill=(80, 80, 90), w=6, r=8)
        c.rect(15, 55, 265, 205, fill=(60, 60, 70), w=7, r=20)
        c.ell(85, 75, 195, 185, fill=(220, 230, 240), w=7)
        c.ell(110, 100, 170, 160, fill=(60, 90, 140), w=5)
        c.ell(215, 75, 240, 95, fill=(255, 90, 90), ol=None)
        return c.done()
    if k == "jacket":
        c = Canvas(360, 380)
        J = (80, 130, 200)
        c.poly([(110, 30), (180, 60), (250, 30), (330, 80), (350, 300), (295, 310), (290, 160),
                (290, 360), (70, 360), (70, 160), (65, 310), (10, 300), (30, 80)], fill=J, w=7)
        c.line([(180, 60), (180, 360)], INK, 5)
        c.poly([(110, 30), (180, 60), (150, 130)], fill=(60, 105, 170), w=5)
        c.poly([(250, 30), (180, 60), (210, 130)], fill=(60, 105, 170), w=5)
        c.rect(95, 170, 155, 215, fill=(60, 105, 170), w=4, r=4)
        c.rect(205, 170, 265, 215, fill=(60, 105, 170), w=4, r=4)
        for y in (110, 170, 230, 290):
            c.ell(193, y - 7, 207, y + 7, fill=(230, 180, 60), w=3)
        return c.done()
    if k == "gold":
        c = Canvas(160, 140)
        c.ell(15, 15, 145, 125, fill=(250, 200, 40), w=7)
        c.arc([40, 35, 90, 80], 200, 300, (255, 240, 170), 8)
        return c.done()
    if k == "bookmark":
        c = Canvas(120, 160)
        c.poly([(15, 10), (105, 10), (105, 150), (60, 115), (15, 150)], fill=YELLOW, w=7)
        c.line([(40, 60), (55, 78), (82, 42)], INK, 7)
        return c.done()
    if k == "subscribe":
        c = Canvas(320, 110)
        c.rect(10, 10, 310, 100, fill=(240, 60, 60), w=7, r=50)
        c.text((160, 56), "ABONNE-TOI", 36, fill=(255, 255, 255))
        return c.done()
    if k == "bill":
        c = Canvas(150, 80)
        c.rect(5, 5, 145, 75, fill=(110, 200, 110), w=5, r=6)
        c.ell(52, 18, 98, 62, fill=(150, 225, 150), w=4)
        c.text((75, 41), "€", 30, fill=(30, 110, 30))
        return c.done()
    raise KeyError(k)


_prop_cache = {}


def prop(k, w):
    key = (k, w)
    if key not in _prop_cache:
        im = prop_img(k)
        _prop_cache[key] = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
    return _prop_cache[key]


# --------------------------------------------------------------------------
# TEXTES (titres, prix, manuscrit, sous-titres)
# --------------------------------------------------------------------------
_txt_cache = {}


def outlined_text(t, size, fill, stroke_col=INK, stroke=None, hand=False, shadow=True):
    key = (t, size, fill, stroke_col, stroke, hand, shadow)
    if key in _txt_cache:
        return _txt_cache[key]
    f = font(size, hand)
    stroke = stroke if stroke is not None else max(3, size // 12)
    bb = f.getbbox(t, stroke_width=stroke)
    pad = stroke + 12
    w, h = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ox, oy = pad - bb[0], pad - bb[1]
    if shadow:
        d.text((ox + size // 18, oy + size // 14), t, font=f, fill=(0, 0, 0, 90), stroke_width=stroke,
               stroke_fill=(0, 0, 0, 90))
    d.text((ox, oy), t, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_col)
    _txt_cache[key] = im
    return im


def ease_back(x):
    x = min(max(x, 0), 1)
    c1 = 1.9
    return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2


def paste_center(base, im, x, y, scale=1.0, rot=0.0, alpha=1.0):
    if scale <= 0.01 or alpha <= 0:
        return
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if abs(scale - 1) > 0.01:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if alpha < 1:
        a = im.getchannel("A").point(lambda v: int(v * alpha))
        im = im.copy(); im.putalpha(a)
    base.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))


# --------------------------------------------------------------------------
# FONDS
# --------------------------------------------------------------------------
def bg_plain():
    im = Image.new("RGBA", (W, H), CREAM + (255,))
    d = ImageDraw.Draw(im)
    d.line([(0, GROUND), (W, GROUND)], fill=INK, width=5)
    return im


def bg_blue():
    im = Image.new("RGBA", (W, H), (196, 206, 250, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, GROUND, W, H], fill=(225, 196, 150))
    for y in range(GROUND + 70, H, 70):
        d.line([(0, y), (W, y)], fill=(200, 170, 125), width=4)
    d.line([(0, GROUND), (W, GROUND)], fill=INK, width=5)
    return im


def bg_sky():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    top, bot = np.array([246, 196, 230]), np.array([255, 228, 170])
    g = np.linspace(0, 1, GROUND)[:, None]
    arr = np.zeros((H, W, 4), np.uint8)
    arr[:GROUND, :, :3] = (top * (1 - g) + bot * g)[:, None, :].astype(np.uint8)
    arr[GROUND:, :, :3] = (215, 215, 215)
    arr[..., 3] = 255
    im = Image.fromarray(arr, "RGBA")
    c = Canvas(W, H - 0)
    c.ell(820, 260, 960, 400, fill=(250, 180, 100), w=5)
    # stands avec auvents rayés
    for i, x0 in enumerate(range(-60, W + 60, 280)):
        cols = [(220, 60, 60), (40, 110, 220), (40, 170, 80)][i % 3]
        x1 = x0 + 250
        for s in range(5):
            sx = x0 + s * 50
            c.poly([(sx, 1130), (sx + 50, 1130), (sx + 50, 1180), (sx, 1180)],
                   fill=cols if s % 2 == 0 else (255, 255, 255), ol=None)
        c.line([(x0, 1130), (x1, 1130)], INK, 5); c.line([(x0, 1180), (x1, 1180)], INK, 5)
        c.line([(x0 + 10, 1180), (x0 + 10, GROUND)], INK, 6); c.line([(x1 - 10, 1180), (x1 - 10, GROUND)], INK, 6)
        c.rect(x0, 1430, x1, 1460, fill=(200, 140, 80), w=5)
    c.line([(0, GROUND), (W, GROUND)], INK, 5)
    for y in range(GROUND + 60, H, 60):
        c.line([(0, y), (W, y)], (195, 195, 195), 3)
    im.alpha_composite(c.done())
    return im


_burst_rays = None


def bg_burst(t):
    im = Image.new("RGBA", (W, H), (255, 236, 190, 255))
    d = ImageDraw.Draw(im)
    cx, cy = W / 2, H * 0.55
    n = 18
    R = 2400
    for i in range(n):
        a0 = t * 0.25 + i * 2 * math.pi / n
        a1 = a0 + math.pi / n
        d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)),
                   (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=(250, 214, 120, 255))
    return im


# --------------------------------------------------------------------------
# RENDU
# --------------------------------------------------------------------------
def build_timeline(clips):
    t = 0.25
    tl = []
    for sc, clip in zip(SCENES, clips):
        d = len(clip) / SR
        tl.append(dict(sc=sc, start=t, end=t + d, words=word_times(sc["cap"], t, d)))
        t += d + 0.12
    total = t + 0.6
    # chaque scène visuelle dure jusqu'au début de la suivante
    for i, s in enumerate(tl):
        s["vstart"] = 0 if i == 0 else tl[i - 1]["vend"]
        s["vend"] = tl[i + 1]["start"] - 0.06 if i + 1 < len(tl) else total
    return tl, total


def render(tl, total, sfx_events):
    statics = {"plain": bg_plain(), "blue": bg_blue(), "sky": bg_sky()}
    nframes = int(total * FPS)
    proc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                             "-crf", "19", "-pix_fmt", "yuv420p", os.path.join(OUT, "video_noaudio.mp4")],
                            stdin=subprocess.PIPE)
    rng = random.Random(7)
    bills = [(rng.uniform(0, W), rng.uniform(-600, 0), rng.uniform(350, 650), rng.uniform(-120, 120),
              rng.uniform(0, 360), rng.uniform(0.6, 1.0)) for _ in range(28)]
    for fi in range(nframes):
        t = fi / FPS
        s = next(x for x in tl if x["vstart"] <= t < x["vend"] + 1e-6) if t < tl[-1]["vend"] else tl[-1]
        sc = s["sc"]
        lt = t - s["vstart"]
        frame = bg_burst(t) if sc["bg"] == "burst" else statics[sc["bg"]].copy()

        def at(widx):
            widx = min(widx, len(s["words"]) - 1)
            return s["words"][widx][1] - 0.05

        # éléments
        for widx, kind, p in sc["els"]:
            t0 = at(widx) if widx > 0 else s["vstart"] + 0.05
            k = (t - t0) / 0.28
            if k <= 0:
                continue
            sc_ = ease_back(k)
            wob = math.sin((t - t0) * 2.2) * 1.2
            if kind == "title":
                im = outlined_text(p["t"], p["s"], p.get("col", ORANGE))
                paste_center(frame, im, p["x"], p["y"], sc_, p.get("rot", 0) + wob * 0.5)
            elif kind == "price":
                im = outlined_text(p["t"], p["s"], GREEN, stroke_col=(20, 80, 20))
                paste_center(frame, im, p["x"], p["y"] + math.sin((t - t0) * 3) * 6, sc_)
            elif kind == "hand":
                im = outlined_text(p["t"], p["s"], (40, 70, 200), stroke=0, hand=True, shadow=False)
                paste_center(frame, im, p["x"], p["y"], 1, -3, alpha=min(1, k))
            elif kind == "prop":
                im = prop(p["k"], p["w"])
                bob = math.sin((t - t0) * 2.5 + p["x"]) * 6
                paste_center(frame, im, p["x"], p["y"] + bob, sc_, p.get("rot", 0) + wob)
            elif kind == "counter":
                box = Canvas(300, 190)
                box.rect(8, 8, 292, 182, fill=(255, 255, 255), w=6, r=8)
                box.rect(8, 8, 292, 60, fill=(235, 235, 235), w=6, r=8)
                box.text((150, 35), p["label"], 22)
                box.text((150, 122), p["n"], 80, fill=BLUE)
                key = ("counter", p["label"])
                if key not in _prop_cache:
                    _prop_cache[key] = box.done()
                paste_center(frame, _prop_cache[key], p["x"], p["y"], sc_)

        # pluie de billets
        if sc.get("money"):
            bill = prop("bill", 150)
            for (bx, by, vy, vr, r0, sz) in bills:
                y = by + vy * lt
                y = (y % (H + 300)) - 150
                paste_center(frame, bill, bx, y, sz, r0 + vr * lt)

        # personnage
        blink = (t % 3.7) < 0.12
        im = char_img(sc["pose"], sc["face"], blink)
        k = min(1, lt / 0.22)
        sq = 1 + 0.06 * math.sin(k * math.pi)  # petit rebond à chaque plan
        bob = math.sin(t * 3.2) * 4
        if sc.get("center"):
            scale = 1.35 * sq
            x, foot = W / 2, GROUND + 40
        else:
            scale = 1.0 * sq
            x, foot = 215, GROUND - 8
        ci = im.resize((int(im.width * scale), int(im.height * (scale + 0.02 * math.sin(t * 6)))), Image.BILINEAR)
        frame.alpha_composite(ci, (int(x - ci.width * 170 / CW), int(foot - ci.height * 585 / CH + bob)))

        # sous-titres : groupes de 3 mots, mot en cours en jaune
        words = s["words"]
        cur = None
        for i, (w_, a, b) in enumerate(words):
            if a <= t < b + 0.15:
                cur = i
        if t > s["start"] - 0.05 and t < s["end"] + 0.12:
            if cur is None:
                cur = 0 if t < s["start"] else len(words) - 1
            g0 = (cur // 3) * 3
            grp = words[g0:g0 + 3]
            ims = []
            for j, (w_, a, b) in enumerate(grp):
                active = g0 + j == cur
                ims.append((outlined_text(w_, 76, YELLOW if active else (255, 255, 255), stroke=7, shadow=True),
                            active, a))
            gap = 18
            total_w = sum(i_.width for i_, _, _ in ims) + gap * (len(ims) - 1)
            cy = 1480 if not sc.get("center") else 1700
            xx = W / 2 - total_w / 2 + (60 if not sc.get("center") else 0)
            fit = min(1.0, (W - 60) / total_w)
            if fit < 1:
                total_w *= fit; gap *= fit
                xx = W / 2 - total_w / 2
            xx = max(30, min(xx, W - 30 - total_w))
            for i_, active, a in ims:
                pop = 1.0
                if active:
                    pk = (t - a) / 0.12
                    pop = 1 + 0.12 * max(0, 1 - abs(pk - 0.5) * 2) if 0 <= pk <= 1 else 1.0
                paste_center(frame, i_, xx + i_.width * fit / 2, cy, pop * fit)
                xx += i_.width * fit + gap

        proc.stdin.write(frame.convert("RGB").tobytes())
        if fi % 150 == 0:
            print(f"  frame {fi}/{nframes}", flush=True)
    proc.stdin.close(); proc.wait()


# --------------------------------------------------------------------------
# SONS : pop, whoosh, cash + petite musique
# --------------------------------------------------------------------------
def env(n, a=0.005, r=0.1):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / r)


def sfx_pop():
    n = int(0.12 * SR); t = np.arange(n) / SR
    f = 900 * np.exp(-t * 25) + 300
    return 0.35 * np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.04)


def sfx_whoosh():
    n = int(0.3 * SR); rng = np.random.default_rng(1)
    noise = rng.normal(0, 1, n)
    k = np.ones(40) / 40
    noise = noise - np.convolve(noise, k, "same")
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    return 0.12 * noise * e


def sfx_cash():
    out = np.zeros(int(0.8 * SR))
    for i, f in enumerate([1318, 1760, 2637]):
        n = len(out) - int(i * 0.06 * SR); t = np.arange(n) / SR
        out[int(i * 0.06 * SR):] += 0.18 * np.sin(2 * np.pi * f * t) * env(n, 0.002, 0.25)
    return out


def music(total):
    n = int(total * SR); out = np.zeros(n)
    bpm = 100; beat = 60 / bpm
    chords = [[261.6, 329.6, 392.0], [220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [196.0, 246.9, 293.7]]
    rng = np.random.default_rng(3)
    b = 0
    while b * beat < total:
        st = int(b * beat * SR)
        ch = chords[(b // 4) % 4]
        # pluck
        for i in range(2):
            f = ch[(b + i) % 3] * 2
            m = int(0.35 * SR); t = np.arange(m) / SR
            sig = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * env(m, 0.003, 0.12)
            s0 = st + int(i * beat / 2 * SR)
            e = min(n, s0 + m)
            if s0 < n:
                out[s0:e] += 0.05 * sig[:e - s0]
        # basse
        if b % 2 == 0:
            m = int(beat * 1.8 * SR); t = np.arange(m) / SR
            sig = np.sin(2 * np.pi * ch[0] / 2 * t) * env(m, 0.01, 0.4)
            e = min(n, st + m); out[st:e] += 0.07 * sig[:e - st]
        # kick / hat
        m = int(0.15 * SR); t = np.arange(m) / SR
        if b % 2 == 0:
            kick = np.sin(2 * np.pi * (50 + 120 * np.exp(-t * 30)) * t) * env(m, 0.001, 0.08)
            e = min(n, st + m); out[st:e] += 0.12 * kick[:e - st]
        hs = st + int(beat / 2 * SR); m2 = int(0.05 * SR)
        if hs + m2 < n:
            out[hs:hs + m2] += 0.025 * rng.normal(0, 1, m2) * env(m2, 0.001, 0.015)
        b += 1
    return out


def mix(tl, clips, total):
    n = int(total * SR) + SR
    out = np.zeros(n)
    m = music(total)
    out[:len(m)] += m * 0.8
    for s, clip in zip(tl, clips):
        a = int(s["start"] * SR)
        out[a:a + len(clip)] += clip * 1.1
    pop, wh, cash = sfx_pop(), sfx_whoosh(), sfx_cash()

    def add(sig, t):
        a = int(t * SR)
        if a < 0 or a >= n:
            return
        e = min(n, a + len(sig)); out[a:e] += sig[:e - a]
    for i, s in enumerate(tl):
        if i > 0:
            add(wh, s["vstart"] - 0.08)
        for widx, kind, p in s["sc"]["els"]:
            if kind in ("title", "price", "prop", "counter"):
                t0 = s["words"][min(widx, len(s["words"]) - 1)][1] - 0.05 if widx > 0 else s["vstart"] + 0.05
                add(pop, t0)
        if s["sc"].get("money"):
            add(cash, s["vstart"] + 0.1); add(cash, s["vstart"] + 0.9)
    out = out[:int(total * SR)]
    out /= max(1.0, np.abs(out).max() / 0.95)
    sf.write(os.path.join(OUT, "audio.wav"), out.astype(np.float32), SR)


def main():
    print("1/3 voix off…")
    clips = tts()
    tl, total = build_timeline(clips)
    print(f"   durée totale : {total:.1f}s")
    print("2/3 audio…")
    mix(tl, clips, total)
    print("3/3 images…")
    render(tl, total, None)
    final = os.path.join(OUT, "video_lea_vintage.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(OUT, "video_noaudio.mp4"),
                    "-i", os.path.join(OUT, "audio.wav"), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", final], check=True)
    print("OK ->", final)


if __name__ == "__main__":
    main()
