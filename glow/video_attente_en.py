"""Video 1 (EN) — "The right moment doesn't exist"."""
import os
import engine
from video_attente import *  # mêmes animations

engine.LANG = "en"
engine.TR.update({
    "PROJET": "PROJECT", "SPORT": "FITNESS", "VOYAGE": "TRAVEL", "LIVRE": "BOOK", "DÉMÉNAGER": "MOVE OUT",
    "LUNDI": "MONDAY", "BIENTÔT": "SOON", "MOIS +1": "MONTH +1", "PLUS TARD": "LATER", "UN JOUR": "SOMEDAY",
    "LE MOIS PROCHAIN": "NEXT MONTH", "L'ANNÉE PROCHAINE": "NEXT YEAR", "PAS PRÊT": "NOT READY",
    "jamais": "never", "t'es sûr ?": "you sure?", "pfff": "pfft", "il rêve": "dream on",
    "ESSAI": "TRY", "ÉCHEC": "FAIL", "RECOMMENCE": "AGAIN", "ENCORE": "AGAIN", "EUX": "THEM",
    "JOURS": "DAYS", "AUJOURD'HUI": "TODAY", "PARTAGE  →": "SHARE  →",
})
CACHE = os.path.join(ROOT, "out", "tts_attente_en")

SCENES = [
    dict(say=["Everyone's waiting for the right moment.", "And *honestly*, so are you."], draw=s1),
    dict(say=["The right moment to start your *business*,", "to get back in shape,", "to finally *go for it*."], draw=s2),
    dict(say=["So you put it off.", "Monday.", "Next month.", "Next *year*."], draw=s3),
    dict(say=["But listen to me.", "Time itself", "won't wait for *you*."], draw=s4),
    dict(say=["One day,", "someone decides to just go.", "Without being *ready*."], draw=s5),
    dict(say=["And suddenly, everyone's watching.", "They *judge*.", "“Who does he think he is?”"], draw=s6),
    dict(say=["His first steps are *terrible*.", "And that's normal."], draw=s7, zoom=1.0),
    dict(say=["Nobody sees the hours,", "the *failures*,", "the times he starts over."], draw=s8, zoom=1.0),
    dict(say=["But every single day,", "he gets a little *further*."], draw=s9),
    dict(say=["One year later,", "the ones who were waiting", "are *still* waiting."], draw=s10),
    dict(say=["Him?", "He's *somewhere else*."], draw=s11, pause=0.3),
    dict(say=["The right moment never comes.", "You *create* it."], draw=s12),
    dict(say=["So stop waiting.", "Start *today*.", "Even small. Even messy."], draw=s13, zoom=1.05),
    dict(say=["Send this to the friend", "who's *still* waiting."], draw=s14),
]
