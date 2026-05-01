"""
RM1.17-N — Normalizzazione Sprite Sheet Berserker
Source of truth: frame count ufficiale fornito dal Game Director.
Detection automatica usata SOLO come controllo di coerenza.
"""
import os
import sys
import json
import hashlib
from PIL import Image

# =============================================================================
# CONFIG UFFICIALE (fornita dal Game Director - source of truth)
# =============================================================================
STATES = {
    "idle": {
        "file": "idle_source.png",
        "frames": 6, "rows": 1, "cols": 6, "layout": "row",
        "fps": 8, "loop": True,
    },
    "attack": {
        "file": "attack_source.png",
        "frames": 5, "rows": 1, "cols": 5, "layout": "row",
        "fps": 12, "loop": False,
    },
    "skill": {
        "file": "skill_source.png",
        "frames": 9, "rows": 2, "cols": 5, "layout": "5plus4",
        "fps": 12, "loop": False,
    },
    "hit": {
        "file": "hit_source.png",
        "frames": 5, "rows": 1, "cols": 5, "layout": "row",
        "fps": 10, "loop": False,
    },
    "death": {
        "file": "death_source.png",
        "frames": 6, "rows": 1, "cols": 6, "layout": "row",
        "fps": 8, "loop": False,
    },
}

ROOT = "/app/frontend/assets/heroes/norse_berserker"
SRC_DIR = os.path.join(ROOT, "source_sheets")
RUN_DIR = os.path.join(ROOT, "runtime")
os.makedirs(RUN_DIR, exist_ok=True)

PADDING_SAFETY = 24  # px di sicurezza intorno al bounding box massimo
CELL_SIZE_CANDIDATES = [512, 640, 768]
FEET_BOTTOM_MARGIN = 16  # distanza dei piedi dal bordo inferiore della cella


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_frames(img: Image.Image, cfg: dict) -> list:
    """Estrae i frame in base al layout ufficiale."""
    W, H = img.size
    frames = []
    layout = cfg["layout"]

    if layout == "row":
        n = cfg["frames"]
        cell_w = W / n
        cell_h = H
        for i in range(n):
            x0 = round(i * cell_w)
            x1 = round((i + 1) * cell_w)
            frames.append(img.crop((x0, 0, x1, cell_h)))
    elif layout == "5plus4":
        # 5 frame top row + 4 frame bottom row, grid 5 colonne 2 righe
        cell_w = W / 5
        cell_h = H / 2
        # top row (5)
        for i in range(5):
            x0 = round(i * cell_w)
            x1 = round((i + 1) * cell_w)
            frames.append(img.crop((x0, 0, x1, round(cell_h))))
        # bottom row (4)
        for i in range(4):
            x0 = round(i * cell_w)
            x1 = round((i + 1) * cell_w)
            frames.append(img.crop((x0, round(cell_h), x1, H)))
    else:
        raise ValueError(f"Layout non supportato: {layout}")

    assert len(frames) == cfg["frames"], \
        f"Frame estratti {len(frames)} != atteso {cfg['frames']}"
    return frames


def alpha_bbox(frame: Image.Image):
    """Bounding box dei pixel non trasparenti."""
    if frame.mode != "RGBA":
        frame = frame.convert("RGBA")
    alpha = frame.split()[-1]
    return alpha.getbbox()


