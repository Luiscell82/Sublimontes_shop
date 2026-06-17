"""
tiktok_promo.mp4 – v2: imagen limpia (sin texto encima) + panel de texto
separado abajo. Resolución 1080x1920 (Full HD vertical) para nitidez.

Layout por escena:
  ┌─────────────────┐
  │                 │
  │   IMAGEN LIMPIA │  ← sin texto, con efecto Ken Burns (zoom suave)
  │                 │
  ├─────────────────┤  ← línea divisoria de acento
  │   PANEL DE TEXTO│  ← fondo de color sólido/degradado, todo el texto va aquí
  └─────────────────┘
"""

from PIL import Image, ImageDraw, ImageFont
import numpy as np, math, os
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

# ── CONFIG ────────────────────────────────────────────────────────────────────
W, H      = 1080, 1920
FPS       = 30
TOTAL     = 30
FRAMES    = FPS * TOTAL
SCENE_DUR = 6
FADE      = 0.40
BASE_DIR  = "/home/user/Sublimontes_shop"

ZOOM_PAD = 1.18   # tamaño extra de la imagen fuente para el efecto Ken Burns

# ── LOAD IMAGES (a tamaño grande, recorte por escena se hace después) ─────────
def load_src(path):
    return Image.open(path).convert("RGB")

SRC = {
    "learn": load_src(f"{BASE_DIR}/img_learn.png"),
    "kit":   load_src(f"{BASE_DIR}/img_kit.png"),
    "teach": load_src(f"{BASE_DIR}/img_teach.png"),
    "book":  load_src(f"{BASE_DIR}/img_book.png"),
}

def cover_resize(img, w, h):
    """Recorta al centro y escala para llenar exactamente w x h (sin deformar)."""
    iw, ih = img.size
    target_ratio = w / h
    src_ratio    = iw / ih
    if src_ratio > target_ratio:
        new_w = int(ih * target_ratio)
        left  = (iw - new_w) // 2
        img   = img.crop((left, 0, left + new_w, ih))
    else:
        new_h = int(iw / target_ratio)
        top   = (ih - new_h) // 2
        img   = img.crop((0, top, iw, top + new_h))
    return img.resize((w, h), Image.LANCZOS)

# cache de imágenes grandes por zona (se genera una vez por tamaño de zona)
_zone_cache = {}
def get_zoom_source(img_key, zone_w, zone_h):
    cache_key = (img_key, zone_w, zone_h)
    if cache_key not in _zone_cache:
        big = cover_resize(SRC[img_key], int(zone_w*ZOOM_PAD), int(zone_h*ZOOM_PAD))
        _zone_cache[cache_key] = big
    return _zone_cache[cache_key]

def ken_burns(img_key, zone_w, zone_h, p):
    """p en [0,1] → zoom progresivo (zoom-in suave)."""
    big = get_zoom_source(img_key, zone_w, zone_h)
    bw, bh = big.size
    shrink = 1.0 - 0.14 * p          # de 1.0 (zoom out) a 0.86 (zoom in)
    cw, ch = int(bw*shrink), int(bh*shrink)
    cw, ch = max(cw, zone_w), max(ch, zone_h)
    x = (bw - cw) // 2
    y = (bh - ch) // 2
    crop = big.crop((x, y, x+cw, y+ch))
    return crop.resize((zone_w, zone_h), Image.LANCZOS)

