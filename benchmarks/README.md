# Benchmarks

Measurements of Epsilon's own plugin builds: CPU, latency, filter and EQ response, dynamics curves, limiter peaks, oscillator aliasing, reverb decay and delay timing. Only Epsilon plugins are measured; there are no comparisons with other products.

## Run

Linux x64 with a C++ toolchain, the X11/Cairo dev headers DPF needs, and Python 3:

```
pip install pedalboard numpy scipy mido
benchmarks/build.sh /tmp/epsilon-build            # VST3 of every plugin at its latest release tag
cd benchmarks && python3 bench.py /tmp/epsilon-build [Plugin ...]
python3 report.py                                  # rewrites the Benchmarks section of the top-level README
```

`bench.py` writes one JSON file per plugin to `results/`, including the release tag and commit it measured, the host, and every setting a test changed. A build that isn't a release (for example a plugin's `main` after a merged fix, with `main` instead of a tag in `versions.txt`) goes to `results/unreleased/` instead. `report.py` lists those under the table as merged changes awaiting a release. Delete the file once that change ships in a tagged release and the release has been re-measured.

## Method

- Offline rendering through [pedalboard](https://github.com/spotify/pedalboard)'s VST3 host at 48 kHz in 512-sample blocks, stereo.
- **CPU** is the best of three 10-second renders, as a percentage of one core in real time. It includes host overhead and depends on the machine (recorded in each result), so compare plugins measured on the same machine rather than treating the numbers as absolute.
- **Latency** is what the plugin reports to the host, in samples, read after each setting change. The host compensates for it, so the other measurements are time-aligned.
- **Delay times** (Strata) are compared with the time the plugin displays. The host can only set parameters to the nearest step it resolves: asking for 375 ms gave 376.906 ms.
- **Filter response** comes from a −40 dBFS impulse, to stay in the linear region of saturating filters.
- **Static compressor curve** uses 1 kHz sines at RMS levels from −60 to 0 dBFS. The detector responds to peaks, so a sine starts compressing about 3 dB below the threshold (a sine's peak sits 3 dB above its RMS).
- **True peak** is measured after 4× oversampling.
- **Aliasing** (synths) is the energy that is not on the harmonic series of the measured fundamental, relative to the harmonic energy, on a held A6 (1760 Hz) with the filter open. Lower is cleaner. It includes noise, so it is an upper bound on aliasing (the noise floor measured about −180 dB, so in practice it is aliasing). It is given in total and counting only what folds back below 10 kHz, since most of it lands near Nyquist.
- **RT60** is a T30 fit on the Schroeder decay of a 100% wet impulse response.
