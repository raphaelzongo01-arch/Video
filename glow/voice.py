"""Voix off : plusieurs moteurs (Piper/VITS, Kokoro) + traitement "voix de pub motivation".

VOICES contient les voix testées ; engine.tts() utilise VOICE (choisie dans la vidéo ou par défaut).
"""
import os, subprocess, tempfile
import numpy as np
import soundfile as sf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.environ.get("ASSETS", os.path.join(ROOT, "assets"))
VDIR = os.path.join(ASSETS, "voices")
SR = 24000

VOICES = {
    # nom : (moteur, modèle, locuteur, vitesse (length_scale), expressivité, chaîne de traitement)
    "miro": ("piper", "fr_FR-miro-high", None, 0.92, 0.75, "male"),
    "tom": ("piper", "fr_FR-tom-medium", None, 0.88, 0.75, "male"),
    "pierre": ("piper", "fr_FR-upmc-medium", 1, 0.85, 0.75, "male"),
    "jessica": ("piper", "fr_FR-upmc-medium", 0, 0.85, 0.75, "female"),
    "siwis": ("kokoro", "ff_siwis", None, 1.12, None, "female"),
}

FX = {
    # voix « coach » : coupe le grave inutile, chaleur, présence, compression serrée
    "male": "highpass=f=75,equalizer=f=140:t=q:w=1:g=3,equalizer=f=400:t=q:w=1.2:g=-2,"
            "equalizer=f=3200:t=q:w=1:g=4,equalizer=f=9000:t=q:w=1:g=2,"
            "acompressor=threshold=-20dB:ratio=4:attack=4:release=90:makeup=4",
    "female": "highpass=f=90,equalizer=f=250:t=q:w=1:g=1.5,equalizer=f=450:t=q:w=1.2:g=-2,"
              "equalizer=f=3500:t=q:w=1:g=3.5,equalizer=f=10000:t=q:w=1:g=2,"
              "acompressor=threshold=-20dB:ratio=4:attack=4:release=90:makeup=4",
}

_cache = {}


def _piper(model, sid, ls, noise, text):
    from piper import PiperVoice, SynthesisConfig
    if model not in _cache:
        d = os.path.join(VDIR, model)
        _cache[model] = PiperVoice.load(os.path.join(d, model + ".onnx"), os.path.join(d, model + ".onnx.json"))
    v = _cache[model]
    cfg = SynthesisConfig(speaker_id=sid, length_scale=ls, noise_scale=noise, noise_w_scale=0.9)
    parts = [np.frombuffer(ch.audio_int16_bytes, np.int16).astype(np.float32) / 32768 for ch in v.synthesize(text, cfg)]
    out, sr = [], v.config.sample_rate
    for i, p in enumerate(parts):
        out.append(p)
        if i < len(parts) - 1:
            out.append(np.zeros(int(0.16 * sr), np.float32))
    return np.concatenate(out), sr


def _kokoro(name, speed, text):
    if "kokoro" not in _cache:
        from kokoro_onnx import Kokoro
        _cache["kokoro"] = Kokoro(os.path.join(ASSETS, "kokoro-v1.0.onnx"), os.path.join(ASSETS, "voices-v1.0.bin"))
    s, sr = _cache["kokoro"].create(text, voice=name, speed=speed, lang="fr-fr")
    return np.asarray(s, np.float32), sr


def _fx(sig, sr, chain):
    with tempfile.TemporaryDirectory() as td:
        a, b = os.path.join(td, "a.wav"), os.path.join(td, "b.wav")
        sf.write(a, sig, sr)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a, "-af", chain + f",aresample={SR}", "-ac", "1", b],
                       check=True)
        out, _ = sf.read(b, dtype="float32")
    return out


def trim(s, sr=SR, thr=0.012, pre=0.02, post=0.07):
    idx = np.nonzero(np.abs(s) > thr)[0]
    if len(idx) == 0:
        return s
    return s[max(0, idx[0] - int(pre * sr)): idx[-1] + int(post * sr)]


def say(text, voice="miro", speed_mul=1.0):
    eng, model, sid, ls, noise, fx = VOICES[voice]
    if eng == "piper":
        sig, sr = _piper(model, sid, ls / speed_mul, noise, text)
    else:
        sig, sr = _kokoro(model, ls * speed_mul, text)
    sig = sig / (np.abs(sig).max() + 1e-6) * 0.7
    out = _fx(sig, sr, FX[fx])
    out = trim(out)
    return (out / (np.abs(out).max() + 1e-6) * 0.85).astype(np.float32)


# ---------------------------------------------------------------- ElevenLabs (une seule prise + minutage)
EL_VOICES = {
    "el_jessica": "cgSgspJ2msm6clMCkdW9",
    "el_sarah": "EXAVITQu4vr4xnSDxMaL",
    "el_alice": "Xb7hH8MSUJpSbSDYk0k2",
    "el_laura": "FGY2WhTYpPnrIDTdsKH5",
    "el_matilda": "XrExE9yKIg1WjnnlVkGX",
}
EL_SETTINGS = dict(stability=0.45, similarity_boost=0.8, style=0.35, use_speaker_boost=True, speed=1.0)
# ton « reproche / provocation » : modèle v3 + indications de jeu (non prononcées), remises à chaque scène
EL_MODEL = "eleven_v3"
EL_V3_SETTINGS = dict(stability=0.5, similarity_boost=0.8)
EL_TAG = "[confident] [motivating]"
EL_CAPS = False
EL_TEMPO = 1.15


def el_take(text, voice, cache_dir, model="eleven_multilingual_v2", tempo=1.0, settings=None, lang="fr"):
    """Retourne (audio 24 kHz traité, liste (car, début, fin) en secondes après accélération)."""
    import hashlib, json, base64, urllib.request
    settings = settings or (EL_V3_SETTINGS if model == "eleven_v3" else EL_SETTINGS)
    os.makedirs(cache_dir, exist_ok=True)
    key = hashlib.md5(repr((text, voice, model, settings)).encode()).hexdigest()
    fj = os.path.join(cache_dir, f"el_{key}.json")
    if not os.path.exists(fj):
        body = json.dumps(dict(text=text, model_id=model, language_code=lang, voice_settings=settings)).encode()
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{EL_VOICES[voice]}/with-timestamps?output_format=mp3_44100_128",
            data=body, headers={"xi-api-key": os.environ.get("ELEVENLABS_API_KEY", "proxy-injected"),
                                "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=300) as r:
            data = json.loads(r.read())
        json.dump(data, open(fj, "w"))
    data = json.load(open(fj))
    with tempfile.TemporaryDirectory() as td:
        a, b = os.path.join(td, "a.mp3"), os.path.join(td, "b.wav")
        open(a, "wb").write(base64.b64decode(data["audio_base64"]))
        chain = FX["female"] + (f",atempo={tempo}" if tempo != 1.0 else "") + f",aresample={SR}"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a, "-af", chain, "-ac", "1", b], check=True)
        out, _ = sf.read(b, dtype="float32")
    al = data["alignment"]
    chars = list(zip(al["characters"], [x / tempo for x in al["character_start_times_seconds"]],
                     [x / tempo for x in al["character_end_times_seconds"]]))
    out = out / (np.abs(out).max() + 1e-6) * 0.85
    return out.astype(np.float32), chars
