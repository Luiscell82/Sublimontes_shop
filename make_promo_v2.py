#!/usr/bin/env python3
"""
Montes Patrol Security LLC — Promo Video v2
Usa las imágenes reales con efectos: Ken Burns, marquesina, fade, slide-in, flash
30 segundos · 1080x1920 · 30fps
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import math

W, H   = 1080, 1920
FPS    = 30
RED    = (190, 20, 20)
DARK_RED = (140, 8, 8)
WHITE  = (255, 255, 255)
NAVY   = (10, 27, 56)
GOLD   = (212, 175, 55)
BLACK  = (0, 0, 0)

FONT_BOLD   = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
FONT_NORMAL = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"

def fnt(size):
    return ImageFont.truetype(FONT_BOLD, size)

def fnt_n(size):
    return ImageFont.truetype(FONT_NORMAL, size)

# ── Image helpers ─────────────────────────────────────────────────────────────

def load_img(path):
    return Image.open(path).convert("RGB").resize((W, H), Image.LANCZOS)

def ken_burns(img, t, duration, zoom_start=1.0, zoom_end=1.12, pan=(0, 0)):
    """Slow zoom + pan (Ken Burns effect)."""
    progress = t / duration
    zoom = zoom_start + (zoom_end - zoom_start) * progress
    new_w = int(W * zoom)
    new_h = int(H * zoom)
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    px = int((new_w - W) * (0.5 + pan[0] * progress))
    py = int((new_h - H) * (0.5 + pan[1] * progress))
    px = max(0, min(px, new_w - W))
    py = max(0, min(py, new_h - H))
    return resized.crop((px, py, px + W, py + H))

def darken(img, factor=0.55):
    return ImageEnhance.Brightness(img).enhance(factor)

def overlay_color(img, color, alpha):
    """Blend a solid color over the image."""
    overlay = Image.new("RGB", (W, H), color)
    return Image.blend(img, overlay, alpha)

# ── Text helpers ──────────────────────────────────────────────────────────────

def draw_text_shadow(draw, text, font, x, y, color=WHITE, shadow_offset=4, shadow_alpha=160):
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font,
              fill=(*BLACK, shadow_alpha))
    draw.text((x, y), text, font=font, fill=color)

def draw_centered(draw, text, font, y, color=WHITE, shadow=True):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    if shadow:
        draw.text((x + 4, y + 4), text, font=font, fill=(*BLACK, 180))
    draw.text((x, y), text, font=font, fill=color)
    return tw

def draw_bar(draw, y, h=6, color=RED, x0=0, x1=W):
    draw.rectangle([x0, y, x1, y + h], fill=color)

# ── Marquee strip ─────────────────────────────────────────────────────────────

MARQUEE_TEXT = ("  24/7 SECURITY COVERAGE  •  FAST RESPONSE TIME  •  "
                "PROFESSIONAL GUARDS  •  MOBILE PATROLS  •  "
                "APARTMENT COMMUNITIES  •  CONSTRUCTION SECURITY  •  "
                "LICENSED & INSURED  •  ")

def draw_marquee(img_rgba, t, y, height=72, bg=(10, 18, 45, 230), speed=280):
    draw = ImageDraw.Draw(img_rgba, "RGBA")
    # Background strip
    draw.rectangle([0, y, W, y + height], fill=bg)
    draw_bar(draw, y, h=4, color=(*RED, 255))
    draw_bar(draw, y + height - 4, h=4, color=(*RED, 255))

    font = fnt(34)
    repeated = MARQUEE_TEXT * 4
    bbox = draw.textbbox((0, 0), repeated, font=font)
    text_w = bbox[2] - bbox[0]
    single_w = text_w // 4

    offset = int(t * speed) % single_w
    draw.text((-offset, y + (height - 40) // 2), repeated,
              font=font, fill=(*WHITE, 240))

# ── Flash / vignette ──────────────────────────────────────────────────────────

def add_vignette(arr, strength=0.55):
    """Dark vignette around edges."""
    h, w = arr.shape[:2]
    Y, X = np.ogrid[:h, :w]
    cx, cy = w / 2, h / 2
    dist = np.sqrt(((X - cx) / cx) ** 2 + ((Y - cy) / cy) ** 2)
    mask = np.clip(dist * strength, 0, 1)
    mask = mask[:, :, np.newaxis]
    arr = arr * (1 - mask) + arr * 0  # darken edges
    arr = (arr * (1 - mask * 0.6)).astype(np.uint8)
    return arr

def fade_alpha(t, fade_in=0.5, fade_out=0.5, duration=7.5):
    """Return opacity 0-255 with fade in/out."""
    if t < fade_in:
        return t / fade_in
    if t > duration - fade_out:
        return (duration - t) / fade_out
    return 1.0

# ── Slide builders ────────────────────────────────────────────────────────────

def slide1_frame(base_img, t, duration=8.0):
    """IS YOUR PROPERTY TRULY SECURE?"""
    alpha = fade_alpha(t, 0.6, 0.5, duration)

    bg = ken_burns(base_img, t, duration, 1.0, 1.10, pan=(0.1, -0.05))
    bg = darken(bg, 0.50)
    arr = np.array(bg)
    arr = add_vignette(arr, 0.5)

    img = Image.fromarray(arr).convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")

    # Top accent bar
    draw.rectangle([W//2 - 50, 38, W//2 + 50, 46], fill=(255, 100, 0, 220))

    # Dark overlay top band for text readability
    draw.rectangle([0, 0, W, 420], fill=(*NAVY, int(alpha * 175)))

    # Main question — slide in from left
    slide = min(1.0, t * 2.2)
    ease = 1 - (1 - slide) ** 3
    x_off = int((1 - ease) * -W * 0.6)

    f_big = fnt(96)
    lines = [("IS YOUR", WHITE), ("PROPERTY", WHITE),
             ("TRULY", WHITE), ("SECURE?", RED)]
    lh = 108
    start_y = 58
    for i, (line, col) in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=f_big)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2 + x_off
        y = start_y + i * lh
        op = int(min(1.0, t * 2.5) * alpha * 255)
        draw.text((x + 5, y + 5), line, font=f_big, fill=(*BLACK, op // 2))
        draw.text((x, y), line, font=f_big, fill=(*col, op))

    # Sub caption
    fade2 = max(0, min(1.0, (t - 1.2) * 1.8))
    f_sub = fnt_n(38)
    sub = ["See how 24/7 licensed patrols",
           "eliminate your after-hours vulnerability."]
    for i, line in enumerate(sub):
        bbox = draw.textbbox((0, 0), line, font=f_sub)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        y = 500 + i * 54
        draw.text((x, y), line, font=f_sub,
                  fill=(*WHITE, int(fade2 * alpha * 200)))

    # Marquee at bottom section
    draw_marquee(img, t, H - 200, height=72)

    # Bottom contact bar
    draw.rectangle([0, H - 128, W, H], fill=(*DARK_RED, int(alpha * 240)))
    draw_centered(draw, "(346) 277-2563", fnt(44), H - 116, color=WHITE, shadow=False)
    draw_centered(draw, "www.montespatrolsecurityllc.com", fnt_n(28),
                  H - 62, color=(*GOLD, 255), shadow=False)

    arr_out = np.array(img.convert("RGB"))
    if alpha < 1.0:
        black = np.zeros_like(arr_out)
        arr_out = (arr_out * alpha + black * (1 - alpha)).astype(np.uint8)
    return arr_out


def slide2_frame(base_img, t, duration=8.0):
    """SAFETY NEVER TAKES A SHIFT OFF"""
    alpha = fade_alpha(t, 0.6, 0.5, duration)

    bg = ken_burns(base_img, t, duration, 1.08, 1.0, pan=(-0.1, 0.0))
    bg = darken(bg, 0.45)
    arr = np.array(bg)
    arr = add_vignette(arr, 0.6)

    img = Image.fromarray(arr).convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")

    # Top dark panel
    draw.rectangle([0, 0, W, 780], fill=(*NAVY, int(alpha * 190)))

    # Big headline — fade in word by word
    f_huge = fnt(118)
    words = [("SAFETY", WHITE, 0.0),
             ("NEVER", WHITE, 0.25),
             ("TAKES", RED, 0.45),
             ("A SHIFT", RED, 0.65),
             ("OFF", WHITE, 0.85)]
    lh = 132
    sy = 35
    for i, (word, col, delay) in enumerate(words):
        word_fade = max(0, min(1.0, (t - delay) * 2.5))
        op = int(word_fade * alpha * 255)
        # slide up
        y_off = int((1 - min(1.0, (t - delay) * 3)) * 60)
        bbox = draw.textbbox((0, 0), word, font=f_huge)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        y = sy + i * lh - y_off
        draw.text((x + 5, y + 5), word, font=f_huge, fill=(*BLACK, op // 2))
        draw.text((x, y), word, font=f_huge, fill=(*col, op))

    # Sub text
    fade2 = max(0, min(1.0, (t - 1.5) * 1.5))
    f_body = fnt_n(42)
    body = ["Most security gaps happen after dark.",
            "We're here to close them",
            "before they start."]
    for i, line in enumerate(body):
        bbox = draw.textbbox((0, 0), line, font=f_body)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        y = 710 + i * 60
        draw.text((x, y), line, font=f_body,
                  fill=(*WHITE, int(fade2 * alpha * 210)))

    # Red separator
    draw_bar(draw, 870, h=6, color=(*RED, int(alpha * 255)))

    # Marquee
    draw_marquee(img, t, H - 185, height=72)

    # Bottom bar
    draw.rectangle([0, H - 113, W, H], fill=(*DARK_RED, int(alpha * 245)))
    draw_centered(draw, "LICENSED  •  INSURED", fnt(44), H - 100,
                  color=WHITE, shadow=False)

    arr_out = np.array(img.convert("RGB"))
    if alpha < 1.0:
        black = np.zeros_like(arr_out)
        arr_out = (arr_out * alpha + black * (1 - alpha)).astype(np.uint8)
    return arr_out


def slide3_frame(base_img, t, duration=7.0):
    """YOUR ASSETS, OUR AUTHORITY"""
    alpha = fade_alpha(t, 0.6, 0.5, duration)

    bg = ken_burns(base_img, t, duration, 1.0, 1.08, pan=(0.0, 0.08))
    bg = darken(bg, 0.55)
    arr = np.array(bg)
    arr = add_vignette(arr, 0.5)

    img = Image.fromarray(arr).convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")

    # Bottom dark panel for text
    draw.rectangle([0, 880, W, H], fill=(*BLACK, int(alpha * 195)))
    draw_bar(draw, 880, h=7, color=(*RED, int(alpha * 255)))

    # Big tagline — slide in from right
    slide = min(1.0, t * 2.0)
    ease = 1 - (1 - slide) ** 3
    x_off = int((1 - ease) * W * 0.7)

    f_tag = fnt(108)
    lines = [("YOUR ASSETS,", WHITE, 930),
             ("OUR", RED, 1045),
             ("AUTHORITY", WHITE, 1158)]
    for line, col, y in lines:
        bbox = draw.textbbox((0, 0), line, font=f_tag)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2 + x_off
        op = int(min(1.0, t * 2.5) * alpha * 255)
        draw.text((x + 5, y + 5), line, font=f_tag, fill=(*BLACK, op // 2))
        draw.text((x, y), line, font=f_tag, fill=(*col, op))

    # Divider line
    fade2 = max(0, min(1.0, (t - 0.8) * 2))
    draw.rectangle([120, 1282, W - 120, 1288],
                   fill=(*WHITE, int(fade2 * alpha * 180)))

    # Sub caption
    f_sub = fnt_n(36)
    sub = ["Join the property managers who trust the shield.",
           "Licensed, insured, and 24/7 available."]
    for i, line in enumerate(sub):
        bbox = draw.textbbox((0, 0), line, font=f_sub)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        y = 1302 + i * 56
        draw.text((x, y), line, font=f_sub,
                  fill=(*WHITE, int(fade2 * alpha * 205)))

    # Marquee
    draw_marquee(img, t, H - 185, height=72)

    # Bottom bar
    draw.rectangle([0, H - 113, W, H], fill=(*NAVY, int(alpha * 245)))
    draw.rectangle([0, H - 115, W, H - 110], fill=(*RED, int(alpha * 255)))
    draw_centered(draw, "(346) 277-2563  |  montespatrolsecurityllc.com",
                  fnt(32), H - 100, color=WHITE, shadow=False)

    arr_out = np.array(img.convert("RGB"))
    if alpha < 1.0:
        black = np.zeros_like(arr_out)
        arr_out = (arr_out * alpha + black * (1 - alpha)).astype(np.uint8)
    return arr_out


def slide4_frame(base_img, t, duration=7.0):
    """PROFESSIONAL ELITE PROTECTION — CTA final"""
    alpha = fade_alpha(t, 0.6, 0.7, duration)

    bg = ken_burns(base_img, t, duration, 1.05, 1.0, pan=(0.05, -0.05))
    bg = darken(bg, 0.48)
    arr = np.array(bg)
    arr = add_vignette(arr, 0.55)

    img = Image.fromarray(arr).convert("RGBA")
    draw = ImageDraw.Draw(img, "RGBA")

    # Bottom overlay panel
    draw.rectangle([0, 1050, W, H], fill=(*NAVY, int(alpha * 200)))
    draw_bar(draw, 1050, h=8, color=(*RED, int(alpha * 255)))

    # CTA text — pops in with scale effect (simulated via opacity stagger)
    f_cta = fnt(92)
    cta = [("PROFESSIONAL", WHITE, 1080, 0.0),
           ("ELITE", RED, 1175, 0.2),
           ("PROTECTION", WHITE, 1270, 0.4)]
    for line, col, y, delay in cta:
        word_fade = max(0, min(1.0, (t - delay) * 3.0))
        op = int(word_fade * alpha * 255)
        bbox = draw.textbbox((0, 0), line, font=f_cta)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        draw.text((x + 5, y + 5), line, font=f_cta, fill=(*BLACK, op // 2))
        draw.text((x, y), line, font=f_cta, fill=(*col, op))

    # Description
    fade2 = max(0, min(1.0, (t - 0.8) * 2))
    f_desc = fnt_n(36)
    desc = ["Licensed guards and mobile patrols",
            "tailored for apartments, retail,",
            "and construction."]
    for i, line in enumerate(desc):
        bbox = draw.textbbox((0, 0), line, font=f_desc)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        y = 1390 + i * 54
        draw.text((x, y), line, font=f_desc,
                  fill=(*WHITE, int(fade2 * alpha * 200)))

    # LICENSED INSURED badge
    fade3 = max(0, min(1.0, (t - 1.0) * 2))
    draw.rectangle([120, 1575, W - 120, 1640],
                   fill=(*DARK_RED, int(fade3 * alpha * 220)))
    draw_centered(draw, "LICENSED  •  INSURED", fnt(48), 1582,
                  color=WHITE, shadow=False)

    # Marquee
    draw_marquee(img, t, H - 185, height=72)

    # Bottom contact
    draw.rectangle([0, H - 113, W, H], fill=(*DARK_RED, int(alpha * 250)))
    # Phone
    draw_centered(draw, "(346) 277-2563", fnt(46), H - 108,
                  color=WHITE, shadow=False)
    draw_centered(draw, "www.montespatrolsecurityllc.com", fnt_n(28),
                  H - 57, color=(*GOLD, 255), shadow=False)

    arr_out = np.array(img.convert("RGB"))
    if alpha < 1.0:
        black = np.zeros_like(arr_out)
        arr_out = (arr_out * alpha + black * (1 - alpha)).astype(np.uint8)
    return arr_out


# ── Main render ───────────────────────────────────────────────────────────────

def build():
    from moviepy import VideoClip

    print("Cargando imágenes...")
    imgs = [load_img(f"slide{i}.png") for i in range(1, 5)]

    durations = [8.0, 8.0, 7.0, 7.0]
    funcs = [slide1_frame, slide2_frame, slide3_frame, slide4_frame]
    clips = []

    for i, (fn, dur, img) in enumerate(zip(funcs, durations, imgs)):
        print(f"Renderizando slide {i+1} ({dur}s)...")
        def make_frame(t, fn=fn, img=img, dur=dur):
            return fn(img, t, dur)
        clip = VideoClip(make_frame, duration=dur).with_fps(FPS)
        clips.append(clip)

    print("Concatenando...")
    from moviepy import concatenate_videoclips
    final = concatenate_videoclips(clips, method="compose")

    out = "/home/user/Sublimontes_shop/montes_patrol_promo_v2.mp4"
    print(f"Escribiendo {out}...")
    final.write_videofile(
        out, fps=FPS, codec="libx264", audio=False,
        preset="fast",
        ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p"],
        logger="bar",
    )
    print("¡Listo!")
    return out


if __name__ == "__main__":
    build()
