"""Signal generators and measurements shared by the benchmark suites.

Everything runs offline at 48 kHz in 512-sample blocks through pedalboard's VST3 host.
"""
import time

import numpy as np
from scipy.signal import resample_poly
from scipy.signal.windows import blackmanharris

SR = 48000
BLOCK = 512


def db(x):
    return 20 * np.log10(np.maximum(np.abs(x), 1e-12))


def rms(x):
    return float(np.sqrt(np.mean(np.square(x, dtype=np.float64))))


# ---------- parameters ----------

def setp(plugin, **values):
    """Set parameters by name in their display units ("1000" Hz, "Bell", ...). Fails loudly."""
    for name, value in values.items():
        if name not in plugin.parameters:
            close = [k for k in plugin.parameters if name.split("_")[0] in k][:12]
            raise KeyError(f"no parameter {name!r}; similar: {close}")
        tries = [value] + ([float(value), "On" if value else "Off"] if isinstance(value, bool) else [])
        for i, v in enumerate(tries):
            try:
                setattr(plugin, name, v)
                break
            except Exception:
                if i == len(tries) - 1:
                    raise


def show(plugin, *names):
    return {n: plugin.parameters[n].string_value.strip() for n in names}


# ---------- signals ----------

def sine(freq, level_db, seconds, channels=2):
    t = np.arange(int(seconds * SR)) / SR
    x = (10 ** (level_db / 20) * np.sqrt(2)) * np.sin(2 * np.pi * freq * t)  # level is RMS dBFS
    return np.tile(x.astype(np.float32), (channels, 1))


def impulse(seconds, at=4800, amp=1.0, channels=2):
    x = np.zeros((channels, int(seconds * SR)), np.float32)
    x[:, at] = amp
    return x


def pink(seconds, level_db=-18, channels=2, seed=1):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    spec = np.fft.rfft(rng.standard_normal((channels, n)), axis=1)
    f = np.maximum(np.fft.rfftfreq(n, 1 / SR), 20)
    x = np.fft.irfft(spec / np.sqrt(f), n=n, axis=1)
    x *= 10 ** (level_db / 20) / np.sqrt(np.mean(x ** 2))
    return x.astype(np.float32)


# ---------- rendering ----------

def run(plugin, x):
    plugin.reset()
    return plugin(x, SR, buffer_size=BLOCK, reset=True)


def play(synth, notes, seconds, velocity=100, start=0.05):
    """Hold `notes` (MIDI numbers) from `start` to the end of the render."""
    import mido
    msgs = [mido.Message("note_on", note=n, velocity=velocity, time=start) for n in notes]
    synth.reset()
    return synth(msgs, duration=seconds, sample_rate=SR, buffer_size=BLOCK, reset=True)


def cpu_percent(render, seconds, repeats=3):
    """Best of `repeats` renders, as % of one core in real time (includes host overhead)."""
    best = 1e9
    for _ in range(repeats):
        t0 = time.perf_counter()
        render()
        best = min(best, time.perf_counter() - t0)
    return 100 * best / seconds


# ---------- measurements ----------

def latency(plugin):
    """Latency the plugin declares to the host, in samples (read after processing, so mode changes apply).

    pedalboard compensates for this when rendering, so output is already time-aligned with the input.
    """
    run(plugin, impulse(0.2))
    return int(plugin.reported_latency_samples)


def null_depth(plugin, seconds=4):
    """How far the (host-compensated) output differs from the input, in dB below the input."""
    x = pink(seconds, -18)
    y = run(plugin, x)
    n = x.shape[1] - SR // 10
    err = rms(y[:, :n] - x[:, :n])
    return float("-inf") if err == 0 else float(db(err / rms(x[:, :n])))


def spectrum(y, seconds=1.0):
    """Blackman-Harris power spectrum of the last `seconds` of channel 0, 1/seconds Hz bins."""
    n = int(seconds * SR)
    seg = y[0, -n:].astype(np.float64)
    return np.abs(np.fft.rfft(seg * blackmanharris(n))) ** 2, SR / n


