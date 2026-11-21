#!/usr/bin/env python3
"""Compose the 1024x1024 front page for news-image-20261120-v2.

Build script (not the entrypoint): it lays out the masthead, the four
AI-generated illustration panels, two procedurally drawn panels (Riyadh
skyline, markets chart) and the day-in-brief list into one newsprint-style
front page, and writes entry.png. Every story on the page was first
reported on Friday 20 November 2026. The entrypoint (main.ts) only decodes
the shipped base64 of the composed image, so the graded program is fully
deterministic with no network.

Usage:  python3 compose.py   (run from this directory)
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
# The four illustration panels live beside the repo (not shipped in it);
# override with NEWS_IMAGE_ASSETS if they are kept elsewhere.
ASSETS = os.environ.get(
    "NEWS_IMAGE_ASSETS",
    os.path.join(os.path.dirname(HERE), "news-image-20261120-v2-assets"))

W, H = 1024, 1024
PAPER = (248, 244, 236)
INK = (20, 20, 20)
RED = (163, 22, 33)
MUTED = (74, 74, 74)
RULE = (20, 20, 20)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_image(path, tw, th):
    """Center-crop an image to the target aspect, then resize."""
    im = Image.open(path).convert("RGB")
    sw, sh = im.size
    target = tw / th
    if sw / sh > target:  # too wide: crop sides
        nw = int(sh * target)
        x0 = (sw - nw) // 2
        im = im.crop((x0, 0, x0 + nw, sh))
    else:  # too tall: crop top/bottom (keep the middle band)
        nh = int(sw / target)
        y0 = (sh - nh) // 2
        im = im.crop((0, y0, sw, y0 + nh))
    return im.resize((tw, th), Image.LANCZOS)


def draw_riyadh(tw, th):
    """Procedural dusk skyline: twisted PIF Tower, smoke, lit windows."""
    im = Image.new("RGB", (tw, th))
    px = im.load()
    top = (58, 32, 66)      # dusk purple
    mid = (196, 94, 52)     # burnt orange horizon
    bot = (30, 22, 34)
    for y in range(th):
        t = y / th
        if t < 0.55:
            a = t / 0.55
            c = tuple(int(top[i] + (mid[i] - top[i]) * a) for i in range(3))
        else:
            a = (t - 0.55) / 0.45
            c = tuple(int(mid[i] + (bot[i] - mid[i]) * a) for i in range(3))
        for x in range(tw):
            px[x, y] = c
    d = ImageDraw.Draw(im, "RGBA")
    # low sun glow behind the tower
    d.ellipse([tw * 0.42, th * 0.30, tw * 0.72, th * 0.95], fill=(255, 170, 80, 70))
    # smoke plume from the tower top
    for i, (cx, cy, r) in enumerate([(205, 18, 16), (215, 8, 20), (228, 2, 14)]):
        d.ellipse([cx - r, cy - r // 2, cx + r, cy + r // 2],
                  fill=(120, 110, 115, 150 - i * 25))
    # building silhouettes (x0, top, x1, shade)
    towers = [(0, 58, 34, 26), (36, 44, 62, 30), (64, 66, 92, 24),
              (94, 38, 128, 30), (130, 60, 158, 26), (240, 52, 268, 28),
              (270, 68, 300, 24), (302, 46, 316, 30)]
    for x0, top_y, x1, shade in towers:
        d.rectangle([x0, top_y, x1, th], fill=(shade, shade - 4, shade + 4))
    # the twisted PIF tower, centre: two leaning slabs
    d.polygon([(168, th), (178, 26), (196, 26), (196, th)], fill=(38, 34, 44))
    d.polygon([(196, th), (196, 30), (214, 22), (222, th)], fill=(30, 28, 38))
    # lit windows
    import random
    rng = random.Random(20261120)
    for _ in range(90):
        x = rng.randint(2, tw - 5)
        y = rng.randint(48, th - 6)
        if 168 <= x <= 222 and y < 60:
            continue
        d.rectangle([x, y, x + 2, y + 2], fill=(255, 196, 90))
    # street line
    d.rectangle([0, th - 6, tw, th], fill=(12, 10, 14))
    return im


def draw_chart(tw, th):
    """Procedural markets panel: a falling red line on a dark board."""
    im = Image.new("RGB", (tw, th), (16, 24, 40))
    d = ImageDraw.Draw(im)
    for gy in range(12, th - 8, 18):
        d.line([(8, gy), (tw - 8, gy)], fill=(38, 52, 76), width=1)
    for gx in range(24, tw - 8, 34):
        d.line([(gx, 8), (gx, th - 8)], fill=(30, 42, 64), width=1)
    # falling line: record debut high, then the day-two slide
    # (points authored for a 316x104 panel; scale to the tile size)
    raw_pts = [(10, 26), (48, 22), (86, 30), (124, 38), (162, 34),
               (196, 52), (228, 58), (258, 76), (288, 88), (306, 96)]
    pts = [(int(x * tw / 316), int(y * th / 104)) for x, y in raw_pts]
    d.line(pts, fill=(232, 64, 64), width=3, joint="curve")
    for x, y in pts:
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(255, 120, 120))
    # faint green IPO-open marker (top-left label only; no dashed line)
    f2 = font(SANS, 11)
    d.text((12, 8), "IPO OPEN $111.50", font=f2, fill=(150, 190, 160))
    f = font(SANS_B, 15)
    d.text((12, th - 22), "ANTHROPIC  -11%", font=f, fill=(255, 120, 120))
    return im


def text_block(d, x, y, w, kicker, headline, deck, hf_size, df_size,
               head_max_lines=3, deck_max_lines=3, kicker_size=12):
    """Kicker + headline + deck; returns the y just below the block."""
    f_k = font(SANS_B, kicker_size)
    d.text((x, y), kicker, font=f_k, fill=RED)
    y += kicker_size + 6
    f_h = font(SERIF_B, hf_size)
    lines = wrap(d, headline, f_h, w)[:head_max_lines]
    for ln in lines:
        d.text((x, y), ln, font=f_h, fill=INK)
        y += hf_size + 4
    y += 2
    f_d = font(SERIF, df_size)
    for ln in wrap(d, deck, f_d, w)[:deck_max_lines]:
        d.text((x, y), ln, font=f_d, fill=MUTED)
        y += df_size + 5
    return y


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 26                      # margin
    CW = W - 2 * M              # 972 content width

    # ---- masthead ------------------------------------------------------
    f_mast = font(SERIF_B, 60)
    title = "THE WORLD TODAY"
    tw = d.textlength(title, font=f_mast)
    d.text(((W - tw) / 2, 20), title, font=f_mast, fill=INK)
    d.line([(M, 94), (W - M, 94)], fill=RULE, width=3)
    d.line([(M, 100), (W - M, 100)], fill=RULE, width=1)
    f_date = font(SANS_B, 15)
    d.text((M, 108), "FRIDAY 20 NOVEMBER 2026", font=f_date, fill=INK)
    mid = "THE WORLD IN ONE DAY"
    d.text(((W - d.textlength(mid, font=f_date)) / 2, 108), mid,
           font=f_date, fill=RED)
    right = "36 STORIES  ·  7 REGIONS"
    d.text((W - M - d.textlength(right, font=f_date), 108), right,
           font=f_date, fill=INK)
    d.line([(M, 130), (W - M, 130)], fill=RULE, width=3)

    # ---- hero row (y 136..520) -----------------------------------------
    hy = 136
    hero_w, hero_img_h = 620, 228
    kx = M + hero_w + 16         # right column x
    kx_w = W - M - kx            # 336
    hero = fit_image(os.path.join(ASSETS,
                                  "media-generation-kyiv-bridges-0-69043332-d69d-46f8-88e3-bec882173008.png"),
                     hero_w, hero_img_h)
    img.paste(hero, (M, hy))
    d.rectangle([M, hy, M + hero_w, hy + hero_img_h], outline=INK, width=1)
    y = text_block(d, M, hy + hero_img_h + 10, hero_w,
                   "UKRAINE  ·  LEAD STORY",
                   "KYIV'S BRIDGES HIT IN OVERNIGHT BARRAGE",
                   "Russia fires 400+ drones and 110 missiles; three Dnipro "
                   "crossings damaged, seven killed in the capital, power cut "
                   "to five districts.", 30, 15)

    cy = fit_image(os.path.join(ASSETS,
                                "media-generation-cyclone-akvan-0-3d0a787b-ffbf-4a6b-806b-4b93ac1735a3.png"),
                   kx_w, 112)
    img.paste(cy, (kx, hy))
    d.rectangle([kx, hy, kx + kx_w, hy + 112], outline=INK, width=1)
    y2 = text_block(d, kx, hy + 120, kx_w,
                    "INDIA  ·  WEATHER",
                    "CYCLONE AKVAN HITS ODISHA",
                    "More than 300,000 evacuated as the storm makes landfall "
                    "on India's east coast.", 18, 12,
                    head_max_lines=1, deck_max_lines=2)
    sy = y2 + 8
    sh = fit_image(os.path.join(ASSETS,
                                "media-generation-shenzhen-summit-0-efc9a057-d4ca-4516-bf3b-89df632cc626.png"),
                   kx_w, 96)
    img.paste(sh, (kx, sy))
    d.rectangle([kx, sy, kx + kx_w, sy + 96], outline=INK, width=1)
    text_block(d, kx, sy + 104, kx_w,
               "DIPLOMACY  ·  SHENZHEN",
               "THREE POWERS, ONE TABLE",
               "Trump, Xi and Putin sign a joint declaration: nuclear war "
               "must never be fought.", 18, 12,
               head_max_lines=1, deck_max_lines=2)
    d.line([(M, 526), (W - M, 526)], fill=RULE, width=1)

    # ---- middle row: three tiles (y 534..721) --------------------------
    my = 534
    tile_w = (CW - 24) // 3     # 316
    tile_img_h = 88
    tiles = []
    icj = fit_image(os.path.join(ASSETS,
                                 "media-generation-icj-hague-0-5eeb2a04-50d2-4265-a74e-3cdbd3c23f86.png"),
                    tile_w, tile_img_h)
    tiles.append((icj, "JUSTICE  ·  THE HAGUE",
                  "COURT: MYANMAR COMMITTED GENOCIDE",
                  "World court finds the state responsible for the 2017 "
                  "atrocities against the Rohingya — a first."))
    tiles.append((draw_riyadh(tile_w, tile_img_h), "MIDDLE EAST  ·  RIYADH",
                  "MISSILE HITS RIYADH'S PIF TOWER",
                  "Houthi strike damages a tower in the Saudi capital's "
                  "financial district; coalition hits Hodeidah."))
    tiles.append((draw_chart(tile_w, tile_img_h), "MARKETS  ·  NEW YORK",
                  "ANTHROPIC SLIDES AFTER RECORD IPO",
                  "Shares fall 11% on day two after an $81.3bn debut; Wall "
                  "Street slumps as Asia's AI rally cools."))
    for i, (tile_img, kicker, head, deck) in enumerate(tiles):
        tx = M + i * (tile_w + 12)
        img.paste(tile_img, (tx, my))
        d.rectangle([tx, my, tx + tile_w, my + tile_img_h], outline=INK, width=1)
        text_block(d, tx, my + tile_img_h + 8, tile_w, kicker, head, deck,
                   16, 11, head_max_lines=2, deck_max_lines=2, kicker_size=11)
    d.line([(M, 726), (W - M, 726)], fill=RULE, width=1)

    # ---- the day in brief (y 734..989) ---------------------------------
    by = 734
    f_sec = font(SANS_B, 14)
    d.text((M, by), "THE DAY IN BRIEF", font=f_sec, fill=INK)
    f_cnt = font(SANS, 12)
    d.text((W - M - d.textlength("30 MORE STORIES", font=f_cnt), by + 1),
           "30 MORE STORIES", font=f_cnt, fill=MUTED)
    d.line([(M, by + 22), (W - M, by + 22)], fill=RULE, width=1)

    col_a = [
        ("EUROPE", "Germany rejects a \u201cnew Yalta\u201d deal on Europe without Europe"),
        ("EUROPE", "UK and EU sign deals on food, carbon and youth mobility"),
        ("EUROPE", "Denmark approves Greenland\u2013US Arctic security pact"),
        ("EUROPE", "Spain's S\u00e1nchez admits mistakes in election debate"),
        ("EUROPE", "Russian missiles enter Polish airspace in Kyiv attack"),
        ("EUROPE", "Cost-of-living protests planned across the continent"),
        ("ASIA", "Taiwan flags 2,700 accounts in alleged China influence op"),
        ("ASIA", "Japan and India agree deeper defence cooperation"),
        ("ASIA", "South Korea confirms first cholera case in a decade"),
        ("ASIA", "China holds rates for 18th month; Japan inflation 2.2%"),
        ("ASIA", "Ukraine drones hit Dorogobuzh chemical plant in Russia"),
        ("ASIA", "Bangladesh political tensions flare again"),
        ("ASIA", "Kerch Bridge rail traffic resumes after strikes"),
        ("ASIA", "Cyclone Xavier, Category 4, tracked in the South Pacific"),
        ("OCEANIA", "Australia and Japan deepen security coordination"),
    ]
    col_b = [
        ("MIDDLE EAST", "Iraq reaches deal with Kataib Hezbollah militia"),
        ("MIDDLE EAST", "Tankers hit mines near the Strait of Hormuz"),
        ("MIDDLE EAST", "Pentagon puts US Iran campaign cost at $48.3bn"),
        ("MIDDLE EAST", "Gaza health officials: 22,000+ children killed"),
        ("AFRICA", "Somalia orders UAE ambassador to leave in 72 hours"),
        ("AFRICA", "Sudan's war grinds on as displacement grows"),
        ("AFRICA", "Nigeria moves to decriminalise attempted suicide"),
        ("AMERICAS", "US Senate passes major permitting reform bill"),
        ("AMERICAS", "US and Venezuela resume joint military training"),
        ("AMERICAS", "Haiti police kill 34 suspected gang members in raid"),
        ("AMERICAS", "El Salvador's Bukele prepares a third-term bid"),
        ("AMERICAS", "Brazil advances Indigenous land rights in Amazon"),
        ("GLOBAL", "COP31 runs into overtime; draft omits fossil fuels"),
        ("GLOBAL", "Intuit sells Mailchimp for $3.68bn, a third of its price"),
        ("GLOBAL", "Voyager 1: radio signals now take a day to reach Earth"),
    ]
    assert len(col_a) + len(col_b) == 30, "brief must hold 30 stories"
    f_tag = font(SANS_B, 11)
    f_item = font(SANS, 12)
    col_w = (CW - 20) // 2
    pitch = 15
    iy = by + 28
    for col, items in enumerate((col_a, col_b)):
        cx = M + col * (col_w + 20)
        yy = iy
        for tag, head in items:
            tag_txt = tag + "  "
            d.text((cx, yy), tag_txt, font=f_tag, fill=RED)
            tx = cx + d.textlength(tag_txt, font=f_tag)
            avail = cx + col_w - tx
            # shorten the headline until it fits on one line
            while head and d.textlength(head, font=f_item) > avail:
                head = head.rsplit(" ", 1)[0] + "\u2026"
            d.text((tx, yy), head, font=f_item, fill=INK)
            yy += pitch
    assert yy <= 988, f"brief overflows: ends at {yy}"

    # ---- footer ----------------------------------------------------------
    d.line([(M, 992), (W - M, 992)], fill=RULE, width=1)
    f_foot = font(SANS, 10)
    foot = ("All stories first reported Friday 20 November 2026  ·  "
            "Illustrations drawn for this edition  ·  36 stories, 7 regions")
    d.text(((W - d.textlength(foot, font=f_foot)) / 2, 1000), foot,
           font=f_foot, fill=MUTED)

    out = os.path.join(HERE, "entry.png")
    img.save(out, "PNG", optimize=True)
    size = os.path.getsize(out)
    print(f"wrote {out}: {size} bytes")
    if size > 1048576:
        img.save(out, "JPEG", quality=88, optimize=True)
        print(f"PNG too big; saved JPEG: {os.path.getsize(out)} bytes")


if __name__ == "__main__":
    main()
