#!/usr/bin/env python3
"""
Genera un video bonito con la frase sobre los padres.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import math

# ── Configuración ──────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1080, 1920
FPS = 30
FONT_BOLD   = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_REGULAR= "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"

# Paleta cálida (crema / ámbar)
BG_TOP    = (255, 248, 220)   # ivory
BG_BOTTOM = (240, 210, 150)   # warm amber
TITLE_BG  = (245, 215, 110)   # golden highlight
TITLE_COLOR  = (60,  35,  10) # dark brown
TEXT_COLOR   = (50,  30,   5)
ACCENT_COLOR = (180, 100,  20)

SEGMENTS = [
    {
        "title": '"UN PADRE NUNCA\nESPERA NADA A CAMBIO\nDE SUS HIJOS"',
        "body": "",
        "duration": 5,
    },
    {
        "title": "",
        "body": "Nunca pide que le devuelvan algo.\nNunca pide regalos.\nNi siquiera espera ser alabado.",
        "duration": 5,
    },
    {
        "title": "",
        "body": "Solo hay una cosa que\nrealmente quiere:\nver que sus hijos vivan\nuna vida mejor que la suya.",
        "duration": 6,
    },
    {
        "title": "",
        "body": "Incluso cuando su cuerpo\ncomienza a cansarse y la edad\nsigue alcanzándolo, aún menciona\nen silencio los nombres de sus\nhijos en sus oraciones.",
        "duration": 7,
    },
    {
        "title": "",
        "body": "Porque para un padre,\nla mayor felicidad no es\nrecibir nada a cambio de sus hijos,",
        "duration": 5,
    },
    {
        "title": "",
        "body": "sino simplemente ver a sus hijos\nsonreír y vivir una vida feliz.",
        "duration": 5,
    },
]

FADE_FRAMES = FPS  # 1 segundo de fade

# ── Helpers ────────────────────────────────────────────────────────────────────

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def make_gradient_bg():
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)
    for y in range(HEIGHT):
        t = y / HEIGHT
        color = lerp_color(BG_TOP, BG_BOTTOM, t)
        draw.line([(0, y), (WIDTH, y)], fill=color)
    return img


def draw_decorative_lines(draw):
    """Líneas decorativas sutiles en los bordes."""
    for offset in [30, 45]:
        draw.rectangle(
            [offset, offset, WIDTH - offset, HEIGHT - offset],
            outline=(*ACCENT_COLOR, 60),
            width=2,
        )


def draw_feather(img, alpha=40):
    """Pluma decorativa semitransparente en el fondo."""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    cx, cy = WIDTH // 2, HEIGHT // 2 + 200

    for i in range(18):
        angle = math.radians(-90 + i * 10 - 90)
        length = 350 + i * 8
        ex = cx + int(length * math.cos(angle))
        ey = cy + int(length * math.sin(angle))
        width = max(1, 8 - i // 3)
        d.line([(cx, cy), (ex, ey)], fill=(*ACCENT_COLOR, alpha), width=width)

        for j in range(1, 6):
            t = j / 6
            bx = int(cx + t * (ex - cx))
            by = int(cy + t * (ey - cy))
            bl = 40 - i * 1.5
            ba = math.radians(angle * 180 / math.pi + 25)
            d.line(
                [(bx, by), (int(bx + bl * math.cos(ba)), int(by + bl * math.sin(ba)))],
                fill=(*ACCENT_COLOR, max(0, alpha - 15)),
                width=max(1, width - 1),
            )

    img_rgba = img.convert("RGBA")
    img_rgba = Image.alpha_composite(img_rgba, overlay)
    return img_rgba.convert("RGB")


def wrap_text(text, font, max_width, draw):
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            test = current + " " + word
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current = test
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def render_frame(seg, progress):
    """
    progress: 0.0 → 1.0 dentro del segmento (incluye fade in/out)
    """
    # fondo con degradado
    bg = make_gradient_bg()
    bg = draw_feather(bg, alpha=35)

    draw = ImageDraw.Draw(bg)
    draw_decorative_lines(draw)

    pad_x = 80
    max_text_w = WIDTH - 2 * pad_x
    y = 200

    if seg["title"]:
        # Caja de título dorada
        font_title = ImageFont.truetype(FONT_BOLD, 68)
        lines = seg["title"].split("\n")
        line_h = 80
        box_h = len(lines) * line_h + 60
        draw.rounded_rectangle(
            [40, y - 20, WIDTH - 40, y + box_h],
            radius=20,
            fill=TITLE_BG,
        )
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font_title)
            tw = bbox[2] - bbox[0]
            draw.text(
                ((WIDTH - tw) / 2, y + 10),
                line,
                font=font_title,
                fill=TITLE_COLOR,
            )
            y += line_h
        y += 60

    if seg["body"]:
        font_body = ImageFont.truetype(FONT_REGULAR, 60)
        lines = seg["body"].split("\n")
        line_h = 80
        total_h = len(lines) * line_h
        y_start = (HEIGHT - total_h) // 2
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font_body)
            tw = bbox[2] - bbox[0]
            draw.text(
                ((WIDTH - tw) / 2, y_start + i * line_h),
                line,
                font=font_body,
                fill=TEXT_COLOR,
            )

    # Marca de agua pequeña
    font_small = ImageFont.truetype(FONT_REGULAR, 32)
    draw.text((WIDTH // 2 - 140, HEIGHT - 80), "Sublimontes Shop", font=font_small, fill=ACCENT_COLOR)

    frame = np.array(bg)

    # Fade in / out
    fade_dur = 0.12
    if progress < fade_dur:
        alpha = progress / fade_dur
        frame = (frame * alpha).astype(np.uint8)
    elif progress > 1 - fade_dur:
        alpha = (1 - progress) / fade_dur
        frame = (frame * alpha).astype(np.uint8)

    return frame


def build_video():
    try:
        from moviepy import ImageClip, concatenate_videoclips
    except ImportError:
        from moviepy.editor import ImageClip, concatenate_videoclips

    clips = []
    for seg in SEGMENTS:
        dur = seg["duration"]
        n_frames = dur * FPS

        frames = []
        for i in range(n_frames):
            progress = i / max(n_frames - 1, 1)
            frames.append(render_frame(seg, progress))

        frames_arr = np.stack(frames)

        def make_frame(t, frames_arr=frames_arr, dur=dur):
            idx = min(int(t / dur * len(frames_arr)), len(frames_arr) - 1)
            return frames_arr[idx]

        clip = ImageClip(make_frame(0), duration=dur)

        try:
            from moviepy import VideoClip
        except ImportError:
            from moviepy.editor import VideoClip

        vc = VideoClip(frame_function=make_frame, duration=dur)
        vc = vc.with_fps(FPS)
        clips.append(vc)

    final = concatenate_videoclips(clips)
    out_path = "/home/user/Sublimontes_shop/frase_padre.mp4"
    final.write_videofile(
        out_path,
        fps=FPS,
        codec="libx264",
        audio=False,
        logger="bar",
    )
    print(f"\n✅ Video guardado en: {out_path}")
    return out_path


if __name__ == "__main__":
    build_video()
