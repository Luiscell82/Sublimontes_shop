#!/usr/bin/env python3
"""
Montes Patrol Security LLC - Promotional Video Generator
30-second MP4 with marquee effects and animated slides
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import math

# ── Config ────────────────────────────────────────────────────────────────────
W, H       = 1080, 1920          # 9:16 vertical (Reels/TikTok/Shorts)
FPS        = 30
NAVY       = (10, 27, 56)        # #0a1b38
DARK_NAVY  = (5, 12, 28)         # #050c1c
RED        = (190, 20, 20)       # #be1414
DARK_RED   = (140, 10, 10)       # #8c0a0a
WHITE      = (255, 255, 255)
GOLD       = (212, 175, 55)      # #d4af37
LIGHT_GRAY = (200, 210, 230)

FONT_BOLD   = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
FONT_NORMAL = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"


def make_font(size):
    return ImageFont.truetype(FONT_BOLD, size)


def make_font_normal(size):
    return ImageFont.truetype(FONT_NORMAL, size)


def gradient_bg(w, h, top_color, bottom_color):
    """Vertical gradient background."""
    arr = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        t = y / h
        r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
        g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
        b = int(top_color[2] * (1 - t) + bottom_color[2] * t)
        arr[y, :] = [r, g, b]
    return arr


def draw_shield(draw, cx, cy, size, alpha=255):
    """Draw a stylised shield shape."""
    s = size
    pts = [
        (cx, cy - s),
        (cx + s * 0.7, cy - s * 0.4),
        (cx + s * 0.7, cy + s * 0.2),
        (cx, cy + s),
        (cx - s * 0.7, cy + s * 0.2),
        (cx - s * 0.7, cy - s * 0.4),
    ]
    pts = [(int(x), int(y)) for x, y in pts]
    draw.polygon(pts, fill=(*NAVY, alpha), outline=(*RED, alpha), width=8)
    # Inner star-like cross
    draw.line([(cx, cy - s // 2), (cx, cy + s // 2)], fill=(*WHITE, alpha), width=6)
    draw.line([(cx - s // 2, cy), (cx + s // 2, cy)], fill=(*WHITE, alpha), width=6)


def draw_star(draw, cx, cy, r, color=(255, 255, 255, 255)):
    """5-pointed star."""
    pts = []
    for i in range(10):
        angle = math.radians(i * 36 - 90)
        radius = r if i % 2 == 0 else r * 0.4
        pts.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    pts = [(int(x), int(y)) for x, y in pts]
    draw.polygon(pts, fill=color)


def draw_red_bar(draw, y, w, h=6):
    """Horizontal red separator bar with glow."""
    draw.rectangle([0, y, w, y + h], fill=RED)


def draw_logo_composite(img, cx, cy, size):
    """Draw the Montes Patrol logo shield + text."""
    draw = ImageDraw.Draw(img, "RGBA")
    s = size
    # Outer circle
    draw.ellipse([cx - s, cy - s, cx + s, cy + s], outline=(*RED, 220), width=10)
    # Shield
    sh_pts = [
        (cx, cy - s * 0.85),
        (cx + s * 0.6, cy - s * 0.3),
        (cx + s * 0.6, cy + s * 0.15),
        (cx, cy + s * 0.85),
        (cx - s * 0.6, cy + s * 0.15),
        (cx - s * 0.6, cy - s * 0.3),
    ]
    sh_pts = [(int(x), int(y)) for x, y in sh_pts]
    # Left half red, right half navy
    draw.polygon(sh_pts, fill=(*RED, 230))
    draw.polygon(
        [(cx, cy - s * 0.85)] + sh_pts[1:3] + [(cx + s * 0.6, cy + s * 0.15), (cx, cy + s * 0.85)],
        fill=(*NAVY, 230),
    )
    # Draw outline
    draw.line(sh_pts + [sh_pts[0]], fill=(*GOLD, 255), width=6)
    # Star in center
    draw_star(draw, cx, cy - int(s * 0.1), int(s * 0.45), color=(*WHITE, 255))
    # Crossed swords hint (simple lines)
    sw = int(s * 0.55)
    draw.line([(cx - sw, cy - sw - 20), (cx + sw, cy + sw - 20)], fill=(*GOLD, 200), width=7)
    draw.line([(cx + sw, cy - sw - 20), (cx - sw, cy + sw - 20)], fill=(*GOLD, 200), width=7)


def wrap_text(text, font, max_width, draw):
    """Wrap text to fit max_width."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_centered_text(draw, text, font, y, color=WHITE, shadow=True, max_width=None):
    """Draw centered text with optional shadow."""
    if max_width:
        lines = wrap_text(text, font, max_width, draw)
    else:
        lines = [text]
    line_h = draw.textbbox((0, 0), "Ag", font=font)[3] + 8
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        ly = y + i * line_h
        if shadow:
            draw.text((x + 3, ly + 3), line, font=font, fill=(0, 0, 0, 160))
        draw.text((x, ly), line, font=font, fill=color)
    return len(lines) * line_h


