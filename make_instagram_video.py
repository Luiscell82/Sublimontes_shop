"""
Instagram Follower Campaign Video Generator
Dynamic promotional video with animations and effects
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio
import math
import os

# ── Settings ──────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1080, 1920   # Instagram Reels/Stories portrait
FPS = 30
OUTPUT = "/home/user/Sublimontes_shop/instagram_followers_video.mp4"

FONT_BOLD  = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
FONT_REG   = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

# Instagram gradient palette
IG_PURPLE  = (131, 58, 180)
IG_PINK    = (225, 48, 108)
IG_ORANGE  = (253, 87, 49)
IG_YELLOW  = (254, 202, 0)
WHITE      = (255, 255, 255)
GOLD       = (255, 215, 0)

# ── Helpers ───────────────────────────────────────────────────────────────────

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def ease_out_cubic(t):
    return 1 - (1 - t) ** 3

def ease_in_out(t):
    return t * t * (3 - 2 * t)

def make_gradient_bg(frame_idx, total_frames):
    """Animated gradient background cycling through IG colors."""
    cycle = [IG_PURPLE, IG_PINK, IG_ORANGE, IG_YELLOW, IG_PINK, IG_PURPLE]
    n = len(cycle) - 1
    t_global = (frame_idx / total_frames) * n
    seg = int(t_global) % n
    t_local = t_global - int(t_global)

    top    = lerp_color(cycle[seg], cycle[(seg + 1) % len(cycle)], t_local)
    bottom = lerp_color(cycle[(seg + 1) % len(cycle)], cycle[(seg + 2) % len(cycle)], t_local)

    img = Image.new("RGB", (WIDTH, HEIGHT))
    pixels = img.load()
    for y in range(HEIGHT):
        t = y / HEIGHT
        c = lerp_color(top, bottom, t)
        for x in range(WIDTH):
            pixels[x, y] = c
    return img

def draw_particles(draw, frame_idx, count=40):
    """Floating sparkle particles."""
    rng = np.random.default_rng(42)
    xs  = rng.integers(50, WIDTH - 50, count)
    ys  = rng.integers(50, HEIGHT - 50, count)
    sizes = rng.integers(4, 18, count)
    speeds = rng.uniform(0.5, 2.0, count)

    for i in range(count):
        phase = (frame_idx * speeds[i] * 0.04 + i * 0.7) % (2 * math.pi)
        alpha = int(abs(math.sin(phase)) * 200 + 55)
        y_off = int(math.sin(phase) * 30)
        x = int(xs[i])
        y = int((ys[i] + y_off) % HEIGHT)
        r = int(sizes[i])
        color = (*WHITE, alpha)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color[:3])

def draw_star(draw, cx, cy, r_out, r_in, points, angle_offset, color):
    """Draw a star shape."""
    pts = []
    for i in range(points * 2):
        angle = math.pi / points * i + angle_offset
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + r * math.cos(angle - math.pi / 2),
                    cy + r * math.sin(angle - math.pi / 2)))
    draw.polygon(pts, fill=color)

def draw_instagram_logo_area(draw, cx, cy, size, alpha_factor=1.0):
    """Minimal IG-style rounded square icon hint."""
    r = size // 2
    box = [cx - r, cy - r, cx + r, cy + r]
    draw.rounded_rectangle(box, radius=size // 5,
                            outline=WHITE, width=max(2, size // 20))
    inner = size // 5
    draw.ellipse([cx - inner, cy - inner, cx + inner, cy + inner],
                 outline=WHITE, width=max(2, size // 25))
    dot_r = size // 12
    dot_x = cx + size // 4
    dot_y = cy - size // 4
    draw.ellipse([dot_x - dot_r, dot_y - dot_r,
                  dot_x + dot_r, dot_y + dot_r], fill=WHITE)

def centered_text(draw, y, text, font, fill=WHITE, shadow=True):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    x = (WIDTH - w) // 2
    if shadow:
        draw.text((x + 3, y + 3), text, font=font, fill=(0, 0, 0, 100))
    draw.text((x, y), text, font=font, fill=fill)

def slide_in_text(draw, frame, start_frame, duration, y, text, font, fill=WHITE, direction="up"):
    elapsed = frame - start_frame
    if elapsed < 0:
        return
    t = min(elapsed / duration, 1.0)
    t = ease_out_cubic(t)
    offset = int((1 - t) * 120) * (1 if direction == "up" else -1)
    alpha = int(t * 255)

    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    x = (WIDTH - w) // 2
    draw.text((x + 2, y + offset + 2), text, font=font, fill=(0, 0, 0))
    draw.text((x, y + offset), text, font=font, fill=fill)

def pulse_scale(frame, period=60):
    t = (frame % period) / period
    return 1.0 + 0.05 * math.sin(2 * math.pi * t)

# ── Frame builders ────────────────────────────────────────────────────────────

def build_frame(frame_idx, total_frames, section_times):
    """Render one RGBA frame."""
    img = make_gradient_bg(frame_idx, total_frames)
    draw = ImageDraw.Draw(img, "RGB")

    # Floating particles always
    draw_particles(draw, frame_idx)

    # ── Section timing
    # t0  intro (0–3s):  logo + username bounce in
    # t1  hook (3–7s):   "Want MORE Followers?" big impact
    # t2  steps (7–16s): 3 tip cards slide in
    # t3  cta  (16–22s): Follow + @handle + heart burst
    # t4  outro (22–30s): thank-you message + star rain

    s = section_times
    f = frame_idx

    try:
        font_huge  = ImageFont.truetype(FONT_BOLD, 110)
        font_large = ImageFont.truetype(FONT_BOLD, 80)
        font_med   = ImageFont.truetype(FONT_BOLD, 58)
        font_sm    = ImageFont.truetype(FONT_REG,  44)
        font_xs    = ImageFont.truetype(FONT_REG,  36)
        font_tag   = ImageFont.truetype(FONT_BOLD, 52)
    except Exception:
        font_huge = font_large = font_med = font_sm = font_xs = font_tag = \
            ImageFont.load_default()

    # ──────────────────────────────────────────────
    # SECTION 0 – INTRO  (frames 0 – s[1])
    # ──────────────────────────────────────────────
    if f < s[1]:
        # IG icon
        scale = pulse_scale(f, 50)
        icon_size = int(180 * scale)
        draw_instagram_logo_area(draw, WIDTH // 2, 480, icon_size)

        slide_in_text(draw, f, 0, 25, 700, "FOLLOW US", font_large, WHITE, "up")
        slide_in_text(draw, f, 10, 25, 820, "ON INSTAGRAM", font_med, GOLD, "up")

        # animated underline
        prog = min((f - 20) / 20, 1.0) if f > 20 else 0.0
        prog = ease_out_cubic(prog)
        lx1 = WIDTH // 2 - int(300 * prog)
        lx2 = WIDTH // 2 + int(300 * prog)
        draw.line([(lx1, 900), (lx2, 900)], fill=GOLD, width=6)

        slide_in_text(draw, f, 15, 30, 980, "& GROW TOGETHER", font_sm, WHITE, "up")

    # ──────────────────────────────────────────────
    # SECTION 1 – HOOK  (frames s[1] – s[2])
    # ──────────────────────────────────────────────
    elif f < s[2]:
        lf = f - s[1]  # local frame

        # Big pulsing question
        scale = pulse_scale(lf, 45)
        fsize = int(100 * scale)
        try:
            f_big = ImageFont.truetype(FONT_BOLD, fsize)
        except Exception:
            f_big = ImageFont.load_default()

        slide_in_text(draw, lf, 0, 20, 500, "Want MORE", f_big, GOLD, "up")
        slide_in_text(draw, lf, 8, 20, 650, "FOLLOWERS?", f_big, WHITE, "up")

        slide_in_text(draw, lf, 20, 25, 820, "We have the strategy", font_med, WHITE, "up")
        slide_in_text(draw, lf, 28, 25, 910, "that actually works!", font_med, GOLD, "up")

        # Stars burst
        if lf > 15:
            t_burst = min((lf - 15) / 30, 1.0)
            for i in range(8):
                angle = (i / 8) * 2 * math.pi
                dist = int(t_burst * 280)
                sx = WIDTH // 2 + int(dist * math.cos(angle))
                sy = 580 + int(dist * 0.4 * math.sin(angle))
                size_star = max(2, int((1 - t_burst) * 28))
                draw_star(draw, sx, sy, size_star, size_star // 2, 5,
                          angle, GOLD)

    # ──────────────────────────────────────────────
    # SECTION 2 – TIPS  (frames s[2] – s[3])
    # ──────────────────────────────────────────────
    elif f < s[3]:
        lf = f - s[2]

        tips = [
            ("01", "Post DAILY", "Consistency is king"),
            ("02", "Use REELS", "Reels = 3× more reach"),
            ("03", "Engage BACK", "Reply to every comment"),
        ]

        # Title
        slide_in_text(draw, lf, 0, 20, 180, "QUICK TIPS", font_large, GOLD, "up")
        slide_in_text(draw, lf, 5, 20, 290, "TO GROW FAST", font_med, WHITE, "up")

        card_h = 220
        card_w = 900
        cx = WIDTH // 2

        for idx, (num, title, sub) in enumerate(tips):
            card_start = 20 + idx * 40
            elapsed_card = lf - card_start
            if elapsed_card < 0:
                continue
            t_c = min(elapsed_card / 30, 1.0)
            t_c = ease_out_cubic(t_c)
            x_off = int((1 - t_c) * (WIDTH + 50))

            cy_card = 460 + idx * (card_h + 30)
            x0 = cx - card_w // 2 + x_off
            y0 = cy_card - card_h // 2
            x1 = cx + card_w // 2 + x_off
            y1 = cy_card + card_h // 2

            # Card shadow
            draw.rounded_rectangle([x0 + 6, y0 + 6, x1 + 6, y1 + 6],
                                    radius=30, fill=(0, 0, 0))
            # Card body
            draw.rounded_rectangle([x0, y0, x1, y1], radius=30,
                                    fill=(255, 255, 255, 30),
                                    outline=WHITE, width=3)
            # Number badge
            badge_r = 45
            draw.ellipse([x0 + 30, y0 + card_h // 2 - badge_r,
                          x0 + 30 + badge_r * 2, y0 + card_h // 2 + badge_r],
                         fill=IG_PINK)
            try:
                fn = ImageFont.truetype(FONT_BOLD, 44)
            except Exception:
                fn = ImageFont.load_default()
            nb = draw.textbbox((0, 0), num, font=fn)
            draw.text((x0 + 30 + badge_r - (nb[2] - nb[0]) // 2,
                       y0 + card_h // 2 - (nb[3] - nb[1]) // 2), num,
                      font=fn, fill=WHITE)
            # Tip text
            try:
                ft = ImageFont.truetype(FONT_BOLD, 52)
                fs = ImageFont.truetype(FONT_REG,  38)
            except Exception:
                ft = fs = ImageFont.load_default()
            draw.text((x0 + 140, y0 + 35), title, font=ft, fill=GOLD)
            draw.text((x0 + 140, y0 + 105), sub, font=fs, fill=WHITE)

    # ──────────────────────────────────────────────
    # SECTION 3 – CTA  (frames s[3] – s[4])
    # ──────────────────────────────────────────────
    elif f < s[4]:
        lf = f - s[3]

        slide_in_text(draw, lf, 0, 20, 300, "JOIN OUR COMMUNITY", font_med, WHITE, "up")

        # Pulsing FOLLOW button
        if lf > 15:
            t_btn = min((lf - 15) / 20, 1.0)
            t_btn = ease_out_cubic(t_btn)
            scale = pulse_scale(lf, 40)
            bw = int(600 * scale)
            bh = int(120 * scale)
            bx = WIDTH // 2 - bw // 2
            by = 500
            draw.rounded_rectangle([bx, by, bx + bw, by + bh],
                                    radius=bh // 2, fill=IG_PINK)
            try:
                fb = ImageFont.truetype(FONT_BOLD, int(60 * scale))
            except Exception:
                fb = ImageFont.load_default()
            centered_text(draw, by + (bh - 60) // 2, "FOLLOW NOW", fb, WHITE, False)

        slide_in_text(draw, lf, 25, 20, 680, "Turn on notifications ", font_sm, GOLD, "up")
        slide_in_text(draw, lf, 32, 20, 760, "so you never miss a post!", font_sm, WHITE, "up")

        # Heart burst
        if lf > 30:
            t_h = min((lf - 30) / 25, 1.0)
            for i in range(12):
                angle = (i / 12) * 2 * math.pi
                dist = int(t_h * 320)
                hx = WIDTH // 2 + int(dist * math.cos(angle))
                hy = 900 + int(dist * 0.5 * math.sin(angle))
                hr = max(1, int((1 - t_h) * 22 + 4))
                draw.ellipse([hx - hr, hy - hr, hx + hr, hy + hr],
                             fill=IG_PINK)

        slide_in_text(draw, lf, 35, 20, 1000, "SHARE this with a friend", font_sm, GOLD, "up")
        slide_in_text(draw, lf, 42, 20, 1080, "who wants to grow too!", font_sm, WHITE, "up")

    # ──────────────────────────────────────────────
    # SECTION 4 – OUTRO  (frames s[4] – end)
    # ──────────────────────────────────────────────
    else:
        lf = f - s[4]
        total_outro = total_frames - s[4]

        # Falling stars
        rng2 = np.random.default_rng(99)
        star_xs = rng2.integers(40, WIDTH - 40, 25)
        star_speeds = rng2.uniform(1.5, 4.0, 25)
        for i in range(25):
            sy = int((lf * star_speeds[i] * 1.8 + i * 75) % HEIGHT)
            sz = rng2.integers(8, 22)
            rot = (lf * 0.05 + i * 0.3) % (2 * math.pi)
            draw_star(draw, int(star_xs[i]), sy, int(sz), int(sz) // 2, 5, rot, GOLD)

        # Main thank-you text
        slide_in_text(draw, lf, 0, 25, 340, "THANK YOU", font_huge, GOLD, "up")
        slide_in_text(draw, lf, 12, 25, 490, "for your support!", font_large, WHITE, "up")

        # Divider line
        if lf > 20:
            prog = min((lf - 20) / 20, 1.0)
            lx1 = WIDTH // 2 - int(350 * prog)
            lx2 = WIDTH // 2 + int(350 * prog)
            draw.line([(lx1, 650), (lx2, 650)], fill=WHITE, width=4)

        slide_in_text(draw, lf, 25, 30, 700,  "Thanks for your collaboration,",   font_sm, WHITE, "up")
        slide_in_text(draw, lf, 35, 30, 780,  "I will be following everyone too!", font_sm, GOLD,  "up")

        slide_in_text(draw, lf, 45, 30, 900,  "Together we grow stronger!", font_sm, WHITE, "up")

        # Pulsing hearts row
        if lf > 50:
            t_row = min((lf - 50) / 20, 1.0)
            heart_y = 1020
            heart_count = 7
            spacing = 110
            start_x = WIDTH // 2 - (heart_count // 2) * spacing
            for hi in range(heart_count):
                pulse = pulse_scale(lf + hi * 8, 35)
                hr = int(22 * t_row * pulse)
                hx = start_x + hi * spacing
                draw.ellipse([hx - hr, heart_y - hr, hx + hr, heart_y + hr],
                             fill=IG_PINK)

        # IG logo at bottom
        if lf > 55:
            t_logo = min((lf - 55) / 20, 1.0)
            t_logo = ease_out_cubic(t_logo)
            icon_y = int(1200 + (1 - t_logo) * 100)
            draw_instagram_logo_area(draw, WIDTH // 2, icon_y, 100)

    return img

# ── Main render ───────────────────────────────────────────────────────────────

def main():
    # Section boundaries in frames
    section_times = [
        0,            # s[0] intro start
        3 * FPS,      # s[1] hook start   (3s)
        7 * FPS,      # s[2] tips start   (7s)
        16 * FPS,     # s[3] cta start    (16s)
        22 * FPS,     # s[4] outro start  (22s)
    ]
    total_seconds = 30
    total_frames  = total_seconds * FPS

    print(f"Rendering {total_frames} frames at {FPS} fps …")
    writer = imageio.get_writer(OUTPUT, fps=FPS, codec="libx264",
                                quality=8, macro_block_size=1,
                                ffmpeg_params=["-crf", "20", "-preset", "fast"])

    for f in range(total_frames):
        if f % FPS == 0:
            print(f"  {f // FPS:02d}s / {total_seconds}s", end="\r", flush=True)
        frame_img = build_frame(f, total_frames, section_times)
        writer.append_data(np.array(frame_img))

    writer.close()
    size_mb = os.path.getsize(OUTPUT) / 1_048_576
    print(f"\nDone! Saved: {OUTPUT}  ({size_mb:.1f} MB)")

if __name__ == "__main__":
    main()
