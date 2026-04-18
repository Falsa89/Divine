"""
Genera 6 frame IDLE del Greek Hoplite usando mesh warping LOCALE con PIL.

Regole:
- Il personaggio resta IDENTICO a base.png (nessuna rigenerazione, nessun crop).
- Gambe e piedi (y >= 510) COMPLETAMENTE FISSI (anchor).
- Movimento LOCALE sottile:
    * Petto/torso: espansione verticale per il respiro (sin wave).
    * Testa/capelli: sway orizzontale leggero (sin wave, fase shiftata).
    * Braccio/scudo (destra): micro-oscillazione ridotta, per non alterare la forma.
- Output: 6 PNG RGBA in /app/frontend/assets/heroes/greek_hoplite/idle/idle_0N.png
"""
from PIL import Image
import math
import os

BASE_PATH = "/app/frontend/assets/heroes/greek_hoplite/base.png"
OUT_DIR = "/app/frontend/assets/heroes/greek_hoplite/idle"
PREVIEW_DIR = "/app/backend/scripts/hoplite_idle_preview"
NUM_FRAMES = 6

# Parametri di warping (pixel)
MAX_BREATH_RISE = 3.0      # quanto si alza al massimo il torace/testa
HAIR_SWAY_AMP = 2.0        # ampiezza sway orizzontale capelli
SHIELD_SWAY_AMP = 1.2      # ampiezza micro-sway scudo (bassa per mantenerlo centrato)

# Anchor (gambe/piedi FISSI sotto questa y)
ANCHOR_Y = 510

# Regioni del personaggio (dall'analisi dell'immagine)
HEAD_TOP = 0
HEAD_BOTTOM = 200       # fine capelli/elmo
SHIELD_X_START = 420    # scudo a destra
SHIELD_Y_TOP = 270
SHIELD_Y_BOTTOM = 720

# Risoluzione mesh (più fine = warping più liscio)
NX = 24
NY = 48


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    """Smoothstep interpolation per transizioni morbide."""
    if edge1 == edge0:
        return 0.0
    t = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
    return t * t * (3 - 2 * t)


def displacement_at(x: float, y: float, breath: float, hair_sway: float, shield_sway: float):
    """
    Ritorna (dx, dy) = offset di sampling.
    In output il pixel a (x,y) viene preso da source (x-dx, y-dy).
    """
    # Gambe e piedi: ZERO movimento
    if y >= ANCHOR_Y:
        return 0.0, 0.0

    # ---- Respiro verticale ----
    # Fattore che cresce allontanandosi dall'anchor (0 all'anchor, 1 in cima)
    t_vert = (ANCHOR_Y - y) / ANCHOR_Y
    # Smorzamento dolce nella zona del bacino (490..510) per non creare strappi
    fade_legs = smoothstep(490, 510, y)  # 0 sopra 490, 1 sotto 510
    t_vert *= (1.0 - fade_legs)
    # breath in [-1, 1]. Negativo = sale, positivo = scende.
    dy = -MAX_BREATH_RISE * breath * t_vert

    # ---- Hair sway orizzontale ----
    # Solo nella zona testa (0..HEAD_BOTTOM), decresce verso il basso
    dx = 0.0
    if y < HEAD_BOTTOM + 30:
        head_factor = 1.0 - smoothstep(HEAD_BOTTOM - 60, HEAD_BOTTOM + 30, y)
        # I capelli laterali oscillano di più di quelli centrali:
        # enfatizza ai bordi della testa
        center_x = 320
        horiz_distance = abs(x - center_x) / 180.0
        horiz_distance = min(1.0, horiz_distance)
        dx += hair_sway * head_factor * (0.4 + 0.6 * horiz_distance)

    # ---- Scudo/braccio destro micro-sway ----
    # Solo nell'area x > SHIELD_X_START e y tra 270 e 720
    if x > SHIELD_X_START and SHIELD_Y_TOP < y < SHIELD_Y_BOTTOM:
        # fade ai bordi della zona scudo per evitare strappi
        fade_top = smoothstep(SHIELD_Y_TOP, SHIELD_Y_TOP + 50, y)
        fade_bottom = 1.0 - smoothstep(SHIELD_Y_BOTTOM - 80, SHIELD_Y_BOTTOM, y)
        fade_left = smoothstep(SHIELD_X_START, SHIELD_X_START + 40, x)
        arm_factor = fade_top * fade_bottom * fade_left

        # micro oscillazione verticale (accompagna il respiro) + orizzontale ridotta
        dy += shield_sway * arm_factor * 0.6
        dx += shield_sway * arm_factor * 0.25

    return dx, dy


def build_mesh(w: int, h: int, breath: float, hair_sway: float, shield_sway: float):
    """Costruisce una mesh NX x NY con displacement locale."""
    # Precompute vertices
    verts = {}
    for i in range(NX + 1):
        for j in range(NY + 1):
            x = i * w / NX
            y = j * h / NY
            dx, dy = displacement_at(x, y, breath, hair_sway, shield_sway)
            verts[(i, j)] = (x, y, dx, dy)

    mesh = []
    for i in range(NX):
        for j in range(NY):
            x0 = int(round(i * w / NX))
            y0 = int(round(j * h / NY))
            x1 = int(round((i + 1) * w / NX))
            y1 = int(round((j + 1) * h / NY))
            target = (x0, y0, x1, y1)

            tl = verts[(i, j)]
            bl = verts[(i, j + 1)]
            br = verts[(i + 1, j + 1)]
            tr = verts[(i + 1, j)]

            # Source quad: 4 angoli (tl, bl, br, tr), 8 valori
            source_quad = (
                tl[0] - tl[2], tl[1] - tl[3],
                bl[0] - bl[2], bl[1] - bl[3],
                br[0] - br[2], br[1] - br[3],
                tr[0] - tr[2], tr[1] - tr[3],
            )
            mesh.append((target, source_quad))
    return mesh


def generate_frame(img: Image.Image, phase: float) -> Image.Image:
    """phase in [0, 1). Ciclo di respiro completo."""
    theta = phase * 2 * math.pi
    breath = math.sin(theta)                         # respiro principale
    hair_sway = math.sin(theta + math.pi / 3)        # fase shiftata per i capelli
    shield_sway = math.sin(theta - math.pi / 4)      # fase ancora diversa per lo scudo

    mesh = build_mesh(img.width, img.height, breath, hair_sway, shield_sway)
    # BILINEAR per un warping liscio e preserva alpha
    out = img.transform(img.size, Image.MESH, mesh, Image.BILINEAR)
    return out


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(PREVIEW_DIR, exist_ok=True)

    base = Image.open(BASE_PATH).convert("RGBA")
    print(f"[hoplite-idle] Base caricata: {base.size}, mode={base.mode}")

    for i in range(NUM_FRAMES):
        phase = i / NUM_FRAMES
        frame = generate_frame(base, phase)

        out_path = os.path.join(OUT_DIR, f"idle_{i + 1:02d}.png")
        frame.save(out_path, "PNG", optimize=True)
        print(f"[hoplite-idle] Generato {out_path}")

        # preview jpg piccola per caricamento veloce nella chat
        preview = frame.copy()
        preview.thumbnail((340, 512))
        # appiattiamo su sfondo scuro per vedere contorni
        bg = Image.new("RGB", preview.size, (22, 24, 33))
        bg.paste(preview, mask=preview.split()[-1])
        bg.save(os.path.join(PREVIEW_DIR, f"idle_{i + 1:02d}.jpg"), "JPEG", quality=80)

    print("[hoplite-idle] Fatto. 6 frame generati.")


if __name__ == "__main__":
    main()
