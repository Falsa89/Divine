"""
Taglia combat_base.png in 7 layer separati per il rig idle del Greek Hoplite.

Approccio:
- Per ogni pixel opaco del PNG sorgente, lo assegnamo a UN SOLO layer.
- Regole di assegnazione:
  1. Se il pixel è dentro la bbox di 'hair' E la bbox di un altro layer:
        - se il colore è "capelli" (rossastro) → va a hair
        - altrimenti → va al layer con priorità più alta tra i non-hair
  2. Altrimenti → layer con priorità più alta tra quelli che contengono il pixel.
- Pixel fuori da TUTTE le bbox → assegnato alla bbox più vicina (safety net).

Questo garantisce la ricomposizione pixel-perfect quando le transform sono azzerate.
Nessuna modifica al design, nessun ridisegno, solo redistribuzione pixel.
"""
from PIL import Image
import os

SRC = "/app/frontend/assets/heroes/greek_hoplite/combat_base.png"
RIG_DIR = "/app/frontend/assets/heroes/greek_hoplite/rig/"
PREVIEW_DIR = "/app/backend/scripts/hoplite_idle_preview/"
os.makedirs(RIG_DIR, exist_ok=True)
os.makedirs(PREVIEW_DIR, exist_ok=True)

im = Image.open(SRC).convert("RGBA")
W, H = im.size
px = im.load()

# Bounding box (x, y, w, h) — verificate visivamente con overlay
# Il personaggio è posizionato verso destra-centro (spear estesa a sinistra)
BBOX = {
    "hair":        (470, 55,  310, 360),   # pennacchio + capelli fluenti ✓
    "head_helmet": (505, 130, 230, 180),   # elmo + viso (ampliato verso basso e lati) ✓
    "torso":       (515, 225, 250, 320),   # petto + addome + cintura (ampliato)
    "spear_arm":   (0,   315, 610, 150),   # braccio sinistro + lancia intera ✓
    "shield_arm":  (680, 340, 345, 475),   # braccio destro + scudo rotondo (esteso fino al bordo)
    "skirt":       (490, 495, 345, 395),   # gonna completa con coda fluente
    "legs":        (520, 645, 340, 320),   # gambe + greave + sandali (esteso)
}

# Priorità: più alta = davanti (vince in overlap)
PRIORITY = {
    "head_helmet": 7,
    "spear_arm":   6,
    "shield_arm":  5,
    "torso":       4,
    "skirt":       3,
    "legs":        2,
    "hair":        1,
}

# Ordine di rendering (back → front) = priorità crescente
RENDER_ORDER = ["hair", "legs", "skirt", "torso", "shield_arm", "spear_arm", "head_helmet"]


def in_bbox(x: int, y: int, bbox) -> bool:
    bx, by, bw, bh = bbox
    return bx <= x < bx + bw and by <= y < by + bh


def is_hair_color(r: int, g: int, b: int) -> bool:
    """Rileva rosso/bruno di capelli/pennacchio. Distingue da oro, pelle e pelle in ombra."""
    if r < 60:
        return False
    if r > 245 and g > 245 and b > 245:
        return False
    if not (r > g and g > b):
        return False
    # pelle ha b alto (>135) o b/r alto (>0.58) anche in ombra
    if b > 135:
        return False
    br_ratio = b / max(1, r)
    if br_ratio >= 0.58:
        return False
    # oro elmo ha g molto vicino a r (r-g piccolo vs g-b grande).
    # capelli: r-g abbastanza grande rispetto a g-b
    rg = r - g
    gb = g - b
    return rg >= gb * 0.75 and rg >= 15


def is_skirt_cloth(r: int, g: int, b: int) -> bool:
    """Rileva il tessuto rosso-arancio della gonna. Distingue da pelle e bronzo dei sandali/greave."""
    if r < 50:
        return False
    if not (r > g and g >= b):
        return False
    # gonna satura: g/r basso (<0.55), b basso (<120)
    gr = g / max(1, r)
    if gr >= 0.55:
        return False  # oro/bronzo/pelle hanno g/r alto
    if b > 120:
        return False  # pelle ha b alto
    # saturazione alta (arancione acceso)
    return True


def dist_to_bbox(x: int, y: int, bbox) -> float:
    bx, by, bw, bh = bbox
    dx = max(bx - x, 0, x - (bx + bw - 1))
    dy = max(by - y, 0, y - (by + bh - 1))
    return (dx * dx + dy * dy) ** 0.5


