#!/usr/bin/env python3
"""
AXIS-B — Canonical Axis Alias Helper safety audit.

Verifies:
  - helper imports cleanly
  - darkness, dark, Oscurita, shadow normalize to 'dark'
  - tides faction is reported as design_pending / not_live
  - live roster tokens resolve to themselves
  - unknown tokens return status='unknown' (not raise)
  - helper not imported by battle_engine.py / battle_core.py / combat.tsx
  - no source JSON mutated (RM1.34-B / AF2-A still untouched)
  - gift draft still uses roster spelling 'dark' and does not mint tides_*
  - matrix still contains darkness / tides until a controlled patch

Read-only. Exit 0 on PASS, non-zero on FAIL.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path('/app')
HELPER = ROOT / 'backend' / 'data' / 'canonical_axis_alias_helper.py'
AXIS_PLAN = ROOT / 'data' / 'design' / 'shared' / 'canonical_faction_element_axis_resolution_plan_v1.json'
BOSS_MATRIX = ROOT / 'data' / 'design' / 'boss_systems' / 'boss_family_element_faction_matrix_v1.json'
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


# 1. Import helper
sys.path.insert(0, str(ROOT / 'backend'))
try:
    from data import canonical_axis_alias_helper as cah  # type: ignore
    record('import_helper', True, '')
except Exception as e:
    record('import_helper', False, f'{e!r}')
    for n, ok, note in checks:
        print(f'  [{ "OK" if ok else "X" }] {n} {note}')
    sys.exit(1)

# 2. Element normalization
def _check_elem(inp: str, expect_canonical: str | None,
                expect_status_in: tuple[str, ...]) -> None:
    r = cah.normalize_element_axis(inp)
    record(f'elem_canonical:{inp}', r.get('canonical') == expect_canonical,
           f'expected {expect_canonical}, got {r.get("canonical")!r}')
    record(f'elem_status:{inp}', r.get('status') in expect_status_in,
           f'expected one of {expect_status_in}, got {r.get("status")!r}')


_check_elem('darkness', 'dark', ('aliased_to_live',))
_check_elem('dark', 'dark', ('live',))
_check_elem('Oscurita', 'dark', ('aliased_to_live',))
_check_elem('shadow', 'dark', ('aliased_to_live',))
_check_elem('water', 'water', ('live',))
_check_elem('fire', 'fire', ('live',))
_check_elem('bogus_element_xyz', None, ('unknown',))

# 3. Faction normalization
def _check_fac(inp: str, expect_canonical: str | None,
               expect_status_in: tuple[str, ...],
               expect_design_pending: bool = False) -> None:
    r = cah.normalize_faction_axis(inp)
    record(f'fac_canonical:{inp}', r.get('canonical') == expect_canonical,
           f'expected {expect_canonical}, got {r.get("canonical")!r}')
    record(f'fac_status:{inp}', r.get('status') in expect_status_in,
           f'expected one of {expect_status_in}, got {r.get("status")!r}')
    record(f'fac_design_pending:{inp}',
           bool(r.get('design_pending')) == expect_design_pending,
           f'expected {expect_design_pending}, got {r.get("design_pending")!r}')


_check_fac('tides', None, ('design_pending',), expect_design_pending=True)
_check_fac('greek', 'greek', ('live',))
_check_fac('japanese_yokai', 'japanese_yokai', ('live',))
_check_fac('yokai', 'japanese_yokai', ('aliased_to_live',))
_check_fac('beasts', 'creature_beast', ('aliased_to_live',))
_check_fac('bogus_faction_xyz', None, ('unknown',))

# 4. validate_axis_value
r = cah.validate_axis_value('darkness', 'element')
record('validate_darkness_valid', r.get('valid') is True, f'{r}')
r = cah.validate_axis_value('tides', 'faction')
record('validate_tides_invalid', r.get('valid') is False, f'{r}')
r = cah.validate_axis_value('greek', 'faction')
record('validate_greek_valid', r.get('valid') is True, f'{r}')
r = cah.validate_axis_value('water', 'element')
record('validate_water_valid', r.get('valid') is True, f'{r}')
r = cah.validate_axis_value('xyz', 'unknown_axis')
record('validate_unknown_axis_type', r.get('valid') is False, '')

# 5. preview_axis_alignment shape
pa = cah.preview_axis_alignment()
for k in ['runtime_attached', 'applied_to_combat', 'db_write']:
    record(f'preview_alignment_{k}_false', pa.get(k) is False, '')
record('preview_alignment_no_source_mutation',
       pa.get('mutates_source_tables') is False, '')
record('preview_alignment_no_patch_rm134b', pa.get('patches_rm134b') is False, '')
record('preview_alignment_no_patch_af2a', pa.get('patches_af2a') is False, '')
record('preview_alignment_design_pending_factions',
       'tides' in (pa.get('design_pending_factions') or []), '')

# 6. helper not imported by live runtime files
tokens = ['canonical_axis_alias_helper', 'normalize_element_axis',
          'normalize_faction_axis']
for f in LIVE_FILES:
    if not f.exists():
        record(f'live_file_present:{f.name}', True, f'absent (skipped)')
        continue
    txt = f.read_text(encoding='utf-8', errors='ignore')
    for tok in tokens:
        ok = re.search(re.escape(tok), txt) is None
        record(f'no_runtime_import:{f.name}:{tok}', ok,
               f'token found' if not ok else '')

# 7. Source tables unmodified
# RM1.34-B still contains darkness + tides
if BOSS_MATRIX.exists():
    m = json.loads(BOSS_MATRIX.read_text(encoding='utf-8'))
    record('boss_matrix_still_contains_darkness',
           'darkness' in (m.get('elements_included') or []),
           'matrix MUST still contain darkness until controlled patch')
    record('boss_matrix_still_contains_tides',
           'tides' in (m.get('faction_groups_included') or []),
           'matrix MUST still contain tides until controlled patch')

# AF2-A gift draft still uses roster spelling dark, no tides_*
if GIFT_DRAFT.exists():
    g = json.loads(GIFT_DRAFT.read_text(encoding='utf-8'))
    record('gift_draft_uses_dark', 'dark' in (g.get('elements_used') or []), '')
    record('gift_draft_no_darkness',
           'darkness' not in (g.get('elements_used') or []),
           'gift draft must not introduce darkness spelling')
    record('gift_draft_no_tides_faction',
           'tides' not in (g.get('factions_used') or []), '')
    entries = g.get('entries') or []
    tides_ids = [e.get('id') for e in entries
                 if isinstance(e, dict) and isinstance(e.get('id'), str)
                 and 'tides_' in e.get('id', '')]
    record('gift_draft_no_tides_entries', not tides_ids,
           f'unexpected tides_*: {tides_ids}')

# 8. Manifest sanity
m = getattr(cah, 'ADAPTER_MANIFEST', {})
for k in ['writes_to_db', 'writes_to_catalogs', 'writes_to_runtime',
          'imported_by_battle_engine', 'imported_by_combat_tsx',
          'applied_to_combat', 'mutates_source_tables',
          'patches_rm134b', 'patches_af2a']:
    record(f'manifest_{k}_false', m.get(k) is False, f'got {m.get(k)!r}')
record('manifest_no_borea_activation', m.get('no_borea_activation') is True, '')


print('=' * 70)
print('AXIS-B — Canonical Axis Alias Helper Safety Audit')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
