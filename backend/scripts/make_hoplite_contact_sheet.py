"""Crea una contact sheet con i 6 frame idle + una immagine diff (dove si muove vs base)."""
from PIL import Image, ImageChops, ImageDraw, ImageFont
import os

IDLE_DIR = "/app/frontend/assets/heroes/greek_hoplite/idle"
BASE_PATH = "/app/frontend/assets/heroes/greek_hoplite/base.png"
OUT_SHEET = "/app/backend/scripts/hoplite_idle_preview/contact_sheet.jpg"
OUT_DIFF = "/app/backend/scripts/hoplite_idle_preview/diff_heatmap.jpg"

os.makedirs(os.path.dirname(OUT_SHEET), exist_ok=True)

frames = []
for i in range(1, 7):
    p = os.path.join(IDLE_DIR, f"idle_{i:02d}.png")
    im = Image.open(p).convert("RGBA")
    im.thumbnail((320, 480))
    bg = Image.new("RGB", im.size, (18, 20, 30))
    bg.paste(im, mask=im.split()[-1])
    frames.append(bg)

w, h = frames[0].size
pad = 10
label_h = 26
sheet_w = w * 6 + pad * 7
sheet_h = h + pad * 2 + label_h
sheet = Image.new("RGB", (sheet_w, sheet_h), (10, 12, 18))

draw = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
except Exception:
    font = ImageFont.load_default()

for i, f in enumerate(frames):
    x = pad + i * (w + pad)
    sheet.paste(f, (x, pad))
    draw.text((x + 8, pad + h + 4), f"idle_{i + 1:02d}", fill=(180, 200, 230), font=font)

sheet.save(OUT_SHEET, "JPEG", quality=85)
print(f"[preview] Contact sheet salvata: {OUT_SHEET} {sheet.size}")

# Diff heatmap: differenza tra frame 01 (che è ~base con breath=0) e frame 04 (picco opposto)
base = Image.open(BASE_PATH).convert("RGB")
full1 = Image.open(os.path.join(IDLE_DIR, "idle_01.png")).convert("RGB")
full4 = Image.open(os.path.join(IDLE_DIR, "idle_04.png")).convert("RGB")
diff14 = ImageChops.difference(full1, full4)
# amplifica il segnale per rendere visibili i piccoli movimenti
diff_enh = diff14.point(lambda p: min(255, p * 6))
diff_enh.thumbnail((400, 600))
diff_enh.save(OUT_DIFF, "JPEG", quality=85)
print(f"[preview] Heatmap diff (idle_01 vs idle_04 x6): {OUT_DIFF}")