def main():
    canvases = {n: Image.new("RGBA", (W, H), (0, 0, 0, 0)) for n in BBOX}
    canvas_px = {n: c.load() for n, c in canvases.items()}

    stats = {n: 0 for n in BBOX}
    lost = 0
    salvaged = 0

    for y in range(H):
        for x in range(W):
            r, g, b, a = px[x, y]
            if a == 0:
                continue

            candidates = [n for n, bb in BBOX.items() if in_bbox(x, y, bb)]

            if not candidates:
                # Safety net: assegna alla bbox più vicina
                nearest = min(BBOX.items(), key=lambda kv: dist_to_bbox(x, y, kv[1]))[0]
                canvas_px[nearest][x, y] = (r, g, b, a)
                stats[nearest] += 1
                salvaged += 1
                continue

            if "hair" in candidates and "head_helmet" in candidates:
                # Conflitto hair vs head_helmet: colore dominante decide
                if is_hair_color(r, g, b):
                    winner = "hair"
                else:
                    # Non-hair in zona testa → head_helmet (elmo/viso)
                    non_hair = [n for n in candidates if n != "hair"]
                    winner = max(non_hair, key=lambda n: PRIORITY[n])
            elif "hair" in candidates and len(candidates) > 1:
                # Altri overlap con hair: solo colore decide
                if is_hair_color(r, g, b):
                    winner = "hair"
                else:
                    non_hair = [n for n in candidates if n != "hair"]
                    winner = max(non_hair, key=lambda n: PRIORITY[n])
            elif "legs" in candidates and "skirt" in candidates:
                # Conflitto legs vs skirt: colore dominante decide
                if is_skirt_cloth(r, g, b):
                    winner = "skirt"
                else:
                    # Pelle/bronzo/sandalo → gambe
                    winner = "legs"
                    # se anche torso/shield_arm nell'overlap, mantieni priorità per quelli
                    other = [n for n in candidates if n not in ("legs", "skirt")]
                    if other:
                        top_other = max(other, key=lambda n: PRIORITY[n])
                        if PRIORITY[top_other] > PRIORITY["legs"]:
                            winner = top_other
            else:
                winner = max(candidates, key=lambda n: PRIORITY[n])

            canvas_px[winner][x, y] = (r, g, b, a)
            stats[winner] += 1

    # Salva
    for name, canv in canvases.items():
        path = os.path.join(RIG_DIR, f"{name}.png")
        canv.save(path, "PNG", optimize=True)
        print(f"[rig] {name}: {stats[name]:,} px → {path}")
    print(f"[rig] salvati (fuori bbox): {salvaged}")
    print(f"[rig] persi: {lost}")

    # ---- Verifica: ricompose i layer in ordine e confronta con originale ----
    recomposed = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for name in RENDER_ORDER:
        recomposed.alpha_composite(canvases[name])
    # diff
    from PIL import ImageChops
    diff = ImageChops.difference(im, recomposed)
    bbox_diff = diff.getbbox()
    print(f"[rig] bbox differenza con originale: {bbox_diff}")

    # Contact sheet dei layer per anteprima
    thumbs = []
    for name in RENDER_ORDER + ["head_helmet"]:  # skip duplicate — fix
        pass
    order_for_sheet = ["hair", "head_helmet", "torso", "spear_arm", "shield_arm", "skirt", "legs"]
    cols = 4
    rows = 2
    thumb_w, thumb_h = 300, 300
    sheet = Image.new("RGB", (cols * thumb_w + 20, rows * thumb_h + 60), (12, 14, 20))
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    except Exception:
        font = ImageFont.load_default()

    # Prima cella: originale
    orig_thumb = im.copy()
    orig_thumb.thumbnail((thumb_w - 20, thumb_h - 40))
    bg_o = Image.new("RGB", (thumb_w, thumb_h), (30, 40, 55))
    off_x = (thumb_w - orig_thumb.width) // 2
    off_y = 20
    bg_o.paste(orig_thumb, (off_x, off_y), mask=orig_thumb.split()[-1])
    sheet.paste(bg_o, (10, 10))
    draw.text((20, 15), "ORIGINAL", fill=(200, 220, 255), font=font)

    # Ricomposto
    rec_thumb = recomposed.copy()
    rec_thumb.thumbnail((thumb_w - 20, thumb_h - 40))
    bg_r = Image.new("RGB", (thumb_w, thumb_h), (30, 40, 55))
    off_x = (thumb_w - rec_thumb.width) // 2
    bg_r.paste(rec_thumb, (off_x, 20), mask=rec_thumb.split()[-1])
    sheet.paste(bg_r, (10 + thumb_w, 10))
    draw.text((20 + thumb_w, 15), "RECOMPOSED", fill=(180, 255, 200), font=font)

    # Ora i layer singoli a partire dalla posizione (2, 0) della griglia
    positions = [(2, 0), (3, 0), (0, 1), (1, 1), (2, 1), (3, 1), (0, 2)]
    # solo 4 colonne x 2 righe, la griglia è 2x4, quindi ridisegna: orig, recomposed, 7 layer → 9 totali → griglia 3x4
    # Rifaccio con 3 righe
    cols = 4
    rows = 3
    sheet = Image.new("RGB", (cols * thumb_w, rows * thumb_h), (12, 14, 20))
    draw = ImageDraw.Draw(sheet)

    cells = [("ORIGINAL", im), ("RECOMPOSED", recomposed)] + [(n, canvases[n]) for n in order_for_sheet]
    for i, (label, img) in enumerate(cells):
        col = i % cols
        row = i // cols
        px_x, py_y = col * thumb_w, row * thumb_h
        # cella con sfondo scuro
        cell = Image.new("RGB", (thumb_w, thumb_h), (30, 40, 55))
        thumb = img.copy()
        thumb.thumbnail((thumb_w - 30, thumb_h - 40))
        cx = (thumb_w - thumb.width) // 2
        cy = 30 + ((thumb_h - 40) - thumb.height) // 2
        cell.paste(thumb, (cx, cy), mask=thumb.split()[-1])
        sheet.paste(cell, (px_x, py_y))
        draw.text((px_x + 8, py_y + 6), label, fill=(200, 220, 255), font=font)

    sheet_path = os.path.join(PREVIEW_DIR, "rig_layers_contact.jpg")
    sheet.save(sheet_path, "JPEG", quality=85)
    print(f"[rig] contact sheet: {sheet_path}")


if __name__ == "__main__":
    main()
