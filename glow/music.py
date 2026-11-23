"""Musique d'ambiance générée (piano doux + nappe + réverb) et petits sons de transition."""
import numpy as np

SR = 24000


def _note(f, dur, kind="piano"):
    n = int(dur * SR)
    t = np.arange(n) / SR
    if kind == "piano":
        sig = (np.sin(2 * np.pi * f * t) + 0.45 * np.sin(4 * np.pi * f * t) * np.exp(-t * 3)
               + 0.18 * np.sin(6 * np.pi * f * t) * np.exp(-t * 5))
        env = np.minimum(1, t / 0.006) * np.exp(-t * 1.6)
    else:  # nappe
        sig = sum(np.sin(2 * np.pi * f * d * t + ph) for d, ph in ((1, 0), (1.004, 1.3), (0.996, 2.1), (2.001, 0.4)))
        sig = sig / 4
        a, r = 1.6, 1.6
        env = np.minimum(1, t / a) * np.minimum(1, (dur - t) / r).clip(0)
    return sig * env


def _reverb(x, secs=3.0, mix=0.35, seed=0):
    rng = np.random.default_rng(seed)
    n = int(secs * SR)
    t = np.arange(n) / SR
    ir = rng.normal(0, 1, n) * np.exp(-t * 2.3)
    ir[0] = 0
    ir /= np.sqrt((ir ** 2).sum())
    L = len(x) + n
    nfft = 1 << (L - 1).bit_length()
    wet = np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[:len(x)]
    return x * (1 - mix) + wet * mix * 1.4


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def ambient(total, scene_starts, opts):
    n = int(total * SR) + SR * 4
    out = np.zeros(n)
    bpm = opts.get("bpm", 68)
    beat = 60 / bpm
    bar = beat * 4
    prog = opts.get("prog", [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]])  # Am F C G
    rng = np.random.default_rng(opts.get("seed", 2))
    nb = int(total / bar) + 2
    for b in range(nb):
        st = int(b * bar * SR)
        ch = prog[b % len(prog)]
        # nappe
        for m in ch:
            s = _note(hz(m - 12), bar + 1.6, "pad")
            e = min(n, st + len(s)); out[st:e] += 0.05 * s[:e - st]
        # basse
        s = _note(hz(ch[0] - 24), bar + 1.0, "pad")
        e = min(n, st + len(s)); out[st:e] += 0.07 * s[:e - st]
        # piano : arpège clairsemé
        pattern = [0, 2, 1, 2] if b % 2 == 0 else [0, 1, 2, 1]
        for i, idx in enumerate(pattern):
            if rng.random() < 0.18:
                continue
            m = ch[idx] + 12 + (12 if (i == 3 and rng.random() < 0.4) else 0)
            s = _note(hz(m), 2.5, "piano")
            p = st + int(i * beat * SR)
            e = min(n, p + len(s))
            if p < n:
                out[p:e] += 0.055 * s[:e - p] * (0.8 + 0.4 * rng.random())
    # entrée progressive
    t = np.arange(n) / SR
    out *= np.minimum(1, t / 2.5)
    # transitions : souffle doux + sub
    for i, s in enumerate(scene_starts[1:], 1):  # noqa
        a = int(max(0, s - 0.25) * SR)
        m = int(0.6 * SR)
        noise = rng.normal(0, 1, m)
        noise = np.convolve(noise, np.ones(12) / 12, "same")
        env = np.sin(np.linspace(0, np.pi, m)) ** 2
        e = min(n, a + m); out[a:e] += 0.018 * (noise * env)[:e - a]
    for si in opts.get("hit_scenes", []):
        a = int((scene_starts[si] + 0.3) * SR)
        m = int(1.8 * SR); tt = np.arange(m) / SR
        boom = np.sin(2 * np.pi * (42 + 30 * np.exp(-tt * 6)) * tt) * np.exp(-tt * 2.2)
        e = min(n, a + m); out[a:e] += 0.22 * boom[:e - a]
    out = _reverb(out, 3.2, 0.4)
    # fondu de fin
    end = int(total * SR)
    fo = int(2.0 * SR)
    out[end - fo:end] *= np.linspace(1, 0, fo)
    out[end:] = 0
    return out[:end] * opts.get("gain", 1.0)
