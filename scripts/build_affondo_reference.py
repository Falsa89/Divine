"""
Extract the 8 approved keyframes from the 2 reference images.
================================================================
v2 (post-bug-fix): usa canvas UNIFORME 520×400 con ancoraggio sui piedi
(feet anchor) per garantire che nessun elemento del personaggio (spalla,
scudo, punta lancia, gonna, elmo) venga tagliato in nessun frame.

Audit real:
  - max estensione SX dai piedi: 177px  (frame 4 RETR, ref1)
  - max estensione DX dai piedi: 249px  (frame 5 AFFONDO PEAK, spear tip)
  - max estensione SOPRA dai piedi: 341px (ref1)
  - baseline piedi: y≈640-642 in entrambe le ref
  - label band sorgente: y≥660 (cut a y=640 lascia 0 label)

Canvas 520×400 con piedi ancorati a (260, 390) copre:
  - 260px dai piedi a sx  (>177 ✓) + 60px margine
  - 260px dai piedi a dx  (>249 ✓) + 11px margine
  - 390px sopra i piedi   (>341 ✓) + 49px margine (sopra la testa)
  - 10px sotto i piedi     (ombra/suolo)
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import label as cc_label

REF1 = '/tmp/ref_01_frames_1-4.png'
REF2 = '/tmp/ref_02_frames_5-8.png'
OUT_DIR = '/app/frontend/assets/heroes/greek_hoplite/affondo'
os.makedirs(OUT_DIR, exist_ok=True)

LABELS = [
    "1. IDLE", "2. PRE-LOAD", "3. RITRAZIONE", "4. AFFONDO MID",
    "5. AFFONDO PEAK", "6. IMPACT HOLD", "7. RETURN MID", "8. IDLE FINALE",
]

# Canvas uniforme (safe margins inclusi)
CANVAS_W = 520
CANVAS_H = 400
FEET_X_IN_CANVAS = CANVAS_W // 2       # 260
FEET_Y_IN_CANVAS = CANVAS_H - 10        # 390 (10px sotto i piedi per ombra)

SRC_SLOT_W = 384
SLOT_CX_AT = lambda k: k * SRC_SLOT_W + SRC_SLOT_W // 2

# Taglio superiore ai label band del sorgente (labels a y≥660)
LABEL_CUTOFF_Y = 655


def black_to_transparent(img_rgb: Image.Image) -> Image.Image:
    arr = np.array(img_rgb.convert('RGB')).astype(np.float32)
    lum = arr.max(axis=2)
    alpha = np.clip((lum - 8) / 28 * 255, 0, 255).astype(np.uint8)
    rgba = np.dstack([arr.astype(np.uint8), alpha])
    return Image.fromarray(rgba, 'RGBA')


def find_feet_anchor(src_rgb: np.ndarray, slot_k: int):
    """Ritorna (feet_cx, feet_y) assoluti nel source per il frame dello slot_k.
    Usa connected-component analysis, restringendo al main body centrato sullo
    slot, e trova il bottom-centroid."""
    mask = src_rgb.max(axis=2) > 18
    # escludi label band
    mask[LABEL_CUTOFF_Y:] = False
    labeled, _ = cc_label(mask)
    slot_cx = SLOT_CX_AT(slot_k)
    roi = labeled[300:LABEL_CUTOFF_Y, max(0, slot_cx - 40):slot_cx + 40]
    best_cid, best_size = None, 0
    for cid in np.unique(roi):
        if cid == 0:
            continue
        sz = int((labeled == cid).sum())
        if sz > best_size:
            best_size = sz
            best_cid = cid
    if best_cid is None:
        return None
    comp = (labeled == best_cid)
    ys, xs = np.where(comp)
    ybot = int(ys.max())
    feet_rows = comp[max(0, ybot - 20):ybot + 1]
    fys, fxs = np.where(feet_rows)
    fx = int(fxs.mean()) if fxs.size else slot_cx
    return fx, ybot


def extract_battle_frames():
    """Estrae 8 frame uniformi 520×400 RGBA con piedi ancorati in (260, 390).
    MASK STEP: per ciascun frame estrae SOLO la connected component principale
    (il personaggio) → rimuove il bleed dalle lance dei frame adiacenti."""
    for ref_idx, src_path in enumerate([REF1, REF2]):
        src_im = Image.open(src_path).convert('RGB')
        src_arr = np.array(src_im)
        src_w, src_h = src_im.size

        # Maschere di CC per ciascun frame (identifica la componente principale)
        mask_full = src_arr.max(axis=2) > 18
        mask_full[LABEL_CUTOFF_Y:] = False  # esclude label band
        labeled, _ = cc_label(mask_full)

        for k in range(4):
            # Trova la componente principale dello slot k
            slot_cx = SLOT_CX_AT(k)
            roi = labeled[300:LABEL_CUTOFF_Y, max(0, slot_cx - 40):slot_cx + 40]
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

            # Feet anchor (uguale a prima)
            ys, xs = np.where(char_mask)
            ybot = int(ys.max())
            feet_rows = char_mask[max(0, ybot - 20):ybot + 1]
            fys, fxs = np.where(feet_rows)
            fx = int(fxs.mean()) if fxs.size else slot_cx
            fy = ybot

            # ISOLATED source: copia source solo per pixel in char_mask, resto nero
            isolated = np.zeros_like(src_arr)
            isolated[char_mask] = src_arr[char_mask]
            isolated_im = Image.fromarray(isolated, 'RGB')

            # Crop uniform 520×400 ancorato ai piedi
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
            frame_no = ref_idx * 4 + k + 1
            out = os.path.join(OUT_DIR, f'frame_{frame_no}.png')
            rgba.save(out, optimize=True)
            print(f"  frame_{frame_no}.png  {rgba.size}  anchor=(src {fx},{fy})  "
                  f"comp_size={best_size}  {os.path.getsize(out)} B")
    print("✓ 8 battle frames saved (masked, uniform canvas, feet-anchored)")


def build_merged_reference():
    """Contact sheet finale mergiata: usa gli 8 frame appena estratti
    (520×400 con alpha) ricomposti su sfondo nero con etichette.
    Source of truth immutabile."""
    # Layout sheet
    SLOT_W, SLOT_H = CANVAS_W, CANVAS_H
    GAP = 40
    LABEL_H = 70
    TITLE_H = 110
    cols = 8
    sheet_w = cols * SLOT_W + (cols + 1) * GAP
    sheet_h = TITLE_H + SLOT_H + LABEL_H + 30

    sheet = Image.new('RGB', (sheet_w, sheet_h), (0, 0, 0))
    draw = ImageDraw.Draw(sheet)

    def font(sz, bold=False):
        p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold \
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        return ImageFont.truetype(p, sz) if os.path.exists(p) else ImageFont.load_default()

    # Title band
    draw.text((GAP, 28),
              "AFFONDO DI FALANGE — REFERENCE LOCKED (8 keyframe, canvas uniforme 520×400)",
              fill=(255, 215, 0), font=font(30, bold=True))
    draw.text((GAP, 70),
              "Greek Hoplite · source of truth · feet-anchored · no clipping · do not modify",
              fill=(170, 170, 180), font=font(16))

    # Paste i frame estratti (RGBA → blit su sfondo nero)
    for i in range(8):
        fp = os.path.join(OUT_DIR, f'frame_{i+1}.png')
        frame = Image.open(fp).convert('RGBA')
        x = GAP + i * (SLOT_W + GAP)
        y = TITLE_H
        # Blend su un slot nero di sfondo
        slot_bg = Image.new('RGBA', (SLOT_W, SLOT_H), (0, 0, 0, 255))
        slot_bg.alpha_composite(frame)
        sheet.paste(slot_bg.convert('RGB'), (x, y))

        # Label
        label = LABELS[i]
        tw = draw.textlength(label, font=font(22, bold=True))
        lx = x + (SLOT_W - tw) // 2
        ly = y + SLOT_H + 18
        draw.text((lx, ly), label, fill=(255, 255, 255), font=font(22, bold=True))

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
