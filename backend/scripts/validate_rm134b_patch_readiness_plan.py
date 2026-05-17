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

# Plan supports two states: PRE-execution (patches_executed=False) and
# POST-execution (patches_executed=True via the ULTRA-COMBO-V6 task).
post_exec = (p.get('post_execution_status') or {}).get('patch_a_applied') is True \
    and (p.get('post_execution_status') or {}).get('patch_b_applied') is True

if post_exec:
    record('flag_design_only', p.get('design_only') is True, '')
    record('flag_patches_executed_true', p.get('patches_executed') is True, '')
    record('flag_baseline_v6_created_true',
           p.get('baseline_v6_created') is True, '')
    record('flag_post_execution_recorded',
           bool(p.get('post_execution_status')), '')
    record('flag_no_borea_activation', p.get('no_borea_activation') is True, '')
    pes = p.get('post_execution_status') or {}
    record('post_exec_design_only', pes.get('design_only') is True, '')
    record('post_exec_runtime_attached_false',
           pes.get('runtime_attached') is False, '')
    record('post_exec_db_write_false', pes.get('db_write') is False, '')
else:
    for k, v in [('design_only', True), ('patches_executed', False),
                 ('baseline_v6_created', False), ('db_write', False),
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

# Source matrix: pre-execution requires darkness+tides present, post-
# execution requires darkness->dark applied and tides deferred.
if MATRIX.exists():
    m = json.loads(MATRIX.read_text(encoding='utf-8'))
    _mm = m.get('metadata') or {}
    _dp = _mm.get('darkness_to_dark_applied') is True \
        and 'RM1.34-B-PATCH-A' in (_mm.get('axis_patches_applied') or [])
    _td = _mm.get('tides_status') == 'deferred_not_live' \
        and 'RM1.34-B-PATCH-B' in (_mm.get('axis_patches_applied') or [])
    if post_exec:
        record('matrix_darkness_patched', _dp,
               f'expected PATCH-A applied (got darkness_patched={_dp})')
        record('matrix_tides_deferred', _td,
               f'expected PATCH-B applied (got tides_deferred={_td})')
    else:
        record('matrix_darkness_unchanged',
               'darkness' in (m.get('elements_included') or []),
               'matrix MUST still contain darkness in this task')
        record('matrix_tides_unchanged',
               'tides' in (m.get('faction_groups_included') or []),
               'matrix MUST still contain tides in this task')

# Baseline v5 anchor present; v6 expected only post-execution
record('baseline_v5_present', BASELINE_V5.exists(), '')
if post_exec:
    record('baseline_v6_present_post_exec',
           len(BASELINE_V6_CANDIDATES) >= 1,
           f'expected v6 baseline file, got {BASELINE_V6_CANDIDATES}')
else:
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
