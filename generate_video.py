"""
Genera tiktok_promo.mp4 con las imágenes reales del producto.
  S1  0–6 s  Hook  → img_learn.png  (niña escribiendo)
  S2  6–12 s Kit   → img_kit.png    (4 libros + accesorios)
  S3 12–18 s Bene  → img_learn.png  (beneficios sobre foto)
  S4 18–24 s Uso   → img_teach.png  (cómo funciona)
  S5 24–30 s CTA   → img_book.png   (portada libro)
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, math, os
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

# ── CONFIG ────────────────────────────────────────────────────────────────────
W, H     = 390, 844
FPS      = 24
TOTAL    = 30
FRAMES   = FPS * TOTAL
SCENE_DUR = 6
FADE      = 0.40
BASE_DIR  = "/home/user/Sublimontes_shop"

# ── LOAD & PREP IMAGES ────────────────────────────────────────────────────────
def prep(path):
    """Recorta centro y escala a WxH."""
    img = Image.open(path).convert("RGB")
    iw, ih = img.size
    # crop centro manteniendo proporción
    target_ratio = W / H
    src_ratio    = iw / ih
    if src_ratio > target_ratio:
        new_w = int(ih * target_ratio)
        left  = (iw - new_w) // 2
        img   = img.crop((left, 0, left + new_w, ih))
    else:
        new_h = int(iw / target_ratio)
        top   = (ih - new_h) // 2
        img   = img.crop((0, top, iw, top + new_h))
    return img.resize((W, H), Image.LANCZOS)

IMGS = {
    "learn": prep(f"{BASE_DIR}/img_learn.png"),
    "kit":   prep(f"{BASE_DIR}/img_kit.png"),
    "teach": prep(f"{BASE_DIR}/img_teach.png"),
    "book":  prep(f"{BASE_DIR}/img_book.png"),
}

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
    "xl":   font(54),
    "lg":   font(42),
    "md":   font(30),
    "sm":   font(22),
    "xs":   font(17),
}

# ── HELPERS ───────────────────────────────────────────────────────────────────
def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3

def lerp(a, b, t): return a + (b - a) * t

def sine(t, amp=10, speed=1.5):
    return math.sin(t * speed * math.pi * 2) * amp

def fade_alpha(st, dur=SCENE_DUR, fade=FADE):
    return min(1.0, st / fade, (dur - st) / fade)

def dark_overlay(img, alpha=0.52):
    """Capa oscura semitransparente sobre la imagen."""
    ov = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.blend(img, ov, alpha)

def gradient_overlay(img, top_alpha=0.0, bot_alpha=0.75):
    """Gradiente negro arriba/abajo para legibilidad del texto."""
    ov  = img.convert("RGBA")
    lyr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d   = ImageDraw.Draw(lyr)
    for y in range(H):
        t = y / H
        a = int(lerp(top_alpha, bot_alpha, t) * 255)
        d.line([(0, y), (W, y)], fill=(0, 0, 0, a))
    return Image.alpha_composite(ov, lyr).convert("RGB")

def rounded_rect_rgba(img, x1, y1, x2, y2, r, fill_rgba):
    base = img.convert("RGBA")
    lyr  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d    = ImageDraw.Draw(lyr)
    d.rounded_rectangle([x1, y1, x2, y2], radius=r, fill=fill_rgba)
    return Image.alpha_composite(base, lyr).convert("RGB")

def text_c(draw, text, y, fnt, color=(255,255,255), shadow=True, shadow_alpha=130):
    bbox = draw.textbbox((0,0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    x  = (W - tw) // 2
    if shadow:
        draw.text((x+3, y+4), text, font=fnt, fill=(0,0,0,shadow_alpha))
    draw.text((x, y), text, font=fnt, fill=color)
    return bbox[3] - bbox[1]

def text_at(draw, text, x, y, fnt, color=(255,255,255), shadow=True):
    if shadow:
        draw.text((x+2, y+3), text, font=fnt, fill=(0,0,0,110))
    draw.text((x, y), text, font=fnt, fill=color)

def pill(img, text, cx, cy, fnt, bg=(255,217,61,220), tc=(30,30,30)):
    """Pastilla con texto centrado en (cx,cy)."""
    d    = ImageDraw.Draw(img)
    bbox = d.textbbox((0,0), text, font=fnt)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    pad = 14
    x1, y1 = cx - tw//2 - pad, cy - th//2 - 8
    x2, y2 = cx + tw//2 + pad, cy + th//2 + 8
    img = rounded_rect_rgba(img, x1, y1, x2, y2, 28, bg)
    d   = ImageDraw.Draw(img)
    d.text((cx - tw//2, cy - th//2), text, font=fnt, fill=tc)
    return img

def progress_bar(draw, total_t):
    draw.rectangle([0, 0, W, 5], fill=(255,255,255,40))
    pw = int(W * total_t / TOTAL)
    if pw > 0:
        draw.rectangle([0, 0, pw, 5], fill=(255,217,61))

# ── SCENE 1: HOOK ─────────────────────────────────────────────────────────────
#   Imagen: niña escribiendo (img_learn)
#   Texto:  "¿Tu niño aprende  jugando?" + subtítulo

def scene1(base_img, st, total_t):
    img = base_img.copy()
    img = gradient_overlay(img, top_alpha=0.65, bot_alpha=0.20)

    sl  = ease_out(st / 0.55)
    ty  = int(lerp(-120, 55, sl))

    draw = ImageDraw.Draw(img)
    text_c(draw, "Does your kid",  ty,       F["xl"])
    text_c(draw, "learn by",       ty + 65,  F["xl"])
    text_c(draw, "playing?",       ty + 130, F["xl"], color=(255,237,61))

    sub_sl = ease_out(max(0, st - 0.5) / 0.4)
    sy_off = int(lerp(30, 0, sub_sl))
    sub_a  = sub_sl
    if sub_a > 0:
        img = pill(img, "Now they can! 🎉",
                   W//2, ty + 215 + sy_off,
                   F["md"], bg=(255,107,107,220), tc=(255,255,255))

    draw = ImageDraw.Draw(img)
    progress_bar(draw, total_t)
    return img

# ── SCENE 2: PRODUCTO / KIT ───────────────────────────────────────────────────
#   Imagen: kit completo (img_kit) — muestra los 4 libros + accesorios
#   Texto:  título + badges de los libros + kit badge

def scene2(base_img, st, total_t):
    img = base_img.copy()
    img = gradient_overlay(img, top_alpha=0.70, bot_alpha=0.55)

    sl  = ease_out(st / 0.5)
    ty  = int(lerp(-80, 42, sl))

    draw = ImageDraw.Draw(img)
    text_c(draw, "✨ Magic Groove",      ty,      F["md"])
    text_c(draw, "Practice Copybook",   ty + 36, F["md"])

    # 4 badges de libros
    BOOKS = [
        ("🎨 Dibujo",       (255, 90, 90, 210)),
        ("🔤 Abecedario",   ( 60,130,255, 210)),
        ("🔢 Números",      (255,200, 40, 230)),
        ("➕ Matemáticas",  ( 80,200,100, 210)),
    ]
    bw, bh, gap = 155, 52, 10
    bx0 = (W - (bw*2 + gap)) // 2
    by0 = ty + 82
    for i,(label,bg) in enumerate(BOOKS):
        delay = ease_out(max(0, st - 0.15 - i*0.13) / 0.35)
        col, row = i % 2, i // 2
        bx = bx0 + col*(bw+gap)
        by = by0 + row*(bh+gap)
        oy = int(lerp(40, 0, delay))
        tc = (30,30,30) if i==2 else (255,255,255)
        img = rounded_rect_rgba(img, bx, by+oy, bx+bw, by+bh+oy, 16, bg)
        draw = ImageDraw.Draw(img)
        bbox = draw.textbbox((0,0), label, font=F["sm"])
        tw = bbox[2]-bbox[0]
        draw.text(((W//2 - bw//2 - gap//2 + col*(bw+gap) + (bw-tw)//2),
                   by + 14 + oy), label, font=F["sm"], fill=tc)

    # badge kit
    kit_sl = ease_out(max(0, st-0.7)/0.35)
    ky_off = int(lerp(30,0,kit_sl))
    by_kit = by0 + 2*(bh+gap) + 14
    img = pill(img, "📦 4 books · pen · 6 refills · grip",
               W//2, by_kit + ky_off, F["xs"],
               bg=(255,255,255,55), tc=(255,255,255))

    draw = ImageDraw.Draw(img)
    progress_bar(draw, total_t)
    return img

# ── SCENE 3: BENEFICIOS ───────────────────────────────────────────────────────
#   Imagen: niña escribiendo (img_learn)

BENEFITS = [
    ("✍️", "Improves handwriting"),
    ("👁️", "Hand-eye coordination"),
    ("🧠", "Builds concentration"),
]

def scene3(base_img, st, total_t):
    img = base_img.copy()
    img = gradient_overlay(img, top_alpha=0.75, bot_alpha=0.50)

    sl  = ease_out(st / 0.45)
    ty  = int(lerp(-60, 55, sl))

    draw = ImageDraw.Draw(img)
    text_c(draw, "Why does it work? 🤔", ty, F["md"])

    bh, gap = 86, 14
    by0 = ty + 68
    for i,(em,label) in enumerate(BENEFITS):
        delay = ease_out(max(0, st - 0.2 - i*0.18) / 0.38)
        ox    = int(lerp(-W, 0, delay))
        y1    = by0 + i*(bh+gap)
        img   = rounded_rect_rgba(img, 22+ox, y1, W-22+ox, y1+bh, 20,
                                  (255,255,255,55))
        draw  = ImageDraw.Draw(img)
        try:
            draw.text((42+ox, y1+24), em, font=F["md"], fill=(255,255,255))
        except:
            pass
        text_at(draw, label, 92+ox, y1+28, F["sm"])

    draw = ImageDraw.Draw(img)
    progress_bar(draw, total_t)
    return img

# ── SCENE 4: CÓMO FUNCIONA ────────────────────────────────────────────────────
#   Imagen: img_teach (niña dibujando con libro)

STEPS = [
    ("1", "Trace the magic grooves"),
    ("2", "Ink disappears ✨"),
    ("3", "Practice again & again!"),
]

def scene4(base_img, st, total_t):
    img = base_img.copy()
    img = gradient_overlay(img, top_alpha=0.72, bot_alpha=0.45)

    sl  = ease_out(st / 0.45)
    ty  = int(lerp(-70, 48, sl))

    draw = ImageDraw.Draw(img)
    text_c(draw, "So easy to use! 🖊️",  ty,     F["md"])
    text_c(draw, "For kids ages 3+ 👶", ty+40,  F["sm"],
           color=(255,237,61))

    bh, gap = 92, 16
    by0 = ty + 96
    for i,(num,label) in enumerate(STEPS):
        delay = ease_out(max(0, st - 0.18 - i*0.18) / 0.38)
        ox    = int(lerp(-W, 0, delay))
        y1    = by0 + i*(bh+gap)
        img   = rounded_rect_rgba(img, 22+ox, y1, W-22+ox, y1+bh, 20,
                                  (0,0,0,90))
        draw  = ImageDraw.Draw(img)
        # círculo numerado
        draw.ellipse([38+ox, y1+22, 82+ox, y1+66],
                     fill=(255,107,107,230))
        bbox = draw.textbbox((0,0), num, font=F["md"])
        nw   = bbox[2]-bbox[0]
        draw.text((60+ox-nw//2, y1+28), num, font=F["md"],
                  fill=(255,255,255))
        text_at(draw, label, 98+ox, y1+30, F["sm"])

    draw = ImageDraw.Draw(img)
    progress_bar(draw, total_t)
    return img

# ── SCENE 5: CTA ──────────────────────────────────────────────────────────────
#   Imagen: portada del libro (img_book)

def scene5(base_img, st, total_t):
    img = base_img.copy()
    img = gradient_overlay(img, top_alpha=0.60, bot_alpha=0.82)

    pulse = 1.0 + 0.04 * math.sin(st * math.pi * 2.5)
    sl    = ease_out(st / 0.45)
    ty    = int(lerp(-80, 100, sl))

    draw = ImageDraw.Draw(img)
    text_c(draw, "Get yours now! 🛍️",  ty,      F["lg"])
    text_c(draw, "🔥 Special offer",   ty + 58, F["md"],
           color=(255,237,61))

    # botón CTA
    btn_w = int(288 * pulse)
    btn_h = int(62  * pulse)
    bx    = (W - btn_w) // 2
    by    = ty + 120
    btn_sl = ease_out(max(0, st-0.5)/0.35)
    by_off = int(lerp(30,0,btn_sl))
    img   = rounded_rect_rgba(img, bx, by+by_off, bx+btn_w, by+btn_h+by_off,
                               32, (255,255,255,240))
    draw  = ImageDraw.Draw(img)
    bbox  = draw.textbbox((0,0), "VER PRODUCTO →", font=F["sm"])
    tw    = bbox[2]-bbox[0]
    draw.text(((W-tw)//2, by+16+by_off), "VER PRODUCTO →",
              font=F["sm"], fill=(255,90,90))

    # info tienda
    info_sl = ease_out(max(0, st-0.65)/0.35)
    iy_off  = int(lerp(20,0,info_sl))
    text_c(draw, "📍 Sublimontes Shop",
           by + btn_h + 24 + iy_off, F["sm"])
    text_c(draw, "Link in bio ⬆️",
           by + btn_h + 56 + iy_off, F["xs"],
           color=(255,255,200))
    text_c(draw, "@sublimontesshop",
           by + btn_h + 84 + iy_off, F["xs"],
           color=(255,255,200))

    draw = ImageDraw.Draw(img)
    progress_bar(draw, total_t)
    return img

# ── SCENE MAP ─────────────────────────────────────────────────────────────────
SCENE_CFG = [
    (scene1, "learn"),
    (scene2, "kit"),
    (scene3, "learn"),
    (scene4, "teach"),
    (scene5, "book"),
]

# ── RENDER FRAME ─────────────────────────────────────────────────────────────
def render_frame(idx):
    total_t   = idx / FPS
    s_idx     = min(int(total_t // SCENE_DUR), 4)
    st        = total_t - s_idx * SCENE_DUR
    alpha     = fade_alpha(st)

    fn, img_key = SCENE_CFG[s_idx]
    frame = fn(IMGS[img_key], st, total_t)

    # watermark
    draw = ImageDraw.Draw(frame)
    draw.text((14, H-28), "@sublimontesshop", font=F["xs"],
              fill=(255,255,255,160))

    # fade in/out
    if alpha < 0.98:
        black = Image.new("RGB", (W, H), (0,0,0))
        frame = Image.blend(black, frame, alpha)

    return np.array(frame)

# ── MAIN ─────────────────────────────────────────────────────────────────────
print(f"Generando {FRAMES} frames con imágenes reales…")
frames = []
for i in range(FRAMES):
    if i % (FPS * 2) == 0:
        print(f"  {i}/{FRAMES}  ({i//FPS}s)", flush=True)
    frames.append(render_frame(i))

out = f"{BASE_DIR}/tiktok_promo.mp4"
print("Compilando MP4…")
clip = ImageSequenceClip(frames, fps=FPS)
clip.write_videofile(out, codec="libx264", fps=FPS, audio=False, logger=None,
                     ffmpeg_params=["-pix_fmt","yuv420p","-crf","18"])
print(f"✅  {out}")
