#!/usr/bin/env python3
"""
Voz en off v2 — timing exacto por línea + MBROLA (voz natural) + sox processing.

Cada frase se genera en el momento en que el texto correspondiente
aparece en pantalla (según las animaciones del video v3).
"""

import subprocess, wave, os, numpy as np

SR = 22050   # sample rate de salida

# ── Timing map ────────────────────────────────────────────────────────────────
# (texto, tiempo_absoluto_en_video_segundos)
# Los tiempos reflejan cuando el texto es visible en pantalla + 0.15 s de margen.

LINES = [
    # ── SLIDE 1  (0–8 s) ─────────────────────────────────────────────────────
    ("Is your property...",               0.45),
    ("truly secure?",                     1.10),
    ("See how our 24/7 licensed patrols", 2.20),
    ("eliminate your vulnerability.",     3.80),

    # ── SLIDE 2  (8–16 s) ────────────────────────────────────────────────────
    ("Safety...",                         8.45),
    ("never takes a shift off.",          9.20),
    ("Most security gaps happen after dark.", 10.30),
    ("We are here to close them...",      11.80),
    ("before they start.",                12.80),

    # ── SLIDE 3  (16–23 s) ───────────────────────────────────────────────────
    ("Your assets.",                      16.45),
    ("Our authority.",                    17.15),
    ("Join the property managers who trust the shield.", 18.00),
    ("Licensed. Insured. 24/7 available.", 19.80),

    # ── SLIDE 4  (23–30 s) ───────────────────────────────────────────────────
    ("Professional elite protection.",    23.45),
    ("Licensed guards and mobile patrols", 24.50),
    ("for apartments, retail and construction.", 25.50),
    ("Call us today.",                    27.00),
    ("Three four six... two seven seven... twenty five sixty three.", 27.70),
]

TOTAL_DUR = 30.0

# ── Helpers ───────────────────────────────────────────────────────────────────

def gen_wav(text, path, speed=118, pitch=38, voice="mb-us2"):
    """eSpeak-NG + MBROLA voice → wav."""
    subprocess.run([
        "espeak-ng",
        "-v", voice,
        "-s", str(speed),
        "-p", str(pitch),
        "-a", "200",
        "-w", path,
        text
    ], capture_output=True)

def sox_process(in_wav, out_wav):
    """
    sox post-processing:
      • Leve bajo (bass +4)     → voz más grave/cálida
      • Compander               → dinámica más pareja
      • Reverb ligero (sala pequeña) → profundidad cinematográfica
      • Normalizar
    """
    subprocess.run([
        "sox", in_wav, out_wav,
        "bass", "+4",
        "compand", "0.02,0.2", "6:-70,-60,-20", "-5", "-90", "0.1",
        "reverb", "18", "25", "60",
        "norm", "-1",
    ], capture_output=True)

def read_wav(path):
    with wave.open(path, "rb") as w:
        raw  = w.readframes(w.getnframes())
        rate = w.getframerate()
        ch   = w.getnchannels()
    arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
    if ch == 2:
        arr = arr.reshape(-1, 2).mean(axis=1)
    # Resample to SR if needed
    if rate != SR:
        n   = int(len(arr) * SR / rate)
        arr = np.interp(np.linspace(0, len(arr)-1, n), np.arange(len(arr)), arr)
    return arr

def write_wav(path, arr):
    i16 = np.clip(arr, -32767, 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(i16.tobytes())

def fade_clip(arr, fin_s=0.04, fout_s=0.08):
    fi = int(SR * fin_s); fo = int(SR * fout_s)
    if fi: arr[:fi]  *= np.linspace(0, 1, fi)
    if fo: arr[-fo:] *= np.linspace(1, 0, fo)
    return arr

# ── Build master track ────────────────────────────────────────────────────────

def build():
    master = np.zeros(int(TOTAL_DUR * SR), dtype=np.float32)

    for i, (text, t_start) in enumerate(LINES):
        print(f"  [{t_start:5.2f}s]  {text[:55]}")
        raw  = f"/tmp/line_{i}_raw.wav"
        proc = f"/tmp/line_{i}.wav"
        gen_wav(text, raw)
        sox_process(raw, proc)

        arr = read_wav(proc)
        arr = fade_clip(arr)

        s = int(t_start * SR)
        e = s + len(arr)

        # If clip overruns next line's start, trim it
        if i + 1 < len(LINES):
            next_start = int(LINES[i+1][1] * SR)
            max_len    = next_start - s - int(SR * 0.08)   # 80ms gap
            if len(arr) > max_len > 0:
                arr = arr[:max_len]
                e   = s + len(arr)

        if e <= len(master):
            master[s:e] += arr
        elif s < len(master):
            trim = len(master) - s
            master[s:] += arr[:trim]

    # Global normalize
    peak = np.max(np.abs(master))
    if peak > 0:
        master = master / peak * 0.88 * 32767

    out = "/tmp/voiceover_v2.wav"
    write_wav(out, master)
    print(f"\n  Audio listo: {out}")
    return out

# ── Merge with video ──────────────────────────────────────────────────────────

def merge(video, audio, out):
    from imageio_ffmpeg import get_ffmpeg_exe
    ffmpeg = get_ffmpeg_exe()
    r = subprocess.run([
        ffmpeg, "-y",
        "-i", video,
        "-i", audio,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        out
    ], capture_output=True, text=True)
    if r.returncode != 0:
        print("FFmpeg error:", r.stderr[-300:])

# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Generando voz en off (MBROLA + sox)...\n")
    audio = build()

    out = "/home/user/Sublimontes_shop/montes_patrol_VOZ_v2.mp4"
    print(f"\nMezclando video + voz → {out}")
    merge(
        "/home/user/Sublimontes_shop/montes_patrol_v3.mp4",
        audio, out
    )
    print(f"¡Listo!  {os.path.getsize(out)/1e6:.1f} MB")
