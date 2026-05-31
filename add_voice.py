#!/usr/bin/env python3
"""
Genera voz en off estilo cine y la mezcla con el video v3.
Usa eSpeak-NG (offline) con post-procesamiento de audio:
  • Pitch bajo y grave  • Velocidad cinematográfica  • Eco/reverb
  • Fade in/out por segmento
"""

import subprocess, os, struct, wave, math
import numpy as np

# ── Script de voz por slide ───────────────────────────────────────────────────
# Durations: slide1=8s  slide2=8s  slide3=7s  slide4=7s  total=30s

VOICE_SCRIPT = [
    # (texto, duracion_slide, inicio_s)
    ("Is your property... truly secure? "
     "See how our 24/7 licensed patrols "
     "eliminate your after-hours vulnerability.",
     8.0, 0.0),

    ("Safety never takes a shift off. "
     "Most security gaps happen after dark. "
     "We are here to close them... before they start.",
     8.0, 8.0),

    ("Your assets. Our authority. "
     "Join the property managers who trust the shield. "
     "Licensed. Insured. And 24/7 available.",
     7.0, 16.0),

    ("Professional elite protection. "
     "Licensed guards and mobile patrols "
     "tailored for apartments, retail, and construction. "
     "Call us today. Three four six... two seven seven... twenty five sixty three.",
     7.0, 23.0),
]

SAMPLE_RATE = 22050

# ── Generate speech segment ───────────────────────────────────────────────────

def gen_speech(text, out_wav, speed=130, pitch=35, voice="en-us"):
    """Generate speech with espeak-ng."""
    subprocess.run([
        "espeak-ng",
        "-v", voice,
        "-s", str(speed),   # words per minute (slower = cinematic)
        "-p", str(pitch),   # pitch 0-99 (lower = deeper voice)
        "-a", "180",        # amplitude
        "--ipa",
        "-w", out_wav,
        text
    ], capture_output=True)

def read_wav(path):
    with wave.open(path, 'rb') as w:
        frames = w.readframes(w.getnframes())
        rate   = w.getframerate()
        ch     = w.getnchannels()
        sw     = w.getsampwidth()
    arr = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
    if ch == 2:
        arr = arr.reshape(-1, 2).mean(axis=1)
    # Resample to SAMPLE_RATE if needed
    if rate != SAMPLE_RATE:
        ratio  = SAMPLE_RATE / rate
        new_len = int(len(arr) * ratio)
        arr    = np.interp(
            np.linspace(0, len(arr)-1, new_len),
            np.arange(len(arr)), arr
        )
    return arr

def write_wav(path, arr, rate=SAMPLE_RATE):
    arr_i16 = np.clip(arr, -32767, 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(arr_i16.tobytes())

# ── Audio effects ─────────────────────────────────────────────────────────────

def add_reverb(arr, rate=SAMPLE_RATE, delay_ms=55, decay=0.30, num=4):
    """Simple comb-filter reverb for "large hall" feel."""
    delay_samples = int(rate * delay_ms / 1000)
    out = arr.copy()
    for i in range(1, num + 1):
        d   = delay_samples * i
        att = decay ** i
        pad = np.zeros(d)
        delayed = np.concatenate([pad, arr * att])[:len(arr)]
        out = out + delayed
    return out

def normalize(arr, peak=0.90):
    mx = np.max(np.abs(arr))
    if mx > 0:
        arr = arr / mx * peak * 32767
    return arr

def fade(arr, rate=SAMPLE_RATE, fin=0.08, fout=0.12):
    fi = int(rate * fin);  fo = int(rate * fout)
    arr[:fi]  *= np.linspace(0, 1, fi)
    arr[-fo:] *= np.linspace(1, 0, fo)
    return arr

def add_cinematic_eq(arr):
    """Boost low-mids slightly for deeper voice feel (simple IIR)."""
    out   = arr.copy()
    alpha = 0.15
    prev  = 0.0
    for i in range(len(out)):
        out[i] = out[i] * (1 - alpha) + prev * alpha
        prev   = out[i]
    # Mix original + low-pass 70/30
    return arr * 0.70 + out * 0.30

def fit_to_duration(arr, dur_s, rate=SAMPLE_RATE):
    """Pad or trim to exact duration."""
    target = int(dur_s * rate)
    if len(arr) < target:
        arr = np.concatenate([arr, np.zeros(target - len(arr))])
    else:
        arr = arr[:target]
    return arr

# ── Build full audio track ────────────────────────────────────────────────────

def build_audio():
    total_samples = int(30.0 * SAMPLE_RATE)
    master = np.zeros(total_samples, dtype=np.float32)

    for i, (text, dur, start) in enumerate(VOICE_SCRIPT):
        print(f"  Generando voz segmento {i+1}...")
        raw = f"/tmp/seg{i}.wav"
        gen_speech(text, raw, speed=125, pitch=32, voice="en-us")

        arr = read_wav(raw).astype(np.float32)
        arr = add_cinematic_eq(arr)
        arr = add_reverb(arr, delay_ms=60, decay=0.28, num=3)
        arr = fade(arr, fin=0.06, fout=0.18)
        arr = fit_to_duration(arr, dur - 0.3)

        s = int(start * SAMPLE_RATE)
        e = s + len(arr)
        if e <= total_samples:
            master[s:e] += arr

    master = normalize(master, 0.88)
    out = "/tmp/voiceover.wav"
    write_wav(out, master)
    print(f"  Audio guardado: {out}")
    return out

# ── Merge audio + video ───────────────────────────────────────────────────────

def merge(video_in, audio_in, video_out):
    from imageio_ffmpeg import get_ffmpeg_exe
    ffmpeg = get_ffmpeg_exe()
    cmd = [
        ffmpeg, "-y",
        "-i", video_in,
        "-i", audio_in,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",
        "-movflags", "+faststart",
        video_out
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FFmpeg error:", r.stderr[-400:])
    else:
        print(f"  Video final: {video_out}")

# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Generando pista de voz en off...")
    audio = build_audio()

    print("Mezclando con video v3...")
    merge(
        "/home/user/Sublimontes_shop/montes_patrol_v3.mp4",
        audio,
        "/home/user/Sublimontes_shop/montes_patrol_VOZ.mp4"
    )

    sz = os.path.getsize("/home/user/Sublimontes_shop/montes_patrol_VOZ.mp4")
    print(f"¡Listo!  {sz/1e6:.1f} MB")
