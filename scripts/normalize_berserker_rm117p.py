"""
RM1.17-P — Regenerate Berserker runtime sheets matching Hoplite body size.

Policy:
  - Per-state UNION bbox trim (same crop for all frames of a state)
    → NOT per-frame bbox recenter; body/root anchor preserved by design
    because all frames of a state use identical crop.
  - Per-state scale targeted to body_h_display = 0.91 × size (match Hoplite).
  - Width cap: if per-state scale exceeds cell width, cap at cell_w constraint.
  - Uniform runtime cell 640×768.
  - Bottom-anchor feet, center-horizontal.
"""
import os
import sys
import json
import hashlib
from PIL import Image, ImageDraw

ROOT = "/app/frontend/assets/heroes/norse_berserker"
SRC = os.path.join(ROOT, "source_sheets")
RUN = os.path.join(ROOT, "runtime")
os.makedirs(RUN, exist_ok=True)

TARGET_W = 640
TARGET_H = 768

# Hoplite reference: body fills ~91% of square rig 1024×1024 → display 0.91×size.
# BattleSprite display frame = size × size*1.25 → target body_h_runtime such
# that body_h_display = 0.91 × size:
#   body_h_display = body_h_runtime / TARGET_H × (size × 1.25)
#   → body_h_runtime = 0.91 × size × TARGET_H / (1.25 × size) = 0.91 × 614.4 = 559
HOPLITE_BODY_H_DISPLAY_RATIO = 0.91
TARGET_BODY_H_RUNTIME = int(HOPLITE_BODY_H_DISPLAY_RATIO * TARGET_H / 1.25)  # 559

# Safety padding (px) intorno al body per evitare clipping edge da VFX sottili
SAFETY_PAD = 12

STATES = {
    "idle":   {"file": "idle_source.png",   "frames": 6, "cols": 6, "rows": 1, "layout": "row",       "fps": 8,  "loop": True,  "runtime_cols": 6, "runtime_rows": 1},
    "attack": {"file": "attack_source.png", "frames": 5, "cols": 5, "rows": 1, "layout": "row",       "fps": 12, "loop": False, "runtime_cols": 5, "runtime_rows": 1},
    "skill":  {"file": "skill_source.png",  "frames": 9, "cols": 5, "rows": 2, "layout": "5x2_take9", "fps": 12, "loop": False, "runtime_cols": 5, "runtime_rows": 2},
    "hit":    {"file": "hit_source.png",    "frames": 5, "cols": 5, "rows": 1, "layout": "row",       "fps": 10, "loop": False, "runtime_cols": 5, "runtime_rows": 1},
    "death":  {"file": "death_source.png",  "frames": 6, "cols": 6, "rows": 1, "layout": "row",       "fps": 8,  "loop": False, "runtime_cols": 6, "runtime_rows": 1},
}


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_cells(img, cfg):
    W, H = img.size
    out = []
    if cfg["layout"] == "row":
        cw = W / cfg["frames"]
        for i in range(cfg["frames"]):
            out.append(img.crop((round(i * cw), 0, round((i + 1) * cw), H)))
    elif cfg["layout"] == "5x2_take9":
        cw = W / 5
        ch = H / 2
        for i in range(5):
            out.append(img.crop((round(i * cw), 0, round((i + 1) * cw), round(ch))))
        for i in range(4):
            out.append(img.crop((round(i * cw), round(ch), round((i + 1) * cw), H)))
    return out


def bbox_union(bboxes):
    valid = [b for b in bboxes if b is not None]
    if not valid:
        return None
    x0 = min(b[0] for b in valid)
    y0 = min(b[1] for b in valid)
    x1 = max(b[2] for b in valid)
    y1 = max(b[3] for b in valid)
    return (x0, y0, x1, y1)


