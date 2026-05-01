"""Analisi dimensioni body per stato — serve per calibrare RM1.17-P."""
import os
from PIL import Image

SRC = "/app/frontend/assets/heroes/norse_berserker/source_sheets"

STATES = {
    "idle":   {"file": "idle_source.png",   "frames": 6, "layout": "row"},
    "attack": {"file": "attack_source.png", "frames": 5, "layout": "row"},
    "skill":  {"file": "skill_source.png",  "frames": 9, "layout": "5x2_take9"},
    "hit":    {"file": "hit_source.png",    "frames": 5, "layout": "row"},
    "death":  {"file": "death_source.png",  "frames": 6, "layout": "row"},
}


def extract_cells(img, cfg):
    W, H = img.size
    cells = []
    if cfg["layout"] == "row":
        n = cfg["frames"]
        cw = W / n
        for i in range(n):
            cells.append(img.crop((round(i*cw), 0, round((i+1)*cw), H)))
    elif cfg["layout"] == "5x2_take9":
        cw = W / 5
        ch = H / 2
        for i in range(5):
            cells.append(img.crop((round(i*cw), 0, round((i+1)*cw), round(ch))))
        for i in range(4):
            cells.append(img.crop((round(i*cw), round(ch), round((i+1)*cw), H)))
    return cells


print(f"{'state':>7} | {'src_cell':>14} | {'bbox_max_w':>10} | {'bbox_max_h':>10} | {'union_bbox':>22} | {'union_wxh':>12}")
print("-" * 90)

for state, cfg in STATES.items():
    img = Image.open(f"{SRC}/{cfg['file']}").convert("RGBA")
    cells = extract_cells(img, cfg)
    max_w = 0; max_h = 0
    union = None  # (x0,y0,x1,y1)
    for c in cells:
        bb = c.split()[-1].getbbox()
        if bb is None: continue
        w = bb[2]-bb[0]; h = bb[3]-bb[1]
        max_w = max(max_w, w); max_h = max(max_h, h)
        if union is None:
            union = bb
        else:
            union = (min(union[0], bb[0]), min(union[1], bb[1]),
                     max(union[2], bb[2]), max(union[3], bb[3]))
    cw, ch = cells[0].size if cells else (0,0)
    uw = union[2]-union[0] if union else 0
    uh = union[3]-union[1] if union else 0
    print(f"{state:>7} | {cw:>5}x{ch:<6} | {max_w:>10} | {max_h:>10} | {str(union):>22} | {uw}x{uh}")

print()
print("=== Hoplite reference ===")
h = Image.open("/app/frontend/assets/heroes/greek_hoplite/combat_base.png").convert("RGBA")
bb = h.split()[-1].getbbox()
print(f"combat_base {h.size}: bbox={bb}  body {bb[2]-bb[0]}x{bb[3]-bb[1]}  body_h/img_h={((bb[3]-bb[1])/h.size[1])*100:.1f}%")
# Hoplite idle frame
idle = Image.open("/app/frontend/assets/heroes/greek_hoplite/idle/idle_01.png").convert("RGBA")
ibb = idle.split()[-1].getbbox()
print(f"idle_01 {idle.size}: bbox={ibb}  body {ibb[2]-ibb[0]}x{ibb[3]-ibb[1]}  body_h/img_h={((ibb[3]-ibb[1])/idle.size[1])*100:.1f}%")
