#!/usr/bin/env python3
"""
RM1.34-B-PATCH-A — Controlled source patch: rename canonical element
key `darkness` -> `dark` in the boss family element/faction matrix.

Behavior:
- Reads /app/data/design/boss_systems/boss_family_element_faction_matrix_v1.json
- Replaces every textual occurrence of the canonical token "darkness"
  with "dark" in keys/values where the token is recognized as the
  canonical element.
- Preserves every numeric value, modifier, note, tag and family count.
- Adds patch metadata into the file: axis_patch_id,
  darkness_to_dark_applied, previous_alias_preserved_in_history,
  design_only, runtime_attached.
- Writes the file in-place ONLY if `--apply` is passed.
- Default: `--dry-run` — prints the change set and exits 0.

Stop-gates enforced inside this script:
- /app/api/heroes must be reachable AND return exactly 100 heroes
  with no Borea aliases (verified at the API level).
- backup directory MUST exist (the latest /app/backups/axis_patch_rm134b_pre_*).
- battle_engine.py / battle_core.py / combat.tsx MUST NOT mention
  `darkness_to_dark_applied` (this script never touches them).

NO DB / runtime / catalog mutation outside the single matrix JSON.
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
BACKUPS_DIR = ROOT / 'backups'
LIVE_FILES = [
    ROOT / 'backend' / 'battle_engine.py',
    ROOT / 'backend' / 'battle_core.py',
    ROOT / 'frontend' / 'app' / 'combat.tsx',
]

# Patch metadata
PATCH_ID = 'RM1.34-B-PATCH-A'


def _replace_token(obj, old: str, new: str) -> int:
    """Recursively replace the token `old` with `new` in dict keys
    and exact-match string values. Returns the number of replacements.
    """
    count = 0
    if isinstance(obj, dict):
        keys = list(obj.keys())
        for k in keys:
            v = obj[k]
            if isinstance(k, str) and k == old:
                obj[new] = obj.pop(k)
                count += 1
                v = obj[new]
            n = _replace_token(v, old, new)
            count += n
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, str) and v == old:
                obj[i] = new
                count += 1
            else:
                count += _replace_token(v, old, new)
    return count


def check_stop_gates() -> list[str]:
    blockers: list[str] = []
    # 1. /api/heroes
    try:
        with urlopen('http://127.0.0.1:8001/api/heroes', timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        heroes = data if isinstance(data, list) else (data.get('heroes') or [])
        if len(heroes) != 100:
            blockers.append(f'/api/heroes count != 100 (got {len(heroes)})')
        ids = {h.get('id') for h in heroes if isinstance(h, dict)}
        if 'borea' in ids or 'greek_borea' in ids or 'primordial_gaia' in ids:
            blockers.append('Borea alias present in /api/heroes')
    except (HTTPError, URLError, Exception) as e:
        blockers.append(f'/api/heroes unreachable: {e!r}')

    # 2. backup directory
    if not BACKUPS_DIR.exists() or not any(
        p.name.startswith('axis_patch_rm134b_pre_') for p in BACKUPS_DIR.iterdir()
    ):
        blockers.append('no axis_patch_rm134b_pre_* backup directory found')

    # 3. live files MUST NOT already mention darkness_to_dark_applied
    for f in LIVE_FILES:
        if f.exists() and 'darkness_to_dark_applied' in f.read_text(encoding='utf-8', errors='ignore'):
            blockers.append(f'{f.name} unexpectedly references darkness_to_dark_applied')

    return blockers


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true',
                    help='Write the matrix file in place')
    ap.add_argument('--force', action='store_true',
                    help='Apply even if stop gates are flagged (NOT recommended)')
    args = ap.parse_args(argv)

    print(f'{PATCH_ID} — darkness -> dark canonical element patch')
    print('=' * 70)
    blockers = check_stop_gates()
    if blockers:
        print('STOP GATES TRIGGERED:')
        for b in blockers:
            print(f'  - {b}')
        if not args.force:
            print('Aborting (use --force to override; not recommended).')
            return 2
        print('Continuing because --force was passed.')

    if not MATRIX.exists():
        print(f'Matrix not found: {MATRIX}')
        return 1

    doc = json.loads(MATRIX.read_text(encoding='utf-8'))

    elements = doc.get('elements_included') or []
    print(f'Elements before: {elements}')
    if 'darkness' not in elements:
        if 'dark' in elements:
            print('Already patched: "dark" present, "darkness" absent. NOOP.')
            return 0
        print('Cannot patch: neither "darkness" nor "dark" in elements_included.')
        return 1

    # Replace canonical token recursively
    replacements = _replace_token(doc, 'darkness', 'dark')
    print(f'Replacements made (canonical token only): {replacements}')

    # Metadata
    meta = doc.get('metadata') or {}
    if isinstance(meta, dict):
        meta.setdefault('axis_patches_applied', [])
        if PATCH_ID not in meta['axis_patches_applied']:
            meta['axis_patches_applied'].append(PATCH_ID)
        meta['darkness_to_dark_applied'] = True
        meta['previous_alias_preserved_in_history'] = True
        meta['darkness_alias_history'] = (
            meta.get('darkness_alias_history') or []
        ) + [{
            'patch_id': PATCH_ID,
            'from': 'darkness',
            'to': 'dark',
            'applied_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'design_only': True,
            'runtime_attached': False,
        }]
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
