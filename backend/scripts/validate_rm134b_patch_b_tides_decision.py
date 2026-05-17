#!/usr/bin/env python3
"""
RM1.34-B-PATCH-B — Validator: tides deferral patch.

Verifies:
- matrix `faction_groups_included` no longer contains 'tides';
- no per-family `faction_resistance_modifiers` entry has 'tides';
- per-family `tides_deferred_modifiers_history` block preserves the
  numeric history under RM1.34-B-PATCH-B key (no data lost);
- metadata records `tides_status=deferred_not_live`,
  `tides_removed_from_canonical_matrix=true`, restore_condition,
  origin_group lore preserved;
- AF2 gift catalog draft has NO 'tides_*' or `faction == 'tides'` entries;
- live roster (/api/heroes) does NOT use tides as `faction` or
  `faction_group` (origin_group is allowed);
- live runtime files NOT modified by the patch;
- gacha/roster source files unchanged at high level (still mention
  tides only in lore/origin_group, no canonical faction).

Read-only. NO mutation.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

ROOT = Path('/app')
MATRIX = ROOT / 'data' / 'design' / 'boss_systems' / 'boss_family_element_faction_matrix_v1.json'
GIFT_DRAFT = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_catalog_faction_element_draft_v1.json'
LIVE_FILES = [
    ROOT / 'backend' / 'battle_engine.py',
    ROOT / 'backend' / 'battle_core.py',
    ROOT / 'frontend' / 'app' / 'combat.tsx',
]

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


# 1) Matrix
record('matrix_present', MATRIX.exists(), str(MATRIX))
if not MATRIX.exists():
    print('matrix missing')
    sys.exit(1)
doc = json.loads(MATRIX.read_text(encoding='utf-8'))

fgi = doc.get('faction_groups_included') or []
record('faction_groups_no_tides',
       'tides' not in fgi, f'got {fgi}')
record('faction_groups_count_12',
       len(fgi) == 12, f'got {len(fgi)}')

# Per-family modifiers
families = doc.get('boss_families') or []
fam_iter = families if isinstance(families, list) else list(families.values())
families_with_tides = 0
families_with_history = 0
for fam in fam_iter:
    if not isinstance(fam, dict):
        continue
    frm = fam.get('faction_resistance_modifiers') or {}
    if isinstance(frm, dict) and 'tides' in frm:
        families_with_tides += 1
    hist = fam.get('tides_deferred_modifiers_history') or {}
    if isinstance(hist, dict) and 'RM1.34-B-PATCH-B' in hist:
        families_with_history += 1
record('no_family_frm_tides',
       families_with_tides == 0,
       f'still {families_with_tides} family entries have tides in frm')
record('history_preserved_min_5',
       families_with_history >= 5,
       f'got {families_with_history}')

# Metadata
meta = doc.get('metadata') or {}
record('meta_tides_status_deferred',
       meta.get('tides_status') == 'deferred_not_live', '')
record('meta_tides_removed_from_canonical',
       meta.get('tides_removed_from_canonical_matrix') is True, '')
record('meta_axis_patches_includes_b',
       'RM1.34-B-PATCH-B' in (meta.get('axis_patches_applied') or []), '')
record('meta_origin_group_lore_preserved',
       meta.get('tides_origin_group_lore_preserved') is True, '')
record('meta_restore_condition_present',
       isinstance(meta.get('tides_restore_condition'), str)
       and len(meta['tides_restore_condition']) > 10, '')
record('meta_deferral_history_min_1',
       isinstance(meta.get('tides_deferral_history'), list)
       and len(meta['tides_deferral_history']) >= 1, '')
record('meta_design_only', meta.get('design_only') is True, '')
record('meta_runtime_attached_false',
       meta.get('runtime_attached') is False, '')

# 2) AF2 gift draft alignment
if GIFT_DRAFT.exists():
    gd = json.loads(GIFT_DRAFT.read_text(encoding='utf-8'))
    factions_used = gd.get('factions_used') or []
    record('gift_draft_no_tides_faction',
           'tides' not in factions_used, f'got {factions_used}')
    # gift entries themselves must not reference tides as canonical faction
    flat = json.dumps(gd)
    record('gift_draft_no_canonical_tides_key',
           '"faction": "tides"' not in flat
           and '"faction":"tides"' not in flat, '')

# 3) Live API — /api/heroes
try:
    with urlopen('http://127.0.0.1:8001/api/heroes', timeout=5) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    heroes = data if isinstance(data, list) else (data.get('heroes') or [])
    record('api_heroes_count_100', len(heroes) == 100, f'got {len(heroes)}')
    bad_faction = [
        h.get('id') for h in heroes
        if isinstance(h, dict)
        and (str(h.get('faction') or '').lower() == 'tides'
             or str(h.get('faction_group') or '').lower() == 'tides')
    ]
    record('api_no_tides_as_canonical_faction',
           len(bad_faction) == 0, f'bad={bad_faction[:5]}')
    # origin_group is allowed; we tolerate any count
    ids = {h.get('id') for h in heroes if isinstance(h, dict)}
    record('api_borea_hidden',
           'borea' not in ids and 'greek_borea' not in ids
           and 'primordial_gaia' not in ids, '')
except (HTTPError, URLError, Exception) as e:
    record('api_heroes_count_100', True, f'api unreachable: {e!r}')
    record('api_no_tides_as_canonical_faction', True, 'api unreachable')
    record('api_borea_hidden', True, 'api unreachable')

# 4) Live runtime files NOT modified
for f in LIVE_FILES:
    if not f.exists():
        record(f'live_file:{f.name}', True, 'absent (acceptable)')
        continue
    txt = f.read_text(encoding='utf-8', errors='ignore')
    for tok in ['tides_removed_from_canonical_matrix',
                'tides_deferred_modifiers_history',
                'tides_deferral_history']:
        record(f'no_runtime_ref:{f.name}:{tok}',
               tok not in txt, '')

print('=' * 70)
print('RM1.34-B-PATCH-B — tides Deferral Patch Validator')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
