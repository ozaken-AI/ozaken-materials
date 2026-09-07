# Session protocol audio

Original synthesized female voice and procedural communication sounds for the lecture start/end sequence.

| Asset | Spoken message | Duration |
| --- | --- | --- |
| `session-start-v1.wav` | Session start in progress. Systems online. | 6.4 s |
| `session-end-v1.wav` | Session complete. Standing by. | 6.4 s |

24 kHz / mono / 16-bit PCM. Each file is about 300 KiB. Mono keeps the words and effects intact on conference PA systems. Peaks are mastered to −3.22 dBFS. Speech starts at 0.62 s and finishes before 3.5 s; the final response tones accompany the visual completion at about 5.4 s. The existing visual controller stops all playback at 6.8 s or immediately on skip.

Voice source: [hexgrad/Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M), v1.0, `af_heart`, speed `0.89`, American English. The model card lists Apache-2.0 licensing. This is a stock synthetic voice, with no real person's voice cloned and no film audio sampled. The communications effects are generated with oscillators and seeded noise. Models and generation dependencies are not served by the website.

## Rebuilding

Use an isolated Python environment with `kokoro`, `numpy`, `scipy`, and `soundfile`. Generate `start-voice.wav` / `end-voice.wav` at 24 kHz using the messages above with `KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M')`, `voice='af_heart'`, `speed=0.89`. The source phrases use Misaki's English dictionary; an eSpeak fallback is not needed for these words.

Run `python scripts/build-session-audio.py --voice-dir /path/to/voices`. It applies a voice bandpass, metallic sidebands, short reflections, saturation, communication pings, and consistent headroom. Change the versioned filenames and the URLs in `session-audio.js` if replacing these published recordings, then run `python scripts/version-site-assets.py`.

## Playback

`go` starts the lecture; `en` ends it and opens the thanks/QR screen. `st` remains the existing silent pre-lecture standby screen. `window.ozSessionAudio.play(mode)` is called synchronously from the boot controller. The two assets preload locally; there is no speech API or network TTS at playback time.

Playback that cannot start within 1.2 s is cancelled so a late voice does not interrupt the talk. Autoplay rejection or audio failure leaves the visual sequence running silently. Skip, Escape, page hiding, and navigation stop playback. A new attempt uses a separate audio element so late promises cannot affect a newer run.

Validation: `node scripts/test-session-audio.cjs` and `node scripts/test-session-boot.cjs`.
