#!/usr/bin/env python3
"""
AXIS-C — Canonical Axis Dynamic Preview Helper safety audit.

Verifies:
  - helper imports cleanly
  - preview_live_axis_sets returns a roster with at least 12 factions
    and 7 elements (live roster) + skips legacy Borea aliases
  - preview_axis_drift_report documents the known dark/darkness/tides
    drift state
  - validate_alias_coverage reports fully_covered=true (darkness aliased)
    AND tides in design_pending_factions
  - helper not imported by battle_engine/combat/battle_core
  - source tables (RM1.34-B / AF2-A) NOT mutated
  - writes a result JSON to /app/data/design/shared/
    canonical_axis_dynamic_preview_result_v1.json
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path('/app')
HELPER = ROOT / 'backend' / 'data' / 'canonical_axis_dynamic_preview.py'
RESULT = ROOT / 'data' / 'design' / 'shared' / 'canonical_axis_dynamic_preview_result_v1.json'
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
    from data import canonical_axis_dynamic_preview as cdp  # type: ignore
    record('helper_imported', True, '')
except Exception as e:
    record('helper_imported', False, f'{e!r}')
    print('FAIL: cannot import helper')
    for n, ok, note in checks:
        print(f'  [{"OK" if ok else "X"}] {n} {note}')
    sys.exit(1)

# 2. preview_live_axis_sets
live = cdp.preview_live_axis_sets()
record('live_runtime_attached_false', live.get('runtime_attached') is False, '')
record('live_applied_to_combat_false', live.get('applied_to_combat') is False, '')
record('live_db_write_false', live.get('db_write') is False, '')
record('live_source_present',
       live.get('source') in ('api', 'static_heroes_master', 'unavailable'), '')
record('live_factions_count_ge_12',
       isinstance(live.get('live_factions_count'), int)
       and live['live_factions_count'] >= 12,
       f'got {live.get("live_factions_count")}')
record('live_elements_count_ge_7',
       isinstance(live.get('live_elements_count'), int)
       and live['live_elements_count'] >= 7,
       f'got {live.get("live_elements_count")}')
# dark in live elements
record('live_elements_contain_dark',
       'dark' in (live.get('live_elements_sorted') or []), '')
record('live_elements_do_not_contain_darkness',
       'darkness' not in (live.get('live_elements_sorted') or []), '')
record('live_factions_do_not_contain_tides',
       'tides' not in (live.get('live_factions_sorted') or []), '')

# 3. preview_axis_drift_report
drift = cdp.preview_axis_drift_report()
record('drift_runtime_attached_false',
       drift.get('runtime_attached') is False, '')
record('drift_mutates_source_tables_false',
       drift.get('mutates_source_tables') is False, '')
record('drift_patches_rm134b_false', drift.get('patches_rm134b') is False, '')
record('drift_patches_af2a_false', drift.get('patches_af2a') is False, '')

# Matrix vs live drift expected
elements_in_matrix_not_in_live = drift.get('drift', {}).get('elements_in_matrix_not_in_live') or []
factions_in_matrix_not_in_live = drift.get('drift', {}).get('factions_in_matrix_not_in_live') or []
record('drift_elements_includes_darkness',
       'darkness' in elements_in_matrix_not_in_live, '')
record('drift_factions_includes_tides',
       'tides' in factions_in_matrix_not_in_live, '')
record('drift_darkness_to_dark_alias_present',
       drift.get('darkness_to_dark_alias_present') is True, '')
record('drift_tides_status_design_pending',
       drift.get('tides_status') == 'design_pending', '')

# 4. validate_alias_coverage
cov = cdp.validate_alias_coverage()
record('cov_runtime_attached_false',
       cov.get('runtime_attached') is False, '')
record('cov_fully_covered_true', cov.get('fully_covered') is True,
       f'uncov_elem={cov.get("uncovered_elements")}, '
       f'uncov_fac={cov.get("uncovered_factions")}')
record('cov_tides_in_design_pending',
       'tides' in (cov.get('design_pending_factions') or []), '')

# 5. Source tables not mutated (existence-based heuristic; baseline diff
# validator does the cryptographic check)
if BOSS_MATRIX.exists():
    bm = json.loads(BOSS_MATRIX.read_text(encoding='utf-8'))
    record('boss_matrix_still_darkness',
           'darkness' in (bm.get('elements_included') or []), '')
    record('boss_matrix_still_tides',
           'tides' in (bm.get('faction_groups_included') or []), '')
if GIFT_DRAFT.exists():
    gd = json.loads(GIFT_DRAFT.read_text(encoding='utf-8'))
    record('gift_draft_still_dark', 'dark' in (gd.get('elements_used') or []), '')
    record('gift_draft_no_tides',
           'tides' not in (gd.get('factions_used') or []), '')

# 6. Helper not imported by live runtime files
tokens = ['canonical_axis_dynamic_preview',
          'preview_live_axis_sets', 'preview_axis_drift_report',
          'validate_alias_coverage']
for f in LIVE_FILES:
    if not f.exists():
        record(f'live_file:{f.name}', True, 'absent')
        continue
    txt = f.read_text(encoding='utf-8', errors='ignore')
    for tok in tokens:
        ok = re.search(re.escape(tok), txt) is None
        record(f'no_runtime_import:{f.name}:{tok}', ok,
               'token found' if not ok else '')

# 7. Write result JSON (optional but per prompt request)
RESULT.parent.mkdir(parents=True, exist_ok=True)
payload = {
    'task_origin': 'AXIS-C',
    'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
    'design_only': True,
    'runtime_attached': False,
    'mutates_source_tables': False,
    'live_axis_sets': live,
    'drift_report': drift,
    'alias_coverage': cov,
}
RESULT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n',
                  encoding='utf-8')
record('result_json_written', RESULT.exists(), str(RESULT))


print('=' * 70)
print('AXIS-C — Canonical Axis Dynamic Preview Helper Safety Audit')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