# ── Frame generators ──────────────────────────────────────────────────────────

def frame_slide1(t, duration=8.0):
    """Slide 1: Is your property truly secure?  0-8s"""
    bg = gradient_bg(W, H, DARK_NAVY, (15, 30, 70))
    img = Image.fromarray(bg.astype(np.uint8)).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Animated scanning line
    scan_y = int((t % 3) / 3 * H)
    draw.rectangle([0, scan_y, W, scan_y + 4], fill=(*RED, 60))

    # Top orange accent line (brand color)
    draw.rectangle([W // 2 - 60, 40, W // 2 + 60, 48], fill=(255, 100, 0, 230))

    # Logo shield area
    fade = min(1.0, t * 2)
    logo_alpha = int(fade * 255)
    draw_logo_composite(img, W // 2, 280, 120)

    # Company name
    f_company = make_font(48)
    draw_centered_text(draw, "MONTES PATROL", f_company, 430, color=WHITE)
    f_sub = make_font_normal(28)
    draw_centered_text(draw, "— SECURITY LLC —", f_sub, 488, color=GOLD)

    # Red divider
    draw_red_bar(draw, 540, W, 5)

    # Main question - slides in from left
    slide = min(1.0, t * 1.5)
    text_x_offset = int((1 - slide) * -W)
    f_big = make_font(90)
    lines = ["IS YOUR", "PROPERTY", "TRULY", "SECURE?"]
    line_h = 105
    start_y = 580
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=f_big)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2 + text_x_offset
        y = start_y + i * line_h
        draw.text((x + 4, y + 4), line, font=f_big, fill=(0, 0, 0, 120))
        col = RED if line == "SECURE?" else WHITE
        draw.text((x, y), line, font=f_big, fill=col)

    # Sub-caption
    fade2 = max(0, min(1.0, (t - 1.5) * 2))
    f_cap = make_font_normal(36)
    cap = "See how 24/7 licensed patrols\neliminate your vulnerability."
    for idx, cline in enumerate(cap.split("\n")):
        bbox = draw.textbbox((0, 0), cline, font=f_cap)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        y = 1010 + idx * 52
        alpha_val = int(fade2 * 200)
        draw.text((x, y), cline, font=f_cap, fill=(*LIGHT_GRAY, alpha_val))

    # Bottom contact bar
    draw.rectangle([0, H - 130, W, H], fill=(*RED, 220))
    f_contact = make_font(38)
    draw_centered_text(draw, "(346) 277-2563", f_contact, H - 115, color=WHITE, shadow=False)
    f_web = make_font_normal(26)
    draw_centered_text(draw, "www.montespatrolsecurityllc.com", f_web, H - 68, color=(*GOLD, 255), shadow=False)

    return np.array(img.convert("RGB"))


def frame_slide2(t, duration=8.0):
    """Slide 2: Safety never takes a shift off.  8-16s"""
    bg = gradient_bg(W, H, (5, 10, 25), DARK_NAVY)
    img = Image.fromarray(bg.astype(np.uint8)).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Pulsing glow effect (simulated)
    pulse = 0.5 + 0.5 * math.sin(t * math.pi * 2)
    glow_r = int(40 + pulse * 20)
    draw.ellipse([W // 2 - 300, 80, W // 2 + 300, 680], fill=(20, 30, 80, 180))

    # Big headline - fade in
    fade = min(1.0, t * 1.2)
    f_huge = make_font(110)
    lines_txt = [("SAFETY", WHITE), ("NEVER", WHITE), ("TAKES", RED), ("A SHIFT", RED), ("OFF", WHITE)]
    line_h = 125
    start_y = 60
    for i, (line, col) in enumerate(lines_txt):
        bbox = draw.textbbox((0, 0), line, font=f_huge)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        y = start_y + i * line_h
        opacity = int(min(1.0, fade * (i + 1) / len(lines_txt) * 3) * 255)
        draw.text((x + 5, y + 5), line, font=f_huge, fill=(0, 0, 0, opacity // 2))
        draw.text((x, y), line, font=f_huge, fill=(*col, opacity))

    # Body text
    f_body = make_font_normal(40)
    body = "Most security gaps happen after dark.\nWe're here to close them\nbefore they start."
    fade2 = max(0, min(1.0, (t - 1.0) * 1.5))
    body_y = 720
    for idx, bline in enumerate(body.split("\n")):
        bbox = draw.textbbox((0, 0), bline, font=f_body)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        y = body_y + idx * 56
        draw.text((x, y), bline, font=f_body, fill=(*LIGHT_GRAY, int(fade2 * 220)))

    # Car icon row (stylized)
    draw.rectangle([0, 920, W, 930], fill=(*RED, 200))

    # Services marquee (scrolling left)
    services = "24/7 COVERAGE  •  FAST RESPONSE  •  MOBILE PATROLS  •  APARTMENT COMMUNITIES  •  CONSTRUCTION  •  "
    f_marquee = make_font(36)
    marquee_text = services * 3
    bbox = draw.textbbox((0, 0), marquee_text, font=f_marquee)
    text_w = bbox[2] - bbox[0]
    scroll_speed = 200  # px/sec
    offset = int(t * scroll_speed) % (text_w // 3)

    # Marquee strip background
    draw.rectangle([0, 940, W, 1010], fill=(20, 20, 50, 240))
    draw.text((-offset, 952), marquee_text, font=f_marquee, fill=(*WHITE, 230))
    draw.text((-offset + text_w // 3, 952), marquee_text, font=f_marquee, fill=(*WHITE, 230))

    # Feature bullets
    features = [
        ("24/7", "Security Coverage"),
        ("", "Fast Response Time"),
        ("", "Professional Guards"),
        ("", "Reliable Patrols"),
    ]
    f_feat_title = make_font(34)
    f_feat_sub = make_font_normal(28)
    fade3 = max(0, min(1.0, (t - 2.0) * 2))
    feat_y = 1050
    for i, (label, desc) in enumerate(features):
        # Circle icon
        cx, cy = 90, feat_y + i * 110 + 30
        draw.ellipse([cx - 38, cy - 38, cx + 38, cy + 38], fill=(*RED, int(fade3 * 200)))
        if label:
            bbox = draw.textbbox((0, 0), label, font=f_feat_sub)
            lw = bbox[2] - bbox[0]
            draw.text((cx - lw // 2, cy - 14), label, font=f_feat_sub, fill=(*WHITE, int(fade3 * 255)))
        else:
            draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=(*WHITE, int(fade3 * 200)))
        draw.text((150, feat_y + i * 110 + 8), desc, font=f_feat_title, fill=(*WHITE, int(fade3 * 230)))

    # Red bottom bar
    draw.rectangle([0, H - 100, W, H], fill=(*DARK_RED, 240))
    f_bottom = make_font(34)
    draw_centered_text(draw, "LICENSED  •  INSURED", f_bottom, H - 80, color=WHITE, shadow=False)

    return np.array(img.convert("RGB"))


def frame_slide3(t, duration=7.0):
    """Slide 3: Your assets, our authority.  16-23s"""
    bg = gradient_bg(W, H, (8, 8, 18), (15, 20, 45))
    img = Image.fromarray(bg.astype(np.uint8)).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Logo big (zooms in)
    zoom = min(1.0, 0.4 + t * 0.3)
    logo_size = int(280 * zoom)
    draw_logo_composite(img, W // 2, 480, logo_size)

    # Company brand text
    fade = min(1.0, t * 1.5)
    f_brand = make_font(62)
    f_brand_sub = make_font(32)
    cx_text = W // 2
    bbox = draw.textbbox((0, 0), "MONTES PATROL", font=f_brand)
    tw = bbox[2] - bbox[0]
    draw.text((cx_text - tw // 2 + 3, 793), "MONTES PATROL", font=f_brand, fill=(0, 0, 0, 100))
    draw.text((cx_text - tw // 2, 790), "MONTES PATROL", font=f_brand, fill=(*WHITE, int(fade * 255)))
    bbox2 = draw.textbbox((0, 0), "— SECURITY LLC —", font=f_brand_sub)
    tw2 = bbox2[2] - bbox2[0]
    draw.text((cx_text - tw2 // 2, 862), "— SECURITY LLC —", font=f_brand_sub, fill=(*GOLD, int(fade * 200)))

    # Red bar
    draw_red_bar(draw, 910, W, 6)

    # Big tagline
    slide_x = int((1 - min(1.0, t * 2)) * W)
    f_tag = make_font(105)
    for line, ypos, col in [("YOUR ASSETS,", 960, WHITE), ("OUR", 1070, RED), ("AUTHORITY", 1175, WHITE)]:
        bbox = draw.textbbox((0, 0), line, font=f_tag)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2 - slide_x
        draw.text((x + 4, ypos + 4), line, font=f_tag, fill=(0, 0, 0, 130))
        draw.text((x, ypos), line, font=f_tag, fill=col)

    # Underline bar
    draw.rectangle([120, 1305, W - 120, 1311], fill=(*WHITE, 180))

    # Sub caption
    fade2 = max(0, min(1.0, (t - 1.0) * 2))
    f_sub = make_font_normal(34)
    sub = "Join the property managers who\ntrust the shield.\nLicensed, insured, and 24/7 available."
    for idx, sline in enumerate(sub.split("\n")):
        bbox = draw.textbbox((0, 0), sline, font=f_sub)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        y = 1325 + idx * 52
        draw.text((x, y), sline, font=f_sub, fill=(*LIGHT_GRAY, int(fade2 * 220)))

    # Stars decoration
    for i in range(5):
        star_x = 200 + i * 175
        draw_star(draw, star_x, 1520, 22, color=(*GOLD, int(fade2 * 200)))

    # Bottom bar
    draw.rectangle([0, H - 120, W, H], fill=(*NAVY, 250))
    draw.rectangle([0, H - 122, W, H - 118], fill=(*RED, 255))
    f_contact = make_font(36)
    draw_centered_text(draw, "(346) 277-2563  |  montespatrolsecurityllc.com", f_contact, H - 100, color=WHITE, shadow=False)

    return np.array(img.convert("RGB"))


def frame_slide4(t, duration=7.0):
    """Slide 4: Professional Elite Protection — CTA.  23-30s"""
    bg = gradient_bg(W, H, NAVY, (12, 24, 55))
    img = Image.fromarray(bg.astype(np.uint8)).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # Top badge area
    draw.rectangle([50, 50, W - 50, 320], fill=(20, 35, 80, 220), outline=(*RED, 200), width=5)
    f_badge1 = make_font(44)
    f_badge2 = make_font(32)
    draw_centered_text(draw, "PATROL & SECURITY", f_badge1, 80, color=WHITE)
    draw_centered_text(draw, "SERVICES", f_badge1, 130, color=RED)
    draw_logo_composite(img, W // 2, 240, 90)

    # Services list with checkmarks
    services_list = [
        "On-Site Security Guards",
        "Mobile Patrol Units",
        "Construction Site Security",
        "Apartment Communities",
    ]
    f_serv = make_font(40)
    fade_serv = max(0, min(1.0, (t - 0.5) * 2))
    serv_y = 380
    for i, svc in enumerate(services_list):
        item_fade = max(0, min(1.0, (t - 0.3 - i * 0.3) * 3))
        # Checkmark square
        bx, by = 80, serv_y + i * 80
        draw.rectangle([bx, by + 2, bx + 36, by + 38], fill=(*RED, int(item_fade * 230)))
        draw.text((bx + 4, by + 2), "✓", font=make_font(28), fill=(*WHITE, int(item_fade * 255)))
        draw.text((bx + 50, by), svc, font=f_serv, fill=(*WHITE, int(item_fade * 230)))

    # Red separator
    draw_red_bar(draw, 720, W, 8)

    # Big CTA text
    f_cta = make_font(85)
    cta_lines = [("PROFESSIONAL", WHITE), ("ELITE", RED), ("PROTECTION", WHITE)]
    cta_y = 760
    for i, (line, col) in enumerate(cta_lines):
        slide = min(1.0, max(0.0, t * 1.8 - i * 0.3))
        bbox = draw.textbbox((0, 0), line, font=f_cta)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        y = cta_y + i * 98
        draw.text((x + 4, y + 4), line, font=f_cta, fill=(0, 0, 0, int(slide * 120)))
        draw.text((x, y), line, font=f_cta, fill=(*col, int(slide * 255)))

    # Description
    f_desc = make_font_normal(36)
    desc = "Licensed guards and mobile patrols\ntailored for apartments,\nretail, and construction."
    fade_desc = max(0, min(1.0, (t - 1.2) * 2))
    desc_y = 1060
    for idx, dline in enumerate(desc.split("\n")):
        bbox = draw.textbbox((0, 0), dline, font=f_desc)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        y = desc_y + idx * 54
        draw.text((x, y), dline, font=f_desc, fill=(*LIGHT_GRAY, int(fade_desc * 210)))

    # LICENSED • INSURED bar
    draw.rectangle([0, 1230, W, 1300], fill=(*DARK_RED, 240))
    f_li = make_font(48)
    draw_centered_text(draw, "LICENSED  •  INSURED", f_li, 1242, color=WHITE, shadow=False)

    # Bottom contact
    draw.rectangle([0, H - 200, W, H], fill=(*DARK_NAVY, 255))
    draw.rectangle([0, H - 202, W, H - 197], fill=(*RED, 255))
    f_phone = make_font(52)
    f_web2 = make_font_normal(32)

    # Phone icon indicator
    draw.ellipse([80, H - 185, 130, H - 135], fill=(*RED, 220))
    draw.text((88, H - 180), "☎", font=make_font_normal(32), fill=WHITE)

    bbox = draw.textbbox((0, 0), "(346) 277-2563", font=f_phone)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, H - 188), "(346) 277-2563", font=f_phone, fill=(*WHITE, 255))

    # Globe icon
    draw.ellipse([80, H - 108, 116, H - 75], fill=(*NAVY, 200), outline=(*WHITE, 150), width=2)
    draw.text((82, H - 106), "⊕", font=make_font_normal(28), fill=(*WHITE, 180))

    bbox2 = draw.textbbox((0, 0), "www.montespatrolsecurityllc.com", font=f_web2)
    tw2 = bbox2[2] - bbox2[0]
    draw.text(((W - tw2) // 2, H - 108), "www.montespatrolsecurityllc.com", font=f_web2, fill=(*GOLD, 220))

    return np.array(img.convert("RGB"))


# ── Build video ────────────────────────────────────────────────────────────────

def build_video():
    from moviepy import ImageClip, VideoClip, concatenate_videoclips
    from moviepy.video.fx import FadeIn, FadeOut, CrossFadeIn, CrossFadeOut

    TOTAL = 30.0
    # Segment durations
    d1, d2, d3, d4 = 8.0, 8.0, 7.0, 7.0

    print("Rendering slide 1...")
    clip1 = VideoClip(lambda t: frame_slide1(t, d1), duration=d1)
    clip1 = clip1.with_fps(FPS)

    print("Rendering slide 2...")
    clip2 = VideoClip(lambda t: frame_slide2(t, d2), duration=d2)
    clip2 = clip2.with_fps(FPS)

    print("Rendering slide 3...")
    clip3 = VideoClip(lambda t: frame_slide3(t, d3), duration=d3)
    clip3 = clip3.with_fps(FPS)

    print("Rendering slide 4...")
    clip4 = VideoClip(lambda t: frame_slide4(t, d4), duration=d4)
    clip4 = clip4.with_fps(FPS)

    # Add fade in/out transitions
    FADE = 0.5
    clip1 = clip1.with_effects([FadeIn(FADE), FadeOut(FADE)])
    clip2 = clip2.with_effects([FadeIn(FADE), FadeOut(FADE)])
    clip3 = clip3.with_effects([FadeIn(FADE), FadeOut(FADE)])
    clip4 = clip4.with_effects([FadeIn(FADE), FadeOut(FADE)])

    print("Concatenating clips...")
    final = concatenate_videoclips([clip1, clip2, clip3, clip4], method="compose")

    out_path = "/home/user/Sublimontes_shop/montes_patrol_promo_30s.mp4"
    print(f"Writing to {out_path}...")
    final.write_videofile(
        out_path,
        fps=FPS,
        codec="libx264",
        audio=False,
        preset="fast",
        ffmpeg_params=["-crf", "20", "-pix_fmt", "yuv420p"],
        logger="bar",
    )
    print("Done!")
    return out_path


if __name__ == "__main__":
    out = build_video()
    print(f"Video saved: {out}")
