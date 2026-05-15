#!/usr/bin/env python3
"""
RM1.32-PRE — Hero Skill Kit Catalog Baseline Diff Validator
─────────────────────────────────────────────────────────────────────────
Read-only diff validator. Detects unauthorized future changes to tracked
catalog files by comparing current SHA256 against the baseline snapshot
(`hero_skill_kit_catalog_baseline_rm132pre_v1.json`).

Always re-checks critical invariants regardless of mode:
  - 5★ entries = 20
  - 6★ entries = 13
  - DW records = 13
  - no final_numbers non-null in 5★/6★ slots
  - no runtime_attached / battle_runtime_attached true at slot level
  - no legacy `borea` hero_id in 5★/6★
  - no `primordial_gaia` in 5★/6★
  - no Marchio Boreale leak in non-Borea entries

Modes:
  default (strict)            : fail if any tracked checksum changed
  --allow-changed <file>      : allow listed files to differ (repeatable)
  --summary-only              : print current checksums; do not fail on diff

Exit 0 on PASS, 1 on FAIL.
NO catalog/DB/runtime writes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path

BASELINE_PATH = Path('/app/data/design/hero_skill_kits/hero_skill_kit_catalog_baseline_rm132pre_v1.json')
BASELINE_DIR = Path('/app/data/design/hero_skill_kits')
BASELINE_GLOB = 'hero_skill_kit_catalog_baseline_*.json'


def find_latest_baseline() -> Path | None:
    """Return the most-recent baseline by ISO timestamp / version preference.

    Picks the file with the highest "generated_at_utc" inside the JSON.
    Falls back to the lexically-greatest filename, then None.
    """
    candidates = sorted(BASELINE_DIR.glob(BASELINE_GLOB))
    if not candidates:
        return None
    best: tuple[str, Path] | None = None
    for p in candidates:
        try:
            d = json.loads(p.read_text(encoding='utf-8'))
            ts = d.get('generated_at_utc') or p.name
        except Exception:
            ts = p.name
        if best is None or ts > best[0]:
            best = (ts, p)
    return best[1] if best else None

HSK_5STAR = Path('/app/data/design/hero_skill_kits/hero_skill_kits_5star_full_v1.json')
HSK_6STAR = Path('/app/data/design/hero_skill_kits/hero_skill_kits_6star_borea_v1.json')
DW_CATALOG = Path('/app/data/design/divine_weapons/divine_weapons_catalog_v1.json')

FORBIDDEN_HERO_IDS = {'borea', 'primordial_gaia', 'greek_boreas', 'olympian_borea'}

failures: list[str] = []
warnings: list[str] = []
infos: list[str] = []


def fail(section: str, msg: str) -> None:
    failures.append(f'[{section}] {msg}')


def warn(section: str, msg: str) -> None:
    warnings.append(f'[{section}] {msg}')


def info(msg: str) -> None:
    infos.append(msg)


def sha256_of(p: Path) -> str | None:
    if not p.exists():
        return None
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check_invariants() -> None:
    section = 'invariants'
    try:
        c5 = json.loads(HSK_5STAR.read_text(encoding='utf-8'))
    except Exception as e:
        fail(section, f'cannot read 5★ catalog: {e}')
        c5 = {'entries': []}
    try:
        c6 = json.loads(HSK_6STAR.read_text(encoding='utf-8'))
    except Exception as e:
        fail(section, f'cannot read 6★ catalog: {e}')
        c6 = {'entries': []}
    try:
        dw = json.loads(DW_CATALOG.read_text(encoding='utf-8'))
    except Exception as e:
        fail(section, f'cannot read DW catalog: {e}')
        dw = {'records': []}

    e5 = c5.get('entries') or []
    e6 = c6.get('entries') or []
    dwr = dw.get('records') or []
    if len(e5) != 20:
        fail(section, f'5★ entry count != 20 (got {len(e5)})')
    if len(e6) != 13:
        fail(section, f'6★ entry count != 13 (got {len(e6)})')
    if len(dwr) != 13:
        fail(section, f'DW record count != 13 (got {len(dwr)})')

    for label, entries in (('5★', e5), ('6★', e6)):
        for e in entries:
            hid = e.get('hero_id', '?')
            if hid in FORBIDDEN_HERO_IDS:
                fail(section, f'{label}: forbidden hero_id "{hid}" present')
            if e.get('runtime_attached') is True:
                fail(section, f'{label} {hid}: entry runtime_attached==true')
            for sn, slot in (e.get('skill_package') or {}).items():
                if not isinstance(slot, dict):
                    continue
                fn = slot.get('final_numbers')
                if fn is not None:
                    # Allow 5★ foundation_draft (RM1.32-A) AND 6★ foundation_draft (RM1.32-B)
                    is_foundation_draft = (
                        label in ('5★', '6★')
                        and isinstance(fn, dict)
                        and fn.get('status') == 'foundation_draft'
                        and fn.get('runtime_ready') is False
                    )
                    if not is_foundation_draft:
                        fail(section, f'{label} {hid}.{sn}: final_numbers != null')
                if slot.get('runtime_attached') is True:
                    fail(section, f'{label} {hid}.{sn}: runtime_attached==true')
                if slot.get('battle_runtime_attached') is True:
                    fail(section, f'{label} {hid}.{sn}: battle_runtime_attached==true')

    # Marchio Boreale leak in non-Borea 6★ entries
    for e in e6:
        hid = e.get('hero_id')
        if hid == 'greek_borea':
            continue
        if 'marchio_boreale' in json.dumps(e, ensure_ascii=False).lower():
            fail(section, f'6★ {hid}: marchio_boreale leaked into non-Borea record')

    # Top-level safety flags
    for label, cat in (('5★', c5), ('6★', c6)):
        if cat.get('runtime_attached') is not False:
            fail(section, f'{label} top-level runtime_attached != false')
        if cat.get('battle_runtime_attached') is not False:
            fail(section, f'{label} top-level battle_runtime_attached != false (RM1.31-D/RM1.30-A)')


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog='validate_hero_skill_kit_catalog_baseline_diff')
    ap.add_argument('--allow-changed', action='append', default=[],
                    help='File path allowed to differ from baseline (repeatable)')
    ap.add_argument('--summary-only', action='store_true',
                    help='Print current checksums without failing on diff')
    ap.add_argument('--baseline', default=None,
                    help='Path to the baseline snapshot JSON (default: auto-detect latest baseline file)')
    args = ap.parse_args(argv)

    if args.baseline:
        baseline_path = Path(args.baseline)
    else:
        latest = find_latest_baseline()
        if latest is None:
            fail('baseline', f'no baseline files found in {BASELINE_DIR} matching {BASELINE_GLOB!r}')
            return emit()
        baseline_path = latest
        info(f'auto-detected latest baseline: {baseline_path.name}')
    if not baseline_path.exists():
        fail('baseline', f'baseline file missing: {baseline_path}')
        return emit()
    try:
        baseline = json.loads(baseline_path.read_text(encoding='utf-8'))
    except Exception as e:
        fail('baseline', f'invalid baseline JSON: {e}')
        return emit()

    tracked = baseline.get('tracked_files') or {}
    if not tracked:
        fail('baseline', 'baseline has empty tracked_files map')
        return emit()

    allowed_changed = {str(Path(x).resolve()) for x in args.allow_changed}

    diffs: list[tuple[str, str, str | None]] = []  # (path, expected, actual)
    same: list[str] = []
    missing: list[str] = []
    current_checksums: dict[str, str | None] = {}
    for fpath, meta in tracked.items():
        expected = meta.get('sha256') if isinstance(meta, dict) else meta
        actual = sha256_of(Path(fpath))
        current_checksums[fpath] = actual
        if actual is None:
            missing.append(fpath)
            continue
        if actual != expected:
            if str(Path(fpath).resolve()) in allowed_changed:
                info(f'{fpath}: changed (ALLOWED by --allow-changed)')
                continue
            diffs.append((fpath, expected, actual))
        else:
            same.append(fpath)

    # Critical invariants always
    check_invariants()

    if args.summary_only:
        print('RM1.32-PRE — baseline diff SUMMARY-ONLY (no fail on diff)')
        for f, cur in current_checksums.items():
            exp = tracked[f].get('sha256') if isinstance(tracked[f], dict) else tracked[f]
            tag = 'same' if cur == exp else ('missing' if cur is None else 'DIFF')
            print(f'  [{tag}]  {f}')
            print(f'        baseline={exp}')
            print(f'        current ={cur}')
        if failures:
            print('Invariant failures:')
            for f in failures:
                print(f'  - {f}')
            return 1
        return 0

    if missing:
        for m in missing:
            fail('missing', f'tracked file missing: {m}')
    if diffs:
        for fpath, expected, actual in diffs:
            fail('diff', f'{fpath}: checksum changed (expected {expected[:16]}…, got {(actual or "<missing>")[:16]}…)')

    return emit(same=same, diffs=diffs, missing=missing, allowed=allowed_changed)


def emit(same=None, diffs=None, missing=None, allowed=None) -> int:
    if failures:
        print('FAIL: RM1.32-PRE — Catalog Baseline Diff Validator')
        for f in failures:
            print(f'  - {f}')
        if warnings:
            print('Warnings:')
            for w in warnings:
                print(f'  ! {w}')
        if infos:
            for i in infos:
                print(f'  i {i}')
        return 1
    print('PASS: RM1.32-PRE — Catalog Baseline Diff Validator')
    if same is not None:
        print(f'  tracked files unchanged:  {len(same)}')
        for s in same:
            print(f'    ✓ {s}')
    if diffs:
        print(f'  tracked files diff (allowed): {len(diffs)}')
    if missing:
        print(f'  missing tracked files: {len(missing)}')
    if allowed:
        print(f'  --allow-changed paths: {sorted(allowed)}')
    print('  Invariants:               5★=20, 6★=13, DW=13')
    print('  final_numbers / runtime flags: clean across 5★+6★ slots')
    print('  Marchio Boreale leak:     0 in non-Borea')
    print('  Forbidden hero IDs:       0 (borea / primordial_gaia / aliases)')
    if infos:
        print('Info:')
        for i in infos:
            print(f'  i {i}')
    if warnings:
        for w in warnings:
            print(f'  ! {w}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
