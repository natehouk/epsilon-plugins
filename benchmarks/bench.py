"""Self-benchmarks for every Epsilon plugin.

Usage:
    python3 benchmarks/bench.py <build-dir> [Plugin ...]     # writes benchmarks/results/<Plugin>.json

Each plugin is loaded once (VST3, Linux x64, built by build.sh at its release tag) and measured
offline at 48 kHz / 512-sample blocks. Only Epsilon builds are measured.
"""
import json
import os
import platform
import sys
import traceback

import numpy as np
import pedalboard as pb

from measure import (SR, at_freq, cpu_percent, cutoff_3db, db, inharmonic_db, impulse, latency, null_depth,
                     pink, play, response, rms, rt60, run, setp, show, sine, thd_n_db, true_peak_db)

HERE = os.path.dirname(os.path.abspath(__file__))
CPU_SECONDS = 10


def effect_cpu(p, seconds=CPU_SECONDS):
    x = pink(seconds, -18)
    return round(cpu_percent(lambda: p(x, SR, buffer_size=512, reset=False), seconds), 2)


def synth_cpu(p, notes, seconds=CPU_SECONDS):
    return round(cpu_percent(lambda: play(p, notes, seconds), seconds), 2)


def gain_db(p, freq, level):
    y = run(p, sine(freq, level, 2.0))
    return float(db(rms(y[:, -SR // 2:]) / rms(sine(freq, level, 0.5))))


def filter_metrics(p, cutoff):
    f, h = response(p)
    fc = cutoff_3db(f, h, ref_hz=cutoff / 10)
    slope = at_freq(f, h, cutoff * 8) - at_freq(f, h, cutoff * 4)
    return dict(set_cutoff_hz=cutoff, gain_at_cutoff_db=round(at_freq(f, h, cutoff), 2), measured_3db_hz=round(fc, 1),
                passband_db=round(at_freq(f, h, cutoff / 10), 2), slope_db_per_oct=round(slope, 1))


# ---------------- instruments ----------------

def synth_alias(p, note=93):
    """A6 (1760 Hz) held, filter open: non-harmonic energy relative to the harmonic series."""
    y = play(p, [note], 2.0)
    f0 = 440 * 2 ** ((note - 69) / 12)
    return dict(total_db=round(inharmonic_db(y, f0), 1), below_10khz_db=round(inharmonic_db(y, f0, 10000), 1),
                peak_dbfs=round(float(db(np.abs(y).max())), 1))


def bench_Monolith(p):
    r = {"cpu_1_voice_pct": synth_cpu(p, [48])}
    setp(p, voice_mode="Poly")
    r["cpu_10_voices_pct"] = synth_cpu(p, list(range(48, 68, 2)))
    setp(p, voice_mode="Mono", cutoff_hz=20000, resonance=0, filter_env_amt=0, drive=0, key_track=0)
    r["aliasing_A6"] = synth_alias(p)
    r["settings"] = show(p, "osc_shape", "cutoff_hz", "resonance", "drive")
    return r


def bench_Obsidian(p):
    r = {"cpu_1_voice_pct": synth_cpu(p, [48]), "cpu_8_voices_pct": synth_cpu(p, list(range(48, 64, 2)))}
    setp(p, filter_1_on=False, filter_2_on=False)
    for s in range(1, 9):
        if f"slot_{s}_bypass" in p.parameters:
            setp(p, **{f"slot_{s}_bypass": True})
    r["aliasing_A6"] = synth_alias(p)
    r["settings"] = show(p, "osc_1_wave", "voices", "filter_1_on")
    return r


def bench_Malachite(p):
    setp(p, sequencer="Off (MIDI)")
    r = {"cpu_1_voice_pct": synth_cpu(p, [36])}
    setp(p, waveform="Saw", cutoff=100, resonance=0, env_mod=0)
    r["aliasing_A6"] = synth_alias(p)
    r["settings"] = show(p, "waveform", "sequencer", "cutoff", "resonance")
    return r


# ---------------- filters ----------------

def bench_filter(p, **settings):
    r = {"cpu_default_pct": effect_cpu(p), "latency_samples": latency(p)}
    setp(p, **settings)
    r["lowpass_1khz"] = filter_metrics(p, 1000)
    r["thd_n_200hz_-12dbfs_db"] = round(thd_n_db(run(p, sine(200, -12, 2.0)), 200), 1)
    r["settings"] = show(p, *settings)
    return r


def bench_Caldera(p):
    return bench_filter(p, filter_1_type="Low Pass", filter_1_freq_hz=1000, filter_1_peak=0)


def bench_Basalt(p):
    return bench_filter(p, filter_1_type="Low Pass", filter_1_freq_hz=1000, filter_1_resonance=0)


def bench_Flint(p):
    return bench_filter(p, response="Low Pass", frequency_hz=1000, peak=0)


# ---------------- dynamics ----------------

def bench_Gneiss(p):
    r = {"cpu_default_pct": effect_cpu(p), "latency_samples": latency(p)}
    setp(p, threshold_db=-30, ratio=4, knee_db=0, attack_ms=1, release_ms=50, gain_db=0)
    levels = list(range(-60, 1, 6))
    out = [gain_db(p, 1000, l) + l for l in levels]
    above = [(l, o) for l, o in zip(levels, out) if l >= -18]
    slope = np.polyfit([a for a, _ in above], [b for _, b in above], 1)[0]
    r["static_curve"] = {str(l): round(o, 2) for l, o in zip(levels, out)}
    r["measured_ratio"] = round(1 / slope, 2)
    r["gain_error_below_threshold_db"] = round(out[0] - levels[0], 3)
    r["settings"] = show(p, "style", "threshold_db", "ratio", "knee_db", "attack_ms", "release_ms")
    return r


def bench_Granite(p):
    r = {"cpu_default_pct": effect_cpu(p), "latency_samples": latency(p)}
    rng = np.random.default_rng(3)
    x = pink(6, -20)
    for i in rng.integers(0, x.shape[1] - 2000, 120):  # drum-like transients
        x[:, i:i + 400] += (np.exp(-np.arange(400) / 60) * rng.uniform(0.3, 0.5)).astype(np.float32)
    x *= 10 ** (-6 / 20) / np.abs(x).max()
    setp(p, gain_db=12)
    ceiling = p.parameters["output_level_db"].string_value.strip()
    for osr in p.parameters["oversampling"].valid_values:
        setp(p, oversampling=osr)
        y = run(p, x)[:, SR // 2:]
        r[f"oversampling_{osr.strip().replace(' ', '')}"] = dict(
            sample_peak_dbfs=round(float(db(np.abs(y).max())), 2), true_peak_dbfs=round(true_peak_db(y), 2),
            latency_samples=latency(p))
    r["ceiling"] = ceiling
    r["settings"] = show(p, "style", "gain_db", "lookahead_ms", "attack_ms", "release_ms")
    return r


def bench_Slate(p):
    r = {"cpu_default_pct": effect_cpu(p), "latency_samples": latency(p)}
    setp(p, threshold_db=-40)
    r["gain_open_-20dbfs_db"] = round(gain_db(p, 1000, -20), 2)
    r["gain_closed_-60dbfs_db"] = round(gain_db(p, 1000, -60), 2)
    r["settings"] = show(p, "style", "threshold_db", "range_db", "ratio")
    return r


def bench_Talc(p):
    r = {"cpu_default_pct": effect_cpu(p), "latency_samples": latency(p)}
    r["gain_500hz_-12dbfs_db"] = round(gain_db(p, 500, -12), 2)
    r["gain_7khz_-12dbfs_db"] = round(gain_db(p, 7000, -12), 2)
    r["settings"] = show(p, "mode", "threshold_db", "range_db", "processing")
    return r


def bench_Schist(p):
    r = {"cpu_default_pct": effect_cpu(p), "latency_samples": latency(p), "null_default_db": round(null_depth(p), 1)}
    for b in range(1, 7):
        setp(p, **{f"band_{b}_enabled": True})
    r["cpu_6_bands_pct"] = effect_cpu(p)
    r["settings"] = show(p, "processing_mode", "band_1_threshold_db", "band_1_ratio")
    for mode in p.parameters["processing_mode"].valid_values:
        setp(p, processing_mode=mode)
        r[f"latency_{mode.strip().replace(' ', '_').lower()}_samples"] = latency(p)
    return r


# ---------------- EQ ----------------

def bench_Mica(p):
    r = {"cpu_default_pct": effect_cpu(p), "latency_samples": latency(p), "null_default_db": round(null_depth(p), 1)}
    setp(p, band_1_used=True, band_1_shape="Bell", band_1_frequency_hz=1000, band_1_gain_db=6, band_1_q=1)
    f, h = response(p)
    i = int(np.argmax(h[(f > 100) & (f < 10000)])) + int(np.argmax(f > 100))
    r["bell_1khz_+6db"] = dict(peak_hz=round(float(f[i]), 1), peak_db=round(float(h[i]), 2))
    setp(p, band_1_shape="Low Cut", band_1_frequency_hz=100, band_1_slope="48 dB/oct", band_1_gain_db=0)
    f, h = response(p, seconds=4.0)
    r["low_cut_100hz_48db"] = dict(at_100hz_db=round(at_freq(f, h, 100), 2),
                                   slope_db_per_oct=round(at_freq(f, h, 50) - at_freq(f, h, 25), 1))
    setp(p, band_1_shape="Bell", band_1_gain_db=6, band_1_frequency_hz=1000)
    for b in range(2, 25):
        if f"band_{b}_used" in p.parameters:
            setp(p, **{f"band_{b}_used": True, f"band_{b}_frequency_hz": 30 * 1.3 ** b, f"band_{b}_gain_db": (b % 3) - 1})
    r["cpu_24_bands_pct"] = effect_cpu(p)
    for mode in p.parameters["processing_mode"].valid_values:
        setp(p, processing_mode=mode)
        r[f"latency_{mode.strip().replace(' ', '_').lower()}_samples"] = latency(p)
    return r


# ---------------- distortion ----------------

def bench_Magma(p):
    r = {"cpu_default_pct": effect_cpu(p), "latency_samples": latency(p)}
    y = run(p, sine(2500, -6, 2.0))
    r["default_2_5khz_-6dbfs"] = dict(thd_n_db=round(thd_n_db(y, 2500), 1), inharmonic_db=round(inharmonic_db(y, 2500), 1))
    r["settings"] = show(p, "band_1_style", "band_1_drive", "band_1_mix")
    return r


# ---------------- time-based ----------------

def bench_Strata(p):
    r = {"cpu_default_pct": effect_cpu(p)}
    setp(p, left_sync="Free", right_sync="Free", left_time_ms=250, right_time_ms=375, left_feedback=0, right_feedback=0,
         mix=1, filter_1_on=False, filter_2_on=False, smoothing_s=0.001)
    at = 4800
    for mode in p.parameters["mode"].valid_values:
        setp(p, mode=mode)
        y = run(p, impulse(1.5, at=at, amp=0.25))
        res = {}
        for c, side in ((0, "left"), (1, "right")):
            shown = float(p.parameters[f"{side}_time_ms"].string_value)
            got = (int(np.argmax(np.abs(y[c]))) - at) / SR * 1000
            res[side] = dict(displayed_ms=round(shown, 3), measured_ms=round(got, 3), error_ms=round(got - shown, 3))
        r[f"echo_{mode.strip().lower()}"] = res
    return r


def bench_Geode(p):
    r = {"cpu_default_pct": effect_cpu(p)}
    at = 4800
    y = run(p, impulse(1.0, at=at, amp=0.5))
    r["dry_latency_samples"] = int(np.argmax(np.abs(y[0]) > 1e-6) - at)
    setp(p, mix=100, predelay_ms=0)
    for space in (0.0, 0.5, 1.0):
        p.parameters["space"].raw_value = space
        y = run(p, impulse(14.0, at=at, amp=0.5))
        r[f"rt60_space_{p.parameters['space'].string_value.strip()}_s"] = round(rt60(y, at), 2)
    r["settings"] = show(p, "decay_rate", "character", "mix")
    return r


SUITES = {k[len("bench_"):]: v for k, v in globals().items() if k.startswith("bench_") and k != "bench_filter"}


def main():
    build = sys.argv[1]
    names = sys.argv[2:] or list(SUITES)
    versions = {}
    vf = os.path.join(build, "versions.txt")
    if os.path.exists(vf):
        for line in open(vf):
            n, tag, sha = line.split()
            versions[n] = (tag, sha)
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    for name in names:
        path = os.path.join(build, name.lower(), "bin", f"{name}.vst3")
        out = dict(plugin=name, version=versions.get(name, ("?", "?"))[0], commit=versions.get(name, ("?", "?"))[1],
                   host=f"pedalboard {pb.__version__}", sample_rate=SR, block=512,
                   machine=platform.processor() or platform.machine())
        try:
            out["results"] = SUITES[name](pb.load_plugin(path))
        except Exception:
            out["error"] = traceback.format_exc(limit=3)
        with open(os.path.join(HERE, "results", f"{name}.json"), "w") as f:
            json.dump(out, f, indent=1)
        print(name, json.dumps(out.get("results", out.get("error")))[:600], flush=True)


if __name__ == "__main__":
    main()
