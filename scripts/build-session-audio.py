#!/usr/bin/env python3
"""Master the original session communication cues from two synthesized voice WAVs.

Requires numpy, scipy, soundfile. See 99_assets/audio/README.md for voice generation.
No TTS or audio processing runs in the website.
"""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
from scipy import signal
import soundfile as sf

RATE = 24000
DURATION = 6.4
ROOT = Path(__file__).resolve().parents[1]


def envelope(n, attack=.008, release=.055):
    env = np.ones(n)
    a, r = min(n // 2, int(RATE * attack)), min(n // 2, int(RATE * release))
    env[:a] = np.sin(np.linspace(0, np.pi / 2, a)) ** 2
    env[-r:] = np.cos(np.linspace(0, np.pi / 2, r)) ** 2
    return env


def band(audio, low, high):
    return signal.sosfilt(signal.butter(3, [low, high], btype='bandpass', fs=RATE, output='sos'), audio)


def delayed(audio, seconds):
    n = int(seconds * RATE)
    return np.pad(audio, (n, 0))[:len(audio)]


def radio_voice(path):
    dry, rate = sf.read(path)
    if dry.ndim != 1:
        dry = dry.mean(axis=1)
    if rate != RATE:
        dry = signal.resample_poly(dry, RATE, rate)
    # Preserve breaths/consonants while removing encoder padding at each edge.
    active = np.flatnonzero(np.abs(dry) > .002)
    if not len(active):
        raise ValueError('Silent voice source: ' + str(path))
    dry = dry[max(0, active[0] - 240):min(len(dry), active[-1] + 960)]
    if len(dry) / RATE > 4.65:
        raise ValueError('Voice must finish within the 6.8-second visual sequence.')
    dry = band(dry, 210, 5600)
    dry = np.tanh(dry * 2.3) / 1.6
    # A clear female center with narrow metallic sidebands and a tiny radio reflection.
    t = np.arange(len(dry)) / RATE
    sideband = np.real(signal.hilbert(dry) * np.exp(2j * np.pi * 41 * t))
    voice = .82 * dry + .15 * sideband + .10 * dry * np.sin(2 * np.pi * 67 * t)
    voice += .10 * delayed(dry, .013) + .065 * delayed(dry, .083)
    voice *= envelope(len(voice), .007, .035)
    voice *= .145 / max(.0001, np.sqrt(np.mean(voice ** 2)))
    return np.tanh(voice * 2.0) / 2.0


def master(mode, voice):
    mix = np.zeros(int(DURATION * RATE))
    rng = np.random.default_rng(2909 if mode == 'start' else 2910)
    def add(audio, at):
        offset = int(at * RATE)
        n = min(len(audio), len(mix) - offset)
        mix[offset:offset+n] += audio[:n]
    def ping(frequency, at, duration=.1, gain=.045):
        t = np.arange(int(duration * RATE)) / RATE
        wave = np.sin(2 * np.pi * frequency * t) + .13 * np.sin(2 * np.pi * frequency * 2 * t)
        add(wave * envelope(len(t), .007, duration * .6) * gain, at)
    def burst(at, duration=.1, gain=.025):
        n = int(RATE * duration)
        hiss = band(rng.normal(0, 1, n), 650, 4200)
        add(hiss * envelope(n, .012, .06) * gain, at)
    def glide(start, end, at, duration, gain):
        t = np.arange(int(duration * RATE)) / RATE
        wave = signal.chirp(t, f0=start, f1=end, t1=duration, method='logarithmic')
        add(wave * envelope(len(t), .055, .16) * gain, at)

    # A small channel handshake, followed by the spoken message at 0.62 s.
    burst(.035, .13, .033)
    if mode == 'start':
        glide(190, 570, .02, .43, .042)
        ping(1174.66, .19, .075, .045)
        ping(1760, .30, .13, .037)
    else:
        glide(480, 240, .02, .43, .036)
        ping(1760, .18, .08, .035)
        ping(1174.66, .30, .13, .038)
    burst(.45, .1, .017)
    add(voice, .62)

    # Restrained low-frequency atmosphere; no repetitive beeps under the words.
    t = np.arange(int(5.4 * RATE)) / RATE
    bed = (.009 * np.sin(2 * np.pi * 146.83 * t) + .005 * np.sin(2 * np.pi * 220 * t))
    add(bed * envelope(len(t), .7, 1.0), .35)
    burst(.62 + len(voice) / RATE, .09, .014)
    if mode == 'start':
        for i, f in enumerate([587.33, 880, 1174.66]):
            ping(f, 5.35 + i * .14, .42, .045 - i * .005)
        glide(220, 440, 4.65, .85, .017)
    else:
        for i, f in enumerate([1174.66, 880, 587.33]):
            ping(f, 5.18 + i * .16, .45, .041 - i * .004)
        glide(360, 120, 4.6, .9, .015)
        burst(5.91, .12, .018)
    mix = signal.sosfilt(signal.butter(2, 90, btype='highpass', fs=RATE, output='sos'), mix)
    mix *= .69 / np.max(np.abs(mix))  # -3.22 dBFS headroom, identical voice gain design.
    mix *= envelope(len(mix), .008, .12)
    return mix


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--voice-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, default=ROOT / '99_assets/audio')
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = {}
    for mode in ['start', 'end']:
        voice = radio_voice(args.voice_dir / (mode + '-voice.wav'))
        audio = master(mode, voice)
        path = args.output_dir / ('session-' + mode + '-v1.wav')
        sf.write(path, audio, RATE, subtype='PCM_16')
        report[mode] = {'duration':len(audio)/RATE, 'voiceStart':.62,
                        'voiceEnd':round(.62 + len(voice)/RATE, 3),
                        'peakDBFS':round(20*np.log10(np.max(np.abs(audio))),2),
                        'rmsDBFS':round(20*np.log10(np.sqrt(np.mean(audio**2))),2),
                        'bytes':path.stat().st_size,
                        'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
