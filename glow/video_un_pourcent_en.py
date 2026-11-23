"""Video 2 (EN) — "1% a day"."""
import os
import engine
from video_un_pourcent import *  # mêmes animations

engine.LANG = "en"
engine.TR.update({
    "DÉPART": "START", "25 ANS": "AGE 25", "MÊME TAF": "SAME JOB", "1 800 €": "$1,800",
    "CHAQUE JOUR": "EVERY DAY", "1 € DE CÔTÉ": "$1 SAVED", "€": "$", "JOURS": "DAYS",
    "RÉSULTATS": "RESULTS", "ça marche pas": "not working", "toujours rien": "still nothing",
    "j'arrête": "I quit", "ABANDON": "QUIT", "PARTAGE  →": "SHARE  →",
    "0 %": "0%", "+1 %": "+1%", "3 %": "3%",
})
CACHE = os.path.join(ROOT, "out", "tts_pourcent_en")

SCENES = [
    dict(say=["Picture two friends.", "They start from", "the exact same *place*."], draw=s1),
    dict(say=["Same age.", "Same job.", "Same *salary*."], draw=s2),
    dict(say=["The first one", "changes *nothing*."], draw=s3),
    dict(say=["The second one", ("gets 1% better.", "gets one percent better."), "*Every* single day."], draw=s4),
    dict(say=[("1%?", "One percent?"), "That's nothing, right?", "Ten pages of a book.", "Twenty minutes of exercise.",
              ("One dollar *saved*.", "One dollar saved.")], draw=s5),
    dict(say=["At first,", "you see *no* difference."], draw=s6, zoom=1.15),
    dict(say=["After a month,", "he's *barely* ahead."], draw=s7, zoom=1.15),
    dict(say=["And that's exactly where", "almost everyone", "*quits*."], draw=s8, zoom=1.15),
    dict(say=["Because your brain", "wants results", "*right now*."], draw=s9, zoom=1.15),
    dict(say=["But the math?", "The math", "doesn't *lie*."], draw=s10),
    dict(say=[("1% a day,", "One percent a day,"), "for one year,", "that's",
              ("37 times *better*.", "thirty-seven times better.")], draw=s11, zoom=1.15, pause=0.6),
    dict(say=["And the first one?", "He's still", "in the exact same *place*."], draw=s12, zoom=1.15),
    dict(say=["You don't need", "a massive change.", ("Just 1%.", "Just one percent."), "*Today*."], draw=s13),
    dict(say=["Send this to the friend", "who needs to *hear* it."], draw=s14),
]
