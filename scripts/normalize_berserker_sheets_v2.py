"""
RM1.17-N v2 — Detection ibrida controllata + Repack runtime Berserker

Regole:
- Legge SOLO da source_sheets/*_source.png
- Detection dei blob su profilo colonne (alpha-based)
- Merge iterativo fino a target ufficiale
- Se target non raggiungibile → STOP
- Cell size uniforme per TUTTI gli stati
- Piedi ancorati al bottom, personaggio centrato
"""
import os
import sys
import json
import hashlib
from PIL import Image, ImageDraw

# ---------------------------------------------------------------------------
# CONFIG UFFICIALE (source of truth)
# ---------------------------------------------------------------------------
STATES_CFG = {
    "idle":   {"file": "idle_source.png",   "frames": 6, "layout": "row",     "fps": 8,  "loop": True,  "runtime_cols": 6, "runtime_rows": 1},
    "attack": {"file": "attack_source.png", "frames": 5, "layout": "row",     "fps": 12, "loop": False, "runtime_cols": 5, "runtime_rows": 1},
    "skill":  {"file": "skill_source.png",  "frames": 9, "layout": "5plus4",  "fps": 12, "loop": False, "runtime_cols": 5, "runtime_rows": 2},
    "hit":    {"file": "hit_source.png",    "frames": 5, "layout": "row",     "fps": 10, "loop": False, "runtime_cols": 5, "runtime_rows": 1},
    "death":  {"file": "death_source.png",  "frames": 6, "layout": "row",     "fps": 8,  "loop": False, "runtime_cols": 6, "runtime_rows": 1},
}

ROOT = "/app/frontend/assets/heroes/norse_berserker"
SRC_DIR = os.path.join(ROOT, "source_sheets")
RUN_DIR = os.path.join(ROOT, "runtime")
os.makedirs(RUN_DIR, exist_ok=True)

# Cell size candidates (W, H) in ordine di preferenza
CELL_CANDIDATES = [(512, 768), (640, 768), (640, 896), (768, 1024)]
PADDING_X = 20          # padding orizzontale minimo per lato
PADDING_TOP = 16        # padding in alto
FEET_MARGIN = 16        # distanza piedi dal bordo inferiore

# Detection params
ALPHA_THRESH = 8
MIN_CONTENT_PER_COL = 2   # pixel opachi minimi per considerare colonna "piena"
NOISE_AREA_FRAC = 0.005   # blob con area < 0.5% area totale = rumore
Y_STRIDE = 1              # precisione massima


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def col_profile(img):
    """Array len=W: per ogni colonna conta i pixel opachi."""
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    alpha = img.split()[-1]
    W, H = img.size
    px = alpha.load()
    prof = [0] * W
    for x in range(W):
        c = 0
        for y in range(0, H, Y_STRIDE):
            if px[x, y] > ALPHA_THRESH:
                c += 1
        prof[x] = c
    return prof


def raw_blobs(prof):
    """Regioni [x0,x1) contigue dove prof >= MIN_CONTENT_PER_COL."""
    blobs = []
    start = None
    for x, v in enumerate(prof):
        if v >= MIN_CONTENT_PER_COL:
            if start is None:
                start = x
        else:
            if start is not None:
                blobs.append([start, x])
                start = None
    if start is not None:
        blobs.append([start, len(prof)])
    return blobs


def blob_area(prof, blob):
    return sum(prof[blob[0]:blob[1]])


def merge_closest(blobs):
    """Mergia i due blob con il gap minore."""
    if len(blobs) < 2:
        return blobs, -1
    min_gap = 10 ** 9
    idx = 0
    for i in range(len(blobs) - 1):
        gap = blobs[i + 1][0] - blobs[i][1]
        if gap < min_gap:
            min_gap = gap
            idx = i
    merged = blobs[:idx] + [[blobs[idx][0], blobs[idx + 1][1]]] + blobs[idx + 2:]
    return merged, min_gap


