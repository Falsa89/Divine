"""Debug preview: mostra ogni frame come viene tagliato dalla griglia ufficiale."""
import os
from PIL import Image, ImageDraw

ROOT = "/app/frontend/assets/heroes/norse_berserker"
SRC = os.path.join(ROOT, "source_sheets")
OUT = os.path.join(ROOT, "runtime", "_debug_frame_split.png")

STATES = [
    ("idle_source.png", 6, 1, "row"),
    ("attack_source.png", 5, 1, "row"),
    ("skill_source.png", 9, 2, "5plus4"),
    ("hit_source.png", 5, 1, "row"),
    ("death_source.png", 6, 1, "row"),
]

TILE = 200  # thumbnail size
GAP = 4

rows = []
for fname, n, n_rows, layout in STATES:
    img = Image.open(os.path.join(SRC, fname)).convert("RGBA")
    W, H = img.size
    frames = []
    if layout == "row":
        for i in range(n):
            x0 = round(i * W / n); x1 = round((i + 1) * W / n)
            frames.append(img.crop((x0, 0, x1, H)))
    else:  # 5plus4
        for i in range(5):
            x0 = round(i * W / 5); x1 = round((i + 1) * W / 5)
            frames.append(img.crop((x0, 0, x1, H // 2)))
        for i in range(4):
            x0 = round(i * W / 4); x1 = round((i + 1) * W / 4)
            frames.append(img.crop((x0, H // 2, x1, H)))

    # thumbnail each
    thumbs = []
    for idx, f in enumerate(frames):
        tw, th = f.size
        scale = min(TILE / tw, TILE / th)
        nw, nh = int(tw * scale), int(th * scale)
        t = f.resize((nw, nh))
        tile = Image.new("RGBA", (TILE, TILE), (40, 40, 50, 255))
        tile.paste(t, ((TILE - nw) // 2, (TILE - nh) // 2), t)
        draw = ImageDraw.Draw(tile)
        bbox = f.split()[-1].getbbox()
        if bbox is None:
            draw.rectangle([(0, 0), (TILE - 1, TILE - 1)], outline=(255, 40, 40, 255), width=4)
            draw.text((8, 8), "EMPTY", fill=(255, 40, 40, 255))
        else:
            w = bbox[2] - bbox[0]; h = bbox[3] - bbox[1]
            draw.text((4, 4), f"#{idx} {w}x{h}", fill=(255, 255, 255, 255))
        thumbs.append(tile)

    row_w = TILE * len(thumbs) + GAP * (len(thumbs) - 1)
    row_h = TILE + 24
    row_img = Image.new("RGBA", (row_w + 200, row_h), (20, 20, 30, 255))
    d = ImageDraw.Draw(row_img)
    d.text((4, 4), f"{fname}  {W}x{H}  layout={layout}  atteso={n}", fill=(255, 255, 255, 255))
    for i, t in enumerate(thumbs):
        row_img.paste(t, (200 + i * (TILE + GAP), 20))
    rows.append(row_img)

total_w = max(r.size[0] for r in rows)
total_h = sum(r.size[1] for r in rows) + GAP * (len(rows) - 1)
final = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 255))
y = 0
for r in rows:
    final.paste(r, (0, y))
    y += r.size[1] + GAP
final.save(OUT, "PNG")
print(f"✅ Salvato {OUT}  dimensioni={final.size}")
