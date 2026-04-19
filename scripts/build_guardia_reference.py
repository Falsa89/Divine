"""
Extract 6 approved keyframes for GUARDIA FERREA from reference.
================================================================
Source: /tmp/ref_guardia.png (1536x1024, 6 frame 256 wide)
Labels at y≈700-740 (LABEL_CUTOFF_Y=685 per sicurezza).

Per-frame audit (max extent dai piedi):
  sinistra: 137px, destra: 160px, sopra: 343px (frame 4 col glow).

Canvas uniforme: 420×420 con feet anchor (210, 390):
  sx 210 > 137 ✓, dx 210 > 160 ✓, sopra 390 > 343 ✓, sotto 30 (ombra)
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import label as cc_label

REF = '/tmp/ref_guardia.png'
OUT_DIR = '/app/frontend/assets/heroes/greek_hoplite/guardia_ferrea'
os.makedirs(OUT_DIR, exist_ok=True)

LABELS = [
    "1. IDLE", "2. ANCHOR", "3. SHIELD FORWARD",
    "4. PULSE PEAK", "5. HOLD END", "6. RETURN",
]

CANVAS_W = 420
CANVAS_H = 420
FEET_X_IN_CANVAS = 210
FEET_Y_IN_CANVAS = 390

SRC_SLOT_W = 256
SLOT_CX_AT = lambda k: k * SRC_SLOT_W + SRC_SLOT_W // 2
LABEL_CUTOFF_Y = 685


def black_to_transparent(img_rgb: Image.Image) -> Image.Image:
    arr = np.array(img_rgb.convert('RGB')).astype(np.float32)
    lum = arr.max(axis=2)
    alpha = np.clip((lum - 8) / 28 * 255, 0, 255).astype(np.uint8)
    rgba = np.dstack([arr.astype(np.uint8), alpha])
    return Image.fromarray(rgba, 'RGBA')


def extract_battle_frames():
    """Per ciascun frame: connected-component mask isola il soggetto
    (personaggio + glow quando presente), ancoraggio sui piedi, canvas uniforme."""
    src_im = Image.open(REF).convert('RGB')
    src_arr = np.array(src_im)
    src_w, src_h = src_im.size

    mask_full = src_arr.max(axis=2) > 18
    mask_full[LABEL_CUTOFF_Y:] = False
    labeled, _ = cc_label(mask_full)

    for k in range(6):
        slot_cx = SLOT_CX_AT(k)
        # Trova la componente principale (body) dentro lo slot
        roi = labeled[200:LABEL_CUTOFF_Y, max(0, slot_cx - 40):slot_cx + 40]
        best_cid, best_size = None, 0
        for cid in np.unique(roi):
            if cid == 0:
                continue
            sz = int((labeled == cid).sum())
            if sz > best_size:
                best_size = sz
                best_cid = cid
        if best_cid is None:
            print(f"  ERROR: no component for slot {k+1}")
            continue

        char_mask = (labeled == best_cid)

        # INCLUDI TUTTE le componenti che cadono ENTRO il bounding box dello slot
        # (indispensabile per il glow del PULSE PEAK, che potrebbe essere una
        # componente separata non connessa al corpo se gli spike sono staccati)
        slot_x0 = k * SRC_SLOT_W
        slot_x1 = (k + 1) * SRC_SLOT_W
        for cid in np.unique(labeled):
            if cid == 0 or cid == best_cid:
                continue
            comp = (labeled == cid)
            cys, cxs = np.where(comp)
            if cxs.size == 0:
                continue
            # Componente dentro o molto vicina allo slot (tolleranza ±30px)
            if cxs.min() >= slot_x0 - 30 and cxs.max() <= slot_x1 + 30:
                # include se ragionevolmente grande (evita rumore)
                if comp.sum() > 50:
                    char_mask = char_mask | comp

        # Feet anchor basato sulla componente principale (not glow extras)
        ys, xs = np.where(labeled == best_cid)
        ybot = int(ys.max())
        feet_rows = (labeled[max(0, ybot - 20):ybot + 1] == best_cid)
        fys, fxs = np.where(feet_rows)
        fx = int(fxs.mean()) if fxs.size else slot_cx
        fy = ybot

        # Isolated source
        isolated = np.zeros_like(src_arr)
        isolated[char_mask] = src_arr[char_mask]
        isolated_im = Image.fromarray(isolated, 'RGB')

        # Crop uniforme
        sx0 = fx - FEET_X_IN_CANVAS
        sx1 = fx + (CANVAS_W - FEET_X_IN_CANVAS)
        sy0 = fy - FEET_Y_IN_CANVAS
        sy1 = fy + (CANVAS_H - FEET_Y_IN_CANVAS)
        csx0 = max(0, sx0)
        csx1 = min(src_w, sx1)
        csy0 = max(0, sy0)
        csy1 = min(src_h, sy1)

        canvas = Image.new('RGB', (CANVAS_W, CANVAS_H), (0, 0, 0))
        paste_x = csx0 - sx0
        paste_y = csy0 - sy0
        canvas.paste(isolated_im.crop((csx0, csy0, csx1, csy1)), (paste_x, paste_y))

        rgba = black_to_transparent(canvas)
        frame_no = k + 1
        out = os.path.join(OUT_DIR, f'frame_{frame_no}.png')
        rgba.save(out, optimize=True)
        print(f"  frame_{frame_no}.png  {rgba.size}  anchor=(src {fx},{fy})  "
              f"body_size={best_size}  {os.path.getsize(out)} B")
    print("✓ 6 battle frames saved (masked, uniform canvas 420×420)")


def build_merged_reference():
    SLOT_W, SLOT_H = CANVAS_W, CANVAS_H
    GAP = 40
    LABEL_H = 70
    TITLE_H = 110
    cols = 6
    sheet_w = cols * SLOT_W + (cols + 1) * GAP
    sheet_h = TITLE_H + SLOT_H + LABEL_H + 30

    sheet = Image.new('RGB', (sheet_w, sheet_h), (0, 0, 0))
    draw = ImageDraw.Draw(sheet)

    def font(sz, bold=False):
        p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold \
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        return ImageFont.truetype(p, sz) if os.path.exists(p) else ImageFont.load_default()

    draw.text((GAP, 28),
              "GUARDIA FERREA — REFERENCE LOCKED (6 keyframe, canvas uniforme 420×420)",
              fill=(255, 215, 0), font=font(30, bold=True))
    draw.text((GAP, 70),
              "Greek Hoplite · skill difensiva · shield-focused pulse · source of truth",
              fill=(170, 170, 180), font=font(16))

    for i in range(6):
        fp = os.path.join(OUT_DIR, f'frame_{i+1}.png')
        frame = Image.open(fp).convert('RGBA')
        x = GAP + i * (SLOT_W + GAP)
        y = TITLE_H
        slot_bg = Image.new('RGBA', (SLOT_W, SLOT_H), (0, 0, 0, 255))
        slot_bg.alpha_composite(frame)
        sheet.paste(slot_bg.convert('RGB'), (x, y))
        label = LABELS[i]
        tw = draw.textlength(label, font=font(22, bold=True))
        draw.text((x + (SLOT_W - tw) // 2, y + SLOT_H + 18),
                  label, fill=(255, 255, 255), font=font(22, bold=True))

    locked = os.path.join(OUT_DIR, '_REFERENCE_LOCKED.png')
    sheet.save(locked, optimize=True)
    tmp = '/tmp/guardia_merged_reference.png'
    sheet.save(tmp, optimize=True)
    print(f"✓ merged sheet: {locked}  size={sheet.size}")


if __name__ == '__main__':
    extract_battle_frames()
    build_merged_reference()
