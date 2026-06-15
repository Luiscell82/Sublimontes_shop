"""
Genera tiktok_promo.mp4 – video promocional 30 s, 390×844 px (9:16)
Escenas:
  S1  0–6 s  Hook "¿Tu niño aprende jugando?"
  S2  6–12 s Producto: 4 libros + kit
  S3  12–18 s Beneficios
  S4  18–24 s Cómo funciona
  S5  24–30 s CTA + tienda
"""

from PIL import Image, ImageDraw, ImageFont
import numpy as np
import math, os, sys
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

# ── CONFIG ──────────────────────────────────────────────────────────────────
W, H   = 390, 844
FPS    = 24
TOTAL  = 30          # segundos
FRAMES = FPS * TOTAL # 720 frames

SCENE_DUR = 6        # segundos por escena
FADE      = 0.35     # segundos fade in/out

# ── PALETA ──────────────────────────────────────────────────────────────────
C = {
    "white":   (255, 255, 255),
    "yellow":  (255, 217,  61),
    "pink":    (255, 107, 107),
    "blue":    (77,  150, 255),
    "green":   (107, 203, 119),
    "purple":  (132,  94, 194),
    "orange":  (255, 150, 113),
    "teal":    (  0, 201, 167),
    "navy":    (  0, 129, 207),
    "dark":    ( 40,  40,  40),
    "shadow":  (  0,   0,   0,  80),
    "overlay": (255, 255, 255,  55),
}

GRAD = {
    1: [(255,217,61),  (255,107,107)],
    2: [(107,203,119), (77,150,255)],
    3: [(132,94,194),  (255,150,113)],
    4: [(0,129,207),   (0,201,167)],
    5: [(255,107,107), (255,217,61)],
}

# ── FONTS ───────────────────────────────────────────────────────────────────
def load_font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold
            else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

F = {
    "title":   load_font(52, bold=True),
    "big":     load_font(42, bold=True),
    "mid":     load_font(30, bold=True),
    "sub":     load_font(22, bold=True),
    "small":   load_font(18, bold=True),
    "emoji":   load_font(36),
}

# ── HELPERS ─────────────────────────────────────────────────────────────────
def gradient(img, top_color, bot_color):
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(top_color[0] + (bot_color[0]-top_color[0])*t)
        g = int(top_color[1] + (bot_color[1]-top_color[1])*t)
        b = int(top_color[2] + (bot_color[2]-top_color[2])*t)
        draw.line([(0,y),(W,y)], fill=(r,g,b))

def text_center(draw, text, y, font, color=(255,255,255), shadow=True):
    bbox = draw.textbbox((0,0), text, font=font)
    tw = bbox[2]-bbox[0]
    x = (W - tw) // 2
    if shadow:
        draw.text((x+3, y+3), text, font=font, fill=(0,0,0,100))
    draw.text((x, y), text, font=font, fill=color)
    return bbox[3]-bbox[1]   # height

def text_center_lines(draw, lines, y_start, font, color=(255,255,255), gap=8):
    cy = y_start
    for line in lines:
        h = text_center(draw, line, cy, font, color)
        cy += h + gap
    return cy

def rounded_rect(img, x1,y1,x2,y2, radius, fill):
    overlay = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(overlay)
    d.rounded_rectangle([x1,y1,x2,y2], radius=radius, fill=fill)
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"),
              mask=None)
    # simpler:
    base = img.convert("RGBA")
    d2   = ImageDraw.Draw(base)
    d2.rounded_rectangle([x1,y1,x2,y2], radius=radius, fill=fill)
    return base.convert("RGB")

def lerp(a,b,t): return a + (b-a)*t

def ease_out(t): return 1-(1-t)**3

def fade_alpha(scene_t, scene_dur, fade_dur):
    """0..1 opacity: fade in at start, fade out at end"""
    fi = min(1.0, scene_t / fade_dur)
    fo = min(1.0, (scene_dur - scene_t) / fade_dur)
    return min(fi, fo)

