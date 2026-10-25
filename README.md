# Epsilon Audio Plugins

**Free, open-source audio plugins from Epsilon Records, for macOS, Windows and Linux (VST3 · AU · CLAP · VST2).**

Every plugin is MIT-licensed, built on [DPF](https://github.com/DISTRHO/DPF), and ships as universal macOS, Windows x64 and Linux x64 builds from GitHub Actions. This repository is the index; each plugin lives in its own repo.

## The plugins

| | Plugin | Type | Version | Highlights |
|---|---|---|---|---|
| <img src="https://raw.githubusercontent.com/natehouk/monolith/main/screenshot.png" width="160"> | [**Monolith**](https://github.com/natehouk/monolith) | Synth (instrument) | 1.3 | Morphing single oscillator + sub + noise, 12 dB SVF filter, mono or 10-voice poly. 42 factory presets. |
| <img src="https://raw.githubusercontent.com/natehouk/caldera/main/screenshot.png" width="160"> | [**Caldera**](https://github.com/natehouk/caldera) | Dual filter (effect) | 1.0.1 | Two filters, seven styles from Clean to Raw, serial/parallel, 2 LFOs, envelope follower, MIDI key tracking. 41 factory presets. |
| <img src="https://raw.githubusercontent.com/natehouk/obsidian/main/screenshot.png" width="160"> | [**Obsidian**](https://github.com/natehouk/obsidian) | Polysynth (instrument) | 1.0.1 | Two oscillators, two filters (serial / parallel / split), up to 24 voices with unison, modulation matrix. 42 factory presets. |
| <img src="https://raw.githubusercontent.com/natehouk/strata/main/screenshot.png" width="160"> | [**Strata**](https://github.com/natehouk/strata) | Tape delay (effect) | 1.0.1 | Stereo delay with tape or stretch mode, Caldera's filters in the feedback loop, tap tempo, Obsidian's modulation. 43 factory presets. |
| <img src="https://raw.githubusercontent.com/natehouk/basalt/main/screenshot.png" width="160"> | [**Basalt**](https://github.com/natehouk/basalt) | Dual filter, live (effect) | 1.1.1 | Caldera stripped down for performance: big controls, large drag display, Link Filters, undo/redo, hover tips and a built-in help window. 31 factory presets. |
| <img src="https://raw.githubusercontent.com/natehouk/gneiss/main/screenshot.png" width="160"> | [**Gneiss**](https://github.com/natehouk/gneiss) | Compressor (effect) | 1.0.1 | Clean, Classic and Opto styles, mid/side, external sidechain with 48 dB/oct detector filters, A/B and undo/redo, zero latency. 31 factory presets. |
| <img src="https://raw.githubusercontent.com/natehouk/mica/main/screenshot.png" width="160"> | [**Mica**](https://github.com/natehouk/mica) | Equalizer (effect) | 1.0.1 | Up to 24 bands (bell, shelf, cut up to 48 dB/oct), zero-latency or linear-phase, mid/side and per-band channel, spectrum analyser, A/B and undo/redo. 31 factory presets. |
| <img src="https://raw.githubusercontent.com/natehouk/flint/main/screenshot.png" width="160"> | [**Flint**](https://github.com/natehouk/flint) | Saturating filter (effect) | 1.0.1 | Monolith's 12 dB filter as a lightweight low/high pass with input drive, self-oscillation and an envelope follower (±6 octaves). 24 factory presets. |
| <img src="https://raw.githubusercontent.com/natehouk/granite/main/screenshot.png" width="160"> | [**Granite**](https://github.com/natehouk/granite) | Limiter (effect) | 1.0.1 | Exact brickwall limiting, four styles, up to 10 ms look-ahead, 4× linear-phase oversampling, dither with noise shaping, true-peak and K-System meters. 27 factory presets. |
| <img src="https://raw.githubusercontent.com/natehouk/slate/main/screenshot.png" width="160"> | [**Slate**](https://github.com/natehouk/slate) | Gate (effect) | 1.0 | Gate and expander with five styles (including upward), up to 100:1 and 80 dB range, lookahead, mid/side, external sidechain with 48 dB/oct filters, MIDI triggering. 32 factory presets. |
| <img src="https://raw.githubusercontent.com/natehouk/magma/main/screenshot.png" width="160"> | [**Magma**](https://github.com/natehouk/magma) | Multiband distortion (effect) | 1.0 | Up to six bands, 16 distortion styles (tube, tape, amp, saturation, experimental), 50 drag-and-drop modulation slots with XLFOs, envelopes, envelope followers and XY pads. 42 factory presets. |
| <img src="https://raw.githubusercontent.com/natehouk/talc/main/screenshot.png" width="160"> | [**Talc**](https://github.com/natehouk/talc) | De-esser (effect) | 1.0 | Single-vocal or allround detection, wide-band or linear-phase split-band, sidechain filters set over a live spectrum, up to 15 ms look-ahead, sibilance display. 22 factory presets. |
| <img src="https://raw.githubusercontent.com/natehouk/schist/main/screenshot.png" width="160"> | [**Schist**](https://github.com/natehouk/schist) | Multiband compressor (effect) | 1.0 | Up to six freely placed bands that compress or expand, downward or upward; dynamic, linear or minimum phase; per-band sidechain and custom detection range. 39 factory presets. |
| <img src="https://raw.githubusercontent.com/natehouk/geode/main/screenshot.png" width="160"> | [**Geode**](https://github.com/natehouk/geode) | Reverb (effect) | 1.0 | Stepless space control across fourteen room models, six-band decay rate EQ, six-band post EQ, tempo-synced predelay, zero latency. 35 factory presets. |
| <img src="https://raw.githubusercontent.com/natehouk/malachite/main/screenshot.png" width="160"> | [**Malachite**](https://github.com/natehouk/malachite) | Acid bass synth (instrument) | 1.0 | Saw or square oscillator, squelchy resonant filter, accent with build-up, slide, and a 16-step sequencer with 64 patterns that follows the host tempo. 22 factory sound presets. |

## How they fit together

```
Monolith ──filter──► Caldera ──filters──► Strata (filters in the feedback loop)
    │                   │
    │                   └──simplified──► Basalt (live version)
    ├──filter──► Obsidian ──modulation system──► Strata
    └──filter──► Flint (single filter + envelope follower)
```

- **Monolith's filter** is a style in Caldera, Obsidian, Strata and Basalt (where it's called *Fat*), and Flint is built on it.
- **Strata** combines Caldera's filters with Obsidian's modulation system.
- **Basalt** is Caldera with the modulation removed and the controls enlarged for live use.
- **Gneiss** is the first dynamics plugin, a stereo compressor with sidechain.
- **Mica** is the first mixing EQ.
- **Flint** is a small, CPU-light filter with an envelope follower.
- **Granite** is a look-ahead brickwall limiter for mastering.
- **Slate** is a gate and expander that can also be played from MIDI.
- **Magma** is a multiband distortion with its own drag-and-drop modulation system.
- **Talc** is a de-esser with single-vocal detection and linear-phase split-band processing.
- **Schist** is a multiband compressor and expander with freely placed bands.
- **Geode** is the first reverb, an algorithmic design with a decay rate EQ.
- **Malachite** is an acid bass synth with its own step sequencer, the first plugin based on classic hardware rather than a FabFilter product.

## Download

Each plugin's **Releases** page has three zips:

| Platform | Contains |
|---|---|
| macOS 10.13+ (Apple Silicon + Intel) | VST3, AU, CLAP |
| Windows x64 | VST3, CLAP, VST2 |
| Linux x64 | VST3, CLAP, VST2 |

| Plugin | Latest release |
|---|---|
| Monolith | [natehouk/monolith/releases](https://github.com/natehouk/monolith/releases/latest) |
| Caldera | [natehouk/caldera/releases](https://github.com/natehouk/caldera/releases/latest) |
| Obsidian | [natehouk/obsidian/releases](https://github.com/natehouk/obsidian/releases/latest) |
| Strata | [natehouk/strata/releases](https://github.com/natehouk/strata/releases/latest) |
| Basalt | [natehouk/basalt/releases](https://github.com/natehouk/basalt/releases/latest) |
| Gneiss | [natehouk/gneiss/releases](https://github.com/natehouk/gneiss/releases/latest) |
| Mica | [natehouk/mica/releases](https://github.com/natehouk/mica/releases/latest) |
| Flint | [natehouk/flint/releases](https://github.com/natehouk/flint/releases/latest) |
| Granite | [natehouk/granite/releases](https://github.com/natehouk/granite/releases/latest) |
| Slate | [natehouk/slate/releases](https://github.com/natehouk/slate/releases/latest) |
| Magma | [natehouk/magma/releases](https://github.com/natehouk/magma/releases/latest) |
| Talc | [natehouk/talc/releases](https://github.com/natehouk/talc/releases/latest) |
| Schist | [natehouk/schist/releases](https://github.com/natehouk/schist/releases/latest) |
| Geode | [natehouk/geode/releases](https://github.com/natehouk/geode/releases/latest) |
| Malachite | [natehouk/malachite/releases](https://github.com/natehouk/malachite/releases/latest) |

### Install

| Platform | Copy | To |
|---|---|---|
| macOS | `.vst3` / `.component` / `.clap` | `~/Library/Audio/Plug-Ins/VST3` / `Components` / `CLAP` |
| Windows | `.vst3` (folder) / `.clap` | `C:\Program Files\Common Files\VST3\` / `CLAP\` |
| Linux | `.vst3` / `.clap` | `~/.vst3/` / `~/.clap/` |

**macOS:** builds are ad-hoc signed, not notarized. After copying, clear the quarantine flag for all Epsilon plugins at once:

```
xattr -dr com.apple.quarantine ~/Library/Audio/Plug-Ins/*/{Monolith,Caldera,Obsidian,Strata,Basalt,Gneiss,Mica,Flint,Granite,Slate,Magma,Talc,Schist,Geode,Malachite}*
```

**MIDI on effects:** Caldera, Strata, Magma and Slate accept MIDI (key tracking, MIDI-triggered envelopes, LFO retrigger, MIDI modulation sources, gate triggering). In Logic Pro, insert them as **AU MIDI-controlled effects**; in other DAWs, route a MIDI track to the plugin.

## Common to every plugin

- **Factory presets** browsable from the plugin header.
- **MIDI Learn and user presets** saved as small text files that load the same on every OS (Caldera, Obsidian, Strata, Basalt, Gneiss, Mica, Flint, Granite, Slate, Magma, Talc, Schist, Geode, Malachite; Monolith leaves these to the DAW).
- **Built from published DSP techniques**: PolyBLEP oscillators, Zavalishin topology-preserving state-variable filters, one-pole envelopes.
- **Tests** in each repo's `tests/` folder.
- **Build from source** with DPF:

  ```
  git clone --recursive https://github.com/DISTRHO/DPF.git dpf
  make -C plugins/<Name>                    # Linux / macOS (macOS also builds the AU)
  make -C plugins/<Name> WINDOWS=true CC=x86_64-w64-mingw32-gcc CXX=x86_64-w64-mingw32-g++
  ```

<!-- benchmarks:start -->
## Benchmarks

Measured from each plugin's Linux x64 VST3 at its release tag, rendered offline at 48 kHz in 512-sample blocks. CPU is the share of one core, including host overhead, on a 2-vCPU cloud Linux machine; instruments are measured holding one note. Latency is what the plugin reports to the host. Method, scripts and the full per-plugin results are in [`benchmarks/`](benchmarks).

| Plugin | Version | CPU | Latency | Key measurements |
|---|---|---|---|---|
| Monolith | v1.3 | 1.2% | — | 10 voices 5.6% CPU; aliasing at A6 −31.2 dB (−38.2 dB below 10 kHz) |
| Caldera | v1.0.1 | 0.9% | 0 | 1 kHz low-pass, minimum resonance: −3 dB at 1006 Hz (passband −1.8 dB), 26.7 dB/oct roll-off; THD+N −36.9 dB (200 Hz, −12 dBFS) |
| Obsidian | v1.0.1 | 1.2% | — | 8 voices 5.8% CPU; aliasing at A6 −28.9 dB (−52.3 dB below 10 kHz) |
| Strata | v1.0.1 | 0.8% | — | echoes land within 0.010 ms of the displayed delay time (Tape and Stretch) |
| Basalt | v1.1.1 | 1.7% | 0 | 1 kHz low-pass, minimum resonance: −3 dB at 1000 Hz, 26.7 dB/oct roll-off; THD+N −35.5 dB (200 Hz, −12 dBFS) |
| Gneiss | v1.0.1 | 0.4% | 0 | 4:1 above −30 dB measures 3.95:1; 0.00 dB gain change below threshold |
| Mica | v1.0.1 | 0.1% | 0 | flat: bit-exact; +6 dB bell at 1 kHz measures +5.99 dB at 1000 Hz; 48 dB/oct cut measures 48.1 dB/oct; 24 bands 2.0% CPU; linear phase 6144 smp (128.0 ms) |
| Flint | v1.0.1 | 0.4% | 0 | 1 kHz low-pass, minimum resonance: −3 dB at 655 Hz, 12.9 dB/oct roll-off; THD+N −42.2 dB (200 Hz, −12 dBFS) |
| Granite | v1.0.1 | 0.8% | 96 smp (2.0 ms) | +12 dB into a −0.1 dB ceiling: sample peak −0.10 dBFS; true peak by oversampling: Off +1.00, 2x +0.11, 4x −0.02 dBTP |
| Slate | v1.0 | 0.6% | 0 | −40 dB threshold, 40 dB range: +0.0 dB at −20 dBFS, −40.0 dB at −60 dBFS |
| Magma | v1.0 | 0.8% | 32 smp (0.7 ms) | default (Warm Tube, drive 0.3), 2.5 kHz at −6 dBFS: THD+N −11.9 dB, non-harmonic −63.6 dB |
| Talc | v1.0 | 0.7% | 0 | default (8 dB range): 500 Hz tone +0.0 dB, 7 kHz tone −8.0 dB |
| Schist | v1.0 | 0.2% | 0 | flat: bit-exact; 6 bands 5.7% CPU; linear phase 4096 smp (85.3 ms) |
| Geode | v1.0 | 2.7% | 0 | RT60 at Space 0% 0.43 s, 50% 1.40 s, 100% 8.20 s |
| Malachite | v1.0 | 1.2% | 0 | aliasing at A6 −39.6 dB (−39.6 dB below 10 kHz) |

Merged changes awaiting a release, measured the same way:

- **Malachite** (`main` at [`0f491fa`](https://github.com/natehouk/malachite/commit/0f491fa), not yet in a release): aliasing at A6 −53.1 dB (−53.1 dB below 10 kHz); CPU 1.5%, latency 16 smp (0.3 ms).

<!-- benchmarks:end -->

## Lineage and clean-room note

The series works through FabFilter's catalogue in release order, recreating each product's feature set as a clean-room design. It now covers all fourteen products up to Pro-R:

| Epsilon plugin | Feature set of | Original release |
|---|---|---|
| Monolith | FabFilter One | 2002 |
| Caldera | FabFilter Volcano | May 2005 |
| Obsidian | FabFilter Twin | December 2005 |
| Strata | FabFilter Timeless | October 2006 |
| Basalt | FabFilter Simplon | October 2006 |
| Gneiss | FabFilter Pro-C | August 2007 |
| Mica | FabFilter Pro-Q | November 2009 |
| Flint | FabFilter Micro | January 2010 |
| Granite | FabFilter Pro-L | October 2010 |
| Slate | FabFilter Pro-G | May 2011 |
| Magma | FabFilter Saturn | March 2012 |
| Talc | FabFilter Pro-DS | October 2012 |
| Schist | FabFilter Pro-MB | October 2013 |
| Geode | FabFilter Pro-R | November 2016 |

Malachite starts a second line: classic hardware instruments, recreated the same way.

| Epsilon plugin | Feature set of | Original release |
|---|---|---|
| Malachite | Roland TB-303 | 1981 |

Each plugin was written from scratch, working only from public press releases, product descriptions, manuals and contemporary reviews. No FabFilter or Roland code, binaries, firmware, presets, artwork or trademarks were used, and every interface is an original design. FabFilter and Roland are trademarks of their owners; Epsilon Audio is not affiliated with or endorsed by either.

## Website

The [`site/`](site) folder is a static website for the series (no build step). Netlify serves it via [`netlify.toml`](netlify.toml); to preview locally, open `site/index.html` or run `npx serve site`.

## Machine-readable index

[`plugins.json`](plugins.json) lists every plugin with its repo, latest-release link, screenshot, type, version, formats and plugin IDs, plus the website URL, for websites or scripts that need the catalogue.

## License

The plugins and this index are released under the [MIT License](LICENSE). © 2026 Nate Houk / Epsilon Records.
