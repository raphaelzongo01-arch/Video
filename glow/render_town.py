"""Rendu de la vidéo 3D « In this town » (vertical 1080×1920) : voix + musique + bruitages + sous-titres mot à mot."""
import math, os, re, subprocess, sys, multiprocessing as mp
import numpy as np
import soundfile as sf
import skia
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine
from engine import SR, parse_caption, _tokens, word_times, _compress_silences, _trim_bounds, clamp, eback
import voice as V
from town3d import W, H, render, draw_sky, col4

FPS = 30
PAUSE = 0.32


def build(mod):
    V.EL_TAG = ""            # pas d'indications de jeu : narration naturelle
    t = 0.5
    for sc in mod.SCENES:
        sc["chunks"] = []
        if not sc["say"]:
            sc["start"] = t
            sc["audio_at"] = t
            sc["audio"] = np.zeros(0, np.float32)
            t += sc.get("silent", 1.5)
            sc["speech_end"] = t
        else:
            text, offs, items = "", [], []
            for ch in sc["say"]:
                cap, say = (ch if isinstance(ch, tuple) else (ch, ch.replace("*", "")))
                if offs:
                    text += " "
                offs.append(len(text)); text += say; items.append((cap, say))
            audio, chars = V.el_take(text, mod.VOICE, mod.CACHE, model=V.EL_MODEL, tempo=1.0, lang="en")
            audio, sh = _compress_silences(audio, chars, punct_target=0.28, other_target=0.12)
            a0, a1 = _trim_bounds(audio)
            audio = audio[a0:a1]
            base = t - a0 / SR
            starts = [sh(c[1]) for c in chars]; ends = [sh(c[2]) for c in chars]
            for (cap, say), o in zip(items, offs):
                idx = [o + j for j, cc in enumerate(say) if not cc.isspace()]
                s_ = max(t, base + starts[idx[0]]); e_ = min(max(base + ends[idx[-1]], s_ + 0.2), t + len(audio) / SR)
                words = parse_caption(cap); toks = _tokens(say)
                if len(toks) == len(words):
                    times = [max(t, base + starts[o + p]) for _, p in toks]
                    tend = [min(e_, base + ends[o + p + len(w) - 1]) for w, p in toks]
                else:
                    times = word_times(words, s_, e_ - s_); tend = times[1:] + [e_]
                sc["chunks"].append(dict(cap=cap, words=words, start=s_, end=e_, times=times, tend=tend))
            sc["start"] = t - 0.25
            sc["audio_at"] = t
            sc["audio"] = audio
            t += len(audio) / SR
            sc["speech_end"] = t
            t += PAUSE + sc.get("pause", 0)
        sc["sfx_items"] = [(sc["speech_end"] - sc["start"] + off, lab) for lab, off in sc.get("sfx", [])]
        sc["sfx_draw"] = getattr(sc["shot"], "__name__", "") == "shot_montage"
    for i, sc in enumerate(mod.SCENES):
        sc["end"] = mod.SCENES[i + 1]["start"] if i + 1 < len(mod.SCENES) else t + 1.2
    mod.SCENES[0]["start"] = 0.0
    return mod.SCENES, mod.SCENES[-1]["end"]


# ------------------------------------------------------------------ sons
def _env(n, a, r):
    tt = np.arange(n) / SR
    return np.minimum(1, tt / a) * np.exp(-tt / r)


def sfx(kind):
    rng = np.random.default_rng(len(kind))
    if kind == "TAP!":
        n = int(0.18 * SR); tt = np.arange(n) / SR
        return 0.5 * np.sin(2 * np.pi * (90 + 120 * np.exp(-tt * 40)) * tt) * _env(n, 0.002, 0.05) + \
            0.15 * rng.normal(0, 1, n) * _env(n, 0.001, 0.015)
    if kind == "BWAAAP!":
        n = int(1.1 * SR); tt = np.arange(n) / SR
        s = sum(np.sign(np.sin(2 * np.pi * f * tt)) * g for f, g in ((233, 0.5), (349, 0.35), (466, 0.2)))
        s = np.convolve(s, np.ones(8) / 8, "same")
        return 0.28 * s * np.minimum(1, tt / 0.03) * np.minimum(1, (1.1 - tt) / 0.15)
    if kind == "ZOOM!":
        n = int(0.5 * SR); tt = np.arange(n) / SR
        noise = rng.normal(0, 1, n)
        out = np.zeros(n)
        for i in range(0, n, 256):
            f = 0.02 + 0.25 * (i / n)
            k = max(2, int(1 / f))
            seg = noise[i:i + 256]
            out[i:i + len(seg)] = seg - np.convolve(seg, np.ones(k) / k, "same")
        return 0.35 * out * np.sin(np.pi * tt / 0.5) ** 2
    if kind == "DING":
        n = int(1.2 * SR); tt = np.arange(n) / SR
        return sum(0.18 * np.sin(2 * np.pi * f * tt) * _env(n, 0.002, 0.4) for f in (1318, 1976, 2637))
    return np.zeros(1)