def apply_alpha(frame, alpha):
    if alpha >= 1.0: return frame
    arr = np.array(frame, dtype=np.float32)
    arr = arr * alpha
    return Image.fromarray(arr.astype(np.uint8))

def float_offset(t, amp=10, speed=1.5):
    return math.sin(t * speed * math.pi * 2) * amp

# ── PROGRESS BAR ─────────────────────────────────────────────────────────────
def draw_progress(img, total_t):
    draw = ImageDraw.Draw(img)
    bh = 5
    draw.rectangle([0,0,W,bh], fill=(255,255,255,40))
    pw = int(W * (total_t / TOTAL))
    draw.rectangle([0,0,pw,bh], fill=C["yellow"])

# ── SCENE 1: HOOK ────────────────────────────────────────────────────────────
EMOJIS_S1 = ["⭐","🎨","✏️","📚","🌟","🖊️"]
EMOJI_POS  = [(30,80),(300,100),(20,400),(310,420),(50,600),(310,580)]

def scene1(img, st, alpha):
    draw = ImageDraw.Draw(img)
    # floating emojis
    for i,(em,(ex,ey)) in enumerate(zip(EMOJIS_S1,EMOJI_POS)):
        fo = float_offset(st, amp=12, speed=0.8+i*0.1)
        try:
            draw.text((ex, ey+fo), em, font=F["emoji"], fill=C["white"])
        except Exception:
            pass

    # main text – slides in
    slide = ease_out(min(1.0, st / 0.5))
    ty = int(lerp(H*0.5, H*0.25, slide))

    text_center(draw, "¿Tu niño", ty,        F["title"])
    text_center(draw, "aprende",  ty+62,      F["title"])
    text_center(draw, "jugando?", ty+124,     F["title"], color=C["yellow"])
    text_center(draw, "¡Ahora sí puede! 🎉", ty+200, F["mid"])

# ── SCENE 2: PRODUCTO ────────────────────────────────────────────────────────
BOOKS = [
    ("🎨", "Dibujo",       (255,107,107)),
    ("🔤", "Abecedario",   ( 77,150,255)),
    ("🔢", "Números",      (255,217, 61), (40,40,40)),
    ("➕", "Matemáticas",  (107,203,119)),
]