def main():
    print("=" * 72)
    print("RM1.17-P — NORMALIZE vs HOPLITE")
    print(f"Target body_h_runtime = {TARGET_BODY_H_RUNTIME}px (from 0.91×size match)")
    print("=" * 72)

    state_data = {}
    for state, cfg in STATES.items():
        p = os.path.join(SRC, cfg["file"])
        img = Image.open(p).convert("RGBA")
        cells = extract_cells(img, cfg)
        # union bbox across frames (within cell coordinates)
        bboxes = [c.split()[-1].getbbox() for c in cells]
        union = bbox_union(bboxes)
        if union is None:
            print(f"❌ {state}: empty union bbox")
            sys.exit(1)
        # apply safety pad, clamp to cell bounds
        cw_cell, ch_cell = cells[0].size
        pad_union = (
            max(0, union[0] - SAFETY_PAD),
            max(0, union[1] - SAFETY_PAD),
            min(cw_cell, union[2] + SAFETY_PAD),
            min(ch_cell, union[3] + SAFETY_PAD),
        )
        uw = pad_union[2] - pad_union[0]
        uh = pad_union[3] - pad_union[1]

        # Scale to target body_h, capped by cell width constraint
        scale_h = TARGET_BODY_H_RUNTIME / uh
        scale_w_max = TARGET_W / uw
        scale = min(scale_h, scale_w_max)
        # Also ensure does not exceed cell height
        scale_h_max = TARGET_H / uh
        if scale > scale_h_max:
            scale = scale_h_max

        scaled_w = int(round(uw * scale))
        scaled_h = int(round(uh * scale))
        body_h_after = int(round(uh * scale))
        body_h_display_ratio = body_h_after / TARGET_H * 1.25  # body_h in display units of size

        state_data[state] = {
            "img": img,
            "cells": cells,
            "union": pad_union,
            "uw": uw, "uh": uh,
            "scale": scale,
            "scaled_w": scaled_w, "scaled_h": scaled_h,
            "body_h_display_ratio": body_h_display_ratio,
            "cfg": cfg,
            "sha_source": sha256_file(p),
        }
        print(f"  {state:>6}  union={uw}×{uh}  scale={scale:.3f}  scaled={scaled_w}×{scaled_h}  "
              f"body_h_display={body_h_display_ratio:.3f}×size  "
              f"{'⚠ WIDTH-CAPPED' if scale == scale_w_max else '✓ target-matched'}")

    # ---------- REPACK ----------
    print("\n[REPACK]")
    runtime_files = {}
    first_frames = []
    for state, d in state_data.items():
        cfg = d["cfg"]
        cells = d["cells"]
        union = d["union"]
        scale = d["scale"]
        cols_rt = cfg["runtime_cols"]
        rows_rt = cfg["runtime_rows"]
        sheet_w = cols_rt * TARGET_W
        sheet_h = rows_rt * TARGET_H
        sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))

        for idx, cell in enumerate(cells):
            # CROP using STATE-LEVEL union (same for all frames → preserves positioning)
            cropped = cell.crop(union)
            sw = int(round(cropped.size[0] * scale))
            sh = int(round(cropped.size[1] * scale))
            scaled = cropped.resize((sw, sh), Image.LANCZOS)

            col = idx % cols_rt
            row = idx // cols_rt
            cell_x0 = col * TARGET_W
            cell_y0 = row * TARGET_H
            # Center horizontal, bottom anchor feet at runtime cell bottom
            px = cell_x0 + (TARGET_W - sw) // 2
            py = cell_y0 + (TARGET_H - sh)
            sheet.paste(scaled, (px, py), scaled)

        out_path = os.path.join(RUN, f"{state}_sheet.png")
        sheet.save(out_path, "PNG", optimize=True)
        sha = sha256_file(out_path)
        runtime_files[state] = {
            "path": out_path,
            "relative": f"runtime/{state}_sheet.png",
            "width": sheet_w, "height": sheet_h,
            "frameWidth": TARGET_W, "frameHeight": TARGET_H,
            "frames": cfg["frames"],
            "columns": cols_rt, "rows": rows_rt,
            "fps": cfg["fps"], "loop": cfg["loop"],
            "sha256": sha,
            "state_scale": round(scale, 4),
            "body_h_runtime": d["scaled_h"],
            "body_h_display_ratio": round(d["body_h_display_ratio"], 4),
        }
        print(f"  ✅ {state:>6}  {sheet_w}×{sheet_h}  sha={sha[:16]}...  body_h={d['scaled_h']}px")
        first_frames.append((state, sheet.crop((0, 0, TARGET_W, TARGET_H))))

    # ---------- battle_animations.json v8 ----------
    anim = {
        "heroId": "norse_berserker",
        "version": 8,
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
    print(f"\n[JSON v8] {anim_path}")

    # ---------- Preview runtime (labeled) ----------
    LABEL_H = 30
    thumbnails = []
    for state, m in runtime_files.items():
        s = Image.open(m["path"]).convert("RGBA")
        lbl = Image.new("RGBA", (s.size[0], LABEL_H), (15, 15, 20, 255))
        d = ImageDraw.Draw(lbl)
        d.text((8, 8),
               f"{state}  {m['width']}×{m['height']}  scale={m['state_scale']}  "
               f"body_h={m['body_h_runtime']}px ({m['body_h_display_ratio']}×size)  "
               f"frames={m['frames']}  cols={m['columns']}×{m['rows']}  fps={m['fps']}  loop={m['loop']}",
               fill=(255, 255, 255, 255))
        combined = Image.new("RGBA", (s.size[0], s.size[1] + LABEL_H), (0, 0, 0, 255))
        combined.paste(lbl, (0, 0))
        combined.paste(s, (0, LABEL_H), s)
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
    print(f"[Preview] {prev_path} {preview.size}")

    # ---------- Debug Berserker vs Hoplite comparison ----------
    # Rendering mock: display at size=240 for comparison
    DISP_SIZE = 240
    # Hoplite: combat_base fitted to DISP_SIZE × DISP_SIZE (Hoplite uses square rig)
    hop_img = Image.open("/app/frontend/assets/heroes/greek_hoplite/combat_base.png").convert("RGBA")
    hop_scaled = hop_img.resize((DISP_SIZE, DISP_SIZE), Image.LANCZOS)
    # Berserker frames: runtime cell 640×768 displayed at DISP_SIZE × DISP_SIZE*1.25
    DISP_W = DISP_SIZE
    DISP_H = int(DISP_SIZE * 1.25)
    berserker_disp = {}
    for state, m in runtime_files.items():
        sheet_img = Image.open(m["path"]).convert("RGBA")
        # first frame of state (idx 0)
        cell = sheet_img.crop((0, 0, TARGET_W, TARGET_H))
        scaled = cell.resize((DISP_W, DISP_H), Image.LANCZOS)
        berserker_disp[state] = scaled

    # Stitch side-by-side with ground line + body measurement annotations
    cols_n = 6  # Hoplite + 5 Berserker states
    CELL_H_BG = DISP_H + 60  # label + ground-line area
    FOOTER_H = 30
    comp = Image.new("RGBA", (cols_n * (DISP_W + 8), CELL_H_BG + FOOTER_H), (20, 20, 28, 255))
    dd = ImageDraw.Draw(comp)
    panels = [("Hoplite (ref)", hop_scaled, None)] + [
        (s, img, runtime_files[s]) for s, img in berserker_disp.items()
    ]
    for i, (label, panel_img, meta) in enumerate(panels):
        x = i * (DISP_W + 8)
        dd.text((x + 4, 4), label, fill=(255, 255, 180, 255))
        # ground line = bottom of panel
        ground_y = 20 + DISP_H
        panel_y = 20
        # Hoplite rendered square (DISP_W x DISP_W); center-vertical in panel H
        if label == "Hoplite (ref)":
            paste_y = panel_y + (DISP_H - DISP_W) // 2
            comp.paste(panel_img, (x, paste_y), panel_img)
            # body bbox approximate 91% → mark
            head_y = paste_y + int(DISP_W * 0.045)
            foot_y = paste_y + int(DISP_W * 0.96)
            body_h_px = foot_y - head_y
            dd.line([(x, ground_y), (x + DISP_W, ground_y)], fill=(120, 255, 120, 255), width=2)
            dd.line([(x, head_y), (x + DISP_W, head_y)], fill=(255, 220, 120, 255), width=1)
            dd.line([(x, foot_y), (x + DISP_W, foot_y)], fill=(120, 255, 120, 255), width=2)
            dd.text((x + 4, ground_y + 2),
                    f"body_h={body_h_px}px\n(~0.91×size)",
                    fill=(255, 255, 255, 255))
        else:
            comp.paste(panel_img, (x, panel_y), panel_img)
            dd.line([(x, ground_y), (x + DISP_W, ground_y)], fill=(120, 255, 120, 255), width=2)
            # body height indicator: body_h_runtime × DISP_H/TARGET_H
            body_h_disp = int(meta["body_h_runtime"] * DISP_H / TARGET_H)
            head_y = ground_y - body_h_disp
            dd.line([(x, head_y), (x + DISP_W, head_y)], fill=(255, 220, 120, 255), width=1)
            dd.text((x + 4, ground_y + 2),
                    f"body_h={body_h_disp}px\nscale={meta['state_scale']}\n({meta['body_h_display_ratio']}×size)",
                    fill=(255, 255, 255, 255))
    comp_path = os.path.join(RUN, "_debug_berserker_vs_hoplite_scale.png")
    comp.save(comp_path, "PNG", optimize=True)
    print(f"[Comparison] {comp_path} {comp.size}")

    # ---------- Final report ----------
    print("\n" + "=" * 72)
    print("REPORT FINALE RM1.17-P")
    print("=" * 72)
    idle_body_h = runtime_files["idle"]["body_h_runtime"]
    for state, m in runtime_files.items():
        delta = (m["body_h_runtime"] - idle_body_h) / idle_body_h * 100
        hoplite_match = m["body_h_display_ratio"] / HOPLITE_BODY_H_DISPLAY_RATIO * 100
        print(f"  {state:>6}  body_h_runtime={m['body_h_runtime']:>4}px  "
              f"body_h_display={m['body_h_display_ratio']:.3f}×size  "
              f"vs idle: {delta:+.1f}%  vs Hoplite: {hoplite_match:.1f}%")


if __name__ == "__main__":
    main()