def upbeat(total, gate):
    """Petite musique entraînante (boom-bap léger) ; gate(t) ∈ [0,1] coupe la musique."""
    n = int(total * SR) + SR
    out = np.zeros(n)
    bpm = 96; beat = 60 / bpm
    prog = [[60, 64, 67, 71], [57, 60, 64, 67], [53, 57, 60, 64], [55, 59, 62, 65]]
    rng = np.random.default_rng(4)
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    b = 0
    while b * beat < total + 1:
        st = int(b * beat * SR)
        ch = prog[(b // 4) % 4]
        m = int(0.25 * SR); tt = np.arange(m) / SR
        if b % 2 == 0:  # kick
            k = np.sin(2 * np.pi * (50 + 100 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 12)
            e = min(n, st + m); out[st:e] += 0.35 * k[:e - st]
        else:  # snare
            sn = rng.normal(0, 1, m) * np.exp(-tt * 22) * 0.5 + np.sin(2 * np.pi * 190 * tt) * np.exp(-tt * 30) * 0.4
            e = min(n, st + m); out[st:e] += 0.22 * sn[:e - st]
        for h in (0, 0.5):  # charleston
            p = st + int(h * beat * SR); mh = int(0.05 * SR)
            if p + mh < n:
                hh = rng.normal(0, 1, mh); hh = hh - np.convolve(hh, np.ones(5) / 5, "same")
                out[p:p + mh] += 0.06 * hh * np.exp(-np.arange(mh) / SR * 80)
        if b % 4 == 0:  # accords (pluck)
            for j, mnote in enumerate(ch):
                mm = int(1.6 * SR); t2 = np.arange(mm) / SR
                sig = (np.sin(2 * np.pi * hz(mnote) * t2) + 0.3 * np.sin(4 * np.pi * hz(mnote) * t2)) * np.exp(-t2 * 2.2)
                p = st + int(j * 0.03 * SR); e = min(n, p + mm)
                out[p:e] += 0.05 * sig[:e - p]
        # basse
        mm = int(beat * 0.9 * SR); t2 = np.arange(mm) / SR
        bass = np.sin(2 * np.pi * hz(ch[0] - 24) * t2) * np.exp(-t2 * 3)
        e = min(n, st + mm); out[st:e] += 0.16 * bass[:e - st]
        b += 1
    g = np.array([gate(i / SR) for i in range(0, n, 240)])
    g = np.repeat(g, 240)[:n]
    return out * g


def mix(scenes, total):
    n = int(total * SR) + SR
    a = np.zeros(n)
    for sc in scenes:
        p = int(sc["audio_at"] * SR)
        a[p:p + len(sc["audio"])] += sc["audio"]
        for (tt, lab) in sc["sfx_items"]:
            s = sfx(lab); q = int((sc["start"] + tt) * SR)
            a[q:q + len(s)] += s[:max(0, n - q)]
        if sc["shot"].__name__ == "shot_finish":
            s = sfx("DING"); q = int((sc["start"] + 0.2) * SR); a[q:q + len(s)] += s
    off = [(sc["start"], sc["end"]) for sc in scenes if sc.get("no_music")]

    def gate(t):
        for (s0, s1) in off:
            if s0 - 0.05 <= t <= s1:
                return 0.0
        for (s0, s1) in off:
            if s1 < t < s1 + 1.5:
                return (t - s1) / 1.5
        fade = min(1.0, t / 0.8, max(0.0, (total - t) / 1.5))
        return fade
    music = upbeat(total, gate)
    a[:len(music)] += 0.32 * music[:n]
    a = a[:int(total * SR)]
    return a / max(1.0, np.abs(a).max() / 0.95)


# ------------------------------------------------------------------ images
_G = {}


def _init(name):
    import importlib
    mod = importlib.import_module(name)
    scenes, total = build(mod)
    _G.update(mod=mod, scenes=scenes, total=total, surf=skia.Surface(W, H))


def caption_word(scenes, t):
    for sc in scenes:
        for ch in sc["chunks"]:
            for (w, it), a, b in zip(ch["words"], ch["times"], ch["tend"]):
                if a - 0.03 <= t < max(b, a + 0.18) + 0.06:
                    return re.sub(r"[.,“”\"…:;]", "", w).replace(" ", ""), a
    return None, None


def frame(fi):
    from video_town_en import label
    scenes, surf = _G["scenes"], _G["surf"]
    t = fi / FPS
    sc = [s for s in scenes if s["start"] <= t + 1e-6][-1]
    c = surf.getCanvas()
    Tm = engine.T(sc, t)
    world, cam, L, sky, ov = sc["shot"](Tm)
    draw_sky(c, L, t, **sky)
    render(c, world, cam, L)
    if ov:
        ov(c)
    if sc.get("sfx_draw"):
        for i, (tt, lab) in enumerate(sc["sfx_items"]):
            k = Tm.t - tt
            if 0 < k < 0.32:
                label(c, lab, W / 2 + (i - 1) * 180, 900 - (i % 2) * 60, 130, (255, 255, 255), 1, scale=eback(clamp(k / 0.12)), stroke=14)
    w, a = caption_word(scenes, t)
    if w:
        pop = eback(clamp((t - a) / 0.12))
        label(c, w, W / 2, 1180, 118, (255, 255, 255), 1, stroke=16, scale=0.85 + 0.15 * pop)
    total = _G["total"]
    fade = min(clamp(t / 0.4), clamp((total - t) / 0.6))
    if fade < 1:
        c.drawRect(skia.Rect.MakeWH(W, H), skia.Paint(Color4f=col4((0, 0, 0), 1 - fade)))
    return np.ascontiguousarray(surf.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType)[..., :3]).tobytes()


def main(name, out, preview_times=None):
    import importlib
    mod = importlib.import_module(name)
    scenes, total = build(mod)
    print("durée %.1fs" % total)
    if preview_times:
        _G.update(mod=mod, scenes=scenes, total=total, surf=skia.Surface(W, H))
        from PIL import Image
        ims = [Image.frombytes("RGB", (W, H), frame(int(tt * FPS))).resize((270, 480)) for tt in preview_times]
        cols = 6
        sheet = Image.new("RGB", (270 * cols, 480 * ((len(ims) + cols - 1) // cols)))
        for i, im in enumerate(ims):
            sheet.paste(im, ((i % cols) * 270, (i // cols) * 480))
        sheet.save(out)
        for i, s in enumerate(scenes):
            print(i, s["shot"].__name__ if hasattr(s["shot"], "__name__") else "", round(s["start"], 2), round(s["end"], 2))
        return
    audio = mix(scenes, total)
    wav = out.replace(".mp4", ".wav")
    sf.write(wav, audio.astype(np.float32), SR)
    nf = int(total * FPS)
    tmp = out.replace(".mp4", "_v.mp4")
    proc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                             "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    with mp.get_context("fork").Pool(4, initializer=_init, initargs=(name,)) as pool:
        for i, buf in enumerate(pool.imap(frame, range(nf), chunksize=6)):
            proc.stdin.write(buf)
            if i % 300 == 0:
                print(f"  {i}/{nf}", flush=True)
    proc.stdin.close(); proc.wait()
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-i", wav, "-c:v", "copy", "-af",
                    "loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", out], check=True)
    os.remove(tmp)
    print("OK ->", out)


if __name__ == "__main__":
    if len(sys.argv) > 3 and sys.argv[3] == "--preview":
        main(sys.argv[1], sys.argv[2], [float(x) for x in sys.argv[4:]])
    else:
        main(sys.argv[1], sys.argv[2])
