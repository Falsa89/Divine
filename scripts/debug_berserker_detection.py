"""Debug: visualizza detection vs layout atteso per capire la struttura reale."""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = "/app/frontend/assets/heroes/norse_berserker"
SRC = os.path.join(ROOT, "source_sheets")
OUT = os.path.join(ROOT, "runtime", "_debug_detection.png")

STATES = [
    ("idle_source.png", 6, 1, "6 frame, 1 row"),
    ("attack_source.png", 5, 1, "5 frame, 1 row"),
    ("skill_source.png", 9, 2, "9 frame, 5 top + 4 bot"),
    ("hit_source.png", 5, 1, "5 frame, 1 row"),
    ("death_source.png", 6, 1, "6 frame, 1 row"),
]


def detect_column_ranges(img, threshold=8):
    """Ritorna lista di intervalli (x0,x1) per ogni blob di colonne non vuote."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    alpha = img.split()[-1]
    W, H = img.size
    px = alpha.load()
    col_has = []
    for x in range(W):
        has = False
        for y in range(0, H, 2):
            if px[x, y] > threshold:
                has = True
                break
        col_has.append(has)
    ranges = []
    start = None
    for x, c in enumerate(col_has):
        if c and start is None:
            start = x
        elif not c and start is not None:
            ranges.append((start, x))
            start = None
    if start is not None:
        ranges.append((start, len(col_has)))
    return ranges


thumbs = []
for fname, n_frames, n_rows, label in STATES:
    img = Image.open(os.path.join(SRC, fname)).convert("RGBA")
    W, H = img.size
    # Se ha due righe, analizza separatamente
    row_data = []
    if n_rows == 2:
        top = img.crop((0, 0, W, H // 2))
        bot = img.crop((0, H // 2, W, H))
        row_data.append(("TOP", top, detect_column_ranges(top), 0))
        row_data.append(("BOT", bot, detect_column_ranges(bot), H // 2))
    else:
        row_data.append(("ROW", img, detect_column_ranges(img), 0))

    # disegna overlay
    overlay = img.copy()
    draw = ImageDraw.Draw(overlay)
    # linee verticali della griglia UFFICIALE
    if n_rows == 2:
        # 5 col top, 4 col bot
        for i in range(1, 5):
            x = W * i // 5
            draw.line([(x, 0), (x, H // 2)], fill=(0, 255, 255, 255), width=3)
        for i in range(1, 4):
            x = W * i // 4
            draw.line([(x, H // 2), (x, H)], fill=(0, 255, 255, 255), width=3)
        draw.line([(0, H // 2), (W, H // 2)], fill=(0, 255, 255, 255), width=3)
    else:
        for i in range(1, n_frames):
            x = W * i // n_frames
            draw.line([(x, 0), (x, H)], fill=(0, 255, 255, 255), width=3)

    # box rossi: bbox dei blob rilevati
    for row_name, row_img, ranges, y_off in row_data:
        rh = row_img.size[1]
        for (x0, x1) in ranges:
            draw.rectangle([(x0, y_off), (x1, y_off + rh)], outline=(255, 0, 0, 255), width=2)

    # label superiore
    det_str = " | ".join([f"{r[0]}: {len(r[2])} blobs" for r in row_data])
    txt = f"{fname}  atteso={label}  rilevato={det_str}"
    # scala overlay a larghezza uniforme
    target_w = 1600
    scale = target_w / W
    overlay_small = overlay.resize((target_w, int(H * scale)))

    # aggiungi barra titolo
    bar_h = 40
    framed = Image.new("RGBA", (target_w, overlay_small.size[1] + bar_h), (20, 20, 30, 255))
    framed.paste(overlay_small, (0, bar_h))
    d2 = ImageDraw.Draw(framed)
    d2.text((10, 10), txt, fill=(255, 255, 255, 255))
    thumbs.append(framed)

total_h = sum(t.size[1] for t in thumbs) + 8 * (len(thumbs) - 1)
final = Image.new("RGBA", (1600, total_h), (0, 0, 0, 255))
y = 0
for t in thumbs:
    final.paste(t, (0, y))
    y += t.size[1] + 8
final.save(OUT, "PNG")
print(f"✅ Debug preview salvato: {OUT}")
print(f"   dimensioni: {final.size[0]}x{final.size[1]}")
