"""
Extract the 8 approved keyframes from the 2 reference images.
- Source: /tmp/ref_01_frames_1-4.png (1536x1024, 4 frame 384 wide)
         /tmp/ref_02_frames_5-8.png (1536x1024, 4 frame 384 wide)
- Output A (battle assets): 8 RGBA PNG con sfondo nero → alpha trasparente,
  label area ritagliata, salvati in
  /app/frontend/assets/heroes/greek_hoplite/affondo/frame_{1..8}.png
- Output B (contact sheet locked): singola immagine orizzontale 8 frame
  con label, sfondo nero. Salvata come
  /app/frontend/assets/heroes/greek_hoplite/affondo/_REFERENCE_LOCKED.png
  + /tmp/affondo_merged_reference.png
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

REF1 = '/tmp/ref_01_frames_1-4.png'
REF2 = '/tmp/ref_02_frames_5-8.png'
OUT_DIR = '/app/frontend/assets/heroes/greek_hoplite/affondo'
os.makedirs(OUT_DIR, exist_ok=True)

LABELS = [
    "1. IDLE",
    "2. PRE-LOAD",
    "3. RITRAZIONE",
    "4. AFFONDO MID",
    "5. AFFONDO PEAK",
    "6. IMPACT HOLD",
    "7. RETURN MID",
    "8. IDLE FINALE",
]

# Layout sorgente: 4 frame × 384 px su canvas 1536×1024, label y~950-1000
FRAME_W_SRC = 384
FRAME_H_SRC = 1024
LABEL_CUTOFF_Y = 640  # label band inizia ~y=670, taglio sopra


def black_to_transparent(img_rgb: Image.Image) -> Image.Image:
    """Converte sfondo nero → alpha trasparente con bordi morbidi.
    Preserva il personaggio (alpha 255) e i pixel sottili di contorno."""
    arr = np.array(img_rgb.convert('RGB')).astype(np.float32)
    # Luminosità del pixel come proxy di "quanto non è nero"
    lum = arr.max(axis=2)  # 0 nero puro, 255 bianco puro
    alpha = np.clip((lum - 8) / 28 * 255, 0, 255).astype(np.uint8)
    # soft threshold: lum<=8 → 0, lum>=36 → 255
    rgba = np.dstack([arr.astype(np.uint8), alpha])
    return Image.fromarray(rgba, 'RGBA')


def extract_battle_frames():
    """Salva 8 frame battle-ready (alpha trasparente, no label).
    Tutti i frame hanno STESSO canvas (384×900) e STESSO ground baseline
    → nessuno scatto verticale quando vengono swappati in battle.
    Il personaggio è naturalmente allineato a terra nelle reference."""
    for idx, src in enumerate([REF1, REF2]):
        im = Image.open(src).convert('RGB')
        for k in range(4):
            x0 = k * FRAME_W_SRC
            x1 = x0 + FRAME_W_SRC
            # Crop fisso 384×900 (taglio label band, no tight crop).
            crop = im.crop((x0, 0, x1, LABEL_CUTOFF_Y))
            rgba = black_to_transparent(crop)
            frame_no = idx * 4 + k + 1
            out = os.path.join(OUT_DIR, f'frame_{frame_no}.png')
            rgba.save(out, optimize=True)
            print(f"  frame_{frame_no}.png  {rgba.size}  {os.path.getsize(out)} B")
    print("✓ 8 battle frames saved (fixed canvas, same ground baseline)")


def build_merged_reference():
    """Costruisce la contact sheet finale con tutti 8 frame su una riga.
    Layout: sfondo nero, frame equi-spaziati, etichette sotto."""
    # Larghezza slot target per la sheet unificata
    SLOT_W = 384
    SLOT_H = LABEL_CUTOFF_Y  # altezza slot = altezza del crop senza label
    GAP = 60
    LABEL_H = 80
    TITLE_H = 100
    cols = 8
    sheet_w = cols * SLOT_W + (cols + 1) * GAP
    sheet_h = TITLE_H + SLOT_H + LABEL_H + 30

    sheet = Image.new('RGB', (sheet_w, sheet_h), (0, 0, 0))
    draw = ImageDraw.Draw(sheet)

    # Title
    def font(sz, bold=False):
        paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        for p in paths:
            if os.path.exists(p):
                return ImageFont.truetype(p, sz)
        return ImageFont.load_default()

    draw.text((GAP, 28),
              "AFFONDO DI FALANGE — REFERENCE LOCKED (8-frame sequence)",
              fill=(255, 215, 0), font=font(34, bold=True))
    draw.text((GAP, 66),
              "Greek Hoplite · source of truth · do not modify",
              fill=(170, 170, 180), font=font(16))

    # Combine source slots, preserving look
    for i in range(8):
        src = REF1 if i < 4 else REF2
        im = Image.open(src).convert('RGB')
        k = i % 4
        crop = im.crop((k * FRAME_W_SRC, 0, (k + 1) * FRAME_W_SRC, FRAME_H_SRC))
        x = GAP + i * (SLOT_W + GAP)
        y = TITLE_H
        # Remove the source label band from the crop so we place our own below
        crop_no_label = crop.crop((0, 0, SLOT_W, LABEL_CUTOFF_Y))
        # Center crop_no_label into slot of height SLOT_H with black filler
        slot = Image.new('RGB', (SLOT_W, SLOT_H), (0, 0, 0))
        slot.paste(crop_no_label, (0, 0))
        sheet.paste(slot, (x, y))

        # Label band
        label = LABELS[i]
        tw = draw.textlength(label, font=font(22, bold=True))
        lx = x + (SLOT_W - tw) // 2
        ly = y + SLOT_H + 18
        draw.text((lx, ly), label, fill=(255, 255, 255), font=font(22, bold=True))

    # Save outputs
    locked = os.path.join(OUT_DIR, '_REFERENCE_LOCKED.png')
    sheet.save(locked, optimize=True)
    merged_tmp = '/tmp/affondo_merged_reference.png'
    sheet.save(merged_tmp, optimize=True)
    print(f"✓ merged sheet saved:")
    print(f"   {locked}  {os.path.getsize(locked)} B  size={sheet.size}")
    print(f"   {merged_tmp}")


if __name__ == '__main__':
    extract_battle_frames()
    build_merged_reference()
