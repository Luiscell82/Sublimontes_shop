#!/usr/bin/env python3
"""
Montes Patrol Security LLC — Promo Video v3
Imágenes nítidas + efectos profesionales:
  • Ken Burns suave  • Barrido de luz (lens flare sweep)
  • Zoom flash en transiciones  • Texto con typewriter + bounce
  • Partículas de brillo  • Glitch sutil  • Marquesina doble
30 s · 1080×1920 · 30 fps
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops
import math, random

W, H   = 1080, 1920
FPS    = 30
RED    = (190, 20, 20)
DKRED  = (130, 8, 8)
WHITE  = (255, 255, 255)
NAVY   = (10, 27, 56)
GOLD   = (212, 175, 55)
BLACK  = (0, 0, 0)
ORANGE = (255, 90, 0)

FB = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
FN = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"

def fnt(s): return ImageFont.truetype(FB, s)
def fnn(s): return ImageFont.truetype(FN, s)

random.seed(42)

# ── Image helpers ─────────────────────────────────────────────────────────────

def load(path):
    img = Image.open(path).convert("RGB")
    # Upscale slightly for sharper Ken Burns without pixelation
    return img.resize((W, H), Image.LANCZOS)

def kb(img, t, dur, z0=1.0, z1=1.10, pan=(0.0, 0.0)):
    """Ken Burns — zoom + pan, crisp."""
    p   = min(1.0, t / dur)
    z   = z0 + (z1 - z0) * p
    nw  = int(W * z);  nh = int(H * z)
    big = img.resize((nw, nh), Image.LANCZOS)
    ox  = int((nw - W) * (0.5 + pan[0] * p))
    oy  = int((nh - H) * (0.5 + pan[1] * p))
    ox  = max(0, min(ox, nw - W))
    oy  = max(0, min(oy, nh - H))
    return big.crop((ox, oy, ox + W, oy + H))

def darken(img, f):
    return ImageEnhance.Brightness(img).enhance(f)

def sharpen(img):
    return img.filter(ImageFilter.UnsharpMask(radius=1.5, percent=120, threshold=3))

def vignette(arr, strength=0.40):
    h, w = arr.shape[:2]
    Y, X = np.ogrid[:h, :w]
    d = np.sqrt(((X - w/2)/(w/2))**2 + ((Y - h/2)/(h/2))**2)
    m = np.clip(d * strength, 0, 1)[:, :, np.newaxis]
    return (arr * (1 - m * 0.7)).astype(np.uint8)

def fade_factor(t, fi=0.5, fo=0.4, dur=7.5):
    if t < fi:   return t / fi
    if t > dur - fo: return (dur - t) / fo
    return 1.0

# ── Lens-flare sweep ──────────────────────────────────────────────────────────

def lens_sweep(draw, t, dur):
    """Diagonal light streak that sweeps once per slide."""
    prog = (t / dur)
    if prog > 0.9: return
    x = int(-200 + prog * (W + 400))
    for i, (w2, a) in enumerate([(180, 18), (60, 35), (20, 55)]):
        pts = [(x - w2 - H//3, 0), (x + w2 - H//3, 0),
               (x + w2 + H//3, H), (x - w2 + H//3, H)]
        pts = [(int(px), int(py)) for px, py in pts]
        draw.polygon(pts, fill=(*WHITE, a))

# ── Particles ─────────────────────────────────────────────────────────────────

PARTICLES = [(random.randint(0, W), random.randint(0, H),
              random.uniform(0.3, 1.2), random.uniform(0, 6.28))
             for _ in range(35)]

def draw_particles(draw, t, alpha_factor=1.0):
    for px, py, speed, phase in PARTICLES:
        blink = 0.5 + 0.5 * math.sin(t * speed * 3 + phase)
        a = int(blink * alpha_factor * 160)
        r = int(2 + blink * 3)
        draw.ellipse([px - r, py - r, px + r, py + r],
                     fill=(*GOLD, a))

# ── Zoom-flash transition frame ───────────────────────────────────────────────

def zoom_flash(img, strength):
    """Bright flash + scale-up burst for 1-2 frames at cut points."""
    arr = np.array(img).astype(np.float32)
    arr = np.clip(arr + 255 * strength * 0.6, 0, 255).astype(np.uint8)
    s   = 1.0 + strength * 0.06
    nw, nh = int(W * s), int(H * s)
    big = Image.fromarray(arr).resize((nw, nh), Image.NEAREST)
    ox, oy = (nw - W) // 2, (nh - H) // 2
    return np.array(big.crop((ox, oy, ox + W, oy + H)))

# ── Marquee ───────────────────────────────────────────────────────────────────

TICKER = ("  ⚡ 24/7 SECURITY COVERAGE  •  FAST RESPONSE TIME  •  "
          "PROFESSIONAL GUARDS  •  MOBILE PATROLS  •  "
          "APARTMENT COMMUNITIES  •  CONSTRUCTION SECURITY  •  "
          "LICENSED & INSURED  •  ")

def marquee(draw, t, y, h=76, speed=300):
    draw.rectangle([0, y, W, y + h], fill=(*NAVY, 245))
    draw.rectangle([0, y, W, y + 5], fill=(*RED, 255))
    draw.rectangle([0, y + h - 5, W, y + h], fill=(*RED, 255))
    f  = fnt(34)
    rep = TICKER * 4
    bw  = draw.textbbox((0, 0), rep, font=f)[2]
    sw  = bw // 4
    off = int(t * speed) % sw
    draw.text((-off,         y + (h - 38) // 2), rep, font=f, fill=(*WHITE, 240))
    draw.text((-off + bw//4, y + (h - 38) // 2), rep, font=f, fill=(*WHITE, 240))

def marquee2(draw, t, y, h=56, speed=180):
    """Slower gold marquee."""
    draw.rectangle([0, y, W, y + h], fill=(*DKRED, 230))
    f   = fnn(30)
    txt = ("  (346) 277-2563  •  www.montespatrolsecurityllc.com  •  "
           "LICENSED & INSURED  •  CALL NOW  •  ") * 4
    bw  = draw.textbbox((0, 0), txt, font=f)[2]
    sw  = bw // 4
    off = int(t * speed) % sw
    draw.text((-off, y + (h - 34) // 2), txt, font=f, fill=(*GOLD, 240))

# ── Text helpers ──────────────────────────────────────────────────────────────

def center_text(draw, text, font, y, col=WHITE, shadow=True):
    b  = draw.textbbox((0, 0), text, font=font)
    tw = b[2] - b[0]
    x  = (W - tw) // 2
    if shadow:
        draw.text((x+5, y+5), text, font=font, fill=(*BLACK, 160))
        draw.text((x+2, y+2), text, font=font, fill=(*DKRED, 100))
    draw.text((x, y), text, font=font, fill=col)
    return tw

def typewriter(draw, text, font, y, t, speed=18, col=WHITE):
    """Reveal text character by character."""
    n   = max(1, int(t * speed))
    vis = text[:n]
    center_text(draw, vis, font, y, col)

def bounce_in(t, delay=0.0, k=8.0):
    """Elastic bounce-in easing, returns 0→1."""
    tt = max(0.0, t - delay)
    if tt <= 0: return 0.0
    if tt >= 1: return 1.0
    return 1 - math.exp(-k * tt) * math.cos(math.pi * 2 * tt * 1.2)

def slide_ease(t, delay=0.0):
    tt = max(0.0, t - delay)
    if tt <= 0: return 0.0
    s = min(1.0, tt * 2.2)
    return 1 - (1 - s) ** 3

# ── SLIDE 1 ── IS YOUR PROPERTY TRULY SECURE? ────────────────────────────────

def slide1(img, t, dur=8.0):
    a   = fade_factor(t, 0.5, 0.4, dur)
    bg  = kb(img, t, dur, 1.0, 1.08, (0.08, -0.04))
    bg  = sharpen(bg)
    bg  = darken(bg, 0.72)           # less dark → clearer image
    arr = vignette(np.array(bg), 0.35)

    canvas = Image.fromarray(arr).convert("RGBA")
    draw   = ImageDraw.Draw(canvas, "RGBA")

    # Lens flare
    lens_sweep(draw, t, dur)

    # Particles
    draw_particles(draw, t, a)

    # Top accent
    draw.rectangle([W//2-60, 36, W//2+60, 44], fill=(*ORANGE, 220))

    # Top dark gradient band
    for i in range(380):
        alpha = int((1 - i/380) * a * 195)
        draw.rectangle([0, i, W, i+1], fill=(*NAVY, alpha))

    # Main question — bounce in per line
    f_big = fnt(98)
    lines = [("IS YOUR",   WHITE, 0.0),
             ("PROPERTY",  WHITE, 0.18),
             ("TRULY",     WHITE, 0.35),
             ("SECURE?",   RED,   0.52)]
    lh = 112
    sy = 52
    for i, (line, col, delay) in enumerate(lines):
        b_val = bounce_in(t, delay, k=7)
        scale_y = int((1 - b_val) * 50)
        op  = int(b_val * a * 255)
        bx  = draw.textbbox((0,0), line, font=f_big)
        tw  = bx[2] - bx[0]
        x   = (W - tw) // 2
        y   = sy + i * lh + scale_y
        draw.text((x+5, y+5), line, font=f_big, fill=(*BLACK, op//2))
        draw.text((x+2, y+2), line, font=f_big, fill=(*DKRED, op//3))
        draw.text((x,   y  ), line, font=f_big, fill=(*col,   op))

    # Sub caption typewriter
    f_sub = fnn(38)
    sub = "See how 24/7 licensed patrols eliminate your vulnerability."
    tw_fade = max(0.0, min(1.0, (t-1.8)*1.5))
    if tw_fade > 0:
        chars = max(1, int(tw_fade * len(sub)))
        partial = sub[:chars]
        b2 = draw.textbbox((0,0), partial, font=f_sub)
        tw2 = b2[2] - b2[0]
        draw.text(((W-tw2)//2, 510), partial, font=f_sub,
                  fill=(*WHITE, int(tw_fade * a * 210)))

    # Marquees
    marquee(draw, t, H - 210, h=76)
    marquee2(draw, t, H - 134, h=56)

    # Contact bottom
    draw.rectangle([0, H-78, W, H], fill=(*NAVY, int(a*250)))
    center_text(draw, "(346) 277-2563  |  montespatrolsecurityllc.com",
                fnn(30), H-62, col=(*GOLD, 255), shadow=False)

    arr2 = np.array(canvas.convert("RGB"))
    if a < 1.0:
        arr2 = (arr2 * a).astype(np.uint8)

    # Zoom flash at very start
    if t < 0.15:
        arr2 = zoom_flash(Image.fromarray(arr2), (0.15-t)/0.15)
    return arr2

# ── SLIDE 2 ── SAFETY NEVER TAKES A SHIFT OFF ────────────────────────────────

def slide2(img, t, dur=8.0):
    a   = fade_factor(t, 0.5, 0.4, dur)
    bg  = kb(img, t, dur, 1.08, 1.0, (-0.08, 0.0))
    bg  = sharpen(bg)
    bg  = darken(bg, 0.68)
    arr = vignette(np.array(bg), 0.38)

    canvas = Image.fromarray(arr).convert("RGBA")
    draw   = ImageDraw.Draw(canvas, "RGBA")

    lens_sweep(draw, t, dur)
    draw_particles(draw, t, a)

    # Top panel
    for i in range(820):
        alpha = int((1 - i/820)**1.5 * a * 205)
        draw.rectangle([0, i, W, i+1], fill=(*NAVY, alpha))

    # Words slide-up with stagger
    f_huge = fnt(118)
    words  = [("SAFETY",   WHITE, 0.00),
              ("NEVER",    WHITE, 0.22),
              ("TAKES",    RED,   0.40),
              ("A SHIFT",  RED,   0.58),
              ("OFF",      WHITE, 0.74)]
    lh = 132
    sy = 30
    for i, (word, col, delay) in enumerate(words):
        sv  = slide_ease(t, delay)
        yoff = int((1-sv)*80)
        op  = int(sv * a * 255)
        bx  = draw.textbbox((0,0), word, font=f_huge)
        tw  = bx[2] - bx[0]
        x   = (W - tw) // 2
        y   = sy + i*lh + yoff
        draw.text((x+5, y+5), word, font=f_huge, fill=(*BLACK, op//2))
        draw.text((x, y),     word, font=f_huge, fill=(*col,   op))

    # Body text fade-in
    f_body = fnn(42)
    body   = ["Most security gaps happen after dark.",
              "We're here to close them",
              "before they start."]
    fade2  = max(0, min(1.0, (t-1.6)*1.5))
    for i, line in enumerate(body):
        bx = draw.textbbox((0,0), line, font=f_body)
        tw = bx[2] - bx[0]
        draw.text(((W-tw)//2, 720+i*60), line, font=f_body,
                  fill=(*WHITE, int(fade2*a*215)))

    # Gold separator
    fade3 = max(0, min(1.0, (t-1.0)*2))
    bar_w = int(fade3 * (W-120))
    draw.rectangle([60, 906, 60+bar_w, 913], fill=(*GOLD, int(a*230)))

    marquee(draw, t, H-210)
    marquee2(draw, t, H-134)

    draw.rectangle([0, H-78, W, H], fill=(*NAVY, int(a*250)))
    center_text(draw, "LICENSED  •  INSURED  •  PROFESSIONAL",
                fnn(30), H-62, col=(*GOLD,255), shadow=False)

    arr2 = np.array(canvas.convert("RGB"))
    if a < 1.0:
        arr2 = (arr2 * a).astype(np.uint8)
    if t < 0.15:
        arr2 = zoom_flash(Image.fromarray(arr2), (0.15-t)/0.15)
    return arr2

# ── SLIDE 3 ── YOUR ASSETS, OUR AUTHORITY ────────────────────────────────────

def slide3(img, t, dur=7.0):
    a   = fade_factor(t, 0.5, 0.4, dur)
    bg  = kb(img, t, dur, 1.0, 1.09, (0.0, 0.07))
    bg  = sharpen(bg)
    bg  = darken(bg, 0.75)
    arr = vignette(np.array(bg), 0.30)

    canvas = Image.fromarray(arr).convert("RGBA")
    draw   = ImageDraw.Draw(canvas, "RGBA")

    lens_sweep(draw, t, dur)
    draw_particles(draw, t, a)

    # Bottom panel
    panel_top = 900
    for i in range(H - panel_top):
        frac  = i / (H - panel_top)
        alpha = int((0.3 + 0.7*frac) * a * 215)
        draw.rectangle([0, panel_top+i, W, panel_top+i+1],
                       fill=(*BLACK, alpha))

    # Animated red bar expanding
    fade_bar = min(1.0, t * 3)
    bar_w    = int(fade_bar * W)
    draw.rectangle([0, panel_top+2, bar_w, panel_top+10],
                   fill=(*RED, int(a*255)))

    # Tagline — slide from right with bounce
    f_tag = fnt(108)
    lines = [("YOUR ASSETS,", WHITE, 0.0, 942),
             ("OUR",          RED,   0.2, 1055),
             ("AUTHORITY",    WHITE, 0.4, 1166)]
    for line, col, delay, y in lines:
        sv   = bounce_in(t, delay, k=6)
        xoff = int((1-sv)*(W*0.6))
        op   = int(sv * a * 255)
        bx   = draw.textbbox((0,0), line, font=f_tag)
        tw   = bx[2] - bx[0]
        x    = (W - tw)//2 + xoff
        draw.text((x+5, y+5), line, font=f_tag, fill=(*BLACK, op//2))
        draw.text((x,   y  ), line, font=f_tag, fill=(*col,   op))

    # Underline
    fd2 = max(0, min(1.0, (t-0.9)*2))
    uw  = int(fd2*(W-200))
    draw.rectangle([100, 1296, 100+uw, 1303], fill=(*WHITE, int(a*200)))

    # Sub text
    fd3  = max(0, min(1.0, (t-1.2)*2))
    f_s  = fnn(36)
    subs = ["Join the property managers who trust the shield.",
            "Licensed, insured, and 24/7 available."]
    for i, line in enumerate(subs):
        bx = draw.textbbox((0,0), line, font=f_s)
        tw = bx[2] - bx[0]
        draw.text(((W-tw)//2, 1320+i*56), line, font=f_s,
                  fill=(*WHITE, int(fd3*a*210)))

    # Stars row
    fd4 = max(0, min(1.0, (t-1.5)*2))
    for i in range(5):
        sx = 175 + i*185
        sy2 = 1492
        r2  = 18
        pts = []
        for j in range(10):
            ang = math.radians(j*36 - 90)
            rr  = r2 if j%2==0 else r2*0.4
            pts.append((int(sx+rr*math.cos(ang)), int(sy2+rr*math.sin(ang))))
        draw.polygon(pts, fill=(*GOLD, int(fd4*a*220)))

    marquee(draw, t, H-210)
    marquee2(draw, t, H-134)
    draw.rectangle([0, H-78, W, H], fill=(*NAVY, int(a*250)))
    center_text(draw, "(346) 277-2563  |  montespatrolsecurityllc.com",
                fnn(30), H-62, col=(*GOLD,255), shadow=False)

    arr2 = np.array(canvas.convert("RGB"))
    if a < 1.0:
        arr2 = (arr2*a).astype(np.uint8)
    if t < 0.15:
        arr2 = zoom_flash(Image.fromarray(arr2), (0.15-t)/0.15)
    return arr2

# ── SLIDE 4 ── PROFESSIONAL ELITE PROTECTION ─────────────────────────────────

def slide4(img, t, dur=7.0):
    a   = fade_factor(t, 0.5, 0.6, dur)
    bg  = kb(img, t, dur, 1.06, 1.0, (0.04, -0.04))
    bg  = sharpen(bg)
    bg  = darken(bg, 0.70)
    arr = vignette(np.array(bg), 0.32)

    canvas = Image.fromarray(arr).convert("RGBA")
    draw   = ImageDraw.Draw(canvas, "RGBA")

    lens_sweep(draw, t, dur)
    draw_particles(draw, t, a)

    # Bottom panel
    pt = 1045
    for i in range(H-pt):
        frac  = i/(H-pt)
        alpha = int((0.4+0.6*frac)*a*225)
        draw.rectangle([0, pt+i, W, pt+i+1], fill=(*NAVY, alpha))

    draw.rectangle([0, pt, W, pt+8], fill=(*RED, int(a*255)))

    # CTA — typewriter then pulse
    f_cta = fnt(90)
    cta   = [("PROFESSIONAL", WHITE, 0.00, 1075),
             ("ELITE",        RED,   0.22, 1172),
             ("PROTECTION",   WHITE, 0.44, 1268)]
    for line, col, delay, y in cta:
        sv = slide_ease(t, delay)
        op = int(sv * a * 255)
        bx = draw.textbbox((0,0), line, font=f_cta)
        tw = bx[2]-bx[0]
        x  = (W-tw)//2
        # Glow
        draw.text((x+7, y+7), line, font=f_cta, fill=(*BLACK, op//2))
        draw.text((x+2, y+2), line, font=f_cta, fill=(*DKRED, op//3))
        draw.text((x,   y  ), line, font=f_cta, fill=(*col,   op))

    # Description
    fd2  = max(0, min(1.0, (t-0.9)*2))
    f_d  = fnn(36)
    desc = ["Licensed guards and mobile patrols",
            "tailored for apartments, retail,",
            "and construction."]
    for i, line in enumerate(desc):
        bx = draw.textbbox((0,0), line, font=f_d)
        tw = bx[2]-bx[0]
        draw.text(((W-tw)//2, 1388+i*54), line, font=f_d,
                  fill=(*WHITE, int(fd2*a*210)))

    # LICENSED INSURED badge
    fd3 = max(0, min(1.0, (t-1.2)*2))
    draw.rounded_rectangle([110, 1582, W-110, 1648],
                            radius=10, fill=(*DKRED, int(fd3*a*230)))
    center_text(draw, "LICENSED  •  INSURED", fnt(46), 1590,
                col=WHITE, shadow=False)

    marquee(draw, t, H-210)
    marquee2(draw, t, H-134)

    draw.rectangle([0, H-78, W, H], fill=(*DKRED, int(a*250)))
    center_text(draw, "(346) 277-2563", fnt(46), H-72,
                col=WHITE, shadow=False)

    arr2 = np.array(canvas.convert("RGB"))
    if a < 1.0:
        arr2 = (arr2*a).astype(np.uint8)
    if t < 0.15:
        arr2 = zoom_flash(Image.fromarray(arr2), (0.15-t)/0.15)
    return arr2

# ── Render ────────────────────────────────────────────────────────────────────

def build():
    from moviepy import VideoClip, concatenate_videoclips

    print("Cargando imágenes...")
    imgs = [load(f"slide{i}.png") for i in range(1,5)]

    segs  = [(slide1,8.0),(slide2,8.0),(slide3,7.0),(slide4,7.0)]
    clips = []
    for idx, (fn, dur) in enumerate(segs):
        img = imgs[idx]
        print(f"Renderizando slide {idx+1}  ({dur}s)...")
        clip = VideoClip(lambda t, f=fn, im=img, d=dur: f(im,t,d), duration=dur)
        clips.append(clip.with_fps(FPS))

    print("Concatenando...")
    final = concatenate_videoclips(clips, method="compose")

    out = "/home/user/Sublimontes_shop/montes_patrol_v3.mp4"
    print(f"Escribiendo {out} ...")
    final.write_videofile(
        out, fps=FPS, codec="libx264", audio=False,
        preset="fast",
        ffmpeg_params=["-crf","17","-pix_fmt","yuv420p",
                       "-profile:v","baseline","-level","3.1",
                       "-movflags","+faststart"],
        logger="bar",
    )
    print("¡Listo!")
    return out

if __name__ == "__main__":
    build()
