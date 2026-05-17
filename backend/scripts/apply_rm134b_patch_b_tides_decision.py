#!/usr/bin/env python3
"""
RM1.34-B-PATCH-B — Controlled tides faction decision.

DEFAULT DECISION: tides is only an `origin_group/lore tag` in the live
roster (Character Bible, heroes_master.json, heroes_kits_*.json). It
is NOT a canonical `faction` nor `faction_group` in the live data.
Therefore the matrix-level `faction_groups_included` entry `tides` is
a design orphan and is DEFERRED / removed from the canonical matrix.

This script:
- Confirms tides is absent from live `/api/heroes[*].faction` and from
  `/api/heroes[*].faction_group` (it MAY appear as `origin_group`
  which is preserved untouched).
- Removes 'tides' from doc['faction_groups_included'].
- Removes per-family 'tides' entries from
  `faction_resistance_modifiers` (if present).
- Stores metadata: tides_status='deferred_not_live',
  tides_removed_from_canonical_matrix=true,
  restore_condition='Character Bible / live roster confirms canonical
  faction (not origin_group)'.
- Writes the file in-place ONLY if `--apply` is passed.

NO DB / runtime / catalog mutation outside this matrix JSON.
NO change to roster / Character Bible / gacha.
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

ROOT = Path('/app')
MATRIX = ROOT / 'data' / 'design' / 'boss_systems' / 'boss_family_element_faction_matrix_v1.json'
LIVE_FILES = [
    ROOT / 'backend' / 'battle_engine.py',
    ROOT / 'backend' / 'battle_core.py',
    ROOT / 'frontend' / 'app' / 'combat.tsx',
]
PATCH_ID = 'RM1.34-B-PATCH-B'


def check_stop_gates() -> list[str]:
    """Verify tides is safe to defer (only origin_group, never faction)."""
    blockers: list[str] = []
    try:
        with urlopen('http://127.0.0.1:8001/api/heroes', timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        heroes = data if isinstance(data, list) else (data.get('heroes') or [])
        if len(heroes) != 100:
            blockers.append(f'/api/heroes count != 100 (got {len(heroes)})')
        # tides must NEVER appear as `faction` or `faction_group`
        bad_faction = [
            h.get('id') for h in heroes
            if isinstance(h, dict)
            and (str(h.get('faction') or '').lower() == 'tides'
                 or str(h.get('faction_group') or '').lower() == 'tides')
        ]
        if bad_faction:
            blockers.append(f'tides is a live faction/faction_group on: {bad_faction[:5]}')
    except (HTTPError, URLError, Exception) as e:
        blockers.append(f'/api/heroes unreachable: {e!r}')

    for f in LIVE_FILES:
        if f.exists() and 'tides_removed_from_canonical_matrix' in f.read_text(encoding='utf-8', errors='ignore'):
            blockers.append(f'{f.name} unexpectedly references tides_removed_from_canonical_matrix')

    return blockers


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--force', action='store_true')
    args = ap.parse_args(argv)

    print(f'{PATCH_ID} — tides deferral patch')
    print('=' * 70)
    blockers = check_stop_gates()
    if blockers:
        print('STOP GATES TRIGGERED:')
        for b in blockers:
            print(f'  - {b}')
        if not args.force:
            print('Aborting (use --force to override; not recommended).')
            return 2

    if not MATRIX.exists():
        print(f'Matrix missing: {MATRIX}')
        return 1
    doc = json.loads(MATRIX.read_text(encoding='utf-8'))

    fgi = doc.get('faction_groups_included') or []
    print(f'faction_groups_included before: {fgi}')

    tides_present_now = 'tides' in fgi
    if tides_present_now:
        doc['faction_groups_included'] = [f for f in fgi if f != 'tides']
    else:
        print('tides already absent from faction_groups_included.')

    # Remove tides from per-family faction_resistance_modifiers
    families = doc.get('boss_families') or []
    per_family_removed: int = 0
    if isinstance(families, list):
        for fam in families:
            if not isinstance(fam, dict):
                continue
            frm = fam.get('faction_resistance_modifiers')
            if isinstance(frm, dict) and 'tides' in frm:
                # Preserve modifier history under tides_deferred_modifiers
                hist = fam.setdefault('tides_deferred_modifiers_history', {})
                hist[PATCH_ID] = frm.pop('tides')
                per_family_removed += 1
    elif isinstance(families, dict):
        for _, fam in families.items():
            if not isinstance(fam, dict):
                continue
            frm = fam.get('faction_resistance_modifiers')
            if isinstance(frm, dict) and 'tides' in frm:
                hist = fam.setdefault('tides_deferred_modifiers_history', {})
                hist[PATCH_ID] = frm.pop('tides')
                per_family_removed += 1

    print(f'Per-family tides modifier entries deferred: {per_family_removed}')

    # Metadata
    meta = doc.get('metadata') or {}
    meta.setdefault('axis_patches_applied', [])
    if PATCH_ID not in meta['axis_patches_applied']:
        meta['axis_patches_applied'].append(PATCH_ID)
    meta['tides_status'] = 'deferred_not_live'
    meta['tides_removed_from_canonical_matrix'] = True
    meta['tides_origin_group_lore_preserved'] = True
    meta['tides_restore_condition'] = (
        'Character Bible / live roster confirms tides as a canonical '
        'faction (not origin_group). Until then, tides remains a lore tag.'
    )
    meta.setdefault('tides_deferral_history', []).append({
        'patch_id': PATCH_ID,
        'action': 'remove_from_faction_groups_included_and_per_family_modifiers',
        'applied_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'design_only': True,
        'runtime_attached': False,
        'origin_group_lore_preserved': True,
        'per_family_modifier_entries_deferred': per_family_removed,
    })
    meta['runtime_attached'] = False
    meta['design_only'] = True
    doc['metadata'] = meta

    if args.apply:
        MATRIX.write_text(
            json.dumps(doc, indent=2, ensure_ascii=False) + '\n',
            encoding='utf-8',
        )
        print(f'PATCH APPLIED: {MATRIX}')
    else:
        print('DRY-RUN: matrix NOT written. Pass --apply to commit.')
    print('Done.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
