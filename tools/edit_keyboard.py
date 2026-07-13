"""Add the mod's L-key (language toggle) to the keyboard-help images
(config5/bg_config5.png) for en and ja, in the art's own style:
- highlight the L keycap with a gradient rebuilt from the S keycap's corners
- append a legend row under the middle column

Outputs to analysis/kb_edit/pc/<lang>/config5/bg_config5.png
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pfs import PfsArchive
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AN = os.path.join(ROOT, "analysis")


def home_row_caps(im_en, y=363, x0=250, x1=820):
    """Scan the EN image's home row at height y for bright keycap runs
    separated by dark gaps. Returns list of (xstart, xend) runs."""
    px = im_en.convert("RGB").load()
    runs = []
    cur = None
    for x in range(x0, x1):
        bright = sum(px[x, y]) > 380
        if bright and cur is None:
            cur = x
        elif not bright and cur is not None:
            if x - cur > 15:
                runs.append((cur, x - 1))
            cur = None
    if cur is not None:
        runs.append((cur, x1 - 1))
    return runs


def cap_vertical(im_en, xc, yc=363):
    """Extend up/down from (xc, yc) while bright to get cap top/bottom."""
    px = im_en.convert("RGB").load()
    top = bot = yc
    while sum(px[xc, top - 1]) > 380:
        top -= 1
    while sum(px[xc, bot + 1]) > 380:
        bot += 1
    return top, bot


def gradient_cap(im, src_box, dst_box, label, font, radius=6):
    """Rebuild the keycap gradient from src_box corner samples, paint it as a
    rounded rect at dst_box, draw the label."""
    sx0, sy0, sx1, sy1 = src_box
    px = im.load()  # RGBA: interpolate color AND alpha (caps are alpha≈128,
    ins = 6         # composited over the backdrop; glyphs are opaque white)
    c00 = px[sx0 + ins, sy0 + ins]
    c10 = px[sx1 - ins, sy0 + ins]
    c01 = px[sx0 + ins, sy1 - ins]
    c11 = px[sx1 - ins, sy1 - ins]
    nch = len(c00)
    dx0, dy0, dx1, dy1 = dst_box
    w, h = dx1 - dx0 + 1, dy1 - dy0 + 1
    grad = Image.new("RGBA", (w, h))
    gp = grad.load()
    for y in range(h):
        fy = y / max(h - 1, 1)
        for x in range(w):
            fx = x / max(w - 1, 1)
            gp[x, y] = tuple(
                int((c00[i] * (1 - fx) + c10[i] * fx) * (1 - fy)
                    + (c01[i] * (1 - fx) + c11[i] * fx) * fy)
                for i in range(nch))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1],
                                           radius=radius, fill=255)
    im.paste(grad, (dx0, dy0), mask)
    d = ImageDraw.Draw(im)
    bb = d.textbbox((0, 0), label, font=font)
    d.text((dx0 + (w - bb[2] + bb[0]) // 2 - bb[0],
            dy0 + (h - bb[3] + bb[1]) // 2 - bb[1]),
           label, font=font, fill=(255, 255, 255, 255))


def legend_row(im, x_key, x_desc, y, key, desc, font_key, font_desc,
               line_x1, key_color=(255, 222, 0, 255)):
    d = ImageDraw.Draw(im)
    d.text((x_key, y), key, font=font_key, fill=key_color)
    d.text((x_desc, y), desc, font=font_desc, fill=(255, 255, 255, 255))
    # underline like other rows
    d.line([(x_key, y + 26), (line_x1, y + 26)],
           fill=(255, 255, 255, 255), width=1)


def load(archive, name):
    """Keep alpha: EN art is RGBA with meaningful transparency (composited
    over the game's backdrop); flattening it wrecks the page in-game."""
    a = PfsArchive(os.path.join(ROOT, archive))
    im = Image.open(io.BytesIO(a.read(name))).convert("RGBA")
    a.close()
    return im


CREDIT = "JP patch by That-Ruben"


def process(im, out_rel, desc_text, font_path, s_box, l_box):
    cap_font = ImageFont.truetype(font_path, 20)
    gradient_cap(im, s_box, l_box, "L", cap_font)
    fk = ImageFont.truetype(font_path, 17)
    fd = ImageFont.truetype(font_path, 15)
    legend_row(im, 490, 626, 809, "L", desc_text, fk, fd, 876)
    # discreet credit, bottom-right
    d = ImageDraw.Draw(im)
    fc = ImageFont.truetype(font_path, 14)
    bb = d.textbbox((0, 0), CREDIT, font=fc)
    d.text((1530 - (bb[2] - bb[0]), 852), CREDIT, font=fc,
           fill=(255, 255, 255, 110))
    out = os.path.join(AN, "kb_edit", out_rel.replace("\\", os.sep))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.save(out)
    print("wrote", out)


if __name__ == "__main__":
    font = os.path.join(AN, "fonts", "font", "hp",
                        "rounded-x-mgenplus-1p-bold.ttf")
    im_en = load("HENPRI/HENPRI.pfs", "pc\\en\\config5\\bg_config5.png")
    runs = home_row_caps(im_en)
    print("home row runs:", runs)
    if len(runs) < 9:
        raise SystemExit("need 9 home-row caps (A..L), got %d" % len(runs))
    s0, s1 = runs[1]
    l0, l1 = runs[8]
    d_mid = sum(runs[2]) // 2
    top, bot = cap_vertical(im_en, d_mid)
    print("cap vertical:", top, bot)
    s_box, l_box = (s0, top, s1, bot), (l0, top, l1, bot)
    process(im_en, "pc\\en\\config5\\bg_config5.png",
            "Toggle language (JP/EN)", font, s_box, l_box)
    im_ja = load("HENPRI_JP/HENPRI.pfs", "pc\\ja\\config5\\bg_config5.png")
    process(im_ja, "pc\\ja\\config5\\bg_config5.png",
            "【ADV】言語切替（日本語⇄ENGLISH）", font, s_box, l_box)