def fundamental(p, df, guess):
    lo, hi = int(guess * 0.9 / df), int(guess * 1.1 / df)
    k = lo + int(np.argmax(p[lo:hi]))
    a, b, c = np.log(p[k - 1:k + 2] + 1e-30)
    return (k + 0.5 * (a - c) / (a - 2 * b + c)) * df


def harmonic_split(y, f0_guess):
    """Energy at harmonics of the measured fundamental vs. everything else (aliasing + noise)."""
    p, df = spectrum(y)
    f0 = fundamental(p, df, f0_guess)
    mask = np.zeros(len(p), bool)
    for k in range(1, int((SR / 2) / f0) + 1):
        c = int(round(k * f0 / df))
        mask[max(c - 4, 0):c + 5] = True
    mask[:5] = False  # DC
    fund = np.zeros(len(p), bool)
    c = int(round(f0 / df))
    fund[c - 4:c + 5] = True
    other = p[~mask].sum() - p[:5].sum()
    return dict(f0=f0, fund=p[fund].sum(), harm=p[mask & ~fund].sum(), other=other)


def thd_n_db(y, f0):
    s = harmonic_split(y, f0)
    return float(10 * np.log10((s["harm"] + s["other"]) / s["fund"]))


def inharmonic_db(y, f0, below_hz=None):
    """Non-harmonic energy (aliasing + noise) relative to the harmonic series, in dB.

    With `below_hz`, only non-harmonic energy under that frequency is counted (the audible-band figure).
    """
    p, df = spectrum(y)
    s = harmonic_split(y, f0)
    if below_hz is None:
        other = s["other"]
    else:
        mask = np.zeros(len(p), bool)
        for k in range(1, int((SR / 2) / s["f0"]) + 1):
            c = int(round(k * s["f0"] / df))
            mask[max(c - 4, 0):c + 5] = True
        mask[:5] = True
        lim = int(below_hz / df)
        other = p[:lim][~mask[:lim]].sum()
    return float(10 * np.log10(max(other, 1e-30) / (s["fund"] + s["harm"])))


def response(plugin, amp=0.01, seconds=2.0):
    """Magnitude response (dB) from an impulse; for linear settings. Returns (freqs, dB)."""
    at = 4800
    y = run(plugin, impulse(seconds, at=at, amp=amp))[0, at:]
    h = np.fft.rfft(y) / amp
    return np.fft.rfftfreq(len(y), 1 / SR), db(h)


def at_freq(f, h, hz):
    return float(np.interp(hz, f, h))


def cutoff_3db(f, h, ref_hz=100, lowpass=True):
    ref = at_freq(f, h, ref_hz)
    idx = np.where((f > ref_hz) & (h < ref - 3))[0] if lowpass else np.where((f < ref_hz) & (h < ref - 3))[0]
    if not len(idx):
        return float("nan")
    i = idx[0] if lowpass else idx[-1]
    j = i - 1 if lowpass else i + 1
    return float(np.interp(ref - 3, sorted([h[i], h[j]]), [f[i], f[j]] if h[i] < h[j] else [f[j], f[i]]))


def true_peak_db(y):
    return float(db(np.abs(resample_poly(y, 4, 1, axis=1)).max()))


def rt60(y, start):
    """RT60 from a T30 fit (-5 to -35 dB) on the Schroeder decay of channel 0."""
    e = np.square(y[0, start:].astype(np.float64))
    sch = 10 * np.log10(np.maximum(np.cumsum(e[::-1])[::-1] / e.sum(), 1e-30))
    i5, i35 = np.argmax(sch <= -5), np.argmax(sch <= -35)
    if i35 <= i5:
        return float("nan")
    t = np.arange(i5, i35) / SR
    slope = np.polyfit(t, sch[i5:i35], 1)[0]
    return float(-60 / slope)