def merge_smallest_into_neighbor(blobs, prof):
    """
    Euristica migliore: trova il blob di area minima e lo mergia col vicino
    di gap minore. Questo assorbe residui/scintille nel frame che li contiene
    davvero, invece di fondere due frame grandi tra loro.
    """
    if len(blobs) < 2:
        return blobs, {"merged_area": -1, "gap": -1}
    areas = [blob_area(prof, b) for b in blobs]
    min_i = min(range(len(areas)), key=lambda k: areas[k])
    if min_i == 0:
        target = 1
        gap = blobs[1][0] - blobs[0][1]
    elif min_i == len(blobs) - 1:
        target = len(blobs) - 2
        gap = blobs[min_i][0] - blobs[target][1]
    else:
        gap_left = blobs[min_i][0] - blobs[min_i - 1][1]
        gap_right = blobs[min_i + 1][0] - blobs[min_i][1]
        if gap_left <= gap_right:
            target = min_i - 1
            gap = gap_left
        else:
            target = min_i + 1
            gap = gap_right
    a, b = sorted((min_i, target))
    merged = blobs[:a] + [[blobs[a][0], blobs[b][1]]] + blobs[b + 1:]
    return merged, {"absorbed_area": areas[min_i], "gap": gap, "abs_idx": min_i}


def blob_bbox_height(img, blob):
    region = img.crop((blob[0], 0, blob[1], img.size[1]))
    bb = region.split()[-1].getbbox()
    return 0 if bb is None else (bb[3] - bb[1])


