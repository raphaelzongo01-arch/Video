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
