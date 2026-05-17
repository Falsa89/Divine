#!/usr/bin/env python3
"""
PATCH-READINESS-A — Validator for the RM1.34-B patch readiness plan.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path('/app')
PLAN = ROOT / 'data' / 'design' / 'shared' / 'rm134b_patch_readiness_plan_v1.json'
MATRIX = ROOT / 'data' / 'design' / 'boss_systems' / 'boss_family_element_faction_matrix_v1.json'
BASELINE_V5 = ROOT / 'data' / 'design' / 'hero_skill_kits' / 'hero_skill_kit_catalog_baseline_rm132c2_v5.json'
BASELINE_V6_CANDIDATES = list(
    (ROOT / 'data' / 'design' / 'hero_skill_kits').glob('*baseline*v6*.json')
)

failures: list[str] = []
checks: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, note: str = '') -> None:
    checks.append((name, ok, note))
    if not ok:
        failures.append(f'{name}: {note}')


record('plan_present', PLAN.exists(), str(PLAN))
p = json.loads(PLAN.read_text(encoding='utf-8'))
record('plan_id', p.get('plan_id') == 'rm134b_patch_readiness_plan_v1', '')
record('task_origin', p.get('task_origin') == 'PATCH-READINESS-A', '')
for k, v in [('design_only', True), ('patches_executed', False),
             ('baseline_v6_created', false := False), ('db_write', False),
             ('no_borea_activation', True),
             ('no_source_patch_in_this_task', True),
             ('no_baseline_v6_in_this_task', True)]:
    record(f'flag_{k}', p.get(k) == v, f'expected {v}, got {p.get(k)!r}')

patches = p.get('patches') or []
ids = {x.get('id') for x in patches if isinstance(x, dict)}
for req in ['RM1.34-B-PATCH-A', 'RM1.34-B-PATCH-B']:
    record(f'patch_present:{req}', req in ids, '')

for x in patches:
    if not isinstance(x, dict):
        continue
    pid = x.get('id')
    record(f'patch_do_not_execute:{pid}',
           x.get('do_not_execute_in_this_task') is True, '')
    record(f'patch_validators_listed:{pid}',
           isinstance(x.get('validators_to_rerun'), list)
           and len(x.get('validators_to_rerun')) >= 4, '')
    record(f'patch_rollback_listed:{pid}',
           isinstance(x.get('rollback_procedure'), list)
           and len(x.get('rollback_procedure')) >= 2, '')
    record(f'patch_baseline_v6_candidate_label:{pid}',
           'v6_candidate' in str(x.get('baseline_after_patch', '')), '')

# PATCH-B has two branches
pb = next((x for x in patches if isinstance(x, dict) and x.get('id') == 'RM1.34-B-PATCH-B'), None)
if pb:
    branches = pb.get('branches') or []
    bids = {b.get('branch_id') for b in branches if isinstance(b, dict)}
    for req in ['PATCH-B-BRANCH-MINT', 'PATCH-B-BRANCH-STRIKE']:
        record(f'patch_b_branch:{req}', req in bids, '')

# Source NOT mutated (RM1.34-B still contains darkness + tides)
if MATRIX.exists():
    m = json.loads(MATRIX.read_text(encoding='utf-8'))
    record('matrix_darkness_unchanged',
           'darkness' in (m.get('elements_included') or []),
           'matrix MUST still contain darkness in this task')
    record('matrix_tides_unchanged',
           'tides' in (m.get('faction_groups_included') or []),
           'matrix MUST still contain tides in this task')

# Baseline v5 anchor present, NO v6 file created
record('baseline_v5_present', BASELINE_V5.exists(), '')
record('no_baseline_v6_file', not BASELINE_V6_CANDIDATES,
       f'unexpected v6 baseline files: {BASELINE_V6_CANDIDATES}')

blocked = p.get('baseline_v6_creation_blocked_until') or []
record('baseline_v6_blocked_until_min_3', len(blocked) >= 3,
       f'got {len(blocked)}')

print('=' * 70)
print('PATCH-READINESS-A — RM1.34-B Patch Readiness Plan Validator')
print('=' * 70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-' * 70)
print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} '
      f'failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