def find_valleys_in_range(prof, x0, x1, n_valleys, edge_margin_frac=0.15):
    """Trova gli n_valleys punti di minimo contenuto nel range [x0, x1)
    con esclusione dei bordi e distanza minima."""
    region = prof[x0:x1]
    if not region or n_valleys <= 0:
        return []
    margin = max(30, int(len(region) * edge_margin_frac))
    if len(region) < 2 * margin + n_valleys:
        return []
    min_sep = max(60, (len(region) - 2 * margin) // (n_valleys + 1))
    # ordina gli indici per profilo crescente (valli più profonde prima)
    sorted_idxs = sorted(range(margin, len(region) - margin), key=lambda i: region[i])
    chosen = []
    for i in sorted_idxs:
        if all(abs(i - c) >= min_sep for c in chosen):
            chosen.append(i)
            if len(chosen) == n_valleys:
                break
    if len(chosen) < n_valleys:
        return []
    return sorted(x0 + c for c in chosen)


def try_split_wide_candidates(img, blob_data, target_n, prof, log):
    """Se candidati < target_n, splitta i candidati anomalmente larghi su
    valli del profilo colonne. Questo gestisce il caso di frame connessi
    da VFX (es. fiamme che toccano entrambi i personaggi)."""
    candidates = [(i, d) for i, d in enumerate(blob_data) if d["is_candidate"]]
    if len(candidates) >= target_n:
        return blob_data

    need = target_n - len(candidates)
    widths = sorted(d["blob"][1] - d["blob"][0] for _, d in candidates)
    if not widths:
        return blob_data
    med_w = widths[len(widths) // 2]
    # candidati larghi ≥1.4× mediana, ordinati per larghezza DESC
    wide = sorted(
        [(i, d) for i, d in candidates if (d["blob"][1] - d["blob"][0]) >= med_w * 1.4],
        key=lambda x: -(x[1]["blob"][1] - x[1]["blob"][0])
    )
    if not wide:
        return blob_data

    splits_applied = {}
    remaining = need
    log.setdefault("splits", [])
    for i, d in wide:
        if remaining <= 0:
            break
        w = d["blob"][1] - d["blob"][0]
        n_sub = max(1, round(w / med_w))
        n_sub = min(n_sub, 1 + remaining)
        if n_sub <= 1:
            continue
        valleys = find_valleys_in_range(prof, d["blob"][0], d["blob"][1], n_sub - 1)
        if len(valleys) != n_sub - 1:
            log["splits"].append({"blob": d["blob"], "n_sub": n_sub, "valleys_found": valleys, "status": "FAILED_valleys"})
            continue
        points = [d["blob"][0]] + valleys + [d["blob"][1]]
        subs = []
        for j in range(n_sub):
            sb = [points[j], points[j + 1]]
            sh = blob_bbox_height(img, sb)
            sa = blob_area(prof, sb)
            subs.append({"blob": sb, "h": sh, "area": sa, "is_candidate": True})
        splits_applied[i] = subs
        remaining -= (n_sub - 1)
        log["splits"].append({"blob": d["blob"], "n_sub": n_sub, "valleys": valleys, "status": "OK"})

    if not splits_applied:
        return blob_data

    new_blob_data = []
    for i, d in enumerate(blob_data):
        if i in splits_applied:
            new_blob_data.extend(splits_applied[i])
        else:
            new_blob_data.append(d)
    return new_blob_data


def detect_frames(img, target_n, label=""):
    """
    Detection ibrida a 2 fasi:
    1. profilo colonne → blob grezzi
    2. classifica blob come 'candidato frame' (altezza >= 40% max_height)
       oppure 'residuo' (scintille/VFX isolati)
    3. se candidati < target → STOP (no frame mancanti inventabili)
    4. merge iterativo: assorbi prima TUTTI i residui nel vicino più vicino,
       poi se restano più candidati del target, assorbi il più piccolo
    5. ritorna target_n blob finali
    """
    CANDIDATE_H_FRAC = 0.40
    CANDIDATE_AREA_FRAC = 0.20  # OR: area >= 20% max area = candidato (utile per death)
    prof = col_profile(img)
    raw = raw_blobs(prof)
    if not raw:
        return None, prof, {"label": label, "stop_reason": "nessun blob"}

    blob_data = []
    for b in raw:
        h = blob_bbox_height(img, b)
        a = blob_area(prof, b)
        blob_data.append({"blob": b, "h": h, "area": a})
    max_h = max(d["h"] for d in blob_data)
    max_a = max(d["area"] for d in blob_data)
    min_h_cand = int(max_h * CANDIDATE_H_FRAC)
    min_a_cand = int(max_a * CANDIDATE_AREA_FRAC)
    for d in blob_data:
        d["is_candidate"] = (d["h"] >= min_h_cand) or (d["area"] >= min_a_cand)

    candidates = [d for d in blob_data if d["is_candidate"]]
    residues = [d for d in blob_data if not d["is_candidate"]]
    log = {
        "label": label,
        "raw_blobs": len(blob_data),
        "max_blob_height": max_h,
        "candidate_h_threshold": min_h_cand,
        "candidates": len(candidates),
        "residues": len(residues),
        "target_n": target_n,
        "merges": [],
    }

    if len(candidates) < target_n:
        # Prova a splittare candidati anomalmente larghi su valli del profilo
        blob_data = try_split_wide_candidates(img, blob_data, target_n, prof, log)
        candidates = [d for d in blob_data if d["is_candidate"]]
        residues = [d for d in blob_data if not d["is_candidate"]]
        log["after_split_candidates"] = len(candidates)
        log["after_split_residues"] = len(residues)
        if len(candidates) < target_n:
            log["stop_reason"] = f"candidates {len(candidates)} < target {target_n} (anche dopo split)"
            return None, prof, log

    # Merge iterativo: prima residui (low-height), poi frame più piccoli
    while len(blob_data) > target_n:
        residue_idxs = [i for i, d in enumerate(blob_data) if not d["is_candidate"]]
        if residue_idxs:
            # scegli il residuo con gap minore verso un vicino (assorbi nel frame più vicino)
            def min_gap_to_neighbor(i):
                left = blob_data[i]["blob"][0] - blob_data[i - 1]["blob"][1] if i > 0 else 10 ** 9
                right = blob_data[i + 1]["blob"][0] - blob_data[i]["blob"][1] if i < len(blob_data) - 1 else 10 ** 9
                return min(left, right)
            idx = min(residue_idxs, key=min_gap_to_neighbor)
            reason = "residue"
        else:
            # tutti candidati → fondi il più piccolo per area col vicino più vicino
            idx = min(range(len(blob_data)), key=lambda i: blob_data[i]["area"])
            reason = "smallest_candidate"

        # scegli vicino: gap minore
        if idx == 0:
            t = 1
        elif idx == len(blob_data) - 1:
            t = idx - 1
        else:
            gl = blob_data[idx]["blob"][0] - blob_data[idx - 1]["blob"][1]
            gr = blob_data[idx + 1]["blob"][0] - blob_data[idx]["blob"][1]
            t = idx - 1 if gl <= gr else idx + 1

        a, b = sorted((idx, t))
        new_blob = [blob_data[a]["blob"][0], blob_data[b]["blob"][1]]
        new_h = blob_bbox_height(img, new_blob)
        new_area = blob_area(prof, new_blob)
        merged = {"blob": new_blob, "h": new_h, "area": new_area,
                  "is_candidate": (new_h >= min_h_cand) or (new_area >= min_a_cand)}
        blob_data = blob_data[:a] + [merged] + blob_data[b + 1:]
        log["merges"].append({"new_count": len(blob_data), "reason": reason,
                              "absorbed_idx": idx, "target_idx": t})

    log["final_count"] = len(blob_data)
    return [d["blob"] for d in blob_data], prof, log


def frame_bbox(img, x0, x1):
    """Bbox alpha absolute nella regione [x0,x1) dell'immagine completa."""
    region = img.crop((x0, 0, x1, img.size[1]))
    bb = region.split()[-1].getbbox()
    if bb is None:
        return None
    return (x0 + bb[0], bb[1], x0 + bb[2], bb[3])


def detect_state_frames(state, img):
    """Ritorna lista di bbox per i frame nell'ordine naturale."""
    cfg = STATES_CFG[state]
    W, H = img.size
    layout = cfg["layout"]

    if layout == "row":
        blobs, prof, log = detect_frames(img, cfg["frames"], label=state)
        if blobs is None:
            return None, [log]
        bboxes = []
        for b in blobs:
            bb = frame_bbox(img, b[0], b[1])
            if bb is None:
                log["stop_reason"] = f"bbox None for blob {b}"
                return None, [log]
            bboxes.append(bb)
        return bboxes, [log]

    elif layout == "5plus4":
        # Dividi top / bot e applica detection a ciascuno
        top = img.crop((0, 0, W, H // 2))
        bot = img.crop((0, H // 2, W, H))
        blobs_t, prof_t, log_t = detect_frames(top, 5, label=f"{state}_top")
        blobs_b, prof_b, log_b = detect_frames(bot, 4, label=f"{state}_bot")
        if blobs_t is None or blobs_b is None:
            return None, [log_t, log_b]
        bboxes = []
        for b in blobs_t:
            bb = frame_bbox(top, b[0], b[1])
            if bb is None:
                log_t["stop_reason"] = f"bbox None for blob {b}"
                return None, [log_t, log_b]
            bboxes.append(bb)  # y relative a top (che parte da 0)
        for b in blobs_b:
            bb = frame_bbox(bot, b[0], b[1])
            if bb is None:
                log_b["stop_reason"] = f"bbox None for blob {b}"
                return None, [log_t, log_b]
            # shift y di H//2 per coordinate absolute
            bboxes.append((bb[0], bb[1] + H // 2, bb[2], bb[3] + H // 2))
        return bboxes, [log_t, log_b]

    else:
        return None, [{"stop_reason": f"layout non supportato {layout}"}]


def extract_and_validate():
    """Esegue detection per tutti gli stati, ritorna dict di bbox + source img."""
    print("=" * 72)
    print("DETECTION IBRIDA CONTROLLATA")
    print("=" * 72)
    results = {}
    all_logs = {}
    global_max_w = 0
    global_max_h = 0

    for state, cfg in STATES_CFG.items():
        src = os.path.join(SRC_DIR, cfg["file"])
        if not os.path.isfile(src):
            print(f"  ❌ MISSING: {src}")
            sys.exit(1)
        img = Image.open(src).convert("RGBA")
        print(f"\n[{state}] {cfg['file']}  {img.size[0]}×{img.size[1]}  target={cfg['frames']}")
        bboxes, logs = detect_state_frames(state, img)
        all_logs[state] = logs

        if bboxes is None:
            print(f"  🛑 STOP per {state}. Log:")
            for lg in logs:
                print(f"     {json.dumps(lg, indent=2)}")
            return None, all_logs

        if len(bboxes) != cfg["frames"]:
            print(f"  🛑 STOP: detected {len(bboxes)} != target {cfg['frames']}")
            return None, all_logs

        # valida: area ragionevole (no frame "quasi vuoto")
        all_areas = []
        for i, bb in enumerate(bboxes):
            w = bb[2] - bb[0]; h = bb[3] - bb[1]
            # area = pixel opachi nel bbox
            region = img.crop(bb)
            alpha = region.split()[-1]
            area_px = sum(1 for p in alpha.getdata() if p > ALPHA_THRESH)
            all_areas.append(area_px)
            print(f"    frame#{i}: bbox=({bb[0]},{bb[1]},{bb[2]},{bb[3]}) w={w} h={h} px={area_px}")

        # verifica che nessun frame sia < 10% della mediana (= quasi vuoto)
        sorted_areas = sorted(all_areas)
        median = sorted_areas[len(sorted_areas) // 2]
        min_allowed = median * 0.10
        for i, a in enumerate(all_areas):
            if a < min_allowed:
                # eccezione: death #5 (ultimo) può essere piccolo (dissolvenza)
                if state == "death" and i == len(all_areas) - 1:
                    print(f"    (death ultimo frame piccolo accettato: dissolvenza naturale)")
                    continue
                print(f"  🛑 STOP: frame#{i} area={a} < 10% mediana {median}")
                return None, all_logs

        # calcola max dims del state
        state_max_w = max(bb[2] - bb[0] for bb in bboxes)
        state_max_h = max(bb[3] - bb[1] for bb in bboxes)
        global_max_w = max(global_max_w, state_max_w)
        global_max_h = max(global_max_h, state_max_h)

        results[state] = {
            "img": img,
            "bboxes": bboxes,
            "areas": all_areas,
            "max_w": state_max_w,
            "max_h": state_max_h,
            "src_path": src,
            "src_sha256": sha256_file(src),
            "src_size": img.size,
        }

    print(f"\nGLOBAL max frame content = {global_max_w}×{global_max_h}")
    return results, all_logs, global_max_w, global_max_h


def choose_cell_size(max_w, max_h):
    need_w = max_w + 2 * PADDING_X
    need_h = max_h + PADDING_TOP + FEET_MARGIN
    print(f"\nRequired cell content: {need_w}×{need_h} (w+2*padX, h+top+feet)")
    for (cw, ch) in CELL_CANDIDATES:
        if need_w <= cw and need_h <= ch:
            print(f"✅ Cell size scelta uniforme: {cw}×{ch}")
            return cw, ch
    print(f"🛑 STOP: richiesto {need_w}×{need_h} > max consentito {CELL_CANDIDATES[-1]}")
    return None, None


def pack_state_sheet(state, data, cell_w, cell_h):
    cfg = STATES_CFG[state]
    cols = cfg["runtime_cols"]
    rows = cfg["runtime_rows"]
    sheet_w = cols * cell_w
    sheet_h = rows * cell_h
    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
    img = data["img"]
    bboxes = data["bboxes"]

    for idx, bb in enumerate(bboxes):
        crop = img.crop(bb)
        cw_f, ch_f = crop.size
        col = idx % cols
        row = idx // cols
        cell_x0 = col * cell_w
        cell_y0 = row * cell_h
        # centro orizzontale
        px = cell_x0 + (cell_w - cw_f) // 2
        # piedi: bottom del crop coincide con cell_y0 + cell_h - FEET_MARGIN
        py = cell_y0 + cell_h - FEET_MARGIN - ch_f
        if py < cell_y0:
            py = cell_y0  # clamp
        sheet.paste(crop, (px, py), crop)

    return sheet, sheet_w, sheet_h


def build_runtime_preview(runtime_sheets, cell_w, cell_h):
    """Costruisce la preview concatenando i runtime sheet con label."""
    rows = []
    LABEL_H = 28
    for state, (sheet, sw, sh) in runtime_sheets.items():
        row_img = Image.new("RGBA", (sw, sh + LABEL_H), (15, 15, 20, 255))
        d = ImageDraw.Draw(row_img)
        cfg = STATES_CFG[state]
        label = f"{state}  frames={cfg['frames']}  cols={cfg['runtime_cols']}  fps={cfg['fps']}  loop={cfg['loop']}  cell={cell_w}x{cell_h}"
        d.text((8, 6), label, fill=(255, 255, 255, 255))
        row_img.paste(sheet, (0, LABEL_H), sheet)
        rows.append(row_img)

    total_w = max(r.size[0] for r in rows)
    total_h = sum(r.size[1] for r in rows) + 4 * (len(rows) - 1)
    preview = Image.new("RGBA", (total_w, total_h), (5, 5, 10, 255))
    y = 0
    for r in rows:
        preview.paste(r, (0, y))
        y += r.size[1] + 4
    return preview


def main():
    result = extract_and_validate()
    if result is None or result[0] is None:
        print("\n🛑 STOP: detection fallita. Nessun file runtime creato.")
        sys.exit(2)
    data_map, logs, gmax_w, gmax_h = result

    cell_w, cell_h = choose_cell_size(gmax_w, gmax_h)
    if cell_w is None:
        sys.exit(3)

    # ---------- REPACK ----------
    print("\n" + "=" * 72)
    print("REPACK RUNTIME SHEETS")
    print("=" * 72)
    runtime_sheets = {}
    runtime_meta = {}
    for state in STATES_CFG:
        sheet, sw, sh = pack_state_sheet(state, data_map[state], cell_w, cell_h)
        out_path = os.path.join(RUN_DIR, f"{state}_sheet.png")
        sheet.save(out_path, "PNG", optimize=True)
        sha = sha256_file(out_path)
        cfg = STATES_CFG[state]
        runtime_sheets[state] = (sheet, sw, sh)
        runtime_meta[state] = {
            "path": out_path,
            "relative": f"runtime/{state}_sheet.png",
            "width": sw, "height": sh,
            "frameWidth": cell_w, "frameHeight": cell_h,
            "frames": cfg["frames"],
            "columns": cfg["runtime_cols"],
            "rows": cfg["runtime_rows"],
            "fps": cfg["fps"],
            "loop": cfg["loop"],
            "sha256": sha,
        }
        print(f"  ✅ {state:>6}  {sw}×{sh}  sha256={sha[:16]}...")

    # ---------- battle_animations.json ----------
    anim_json = {
        "heroId": "norse_berserker",
        "version": 2,
        "frameWidth": cell_w,
        "frameHeight": cell_h,
        "animations": {
            state: {
                "sheet": m["relative"],
                "frames": m["frames"],
                "columns": m["columns"],
                "rows": m["rows"],
                "fps": m["fps"],
                "loop": m["loop"],
                "sha256": m["sha256"],
            }
            for state, m in runtime_meta.items()
        }
    }
    anim_path = os.path.join(RUN_DIR, "battle_animations.json")
    with open(anim_path, "w") as f:
        json.dump(anim_json, f, indent=2)
    print(f"  ✅ battle_animations.json")

    # ---------- Preview ----------
    preview = build_runtime_preview(runtime_sheets, cell_w, cell_h)
    prev_path = os.path.join(RUN_DIR, "_debug_berserker_runtime_preview.png")
    preview.save(prev_path, "PNG", optimize=True)
    prev_sha = sha256_file(prev_path)
    print(f"  ✅ preview {preview.size[0]}×{preview.size[1]}  sha256={prev_sha[:16]}...")

    # ---------- REPORT ----------
    full_report = {
        "source_audit": {
            s: {"file": STATES_CFG[s]["file"],
                "size": f"{data_map[s]['src_size'][0]}x{data_map[s]['src_size'][1]}",
                "sha256": data_map[s]["src_sha256"]}
            for s in STATES_CFG
        },
        "detection_report": {
            s: {
                "target": STATES_CFG[s]["frames"],
                "detected": len(data_map[s]["bboxes"]),
                "verdict": "PASS",
                "frames": [
                    {"index": i, "bbox": list(bb),
                     "w": bb[2] - bb[0], "h": bb[3] - bb[1],
                     "area_px": data_map[s]["areas"][i]}
                    for i, bb in enumerate(data_map[s]["bboxes"])
                ]
            } for s in STATES_CFG
        },
        "cell_size": {"width": cell_w, "height": cell_h,
                      "global_max_content": f"{gmax_w}x{gmax_h}"},
        "runtime_files": runtime_meta,
        "preview": {"path": prev_path, "dimensions": f"{preview.size[0]}x{preview.size[1]}", "sha256": prev_sha},
        "battle_animations_json_path": anim_path,
    }
    report_path = os.path.join(RUN_DIR, "_normalization_report.json")
    with open(report_path, "w") as f:
        json.dump(full_report, f, indent=2, default=str)
    print(f"\n  Report JSON: {report_path}")
    print("\n✅ RM1.17-N normalizzazione completata.")


if __name__ == "__main__":
    main()
