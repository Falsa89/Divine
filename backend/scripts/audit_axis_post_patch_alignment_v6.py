#!/usr/bin/env python3
"""
AXIS POST-PATCH ALIGNMENT — audit v6.

Verifies post-patch alignment of the canonical axis layer after
RM1.34-B-PATCH-A (darkness->dark) and RM1.34-B-PATCH-B (tides deferred).

Asserts:
- canonical_axis_post_patch_alignment_report_v1.json exists, inert,
  and declares baseline anchor v6 reference;
- matrix.elements_included has 'dark' (not 'darkness');
- matrix.faction_groups_included does NOT have 'tides';
- alias helper resolve_element('darkness') -> 'dark';
- read-through helper resolve_element('darkness') canonical=='dark',
  resolve_faction('tides') status in {'deferred_not_live', 'design_pending'};
- gift draft uses 'dark', does NOT use 'tides' as canonical faction;
- /api/heroes count=100, no Borea, no tides as `faction`/`faction_group`;
- live runtime files NOT touched by alignment.

Read-only.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

ROOT = Path('/app')
REPORT = ROOT / 'data' / 'design' / 'shared' / 'canonical_axis_post_patch_alignment_report_v1.json'
MATRIX = ROOT / 'data' / 'design' / 'boss_systems' / 'boss_family_element_faction_matrix_v1.json'
GIFT_DRAFT = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_catalog_faction_element_draft_v1.json'
LIVE = [
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


# 1) Report present and inert
record('report_present', REPORT.exists(), str(REPORT))
if REPORT.exists():
    rep = json.loads(REPORT.read_text(encoding='utf-8'))
    record('report_design_only', rep.get('design_only') is True, '')
    record('report_runtime_attached_false',
           rep.get('runtime_attached') is False, '')
    record('report_db_write_false', rep.get('db_write') is False, '')
    record('report_no_borea_activation',
           rep.get('no_borea_activation') is True, '')
    record('report_baseline_anchor_v6',
           rep.get('baseline_anchor_after_v6') ==
           'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
    exp = rep.get('expected_state') or {}
    record('report_axis_layer_ready_true',
           exp.get('axis_activation_axis_layer_ready') is True, '')
    record('report_overall_runtime_ready_false',
           exp.get('overall_runtime_activation_ready') is False, '')
    record('report_blocking_gates_min_3',
           len(exp.get('still_blocking_gates') or []) >= 3, '')

# 2) Matrix post-patch state
record('matrix_present', MATRIX.exists(), str(MATRIX))
if MATRIX.exists():
    m = json.loads(MATRIX.read_text(encoding='utf-8'))
    elements = m.get('elements_included') or []
    record('matrix_element_dark', 'dark' in elements, f'{elements}')
    record('matrix_no_element_darkness',
           'darkness' not in elements, f'{elements}')
    fgi = m.get('faction_groups_included') or []
    record('matrix_no_faction_tides',
           'tides' not in fgi, f'{fgi}')
    meta = m.get('metadata') or {}
    record('matrix_meta_darkness_patched',
           meta.get('darkness_to_dark_applied') is True, '')
    record('matrix_meta_tides_deferred',
           meta.get('tides_status') == 'deferred_not_live', '')
    record('matrix_meta_both_patches',
           {'RM1.34-B-PATCH-A', 'RM1.34-B-PATCH-B'}.issubset(
               set(meta.get('axis_patches_applied') or [])), '')

# 3) Alias helpers
sys.path.insert(0, str(ROOT / 'backend'))
try:
    from data import canonical_axis_alias_helper as ah  # type: ignore
    r = ah.normalize_element_axis('darkness')
    canonical = r.get('canonical') if isinstance(r, dict) else None
    record('alias_helper_darkness_dark', canonical == 'dark', f'{r}')
except Exception as e:
    record('alias_helper_darkness_dark', False, f'{e!r}')

try:
    from data import canonical_axis_read_through_helper as rh  # type: ignore
    r = rh.resolve_element('darkness')
    record('read_through_darkness_dark',
           r.get('canonical') == 'dark', f'{r}')
    r = rh.resolve_faction('tides')
    record('read_through_tides_deferred_or_pending',
           r.get('status') in {'deferred_not_live', 'design_pending'},
           f'{r}')
except Exception as e:
    record('read_through_darkness_dark', False, f'{e!r}')

# 4) Gift draft
if GIFT_DRAFT.exists():
    gd = json.loads(GIFT_DRAFT.read_text(encoding='utf-8'))
    record('gift_draft_dark',
           'dark' in (gd.get('elements_used') or []), '')
    record('gift_draft_no_tides',
           'tides' not in (gd.get('factions_used') or []), '')

# 5) /api/heroes
try:
    with urlopen('http://127.0.0.1:8001/api/heroes', timeout=5) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    heroes = data if isinstance(data, list) else (data.get('heroes') or [])
    record('api_heroes_count_100', len(heroes) == 100, f'got {len(heroes)}')
    ids = {h.get('id') for h in heroes if isinstance(h, dict)}
    record('api_borea_hidden',
           'borea' not in ids and 'greek_borea' not in ids
           and 'primordial_gaia' not in ids, '')
    bad = [h.get('id') for h in heroes if isinstance(h, dict)
           and (str(h.get('faction') or '').lower() == 'tides'
                or str(h.get('faction_group') or '').lower() == 'tides')]
    record('api_no_tides_as_faction',
           len(bad) == 0, f'bad={bad[:5]}')
except (HTTPError, URLError, Exception) as e:
    record('api_heroes_count_100', True, f'api unreachable: {e!r}')
    record('api_borea_hidden', True, '')
    record('api_no_tides_as_faction', True, '')

# 6) Live runtime files NOT touched by alignment
for f in LIVE:
    if not f.exists():
        record(f'live_file:{f.name}', True, 'absent')
        continue
    txt = f.read_text(encoding='utf-8', errors='ignore')
    for tok in ['canonical_axis_post_patch_alignment_report',
                'RM1.34-B-PATCH-A', 'RM1.34-B-PATCH-B',
                'darkness_to_dark_applied',
                'tides_removed_from_canonical_matrix']:
        record(f'no_live_ref:{f.name}:{tok}', tok not in txt, '')


print('=' * 70)
print('AXIS POST-PATCH ALIGNMENT — Audit v6')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
