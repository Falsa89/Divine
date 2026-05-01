"""
RM1.17-N-RETRY — Import final corrected Berserker battle sheets.

ANTI-DRIFT PACKING POLICY (utente):
  - NO alpha bbox per-frame + recenter (VFX/fuoco muovono il body root)
  - Source cells prese come-sono, intere
  - Scala uniforme globale (stessa scala per tutti i frame di tutti gli stati)
  - Bottom-anchor + center orizzontale sulla cella runtime
  - Preserva positioning manuale dei source (già visivamente approvati)

Source cells:
  idle   2048×853  6 row  → cell 341.33×853
  attack 2048×573  5 row  → cell 409.6×573
  skill  2000×1000 5×2    → cell 400×500
  hit    2000×1000 5 row  → cell 400×1000
  death  2000×1000 6 row  → cell 333.33×1000

Target runtime cell: 640×768.
"""
import os, sys, json, hashlib
from PIL import Image, ImageDraw

ROOT = "/app/frontend/assets/heroes/norse_berserker"
SRC = os.path.join(ROOT, "source_sheets")
RUN = os.path.join(ROOT, "runtime")
os.makedirs(RUN, exist_ok=True)

# Config layout ufficiale
STATES = {
    "idle":   {"file": "idle_source.png",   "frames": 6, "cols": 6, "rows": 1, "layout": "row",       "fps": 8,  "loop": True},
    "attack": {"file": "attack_source.png", "frames": 5, "cols": 5, "rows": 1, "layout": "row",       "fps": 12, "loop": False},
    # v4: 5×2 grid uniforme (NON 5+4). Prime 9 celle sono frame visibili, 10ª
    # (r1c4) è padding trasparente non animato — "frames must remain 9".
    "skill":  {"file": "skill_source.png",  "frames": 9, "cols": 5, "rows": 2, "layout": "5x2_take9", "fps": 12, "loop": False},
    "hit":    {"file": "hit_source.png",    "frames": 5, "cols": 5, "rows": 1, "layout": "row",       "fps": 10, "loop": False},
    "death":  {"file": "death_source.png",  "frames": 6, "cols": 6, "rows": 1, "layout": "row",       "fps": 8,  "loop": False},
}

# Target runtime cell size (uniform per tutti gli stati)
TARGET_W = 640
TARGET_H = 768
# Padding safety orizzontale (evita clipping di weapon/VFX che uscirebbe lateralmente)
SIDE_PAD = 0  # il bottom-anchor + center horizontal gestisce tutto


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def source_cell_size(img_size, cfg):
    """Ritorna (cell_w, cell_h) float in pixel del source SENZA trim."""
    W, H = img_size
    if cfg["layout"] == "row":
        return W / cfg["frames"], H
    elif cfg["layout"] == "5plus4":
        return W / 5, H / 2
    elif cfg["layout"] == "5x2_take9":
        # Grid 5×2 uniforme; prendiamo 9 celle (la 10ª è padding vuoto).
        return W / 5, H / 2
    raise ValueError(cfg["layout"])


def extract_cells_raw(img, cfg):
    """Estrae le celle uniformi dal source SENZA alpha trim.
    Ritorna lista di (pil_image, index)."""
    W, H = img.size
    out = []
    if cfg["layout"] == "row":
        cw = W / cfg["frames"]
        for i in range(cfg["frames"]):
            x0 = int(round(i * cw))
            x1 = int(round((i + 1) * cw))
            cell = img.crop((x0, 0, x1, H))
            out.append(cell)
    elif cfg["layout"] == "5plus4":
        cw = W / 5
        ch = H / 2
        # top 5
        for i in range(5):
            x0 = int(round(i * cw)); x1 = int(round((i + 1) * cw))
            out.append(img.crop((x0, 0, x1, int(round(ch)))))
        # bot 4 (cell = W/4)
        cw_bot = W / 4
        for i in range(4):
            x0 = int(round(i * cw_bot)); x1 = int(round((i + 1) * cw_bot))
            out.append(img.crop((x0, int(round(ch)), x1, H)))
    elif cfg["layout"] == "5x2_take9":
        # 5×2 grid uniforme; prendiamo r0c0..r0c4 + r1c0..r1c3 (9 frame).
        # La cella r1c4 è padding trasparente non animato.
        cw = W / 5
        ch = H / 2
        # top 5
        for i in range(5):
            x0 = int(round(i * cw)); x1 = int(round((i + 1) * cw))
            out.append(img.crop((x0, 0, x1, int(round(ch)))))
        # bot 4 (SOLO i primi 4 della 5×2 grid)
        for i in range(4):
            x0 = int(round(i * cw)); x1 = int(round((i + 1) * cw))
            out.append(img.crop((x0, int(round(ch)), x1, H)))
    return out


