"""Generate pc/*/config1/bt_language_ja.png from an existing language button.

Takes bt_language_cn.png (182x150: rows normal/hover/selected at y=0/50/100),
erases the label by vertical color-cloning inside each box, then draws the
new label with the game's own font.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H, ROW = 182, 150, 50
TEXT_TOP, TEXT_BOT = 10, 40  # label zone to erase inside each row


def erase_label(im, row_top, ref_dy=6):
    px = im.load()
    ref_y = row_top + ref_dy
    for x in range(W):
        r = px[x, ref_y]
        for y in range(row_top + TEXT_TOP, row_top + TEXT_BOT):
            px[x, y] = r


def make(src_path, out_path, label, font_path, size=25, dy=-1):
    im = Image.open(src_path).convert("RGBA")
    # row 0: transparent background, text only -> wipe fully
    for x in range(W):
        for y in range(0, ROW):
            im.putpixel((x, y), (0, 0, 0, 0))
    erase_label(im, 50)
    erase_label(im, 100)

    font = ImageFont.truetype(font_path, size)
    draw = ImageDraw.Draw(im)
    for row_top in (0, 50, 100):
        bbox = draw.textbbox((0, 0), label, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (W - tw) // 2 - bbox[0]
        y = row_top + (48 - th) // 2 - bbox[1] + dy
        draw.text((x, y), label, font=font, fill=(255, 255, 255, 255))
    im.save(out_path)
    print("wrote", out_path)


if __name__ == "__main__":
    src, out, font = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    make(src, out, "日本語", font)
