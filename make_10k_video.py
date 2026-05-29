"""
Instagram 10K Followers Campaign Video
Goal-focused video with animated counter and strong CTAs
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio
import math
import os

WIDTH, HEIGHT = 1080, 1920
FPS = 30
OUTPUT = "/home/user/Sublimontes_shop/instagram_10k_video.mp4"

FONT_BOLD  = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
FONT_REG   = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"

# Color palette — energetic IG vibes
IG_PURPLE = (131, 58,  180)
IG_PINK   = (225, 48,  108)
IG_ORANGE = (253, 87,   49)
IG_YELLOW = (254, 202,   0)
GOLD      = (255, 215,   0)
WHITE     = (255, 255, 255)
DARK      = ( 20,  20,  20)
TEAL      = (  0, 200, 180)

def lerp(a, b, t):
    return a + (b - a) * t

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def ease_out(t):   return 1 - (1 - t) ** 3
def ease_in_out(t): return t * t * (3 - 2 * t)
def bounce(t):
    if t < 0.727: return 7.5625 * t * t
    elif t < 0.909: t -= 0.818; return 7.5625*t*t + 0.75
    elif t < 0.977: t -= 0.954; return 7.5625*t*t + 0.9375
    else: t -= 0.988; return 7.5625*t*t + 0.984375

def pulse(frame, period=50):
    return 1.0 + 0.06 * math.sin(2 * math.pi * frame / period)

def make_bg(f, total):
    stops = [IG_PURPLE, IG_PINK, IG_ORANGE, (80,0,120), IG_PURPLE]
    n = len(stops) - 1
    t_g = (f / total) * n
    seg = int(t_g) % n
    tl = t_g - int(t_g)
    top    = lerp_color(stops[seg],   stops[(seg+1)%len(stops)], tl)
    bottom = lerp_color(stops[(seg+1)%len(stops)], stops[(seg+2)%len(stops)], tl)
    img = Image.new("RGB", (WIDTH, HEIGHT))
    px = img.load()
    for y in range(HEIGHT):
        c = lerp_color(top, bottom, y/HEIGHT)
        for x in range(WIDTH):
            px[x, y] = c
    return img

def draw_star(draw, cx, cy, r_out, r_in, n, angle, color):
    pts = []
    for i in range(n*2):
        a = math.pi/n*i + angle
        r = r_out if i%2==0 else r_in
        pts.append((cx + r*math.cos(a - math.pi/2),
                    cy + r*math.sin(a - math.pi/2)))
    draw.polygon(pts, fill=color)

def particles(draw, f, count=35):
    rng = np.random.default_rng(7)
    xs = rng.integers(30, WIDTH-30, count)
    ys = rng.integers(30, HEIGHT-30, count)
    spds = rng.uniform(0.4, 2.0, count)
    szs  = rng.integers(3, 14, count)
    for i in range(count):
        ph = (f * spds[i] * 0.05 + i * 0.9) % (2*math.pi)
        yy = int((ys[i] + math.sin(ph)*25) % HEIGHT)
        r  = int(szs[i])
        draw.ellipse([xs[i]-r, yy-r, xs[i]+r, yy+r], fill=WHITE)

def txt_center(draw, y, text, font, fill=WHITE, shadow_col=(0,0,0)):
    bb = draw.textbbox((0,0), text, font=font)
    w = bb[2]-bb[0]
    x = (WIDTH - w)//2
    draw.text((x+3, y+3), text, font=font, fill=shadow_col)
    draw.text((x, y),   text, font=font, fill=fill)

def slide(draw, f, start, dur, y, text, font, fill=WHITE, from_side=None):
    el = f - start
    if el < 0: return
    t = ease_out(min(el/dur, 1.0))
    if from_side == "left":
        xoff = int((1-t)*(WIDTH+100)); yoff = 0
    elif from_side == "right":
        xoff = -int((1-t)*(WIDTH+100)); yoff = 0
    else:
        yoff = int((1-t)*110); xoff = 0
    bb = draw.textbbox((0,0), text, font=font)
    w = bb[2]-bb[0]
    x = (WIDTH - w)//2 + xoff
    draw.text((x+3, y+yoff+3), text, font=font, fill=(0,0,0))
    draw.text((x,   y+yoff),   text, font=font, fill=fill)

def draw_progress_ring(draw, cx, cy, radius, progress, thickness, color_fill, color_bg=(255,255,255,60)):
    # background ring
    bb = [cx-radius, cy-radius, cx+radius, cy+radius]
    draw.arc(bb, 0, 360, fill=(255,255,255), width=thickness//2)
    # progress arc
    end_angle = -90 + 360 * progress
    draw.arc(bb, -90, end_angle, fill=color_fill, width=thickness)
    # glow dot at tip
    tip_angle = math.radians(end_angle)
    tx = cx + radius * math.cos(tip_angle)
    ty = cy + radius * math.sin(tip_angle)
    gr = thickness//2 + 4
    draw.ellipse([tx-gr, ty-gr, tx+gr, ty+gr], fill=GOLD)

# ── SECTIONS ───────────────────────────────────────────────────────────────────
# 0s–4s   : Intro / attention grab
# 4s–9s   : "We need YOUR help" — goal reveal
# 9s–18s  : Animated 10K counter + progress ring
# 18s–25s : 4 action cards (Follow / Share / Comment / Tag)
# 25s–35s : Thank-you outro + final message

def build(f, total, st):
    img = make_bg(f, total)
    draw = ImageDraw.Draw(img)
    particles(draw, f)

    try:
        fH  = ImageFont.truetype(FONT_BOLD, 130)
        fL  = ImageFont.truetype(FONT_BOLD,  82)
        fM  = ImageFont.truetype(FONT_BOLD,  60)
        fS  = ImageFont.truetype(FONT_REG,   44)
        fXS = ImageFont.truetype(FONT_REG,   36)
        fNUM= ImageFont.truetype(FONT_BOLD, 160)
    except:
        fH=fL=fM=fS=fXS=fNUM=ImageFont.load_default()

    # ── SECTION 0: INTRO (0–4s) ──────────────────────────────────────────────
    if f < st[1]:
        lf = f
        # Flashing emoji-like stars
        if lf % 10 < 5:
            for ang in [0, 60, 120, 180, 240, 300]:
                a = math.radians(ang + lf*3)
                draw_star(draw, int(WIDTH//2 + 350*math.cos(a)),
                          int(600 + 200*math.sin(a)), 20, 8, 5, a, GOLD)

        slide(draw, lf,  0, 20, 290, "HEY EVERYONE!", fL, GOLD)
        slide(draw, lf,  8, 20, 420, "We need your help!", fM, WHITE)

        # Underline
        if lf > 18:
            p = ease_out(min((lf-18)/20, 1.0))
            draw.line([(int(WIDTH//2-300*p), 510), (int(WIDTH//2+300*p), 510)],
                      fill=GOLD, width=6)

        slide(draw, lf, 22, 25, 560, "We're on a mission", fS, WHITE)
        slide(draw, lf, 30, 25, 640, "to reach a BIG goal...", fS, GOLD)

        # Countdown suspense dots
        if lf > 50:
            for di in range(3):
                dot_t = min((lf - 50 - di*8)/15, 1.0)
                if dot_t <= 0: continue
                dx = WIDTH//2 - 60 + di*60
                dr = int(dot_t * 18)
                draw.ellipse([dx-dr, 780-dr, dx+dr, 780+dr], fill=WHITE)

    # ── SECTION 1: GOAL REVEAL (4–9s) ────────────────────────────────────────
    elif f < st[2]:
        lf = f - st[1]

        slide(draw, lf,  0, 15, 200, "OUR GOAL IS", fL, WHITE)

        # 10K text with scale bounce
        t_10k = min(max(lf-10, 0)/20, 1.0)
        scale = 1.0 + bounce(t_10k) * 0.3 if t_10k < 1 else 1.0
        size_10k = int(200 * scale)
        try:
            f10k = ImageFont.truetype(FONT_BOLD, size_10k)
        except:
            f10k = ImageFont.load_default()
        if lf >= 10:
            bb = draw.textbbox((0,0), "10K", font=f10k)
            w = bb[2]-bb[0]
            draw.text((WIDTH//2-w//2+4, 360+4), "10K", font=f10k, fill=(0,0,0))
            draw.text((WIDTH//2-w//2,   360),   "10K", font=f10k, fill=GOLD)

        slide(draw, lf, 20, 20, 620, "FOLLOWERS!", fL, WHITE)

        # Star burst at reveal
        if 10 <= lf <= 40:
            tb = min((lf-10)/20, 1.0)
            for i in range(12):
                a = (i/12)*2*math.pi
                dist = int(tb*300)
                draw_star(draw, WIDTH//2+int(dist*math.cos(a)),
                          500+int(dist*0.35*math.sin(a)),
                          int((1-tb)*24+4), int((1-tb)*10+2), 5, a, GOLD)

        slide(draw, lf, 30, 25, 760, "We're SO close —", fM, WHITE)
        slide(draw, lf, 40, 25, 850, "HELP us get there!", fM, GOLD)

    # ── SECTION 2: COUNTER + RING (9–18s) ────────────────────────────────────
    elif f < st[3]:
        lf = f - st[2]
        total_sec = st[3] - st[2]

        slide(draw, lf, 0, 20, 130, "PROGRESS TO 10K", fM, WHITE)

        # Animated counter 0 → 9847 (just below 10K for drama)
        t_count = ease_in_out(min(lf / (total_sec * 0.85), 1.0))
        current = int(t_count * 9847)
        progress = current / 10000

        # Progress ring
        ring_cx, ring_cy, ring_r = WIDTH//2, 680, 320
        draw_progress_ring(draw, ring_cx, ring_cy, ring_r, progress, 28,
                           IG_PINK)

        # Number inside ring
        num_str = f"{current:,}"
        bb = draw.textbbox((0,0), num_str, font=fNUM)
        nw = bb[2]-bb[0]; nh = bb[3]-bb[1]
        draw.text((ring_cx-nw//2+3, ring_cy-nh//2-30+3), num_str, font=fNUM, fill=DARK)
        draw.text((ring_cx-nw//2,   ring_cy-nh//2-30),   num_str, font=fNUM, fill=GOLD)

        # "/10,000" label
        lbl = "/ 10,000"
        try: fl = ImageFont.truetype(FONT_REG, 50)
        except: fl = ImageFont.load_default()
        bb2 = draw.textbbox((0,0), lbl, font=fl)
        lw = bb2[2]-bb2[0]
        draw.text((ring_cx-lw//2, ring_cy+60), lbl, font=fl, fill=WHITE)

        # % label
        pct = f"{int(progress*100)}%"
        try: fp = ImageFont.truetype(FONT_BOLD, 54)
        except: fp = ImageFont.load_default()
        bb3 = draw.textbbox((0,0), pct, font=fp)
        pw = bb3[2]-bb3[0]
        draw.text((ring_cx-pw//2, ring_cy+120), pct, font=fp, fill=TEAL)

        slide(draw, lf, 20, 25, 1120, "We need", fM, WHITE)
        slide(draw, lf, 28, 25, 1205, f"{10000-current:,} more followers!", fM, GOLD)
        slide(draw, lf, 50, 25, 1350, "YOU could be one of them!", fS, WHITE)

    # ── SECTION 3: ACTION CARDS (18–25s) ─────────────────────────────────────
    elif f < st[4]:
        lf = f - st[3]

        slide(draw, lf, 0, 18, 100, "HOW TO HELP:", fL, GOLD)

        actions = [
            ("1", "FOLLOW US",    "Tap the Follow button now",   IG_PINK),
            ("2", "SHARE",        "Send this to 3 friends",       IG_ORANGE),
            ("3", "COMMENT",      'Drop a \"10K\" below',         IG_PURPLE),
            ("4", "TAG A FRIEND", "Who needs great content?",     TEAL),
        ]

        for idx, (num, title, sub, color) in enumerate(actions):
            cs = 12 + idx * 22
            el = lf - cs
            if el < 0: continue
            t_c = ease_out(min(el/20, 1.0))
            side = "left" if idx % 2 == 0 else "right"
            xoff = int((1-t_c)*(WIDTH+60)) * (1 if side=="left" else -1)

            cw, ch = 940, 195
            cy2 = 280 + idx*(ch+22)
            x0 = (WIDTH-cw)//2 + xoff
            y0 = cy2

            draw.rounded_rectangle([x0+6,y0+6,x0+cw+6,y0+ch+6], radius=28, fill=DARK)
            draw.rounded_rectangle([x0,y0,x0+cw,y0+ch],
                                   radius=28, fill=color, outline=WHITE, width=3)

            # Badge
            br = 42
            bx, by2 = x0+50+br, y0+ch//2
            draw.ellipse([bx-br,by2-br,bx+br,by2+br], fill=WHITE)
            try: fn2 = ImageFont.truetype(FONT_BOLD, 48)
            except: fn2 = ImageFont.load_default()
            nbb = draw.textbbox((0,0), num, font=fn2)
            draw.text((bx-(nbb[2]-nbb[0])//2, by2-(nbb[3]-nbb[1])//2),
                      num, font=fn2, fill=color)

            try:
                ft2 = ImageFont.truetype(FONT_BOLD, 50)
                fs2 = ImageFont.truetype(FONT_REG,  36)
            except:
                ft2 = fs2 = ImageFont.load_default()
            draw.text((x0+130, y0+28),  title, font=ft2, fill=WHITE)
            draw.text((x0+130, y0+95),  sub,   font=fs2, fill=WHITE)

        slide(draw, lf, 80, 20, 1100, "Every single follow counts!", fS, WHITE)

    # ── SECTION 4: OUTRO (25–35s) ────────────────────────────────────────────
    else:
        lf = f - st[4]
        total_outro = total - st[4]

        # Falling stars
        rng2 = np.random.default_rng(13)
        sxs  = rng2.integers(40, WIDTH-40, 30)
        spds2= rng2.uniform(2.0, 5.0, 30)
        for i in range(30):
            sy = int((lf * spds2[i] * 1.5 + i*65) % HEIGHT)
            sz = rng2.integers(10, 25)
            rot= (lf*0.06 + i*0.4) % (2*math.pi)
            draw_star(draw, int(sxs[i]), sy, int(sz), int(sz)//2, 5, rot, GOLD)

        # Pulsing 10K
        sc = pulse(lf, 40)
        try: fGoal = ImageFont.truetype(FONT_BOLD, int(180*sc))
        except: fGoal = ImageFont.load_default()
        slide(draw, lf, 0, 20, 160, "10K", fGoal, GOLD)

        slide(draw, lf,  5, 22, 440, "HERE WE COME!", fL, WHITE)

        if lf > 18:
            p = ease_out(min((lf-18)/18, 1.0))
            draw.line([(int(WIDTH//2-340*p), 560), (int(WIDTH//2+340*p), 560)],
                      fill=GOLD, width=6)

        slide(draw, lf, 22, 28, 610, "Thanks for your collaboration,",  fS, WHITE)
        slide(draw, lf, 32, 28, 695, "I will be following everyone too!", fS, GOLD)

        slide(draw, lf, 42, 28, 810, "Together we will reach 10K!", fM, WHITE)
        slide(draw, lf, 52, 28, 910, "Let's make it happen TODAY!", fM, GOLD)

        # Heart row
        if lf > 60:
            t_row = ease_out(min((lf-60)/20, 1.0))
            for hi in range(9):
                sc2 = pulse(lf+hi*7, 32)
                hr = int(20*t_row*sc2)
                hx = 80 + hi * (WIDTH-160)//8
                hy = 1060
                draw.ellipse([hx-hr, hy-hr, hx+hr, hy+hr], fill=IG_PINK)

        # IG icon
        if lf > 65:
            t_ic = ease_out(min((lf-65)/20, 1.0))
            iy = int(1200 + (1-t_ic)*120)
            ic = int(90*t_ic)
            box = [WIDTH//2-ic, iy-ic, WIDTH//2+ic, iy+ic]
            draw.rounded_rectangle(box, radius=ic//4, outline=WHITE, width=max(2,ic//12))
            inn = ic//4
            draw.ellipse([WIDTH//2-inn, iy-inn, WIDTH//2+inn, iy+inn],
                         outline=WHITE, width=max(2,ic//16))
            dr2 = ic//8
            draw.ellipse([WIDTH//2+ic//3-dr2, iy-ic//3-dr2,
                          WIDTH//2+ic//3+dr2, iy-ic//3+dr2], fill=WHITE)

    return img

def main():
    section_times = [
        0,
        4  * FPS,   # goal reveal
        9  * FPS,   # counter
        18 * FPS,   # action cards
        25 * FPS,   # outro
    ]
    total_frames = 35 * FPS
    print(f"Rendering {total_frames} frames ({total_frames//FPS}s) …")
    writer = imageio.get_writer(OUTPUT, fps=FPS, codec="libx264",
                                quality=9, macro_block_size=1,
                                ffmpeg_params=["-crf","18","-preset","fast"])
    for fi in range(total_frames):
        if fi % FPS == 0:
            print(f"  {fi//FPS:02d}s / {total_frames//FPS}s", end="\r", flush=True)
        writer.append_data(np.array(build(fi, total_frames, section_times)))
    writer.close()
    mb = os.path.getsize(OUTPUT)/1_048_576
    print(f"\nDone!  {OUTPUT}  ({mb:.1f} MB)")

if __name__ == "__main__":
    main()
