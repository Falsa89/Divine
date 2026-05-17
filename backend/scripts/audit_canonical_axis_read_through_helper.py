#!/usr/bin/env python3
"""
AXIS-E — Canonical Axis Read-Through Helper safety audit.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path('/app')
HELPER = ROOT / 'backend' / 'data' / 'canonical_axis_read_through_helper.py'
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


sys.path.insert(0, str(ROOT / 'backend'))
from data import canonical_axis_read_through_helper as h  # type: ignore

record('helper_present', HELPER.exists(), str(HELPER))

# 1. Element resolution
r = h.resolve_element('darkness')
record('darkness_canonical_dark', r.get('canonical') == 'dark', f'{r}')
record('darkness_valid', r.get('valid') is True, '')
record('darkness_status_aliased',
       r.get('status') == 'aliased_to_live', '')
r = h.resolve_element('water')
record('water_canonical_water', r.get('canonical') == 'water', '')
record('water_valid', r.get('valid') is True, '')
r = h.resolve_element('xyz_unknown')
record('unknown_element_invalid', r.get('valid') is False, '')
record('unknown_element_status_unknown', r.get('status') == 'unknown', '')

# 2. Faction resolution
r = h.resolve_faction('tides')
record('tides_design_pending', r.get('status') == 'design_pending', '')
record('tides_invalid', r.get('valid') is False, '')
r = h.resolve_faction('greek')
record('greek_valid', r.get('valid') is True, '')
r = h.resolve_faction('beasts')
record('beasts_aliased', r.get('canonical') == 'creature_beast', '')

# 3. Bulk APIs
b = h.resolve_elements_bulk(['dark', 'darkness', 'water', 'xyz'])
record('bulk_elements_count_input', b.get('count_input') == 4, '')
record('bulk_elements_count_valid', b.get('count_valid') == 3, '')
record('bulk_elements_count_unknown', b.get('count_unknown') == 1, '')
record('bulk_elements_envelope_runtime_attached_false',
       b.get('runtime_attached') is False, '')

b = h.resolve_factions_bulk(['greek', 'tides', 'beasts', 'xyz'])
record('bulk_factions_count_input', b.get('count_input') == 4, '')
record('bulk_factions_count_valid', b.get('count_valid') == 2, '')
record('bulk_factions_count_design_pending',
       b.get('count_design_pending') == 1, '')
record('bulk_factions_count_unknown', b.get('count_unknown') == 1, '')
record('bulk_factions_envelope_db_write_false',
       b.get('db_write') is False, '')

# 4. axis_health composite
ah = h.axis_health()
record('axis_health_darkness_to_dark',
       ah.get('darkness_resolves_to_dark') is True, '')
record('axis_health_dark_to_dark',
       ah.get('dark_resolves_to_dark') is True, '')
record('axis_health_fire_to_fire',
       ah.get('fire_resolves_to_fire') is True, '')
record('axis_health_greek_to_greek',
       ah.get('greek_resolves_to_greek') is True, '')
record('axis_health_tides_design_pending',
       ah.get('tides_is_design_pending') is True, '')
record('axis_health_mutates_source_tables_false',
       ah.get('mutates_source_tables') is False, '')

# 5. Manifest sanity
m = h.ADAPTER_MANIFEST
for k in ['writes_to_db', 'writes_to_catalogs', 'writes_to_runtime',
          'imported_by_battle_engine', 'imported_by_battle_core',
          'imported_by_combat_tsx', 'applied_to_combat',
          'mutates_source_tables', 'patches_rm134b', 'patches_af2a']:
    record(f'manifest_{k}_false', m.get(k) is False, '')
record('manifest_no_borea_activation', m.get('no_borea_activation') is True, '')
record('manifest_composes_axis_b', m.get('composes_axis_b') is True, '')

# 6. Live runtime files do not import the helper
tokens = ['canonical_axis_read_through_helper', 'resolve_elements_bulk',
          'resolve_factions_bulk', 'axis_health']
for f in LIVE_FILES:
    if not f.exists():
        record(f'live_file:{f.name}', True, 'absent')
        continue
    txt = f.read_text(encoding='utf-8', errors='ignore')
    for tok in tokens:
        ok = re.search(re.escape(tok), txt) is None
        record(f'no_runtime_import:{f.name}:{tok}', ok,
               f'token found' if not ok else '')

print('=' * 70)
print('AXIS-E — Canonical Axis Read-Through Helper Safety Audit')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