def choose_global_scale(source_sizes, target_w, target_h):
    """
    Scala uniforme globale che permette a OGNI cella source di entrare in
    (target_w, target_h) mantenendo aspect ratio.
    scale = min_over_all_cells( min(tw/w, th/h) )
    """
    scales = []
    for (sw, sh) in source_sizes:
        s = min(target_w / sw, target_h / sh)
        scales.append(s)
    return min(scales)


def main():
    print("=" * 72)
    print("RM1.17-N-RETRY — ANTI-DRIFT REPACK")
    print("=" * 72)

    # 1) Load tutti i source e le cell size
    state_data = {}
    cell_sizes = []
    print("\n[1] SOURCE AUDIT")
    for state, cfg in STATES.items():
        p = os.path.join(SRC, cfg["file"])
        if not os.path.isfile(p):
            print(f"  ❌ MISSING: {p}")
            sys.exit(1)
        img = Image.open(p).convert("RGBA")
        sha = sha256_file(p)
        cw, ch = source_cell_size(img.size, cfg)
        cell_sizes.append((cw, ch))
        state_data[state] = {
            "img": img, "sha": sha, "path": p,
            "cell_w": cw, "cell_h": ch, "cfg": cfg,
        }
        print(f"  {state:>6}  {img.size[0]}×{img.size[1]}  cell {cw:.1f}×{ch:.1f}  sha={sha[:16]}...")

    # 2) Scala uniforme globale
    global_scale = choose_global_scale(cell_sizes, TARGET_W, TARGET_H)
    print(f"\n[2] GLOBAL SCALE (uniform for ALL states): {global_scale:.4f}")
    for state, d in state_data.items():
        sw_s = d["cell_w"] * global_scale
        sh_s = d["cell_h"] * global_scale
        print(f"  {state}: scaled cell → {sw_s:.1f}×{sh_s:.1f} (fits {TARGET_W}×{TARGET_H}? "
              f"{sw_s <= TARGET_W and sh_s <= TARGET_H})")
        if sw_s > TARGET_W or sh_s > TARGET_H:
            print(f"  🛑 STOP: {state} scaled cell non entra in target.")
            sys.exit(2)

    # 3) Extract cells + scala + paste con bottom anchor + center horizontal
    print(f"\n[3] REPACK (scale={global_scale:.4f}, anti-drift: NO per-frame bbox)")
    runtime_files = {}
    first_frames = []
    for state, d in state_data.items():
        cfg = d["cfg"]
        cells = extract_cells_raw(d["img"], cfg)
        n = cfg["frames"]
        cols = cfg["cols"]
        rows = cfg["rows"]
        sheet_w = cols * TARGET_W
        sheet_h = rows * TARGET_H
        sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))

        for idx, cell in enumerate(cells):
            # scala la cella source con scala globale (NO per-frame adjust)
            sw_s = int(round(cell.size[0] * global_scale))
            sh_s = int(round(cell.size[1] * global_scale))
            if sw_s < 1 or sh_s < 1:
                print(f"  🛑 STOP: cella {state}#{idx} scalata a {sw_s}×{sh_s}")
                sys.exit(3)
            scaled = cell.resize((sw_s, sh_s), Image.LANCZOS)

            col = idx % cols
            row = idx // cols
            cell_x0 = col * TARGET_W
            cell_y0 = row * TARGET_H
            # center horizontal, bottom anchor
            px = cell_x0 + (TARGET_W - sw_s) // 2
            py = cell_y0 + (TARGET_H - sh_s)
            sheet.paste(scaled, (px, py), scaled)

        out_path = os.path.join(RUN, f"{state}_sheet.png")
        sheet.save(out_path, "PNG", optimize=True)
        sha = sha256_file(out_path)
        runtime_files[state] = {
            "path": out_path,
            "relative": f"runtime/{state}_sheet.png",
            "width": sheet_w, "height": sheet_h,
            "frameWidth": TARGET_W, "frameHeight": TARGET_H,
            "frames": n, "columns": cols, "rows": rows,
            "fps": cfg["fps"], "loop": cfg["loop"],
            "sha256": sha,
        }
        print(f"  ✅ {state:>6}  {sheet_w}×{sheet_h}  sha256={sha[:16]}...")

        # preview tile: primo frame
        first = sheet.crop((0, 0, TARGET_W, TARGET_H))
        first_frames.append((state, first, n, cfg["fps"], cfg["loop"]))

    # 4) battle_animations.json v6
    anim = {
        "heroId": "norse_berserker",
        "version": 6,
        "frameWidth": TARGET_W,
        "frameHeight": TARGET_H,
        "animations": {
            state: {
                "sheet": m["relative"],
                "frames": m["frames"],
                "columns": m["columns"],
                "rows": m["rows"],
                "fps": m["fps"],
                "loop": m["loop"],
                "sha256": m["sha256"],
            } for state, m in runtime_files.items()
        }
    }
    anim_path = os.path.join(RUN, "battle_animations.json")
    with open(anim_path, "w") as f:
        json.dump(anim, f, indent=2)
    print(f"\n[4] battle_animations.json v6 scritto: {anim_path}")

    # 5) Preview composito (tutti i runtime sheet concatenati con label)
    print("\n[5] DEBUG PREVIEW (runtime sheets concatenati con label)")
    LABEL_H = 30
    thumbnails = []
    for state, info in runtime_files.items():
        sheet_img = Image.open(info["path"]).convert("RGBA")
        label_img = Image.new("RGBA", (sheet_img.size[0], LABEL_H), (15, 15, 20, 255))
        d = ImageDraw.Draw(label_img)
        lbl = f"{state}  {info['width']}x{info['height']}  frames={info['frames']}  cols={info['columns']}x{info['rows']}  fps={info['fps']}  loop={info['loop']}"
        d.text((8, 8), lbl, fill=(255, 255, 255, 255))
        combined = Image.new("RGBA", (sheet_img.size[0], sheet_img.size[1] + LABEL_H), (0, 0, 0, 255))
        combined.paste(label_img, (0, 0))
        combined.paste(sheet_img, (0, LABEL_H), sheet_img)
        thumbnails.append(combined)

    total_w = max(t.size[0] for t in thumbnails)
    total_h = sum(t.size[1] for t in thumbnails) + 4 * (len(thumbnails) - 1)
    preview = Image.new("RGBA", (total_w, total_h), (5, 5, 10, 255))
    y = 0
    for t in thumbnails:
        preview.paste(t, (0, y))
        y += t.size[1] + 4
    prev_path = os.path.join(RUN, "_debug_berserker_runtime_preview.png")
    preview.save(prev_path, "PNG", optimize=True)
    prev_sha = sha256_file(prev_path)
    print(f"  ✅ preview {preview.size[0]}×{preview.size[1]}  sha256={prev_sha[:16]}...")

    # 6) Report finale
    report = {
        "task": "RM1.17-N-RETRY",
        "anti_drift_policy": "no per-frame bbox recenter; global uniform scale; center horizontal + bottom anchor",
        "global_scale": round(global_scale, 6),
        "target_cell": {"width": TARGET_W, "height": TARGET_H},
        "source_audit": {
            state: {
                "file": STATES[state]["file"],
                "size": f"{d['img'].size[0]}x{d['img'].size[1]}",
                "mode": d["img"].mode,
                "cell_source": f"{d['cell_w']:.2f}x{d['cell_h']:.2f}",
                "cell_scaled": f"{d['cell_w']*global_scale:.1f}x{d['cell_h']*global_scale:.1f}",
                "sha256": d["sha"],
            } for state, d in state_data.items()
        },
        "runtime_files": runtime_files,
        "preview": {"path": prev_path, "sha256": prev_sha,
                    "dimensions": f"{preview.size[0]}x{preview.size[1]}"},
        "battle_animations_json": anim_path,
    }
    report_path = os.path.join(RUN, "_normalization_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n[6] Report: {report_path}")
    print("\n✅ RM1.17-N-RETRY completato.")


if __name__ == "__main__":
    main()
