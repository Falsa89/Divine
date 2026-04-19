"""
build_animation_sheet.py
------------------------
Standard tool per generare contact sheet di validazione visiva delle
animazioni Hoplite (e altri eroi rig-based).

Output: singola immagine PNG con N frame allineati orizzontalmente,
stessa scala, stesso crop, stesso sfondo, etichette leggibili.

USO:
    python3 /app/scripts/build_animation_sheet.py \
        --src /root/.emergent/automation_output/<timestamp> \
        --out /tmp/<anim>_sheet.png \
        --title "AFFONDO DI FALANGE — contact sheet" \
        --frames sheet_A_idle.jpeg=IDLE:baseline \
                 sheet_B_windup.jpeg=WIND-UP:"t ≈ 140ms" \
                 ...

Se lanciato senza argomenti, usa il preset hardcoded per Guardia Ferrea
(serve come template di riferimento per nuove animazioni).
"""
import os
import sys
import argparse
from PIL import Image, ImageDraw, ImageFont

# ── Layout constants (standard per TUTTE le contact sheet) ──────────────────
CROP = (380, 0, 900, 640)      # crop area del preview 1280x720 (solo rig)
CELL_W = 420
CELL_H = int(CELL_W * 640 / 520)  # 516, preserva aspect ratio
PAD_X = 14
PAD_TITLE = 70
PAD_LABEL = 52
PAD_BOTTOM = 18
BG = (18, 18, 22)
LABEL_BG = (32, 32, 40)
TITLE_COLOR = (255, 215, 0)
SUB_COLOR = (170, 170, 180)
PILL_COLOR = (255, 107, 53)


def _font(sz, bold=False):
    cands_bold = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    cands_reg = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in (cands_bold if bold else cands_reg):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def build_sheet(src_dir: str, out_path: str, title: str, subtitle: str,
                frames: list[tuple[str, str, str]]):
    """frames = [(filename, label, sub_label), ...]"""
    cols = len(frames)
    w = PAD_X + cols * (CELL_W + PAD_X)
    h = PAD_TITLE + PAD_LABEL + CELL_H + PAD_BOTTOM

    sheet = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(sheet)

    # Title band
    draw.text((PAD_X + 8, 14), title, fill=TITLE_COLOR, font=_font(28, True))
    draw.text((PAD_X + 8, 48), subtitle, fill=SUB_COLOR, font=_font(14))

    for i, (fname, label, sub) in enumerate(frames):
        fp = os.path.join(src_dir, fname)
        if not os.path.exists(fp):
            print(f"[miss] {fp}", file=sys.stderr)
            continue
        img = Image.open(fp).convert("RGB").crop(CROP).resize(
            (CELL_W, CELL_H), Image.LANCZOS
        )

        x = PAD_X + i * (CELL_W + PAD_X)
        y_lab = PAD_TITLE
        y_img = y_lab + PAD_LABEL

        draw.rectangle([x, y_lab, x + CELL_W, y_lab + PAD_LABEL - 4], fill=LABEL_BG)
        draw.text((x + 10, y_lab + 6), label,
                  fill=(255, 255, 255), font=_font(18, True))
        draw.text((x + 10, y_lab + 30), sub, fill=(160, 160, 170), font=_font(12))

        sheet.paste(img, (x, y_img))

        # Index pill
        px, py, pw, ph = x + 10, y_img + 10, 34, 22
        draw.rectangle([px, py, px + pw, py + ph], fill=PILL_COLOR)
        draw.text((px + 10, py + 2), str(i + 1),
                  fill=(255, 255, 255), font=_font(18, True))

    sheet.save(out_path, optimize=True)
    print(f"[OK] saved {out_path}  size={sheet.size}  "
          f"bytes={os.path.getsize(out_path)}")


# ── Preset: Guardia Ferrea (riferimento) ────────────────────────────────────
GUARDIA_FERREA_PRESET = {
    "src": "/root/.emergent/automation_output/20260419_011103",
    "out": "/tmp/guardia_ferrea_sheet.png",
    "title": "GUARDIA FERREA — contact sheet",
    "subtitle": "Hoplite · skill difensiva · rig pose (aura pulse non renderizzata in preview)",
    "frames": [
        ("sheet_A_idle.jpeg",        "IDLE",         "baseline · pre-skill"),
        ("sheet_B_anchor.jpeg",      "ANCHOR",       "t ≈ 180ms · shield alzato, crouch"),
        ("sheet_C_hold_pulse.jpeg",  "HOLD / PULSE", "t ≈ 430ms · shield pulse peak"),
        ("sheet_D_hold_stable.jpeg", "HOLD END",     "t ≈ 680ms · posa tenuta"),
        ("sheet_E_release.jpeg",     "RELEASE",      "t ≈ 930ms · rientro morbido"),
        ("sheet_F_return.jpeg",      "RETURN",       "t ≈ 1200ms · home"),
    ],
}


if __name__ == "__main__":
    if len(sys.argv) == 1:
        build_sheet(**GUARDIA_FERREA_PRESET)
        sys.exit(0)

    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--subtitle", default="")
    parser.add_argument("--frames", nargs="+", required=True,
                        help="format: filename=LABEL:sub")
    args = parser.parse_args()
    fs = []
    for spec in args.frames:
        fname, meta = spec.split("=", 1)
        label, _, sub = meta.partition(":")
        fs.append((fname, label, sub))
    build_sheet(args.src, args.out, args.title, args.subtitle, fs)
