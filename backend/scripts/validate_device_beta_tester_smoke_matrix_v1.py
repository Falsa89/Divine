#!/usr/bin/env python3
"""Validator: PROJECT-DEVICE-BETA-TESTER-SMOKE-MATRIX (v51 Track F)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
DESIGN = os.path.join(ROOT, 'data/design/qa/device_beta_tester_smoke_matrix_v1.json')
MARKER = os.path.join(ROOT, 'data/design/qa/device_beta_tester_smoke_matrix_marker_v1.json')
DOC = os.path.join(ROOT, 'docs/divine/297_DEVICE_QA_AND_BETA_TESTER_SMOKE_MATRIX.md')

REQUIRED_FLOWS = {
    'app_boot', 'home', 'heroes', 'story', 'visual_battle',
    'post_battle_report', 'material_raid_alpha', 'reward_preview',
    'guide_codex', 'navigation_back_rotation', 'crash_freeze_performance',
}
REQUIRED_SEVERITY = {'P0', 'P1', 'P2', 'P3'}

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(DESIGN): fail(f'missing design: {DESIGN}')
else:
    d = json.load(open(DESIGN))
    if d.get('contract_version') != 'device_beta_tester_smoke_matrix_v1':
        fail('design contract_version mismatch')
    if not d.get('device_info_fields'): fail('device_info_fields empty')
    if not d.get('build_version_fields'): fail('build_version_fields empty')
    if not d.get('tester_roles'): fail('tester_roles empty')
    sev_ids = {s.get('id') for s in (d.get('bug_severity') or [])}
    miss = REQUIRED_SEVERITY - sev_ids
    if miss: fail(f'bug_severity missing: {sorted(miss)}')
    flows = set(d.get('flows_to_test') or [])
    miss_f = REQUIRED_FLOWS - flows
    if miss_f: fail(f'flows_to_test missing: {sorted(miss_f)}')
    if not d.get('pass_fail_criteria'): fail('pass_fail_criteria empty')
    caveats = set(d.get('known_caveats') or [])
    if 'preview_only_economy' not in caveats: fail('caveat preview_only_economy missing')
    if 'no_live_reward_claim' not in caveats: fail('caveat no_live_reward_claim missing')
    if d.get('db_writes') != 0: fail('design db_writes != 0')
    if d.get('live_apply_allowed') is not False: fail('design live_apply_allowed != False')

if not os.path.exists(MARKER): fail(f'missing marker: {MARKER}')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('contract_version', 'device_beta_tester_smoke_matrix_v1'),
        ('track', 'F'),
        ('flows_count', 12),
        ('tester_roles_count', 3),
        ('db_writes', 0),
        ('public_sync_tag', 'PUBLIC_SYNC_TAG_v51_MEGA_RELEASE_ACCELERATION_1_PLAYABLE_ALPHA_FOUNDATION'),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')
    sev = m.get('bug_severity_levels') or []
    if set(sev) != REQUIRED_SEVERITY:
        fail(f'marker bug_severity_levels mismatch (got {sev})')

if not os.path.exists(DOC): fail(f'missing doc: {DOC}')
else:
    txt = open(DOC).read()
    for needle in ('P0', 'P1', 'P2', 'P3', 'Material Raid', 'visual_battle', 'preview'):
        if needle not in txt: fail(f'doc missing needle: {needle}')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-DEVICE-BETA-TESTER-SMOKE-MATRIX validator')
    sys.exit(1)
print('[PASS] PROJECT-DEVICE-BETA-TESTER-SMOKE-MATRIX validator')
sys.exit(0)