# ── FONTS ─────────────────────────────────────────────────────────────────────
def font(size, bold=True):
    paths = [
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans-{'Bold' if bold else ''}.ttf",
        f"/usr/share/fonts/truetype/liberation/LiberationSans-{'Bold' if bold else 'Regular'}.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

F = {
    "xl": font(86),
    "lg": font(72),
    "md": font(54),
    "sm": font(38),
    "xs": font(30),
}

# ── HELPERS ───────────────────────────────────────────────────────────────────
def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3

def lerp(a, b, t): return a + (b - a) * t

def fade_alpha(st, dur=SCENE_DUR, fade=FADE):
    return min(1.0, st / fade, (dur - st) / fade)

def vgrad_panel(w, h, c_top, c_bot):
    t    = np.linspace(0, 1, h).reshape(h, 1, 1)
    top  = np.array(c_top, dtype=np.float32).reshape(1, 1, 3)
    bot  = np.array(c_bot, dtype=np.float32).reshape(1, 1, 3)
    grad = (top + (bot - top) * t)
    grad = np.repeat(grad, w, axis=1).astype(np.uint8)
    return Image.fromarray(grad)

def rounded_rect_local(panel, x1, y1, x2, y2, r, fill_rgba):
    """Compone un rectángulo redondeado SOLO sobre la región afectada (rápido)."""
    pad = 2
    rx1, ry1 = max(0, x1-pad), max(0, y1-pad)
    rx2, ry2 = min(panel.width, x2+pad), min(panel.height, y2+pad)
    if rx2 <= rx1 or ry2 <= ry1:
        return   # totalmente fuera de pantalla, nada que dibujar
    region = panel.crop((rx1, ry1, rx2, ry2)).convert("RGBA")
    ov = Image.new("RGBA", region.size, (0,0,0,0))
    d  = ImageDraw.Draw(ov)
    d.rounded_rectangle([x1-rx1, y1-ry1, x2-rx1, y2-ry1], radius=r, fill=fill_rgba)
    blended = Image.alpha_composite(region, ov).convert("RGB")
    panel.paste(blended, (rx1, ry1))

def text_c(draw, text, y, fnt, color=(255,255,255), panel_w=W, x_off=0, shadow=True):
    bbox = draw.textbbox((0,0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    x  = x_off + (panel_w - tw) // 2
    if shadow:
        draw.text((x+2, y+3), text, font=fnt, fill=(0,0,0,90))
    draw.text((x, y), text, font=fnt, fill=color)
    return bbox[3] - bbox[1]

def text_l(draw, text, x, y, fnt, color=(255,255,255), shadow=True):
    if shadow:
        draw.text((x+2, y+3), text, font=fnt, fill=(0,0,0,90))
    draw.text((x, y), text, font=fnt, fill=color)

def pill(panel, text, cx, cy, fnt, bg=(255,217,61,235), tc=(30,30,30)):
    d = ImageDraw.Draw(panel)
    bbox = d.textbbox((0,0), text, font=fnt)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    padx, pady = 38, 22
    x1, y1 = cx - tw//2 - padx, cy - th//2 - pady
    x2, y2 = cx + tw//2 + padx, cy + th//2 + pady
    rounded_rect_local(panel, x1, y1, x2, y2, 999, bg)
    d = ImageDraw.Draw(panel)
    d.text((cx - tw//2, cy - th//2), text, font=fnt, fill=tc)

# ── SCENE GRADIENTS (panel de texto) ─────────────────────────────────────────
PANEL_GRAD = {
    "s1": [(255,107,107), (255, 80, 80)],
    "s2": [( 60,150,110), ( 40,110, 90)],
    "s3": [(110, 70,170), ( 80, 50,140)],
    "s4": [(  0,120,180), (  0, 90,150)],
    "s5": [(255,140, 60), (255,100, 40)],
}
ACCENT = (255, 217, 61)   # línea divisoria / acentos

def build_panel(key, w, h):
    return vgrad_panel(w, h, *PANEL_GRAD[key])

# ── ESCENA 1 — HOOK  (zona img 62% / panel 38%) ───────────────────────────────
def scene1(st, total_t):
    img_h = int(H * 0.62)
    pan_h = H - img_h

    frame = ken_burns("learn", W, img_h, st/SCENE_DUR)
    panel = build_panel("s1", W, pan_h)

    sl = ease_out(st/0.55)
    ty = int(lerp(-100, 90, sl))
    draw = ImageDraw.Draw(panel)
    text_c(draw, "Does your kid",  ty,      F["xl"])
    text_c(draw, "learn by",       ty+96,   F["xl"])
    text_c(draw, "playing?",       ty+192,  F["xl"], color=ACCENT)

    sub_sl = ease_out(max(0, st-0.55)/0.4)
    if sub_sl > 0:
        sy = int(lerp(40, 0, sub_sl))
        pill(panel, "Now they can! 🎉", W//2, ty+300+sy, F["md"],
             bg=(255,255,255,235), tc=(200,50,50))

    return frame, panel, img_h

# ── ESCENA 2 — PRODUCTO (zona img 46% / panel 54%) ───────────────────────────
BOOKS = [
    ("🎨  Drawing",      (255, 90, 90, 235)),
    ("🔤  Alphabet",     ( 60,130,255, 235)),
    ("🔢  Numbers",      (255,200, 40, 245)),
    ("➕  Math",         ( 80,200,120, 235)),
]

def scene2(st, total_t):
    img_h = int(H * 0.46)
    pan_h = H - img_h

    frame = ken_burns("kit", W, img_h, st/SCENE_DUR)
    panel = build_panel("s2", W, pan_h)
    draw  = ImageDraw.Draw(panel)

    sl = ease_out(st/0.5)
    ty = int(lerp(-70, 70, sl))
    text_c(draw, "✨ Magic Groove",     ty,    F["md"])
    text_c(draw, "Practice Copybook",  ty+60, F["md"])

    bw, bh, gap = 460, 130, 26
    bx0 = (W - (bw*2 + gap)) // 2
    by0 = ty + 150
    for i, (label, bg) in enumerate(BOOKS):
        delay = ease_out(max(0, st - 0.15 - i*0.13)/0.35)
        col, row = i % 2, i // 2
        bx = bx0 + col*(bw+gap)
        by = by0 + row*(bh+gap)
        oy = int(lerp(50, 0, delay))
        tc = (30,30,30) if i == 2 else (255,255,255)
        rounded_rect_local(panel, bx, by+oy, bx+bw, by+bh+oy, 24, bg)
        draw = ImageDraw.Draw(panel)
        bbox = draw.textbbox((0,0), label, font=F["sm"])
        tw = bbox[2]-bbox[0]
        draw.text((bx+(bw-tw)//2, by+oy+(bh-(bbox[3]-bbox[1]))//2-6),
                  label, font=F["sm"], fill=tc)

    kit_sl = ease_out(max(0, st-0.7)/0.35)
    ky_off = int(lerp(40,0,kit_sl))
    by_kit = by0 + 2*(bh+gap) + 30
    pill(panel, "📦 4 books · pen · 6 refills · grip", W//2, by_kit+ky_off,
         F["xs"], bg=(255,255,255,210), tc=(30,90,70))

    return frame, panel, img_h

# ── ESCENA 3 — BENEFICIOS (zona img 52% / panel 48%) ──────────────────────────
BENEFITS = [
    ("✍️", "Improves handwriting"),
    ("👁️", "Hand-eye coordination"),
    ("🧠", "Builds concentration"),
]

def scene3(st, total_t):
    img_h = int(H * 0.52)
    pan_h = H - img_h

    frame = ken_burns("learn", W, img_h, st/SCENE_DUR)
    panel = build_panel("s3", W, pan_h)
    draw  = ImageDraw.Draw(panel)

    sl = ease_out(st/0.45)
    ty = int(lerp(-60, 70, sl))
    text_c(draw, "Why does it work? 🤔", ty, F["md"])

    bh, gap = 150, 30
    by0 = ty + 110
    for i, (em, label) in enumerate(BENEFITS):
        delay = ease_out(max(0, st - 0.2 - i*0.18)/0.38)
        ox = int(lerp(-W, 0, delay))
        y1 = by0 + i*(bh+gap)
        rounded_rect_local(panel, 50+ox, y1, W-50+ox, y1+bh, 28, (255,255,255,55))
        draw = ImageDraw.Draw(panel)
        draw.text((90+ox, y1+38), em, font=F["md"], fill=(255,255,255))
        text_l(draw, label, 180+ox, y1+48, F["sm"])

    return frame, panel, img_h

# ── ESCENA 4 — CÓMO FUNCIONA (zona img 50% / panel 50%) ──────────────────────
STEPS = [
    ("1", "Trace the magic grooves"),
    ("2", "Ink disappears ✨"),
    ("3", "Practice again & again!"),
]

def scene4(st, total_t):
    img_h = int(H * 0.50)
    pan_h = H - img_h

    frame = ken_burns("teach", W, img_h, st/SCENE_DUR)
    panel = build_panel("s4", W, pan_h)
    draw  = ImageDraw.Draw(panel)

    sl = ease_out(st/0.45)
    ty = int(lerp(-60, 60, sl))
    text_c(draw, "So easy to use! 🖊️", ty, F["md"])
    text_c(draw, "For kids ages 3+ 👶", ty+66, F["sm"], color=ACCENT)

    bh, gap = 150, 28
    by0 = ty + 150
    for i, (num, label) in enumerate(STEPS):
        delay = ease_out(max(0, st - 0.18 - i*0.18)/0.38)
        ox = int(lerp(-W, 0, delay))
        y1 = by0 + i*(bh+gap)
        rounded_rect_local(panel, 50+ox, y1, W-50+ox, y1+bh, 28, (0,0,0,90))
        draw = ImageDraw.Draw(panel)
        draw.ellipse([86+ox, y1+30, 86+ox+90, y1+30+90], fill=(255,107,107,235))
        bbox = draw.textbbox((0,0), num, font=F["md"])
        nw = bbox[2]-bbox[0]
        draw.text((131+ox-nw//2, y1+40), num, font=F["md"], fill=(255,255,255))
        text_l(draw, label, 200+ox, y1+50, F["sm"])

    return frame, panel, img_h

# ── ESCENA 5 — CTA (zona img 44% / panel 56%) ─────────────────────────────────
def scene5(st, total_t):
    img_h = int(H * 0.44)
    pan_h = H - img_h

    frame = ken_burns("book", W, img_h, st/SCENE_DUR)
    panel = build_panel("s5", W, pan_h)
    draw  = ImageDraw.Draw(panel)

    pulse = 1.0 + 0.04*math.sin(st*math.pi*2.5)
    sl = ease_out(st/0.45)
    ty = int(lerp(-90, 90, sl))

    text_c(draw, "Get yours now! 🛍️", ty, F["lg"])
    text_c(draw, "🔥 Special offer",  ty+90, F["md"], color=ACCENT)

    btn_w, btn_h = int(560*pulse), int(110*pulse)
    bx = (W-btn_w)//2
    by = ty + 200
    btn_sl = ease_out(max(0, st-0.5)/0.35)
    by_off = int(lerp(40,0,btn_sl))
    rounded_rect_local(panel, bx, by+by_off, bx+btn_w, by+btn_h+by_off, 56,
                        (255,255,255,245))
    draw = ImageDraw.Draw(panel)
    label = "VIEW PRODUCT →"
    bbox = draw.textbbox((0,0), label, font=F["sm"])
    tw = bbox[2]-bbox[0]
    draw.text(((W-tw)//2, by+by_off+(btn_h-(bbox[3]-bbox[1]))//2-8),
              label, font=F["sm"], fill=(230,90,40))

    info_sl = ease_out(max(0, st-0.65)/0.35)
    iy_off = int(lerp(30,0,info_sl))
    text_c(draw, "📍 Sublimontes Shop", by+btn_h+50+iy_off, F["sm"])
    text_c(draw, "Link in bio ⬆️",     by+btn_h+110+iy_off, F["xs"], color=(255,255,210))
    text_c(draw, "@sublimontesshop",    by+btn_h+150+iy_off, F["xs"], color=(255,255,210))

    return frame, panel, img_h

SCENES = [scene1, scene2, scene3, scene4, scene5]

# ── COMPOSE FRAME ─────────────────────────────────────────────────────────────
def progress_overlay(frame, total_t):
    draw = ImageDraw.Draw(frame)
    draw.rectangle([0,0,W,8], fill=(255,255,255,60))
    pw = int(W * total_t/TOTAL)
    if pw > 0:
        draw.rectangle([0,0,pw,8], fill=ACCENT)

def render_frame(idx):
    total_t = idx/FPS
    s_idx   = min(int(total_t // SCENE_DUR), 4)
    st      = total_t - s_idx*SCENE_DUR
    alpha   = fade_alpha(st)

    img_top, panel, img_h = SCENES[s_idx](st, total_t)

    canvas = Image.new("RGB", (W, H), (0,0,0))
    canvas.paste(img_top, (0, 0))
    canvas.paste(panel,   (0, img_h))

    # línea divisoria de acento entre imagen y panel
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, img_h-6, W, img_h], fill=ACCENT)

    progress_overlay(canvas, total_t)

    # watermark discreto, esquina inferior del panel (no sobre la foto)
    d = ImageDraw.Draw(canvas)
    wm = "@sublimontesshop"
    bbox = d.textbbox((0,0), wm, font=F["xs"])
    d.text((W - (bbox[2]-bbox[0]) - 28, H-56), wm, font=F["xs"],
          fill=(255,255,255,140))

    if alpha < 0.98:
        black = Image.new("RGB", (W,H), (0,0,0))
        canvas = Image.blend(black, canvas, alpha)

    return np.array(canvas)

# ── MAIN ─────────────────────────────────────────────────────────────────────
print(f"Generando {FRAMES} frames a {W}x{H}…")
frames = []
for i in range(FRAMES):
    if i % (FPS*2) == 0:
        print(f"  {i}/{FRAMES}  ({i//FPS}s)", flush=True)
    frames.append(render_frame(i))

out = f"{BASE_DIR}/tiktok_promo.mp4"
print("Compilando MP4 en alta calidad…")
clip = ImageSequenceClip(frames, fps=FPS)
clip.write_videofile(out, codec="libx264", fps=FPS, audio=False, logger=None,
                     ffmpeg_params=["-pix_fmt","yuv420p","-crf","16","-preset","slow"])
print(f"✅  {out}")