def scene2(img, st, alpha):
    draw = ImageDraw.Draw(img)
    slide = ease_out(min(1.0, st / 0.45))

    # title
    ty = int(lerp(-60, 60, slide))
    text_center(draw, "✨ Magic Groove", ty,    F["mid"])
    text_center(draw, "Practice Copybook", ty+36, F["mid"])

    # books grid
    pad, gap = 30, 12
    bw = (W - pad*2 - gap)//2
    bh = 160
    by0 = 140
    for i, book in enumerate(BOOKS):
        em, label, fill = book[0], book[1], book[2]
        txt_color = book[3] if len(book)>3 else (255,255,255)
        col = i % 2
        row = i // 2
        x1 = pad + col*(bw+gap)
        y1 = by0 + row*(bh+gap)
        x2, y2 = x1+bw, y1+bh
        delay = ease_out(min(1.0, max(0, st-i*0.12)/0.4))
        # slide each book from below
        oy = int(lerp(80, 0, delay))
        tmp = img.copy()
        tmp = rounded_rect(tmp, x1, y1+oy, x2, y2+oy, 18, fill)
        # blend
        img.paste(tmp)
        draw = ImageDraw.Draw(img)
        try:
            draw.text((x1+(bw//2)-18, y1+20+oy), em, font=F["emoji"], fill=txt_color)
        except:
            pass
        text_center_at(draw, label, y1+80+oy, x1, x2, F["sub"], txt_color)

    # kit badge
    ky = by0 + 2*bh + 2*gap + 16
    badge_slide = ease_out(min(1.0, max(0, st-0.6)/0.35))
    ky_off = int(lerp(40,0,badge_slide))
    img = rounded_rect(img, 40, ky+ky_off, W-40, ky+52+ky_off, 26,
                        (255,255,255,50))
    draw = ImageDraw.Draw(img)
    text_center(draw, "📦 4 libros + pluma + 6 repuestos",
                ky+12+ky_off, F["small"])
    return img

def text_center_at(draw, text, y, x1, x2, font, color):
    bbox = draw.textbbox((0,0), text, font=font)
    tw = bbox[2]-bbox[0]
    cx = x1 + ((x2-x1)-tw)//2
    draw.text((cx+2,y+2), text, font=font, fill=(0,0,0,80))
    draw.text((cx, y),    text, font=font, fill=color)

# ── SCENE 3: BENEFICIOS ──────────────────────────────────────────────────────
BENEFITS = [
    ("✍️", "Mejora la escritura",       (255,255,255,50)),
    ("👁️", "Coordinación ojo-mano",     (255,255,255,50)),
    ("🧠", "Entrena la concentración",  (255,255,255,50)),
]

def scene3(img, st, alpha):
    draw = ImageDraw.Draw(img)
    slide = ease_out(min(1.0, st/0.4))
    ty = int(lerp(-50, 70, slide))
    text_center(draw, "¿Por qué funciona? 🤔", ty, F["mid"])

    by0 = 180
    bh  = 90
    gap = 16
    for i,(em,label,_) in enumerate(BENEFITS):
        delay = ease_out(min(1.0, max(0, st - 0.2 - i*0.2)/0.4))
        ox = int(lerp(-W, 0, delay))
        y1 = by0 + i*(bh+gap)
        img = rounded_rect(img, 24+ox, y1, W-24+ox, y1+bh, 22, (255,255,255,55))
        draw = ImageDraw.Draw(img)
        try:
            draw.text((44+ox, y1+22), em, font=F["emoji"], fill=(255,255,255))
        except:
            pass
        text_center_at(draw, label, y1+28, 100+ox, W-24+ox, F["sub"], (255,255,255))
    return img

# ── SCENE 4: CÓMO FUNCIONA ───────────────────────────────────────────────────
STEPS = [
    ("1", "Traza los surcos mágicos"),
    ("2", "La tinta desaparece ✨"),
    ("3", "¡Practica una y otra vez!"),
]

def scene4(img, st, alpha):
    draw = ImageDraw.Draw(img)
    slide = ease_out(min(1.0, st/0.4))
    ty = int(lerp(-50, 60, slide))
    text_center(draw, "¡Súper fácil de usar! 🖊️", ty, F["mid"])

    by0 = 170
    bh  = 96
    gap = 18
    for i,(num,label) in enumerate(STEPS):
        delay = ease_out(min(1.0, max(0, st - 0.15 - i*0.2)/0.4))
        ox = int(lerp(-W, 0, delay))
        y1 = by0 + i*(bh+gap)
        img = rounded_rect(img, 24+ox, y1, W-24+ox, y1+bh, 22, (255,255,255,50))
        draw = ImageDraw.Draw(img)
        # circle num
        draw.ellipse([40+ox, y1+22, 84+ox, y1+66], fill=(255,255,255,80))
        bbox = draw.textbbox((0,0), num, font=F["mid"])
        nw = bbox[2]-bbox[0]
        draw.text((62+ox-nw//2, y1+28), num, font=F["mid"], fill=(255,255,255))
        # label
        draw.text((100+ox, y1+30), label, font=F["sub"], fill=(255,255,255))

    # subtitle
    sub_slide = ease_out(min(1.0, max(0, st-0.8)/0.3))
    sy = by0 + 3*(bh+gap) + 10
    sy_off = int(lerp(30,0,sub_slide))
    text_center(draw, "Para niños de 3+ años 👶", sy+sy_off, F["sub"])
    return img

# ── SCENE 5: CTA ─────────────────────────────────────────────────────────────
EMOJIS_S5 = ["🎁","⭐","🛒","💥","🎉","✨"]
EMOJI_POS5 = [(25,90),(300,110),(20,420),(305,440),(50,620),(305,600)]

def scene5(img, st, alpha):
    draw = ImageDraw.Draw(img)
    # floating emojis
    for i,(em,(ex,ey)) in enumerate(zip(EMOJIS_S5,EMOJI_POS5)):
        fo = float_offset(st, amp=12, speed=0.9+i*0.1)
        try:
            draw.text((ex,ey+fo), em, font=F["emoji"], fill=(255,255,255))
        except:
            pass

    pulse = 1.0 + 0.04*math.sin(st * math.pi * 2.5)
    slide = ease_out(min(1.0, st/0.45))

    ty = int(lerp(H*0.5, 120, slide))
    text_center(draw, "¡Cómpralo ya! 🛍️", ty,    F["big"])
    text_center(draw, "🔥 Oferta especial",        ty+64, F["mid"],
                color=C["yellow"])

    # CTA button
    btn_w, btn_h = int(280*pulse), int(62*pulse)
    bx = (W-btn_w)//2
    btn_y = ty + 140
    img = rounded_rect(img, bx, btn_y, bx+btn_w, btn_y+btn_h, 34, (255,255,255))
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0,0), "VER PRODUCTO →", font=F["sub"])
    tw = bbox[2]-bbox[0]
    draw.text(((W-tw)//2, btn_y+16), "VER PRODUCTO →",
              font=F["sub"], fill=C["pink"])

    # store
    text_center(draw, "📍 Sublimontes Shop",   btn_y+82,  F["sub"])
    text_center(draw, "Link en la bio ⬆️",     btn_y+116, F["small"],
                color=(255,255,255,200))
    text_center(draw, "@sublimontesshop",       btn_y+148, F["small"],
                color=(255,255,255,180))
    return img

# ── WATERMARK ────────────────────────────────────────────────────────────────
def draw_watermark(img, draw):
    text_center(draw, "@sublimontesshop", H-30, F["small"],
                color=(255,255,255,150), shadow=False)

# ── FRAME RENDERER ───────────────────────────────────────────────────────────
SCENE_FNS = [scene1, scene2, scene3, scene4, scene5]

def render_frame(frame_idx):
    total_t   = frame_idx / FPS
    scene_idx = min(int(total_t // SCENE_DUR), 4)
    scene_t   = total_t - scene_idx * SCENE_DUR
    alpha     = fade_alpha(scene_t, SCENE_DUR, FADE)

    img  = Image.new("RGB", (W, H), (30,30,30))
    top, bot = GRAD[scene_idx+1]
    gradient(img, top, bot)

    draw = ImageDraw.Draw(img)
    ret  = SCENE_FNS[scene_idx](img, scene_t, alpha)
    if ret is not None:
        img = ret
        draw = ImageDraw.Draw(img)

    draw_progress(img, total_t)
    draw_watermark(img, draw)

    # alpha fade
    if alpha < 0.98:
        overlay = Image.new("RGB", (W, H), (0,0,0))
        img = Image.blend(overlay, img, alpha)

    return np.array(img)

# ── MAIN ─────────────────────────────────────────────────────────────────────
print(f"Generando {FRAMES} frames ({TOTAL}s a {FPS}fps)…")
frames = []
for i in range(FRAMES):
    if i % (FPS*2) == 0:
        print(f"  frame {i}/{FRAMES}  ({i//FPS}s)", flush=True)
    frames.append(render_frame(i))

out_path = "/home/user/Sublimontes_shop/tiktok_promo.mp4"
print("Compilando MP4…")
clip = ImageSequenceClip(frames, fps=FPS)
clip.write_videofile(out_path, codec="libx264", fps=FPS,
                     audio=False, logger=None,
                     ffmpeg_params=["-pix_fmt","yuv420p","-crf","18"])
print(f"✅ Listo: {out_path}")