def detect_content_columns(img: Image.Image, threshold: int = 8):
    """Detection di coerenza: conta 'blob' di colonne con contenuto."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    alpha = img.split()[-1]
    W, H = img.size
    col_has_content = []
    px = alpha.load()
    for x in range(W):
        has = False
        for y in range(0, H, 4):  # stride 4 per velocità
            if px[x, y] > threshold:
                has = True
                break
        col_has_content.append(has)

    # conta transizioni vuoto -> pieno (= numero di blob)
    blobs = 0
    in_blob = False
    for c in col_has_content:
        if c and not in_blob:
            blobs += 1
            in_blob = True
        elif not c:
            in_blob = False
    return blobs


def main():
    print("=" * 70)
    print("RM1.17-N — NORMALIZZAZIONE SPRITE SHEET BERSERKER")
    print("=" * 70)

    # ---------- FASE 1: AUDIT SOURCE ----------
    print("\n[FASE 1] SOURCE AUDIT")
    print("-" * 70)
    source_data = {}
    for state, cfg in STATES.items():
        path = os.path.join(SRC_DIR, cfg["file"])
        if not os.path.isfile(path):
            print(f"  ❌ MISSING: {path}")
            sys.exit(1)
        img = Image.open(path).convert("RGBA")
        W, H = img.size
        sha = sha256_file(path)
        source_data[state] = {"path": path, "img": img, "W": W, "H": H, "sha": sha}
        print(f"  {state:>6}  {W}×{H}  sha256={sha[:16]}...  file={cfg['file']}")

    # ---------- FASE 2: COERENZA DETECTION vs UFFICIALE ----------
    print("\n[FASE 2] COHERENCE CHECK (detection SOLO per warning)")
    print("-" * 70)
    coherence_report = {}
    for state, cfg in STATES.items():
        img = source_data[state]["img"]
        if cfg["layout"] == "5plus4":
            # dividi a metà verticalmente e conta su riga superiore (5 attesi)
            H = img.size[1]
            top = img.crop((0, 0, img.size[0], H // 2))
            bot = img.crop((0, H // 2, img.size[0], H))
            det_top = detect_content_columns(top)
            det_bot = detect_content_columns(bot)
            expected = f"top=5,bot=4"
            detected = f"top={det_top},bot={det_bot}"
            ok = (det_top == 5 and det_bot == 4)
        else:
            det = detect_content_columns(img)
            expected = str(cfg["frames"])
            detected = str(det)
            ok = (det == cfg["frames"])
        mark = "✅" if ok else "⚠️"
        coherence_report[state] = {"expected": expected, "detected": detected, "ok": ok}
        print(f"  {mark} {state:>6}  atteso={expected:>12}  rilevato={detected:>12}")

    # Nota: se detection diverge, si stampa warning ma si prosegue con config ufficiale
    any_warn = any(not v["ok"] for v in coherence_report.values())
    if any_warn:
        print("\n  ⚠️ Alcuni stati hanno detection diversa. Procedo comunque con config ufficiale.")

    # ---------- FASE 3: ESTRAZIONE FRAME + TRIM ----------
    print("\n[FASE 3] ESTRAZIONE FRAME + ALPHA TRIM")
    print("-" * 70)
    state_frames = {}  # state -> list of (trimmed_frame_img, bbox_w, bbox_h)
    global_max_w = 0
    global_max_h = 0
    for state, cfg in STATES.items():
        img = source_data[state]["img"]
        frames = extract_frames(img, cfg)
        trimmed = []
        max_w = max_h = 0
        for i, f in enumerate(frames):
            bbox = alpha_bbox(f)
            if bbox is None:
                print(f"  ❌ Frame {state}#{i} completamente trasparente!")
                sys.exit(1)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            max_w = max(max_w, tw)
            max_h = max(max_h, th)
            trimmed.append({
                "img": f,         # frame raw (non ancora croppato)
                "bbox": bbox,     # bbox dei pixel opachi nel frame raw
                "w": tw, "h": th
            })
        state_frames[state] = trimmed
        global_max_w = max(global_max_w, max_w)
        global_max_h = max(global_max_h, max_h)
        print(f"  {state:>6}  frames={len(trimmed)}  max_bbox={max_w}×{max_h}")

    print(f"\n  GLOBAL max bbox = {global_max_w}×{global_max_h}")

    # ---------- FASE 4: SCELTA CELL SIZE UNIFORME ----------
    print("\n[FASE 4] SCELTA CELL SIZE UNIFORME")
    print("-" * 70)
    required_side = max(global_max_w, global_max_h) + PADDING_SAFETY * 2
    print(f"  Required side (max bbox + 2×padding) = {required_side}px")

    cell_size = None
    for candidate in CELL_SIZE_CANDIDATES:
        if required_side <= candidate:
            cell_size = candidate
            break
    if cell_size is None:
        print(f"\n  🛑 STOP: required_side={required_side}px > max consentito 768px")
        print("  Serve revisione artistica dei source. Non procedo.")
        sys.exit(2)
    print(f"  ✅ Cell size scelta: {cell_size}×{cell_size} (uniforme per tutti gli stati)")

    # ---------- FASE 5: REPACKING IN CELLE UNIFORMI ----------
    print("\n[FASE 5] REPACKING (center H, feet-anchor bottom)")
    print("-" * 70)
    runtime_files = {}
    preview_tiles = []  # per preview composita

    for state, cfg in STATES.items():
        trimmed = state_frames[state]
        n = len(trimmed)
        sheet_w = cell_size * n
        sheet_h = cell_size
        sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
        for i, t in enumerate(trimmed):
            # ritaglia il frame raw al suo bbox
            cropped = t["img"].crop(t["bbox"])
            cw, ch = cropped.size
            # posizione: centrato orizzontalmente, feet-anchor bottom
            x = i * cell_size + (cell_size - cw) // 2
            y = cell_size - ch - FEET_BOTTOM_MARGIN
            # clamp Y se ch + margin > cell_size (non dovrebbe mai succedere)
            if y < 0:
                y = 0
            sheet.paste(cropped, (x, y), cropped)

        out_path = os.path.join(RUN_DIR, f"{state}_sheet.png")
        sheet.save(out_path, "PNG", optimize=True)
        sha = sha256_file(out_path)
        runtime_files[state] = {
            "path": out_path,
            "relative": f"runtime/{state}_sheet.png",
            "width": sheet_w,
            "height": sheet_h,
            "frameWidth": cell_size,
            "frameHeight": cell_size,
            "frames": n,
            "columns": n,
            "fps": cfg["fps"],
            "loop": cfg["loop"],
            "sha256": sha,
        }
        print(f"  ✅ {state:>6}  {sheet_w}×{sheet_h}  frames={n}  sha256={sha[:16]}...")

        # costruisci tile preview (prima frame di ogni stato)
        first_frame = sheet.crop((0, 0, cell_size, cell_size))
        preview_tiles.append((state, first_frame))

    # ---------- FASE 6: PREVIEW SHEET COMPOSITA ----------
    print("\n[FASE 6] PREVIEW SHEET (primo frame di ogni stato)")
    print("-" * 70)
    preview_w = cell_size * len(preview_tiles)
    preview_h = cell_size
    preview = Image.new("RGBA", (preview_w, preview_h), (32, 32, 40, 255))
    for i, (state, tile) in enumerate(preview_tiles):
        preview.paste(tile, (i * cell_size, 0), tile)
    preview_path = os.path.join(RUN_DIR, "_preview_all_states.png")
    preview.save(preview_path, "PNG", optimize=True)
    preview_sha = sha256_file(preview_path)
    print(f"  ✅ preview = {preview_w}×{preview_h}  path={preview_path}")
    print(f"     sha256 = {preview_sha[:32]}...")

    # ---------- FASE 7: GENERA battle_animations.json ----------
    print("\n[FASE 7] battle_animations.json")
    print("-" * 70)
    animations_json = {
        "hero_id": "norse_berserker",
        "version": 1,
        "cell_size": cell_size,
        "padding_safety": PADDING_SAFETY,
        "feet_bottom_margin": FEET_BOTTOM_MARGIN,
        "states": {},
    }
    for state, rt in runtime_files.items():
        animations_json["states"][state] = {
            "sheet": rt["relative"],
            "frameWidth": rt["frameWidth"],
            "frameHeight": rt["frameHeight"],
            "frames": rt["frames"],
            "columns": rt["columns"],
            "fps": rt["fps"],
            "loop": rt["loop"],
            "sha256": rt["sha256"],
        }
    anim_path = os.path.join(RUN_DIR, "battle_animations.json")
    with open(anim_path, "w") as f:
        json.dump(animations_json, f, indent=2)
    print(f"  ✅ {anim_path}")

    # ---------- REPORT FINALE ----------
    print("\n" + "=" * 70)
    print("REPORT FINALE RM1.17-N")
    print("=" * 70)
    report = {
        "source_audit": {
            state: {
                "file": STATES[state]["file"],
                "size": f"{source_data[state]['W']}x{source_data[state]['H']}",
                "sha256": source_data[state]["sha"],
            } for state in STATES
        },
        "coherence_check": coherence_report,
        "cell_size_decision": {
            "required_side": required_side,
            "chosen": cell_size,
            "candidates_tried": CELL_SIZE_CANDIDATES,
        },
        "runtime_files": {
            state: {
                "path": rt["relative"],
                "dimensions": f"{rt['width']}x{rt['height']}",
                "frameWidth": rt["frameWidth"],
                "frameHeight": rt["frameHeight"],
                "frames": rt["frames"],
                "fps": rt["fps"],
                "loop": rt["loop"],
                "sha256": rt["sha256"],
            } for state, rt in runtime_files.items()
        },
        "preview_sheet": {
            "path": preview_path,
            "dimensions": f"{preview_w}x{preview_h}",
            "sha256": preview_sha,
        },
        "animations_json": anim_path,
    }
    report_path = os.path.join(RUN_DIR, "_normalization_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  Report JSON salvato in: {report_path}")
    print("\n✅ RM1.17-N normalizzazione completata.")


if __name__ == "__main__":
    main()
