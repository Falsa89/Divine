#!/usr/bin/env python3
"""
AXIS-D — Validator for the canonical axis activation validation table.

Verifies:
  - table file present and parses
  - design_only=true, runtime_attached=false, activation_ready=false
  - design_preview_ready=true
  - blockers list contains darkness_vs_dark_unpatched AND tides_orphan_unresolved
  - validation_rows include a failed row for both blockers
  - required_before_activation lists all 7 items, with the two
    boss-matrix-dependent gates currently_satisfied=false
  - axes_observed matches the snapshot from AXIS-A plan
  - no source patch (RM1.34-B and AF2-A unchanged)
  - currently_blocking_any_axis_runtime_on=true
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
TABLE = ROOT / 'data' / 'design' / 'shared' / 'canonical_axis_activation_validation_table_v1.json'
BOSS_MATRIX = ROOT / 'data' / 'design' / 'boss_systems' / 'boss_family_element_faction_matrix_v1.json'
GIFT_DRAFT = ROOT / 'data' / 'design' / 'affinity' / 'affinity_gift_catalog_faction_element_draft_v1.json'

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


record('table_present', TABLE.exists(), str(TABLE))
try:
    t = json.loads(TABLE.read_text(encoding='utf-8'))
    record('table_parses', True, '')
except Exception as e:
    t = {}
    record('table_parses', False, f'{e!r}')

# Identity
record('table_id',
       t.get('table_id') == 'canonical_axis_activation_validation_table_v1', '')
record('task_origin', t.get('task_origin') == 'AXIS-D', '')

# Top-level flags
for k, v in [
    ('design_only', True), ('runtime_attached', False),
    ('applied_to_combat', False), ('db_write', False),
    ('no_borea_activation', True),
    ('activation_ready', False),
    ('design_preview_ready', True),
    ('currently_blocking_any_axis_runtime_on', True),
]:
    record(f'flag_{k}', t.get(k) == v,
           f'expected {v}, got {t.get(k)!r}')

# Blockers
blockers = t.get('blockers') or []
blocker_ids = {b.get('id') for b in blockers if isinstance(b, dict)}
for required in ['darkness_vs_dark_unpatched', 'tides_orphan_unresolved']:
    record(f'blocker_present:{required}', required in blocker_ids,
           f'missing blocker: {required}')
# All blockers must be severity blocking_runtime_on
for b in blockers:
    if isinstance(b, dict):
        record(f'blocker_severity:{b.get("id")}',
               b.get('severity') == 'blocking_runtime_on',
               f'got {b.get("severity")!r}')

# Validation rows
rows = t.get('validation_rows') or []
# At least 1 fail row for darkness, 1 fail row for tides
fail_rows = [r for r in rows
             if isinstance(r, dict) and r.get('status') == 'fail']
fail_blocker_ids = {r.get('blocker_id') for r in fail_rows
                    if isinstance(r, dict)}
record('fail_row_for_darkness',
       'darkness_vs_dark_unpatched' in fail_blocker_ids, '')
record('fail_row_for_tides',
       'tides_orphan_unresolved' in fail_blocker_ids, '')

# At least one PASS row for borea_visibility
pass_borea = any(
    isinstance(r, dict) and r.get('axis') == 'borea_visibility'
    and r.get('status') == 'pass'
    for r in rows
)
record('pass_row_for_borea_visibility', pass_borea, '')

# required_before_activation list
rba = t.get('required_before_activation') or []
required_ids = {x.get('id') for x in rba if isinstance(x, dict)}
for req in ['alias_coverage_pass', 'roster_source_confirmed',
            'gift_axis_equals_roster_or_alias_covered',
            'boss_matrix_axis_equals_roster_or_alias_covered',
            'tides_decision_made', 'borea_hidden_check_pass',
            'rebaseline_after_patch']:
    record(f'required_before_activation:{req}', req in required_ids, '')

# Boss-matrix-dependent gates currently_satisfied=false
for req in ['boss_matrix_axis_equals_roster_or_alias_covered',
            'tides_decision_made', 'rebaseline_after_patch']:
    item = next(
        (x for x in rba if isinstance(x, dict) and x.get('id') == req),
        None,
    )
    record(f'gate_currently_unsatisfied:{req}',
           item is not None and item.get('currently_satisfied') is False,
           f'got {item!r}')

# Borea / alias coverage gates currently_satisfied=true
for req in ['alias_coverage_pass', 'roster_source_confirmed',
            'gift_axis_equals_roster_or_alias_covered',
            'borea_hidden_check_pass']:
    item = next(
        (x for x in rba if isinstance(x, dict) and x.get('id') == req),
        None,
    )
    record(f'gate_currently_satisfied:{req}',
           item is not None and item.get('currently_satisfied') is True,
           f'got {item!r}')

# axes_observed snapshot consistency
ao = t.get('axes_observed') or {}
record('axes_live_elements_contain_dark',
       'dark' in (ao.get('live_roster_elements') or []), '')
record('axes_live_elements_no_darkness',
       'darkness' not in (ao.get('live_roster_elements') or []), '')
record('axes_matrix_elements_contain_darkness',
       'darkness' in (ao.get('boss_matrix_rm134b_elements') or []), '')
record('axes_matrix_factions_contain_tides',
       'tides' in (ao.get('boss_matrix_rm134b_factions') or []), '')
record('axes_live_factions_no_tides',
       'tides' not in (ao.get('live_roster_factions') or []), '')
record('axes_gift_draft_no_tides',
       'tides' not in (ao.get('gift_draft_af2a_factions') or []), '')

# No source patch
patches = t.get('do_not_patch_in_this_task') or {}
for k in ['rm134b_matrix', 'af2a_gift_draft', 'axis_a_plan', 'baseline_v5']:
    record(f'do_not_patch_{k}', patches.get(k) is True, '')

# Source tables actually unchanged OR explicitly patched via a known
# axis patch (RM1.34-B-PATCH-A / PATCH-B). When the boss matrix is
# patched in a controlled way, the canonical token mutation is
# acknowledged through metadata.darkness_to_dark_applied=True /
# tides_status='deferred_not_live'. The AXIS-D snapshot still asserts
# that no UNAUTHORIZED mutation occurred.
if BOSS_MATRIX.exists():
    bm = json.loads(BOSS_MATRIX.read_text(encoding='utf-8'))
    bm_meta = bm.get('metadata') or {}
    darkness_in_elements = 'darkness' in (bm.get('elements_included') or [])
    darkness_patched = bm_meta.get('darkness_to_dark_applied') is True \
        and 'RM1.34-B-PATCH-A' in (bm_meta.get('axis_patches_applied') or [])
    record('boss_matrix_darkness_unchanged_or_patched',
           darkness_in_elements or darkness_patched,
           f'darkness_in_elements={darkness_in_elements}, '
           f'darkness_patched={darkness_patched}')

    tides_in_factions = 'tides' in (bm.get('faction_groups_included') or [])
    tides_deferred = bm_meta.get('tides_status') == 'deferred_not_live' \
        and bm_meta.get('tides_removed_from_canonical_matrix') is True \
        and 'RM1.34-B-PATCH-B' in (bm_meta.get('axis_patches_applied') or [])
    record('boss_matrix_tides_unchanged_or_deferred',
           tides_in_factions or tides_deferred,
           f'tides_in_factions={tides_in_factions}, '
           f'tides_deferred={tides_deferred}')
if GIFT_DRAFT.exists():
    gd = json.loads(GIFT_DRAFT.read_text(encoding='utf-8'))
    record('gift_draft_dark_unchanged',
           'dark' in (gd.get('elements_used') or []), '')
    record('gift_draft_no_tides_unchanged',
           'tides' not in (gd.get('factions_used') or []), '')

# Recommended patch order present
record('recommended_patch_order_present',
       isinstance(t.get('recommended_patch_order'), list)
       and len(t.get('recommended_patch_order')) >= 3, '')


print('=' * 70)
print('AXIS-D — Canonical Axis Activation Validation Table Validator')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
