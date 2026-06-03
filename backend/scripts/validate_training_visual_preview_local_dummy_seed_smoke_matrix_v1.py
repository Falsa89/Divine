#!/usr/bin/env python3
"""Validator: PROJECT-TRAINING-VISUAL-PREVIEW-LOCAL-DUMMY-SEED-SMOKE-MATRIX (v56 Track D)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
MATRIX = os.path.join(ROOT, 'data/design/qa/training_visual_preview_local_dummy_seed_smoke_matrix_v1.json')
MARKER = os.path.join(ROOT, 'data/design/qa/training_visual_preview_local_dummy_seed_smoke_matrix_marker_v1.json')
TAG = 'PUBLIC_SYNC_TAG_v56_MEGA_RELEASE_ACCELERATION_5_TRAINING_VISUAL_PREVIEW_LOCAL_DUMMY_SEED'

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(MATRIX): fail('missing matrix')
else:
    m = json.load(open(MATRIX))
    if m.get('public_sync_tag') != TAG: fail('matrix public_sync_tag mismatch')
    if m.get('mode') != 'qa_smoke_matrix': fail('matrix mode mismatch')
    if m.get('db_writes') != 0: fail('matrix db_writes != 0')
    flows = m.get('flows') or []
    if len(flows) < 13: fail(f'matrix flows too few: {len(flows)}')
    sev = {f.get('severity') for f in flows}
    if not {'P0','P1','P2','P3'}.issubset(sev): fail(f'matrix severities missing: {sorted({"P0","P1","P2","P3"} - sev)}')
    names = ' | '.join(f.get('name','') for f in flows).lower()
    for needed in ('training-visual-preview', 'timeline', 'step next', 'reset', 'no claim button', 'no reward', 'no db write', 'no backend fetch', 'no battle_engine call', 'generic router'):
        if needed not in names: fail(f'matrix flow names missing: {needed}')
    forb = m.get('forbidden') or {}
    for k in ('claim_button_present','db_writes_nonzero','backend_fetch_present','battle_engine_called','validator_weakening','fake_pass'):
        if forb.get(k) is not False: fail(f'matrix forbidden.{k} != false')

if not os.path.exists(MARKER): fail('missing marker')
else:
    mk = json.load(open(MARKER))
    for k, v in (
        ('marker_version','training_visual_preview_local_dummy_seed_smoke_matrix_marker_v1'),
        ('track','D'),
        ('public_sync_tag',TAG),
        ('flows_count',16),
        ('db_writes',0),
        ('claim_button_present',False),
        ('battle_engine_called',False),
        ('backend_fetch_present',False),
        ('validator_weakening',False),
        ('fake_pass',False),
    ):
        if mk.get(k) != v: fail(f'marker {k} != {v} (got {mk.get(k)})')
    sev = set(mk.get('severity_levels') or [])
    if sev != {'P0','P1','P2','P3'}: fail(f'marker severity_levels mismatch: {sorted(sev)}')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-TRAINING-VISUAL-PREVIEW-LOCAL-DUMMY-SEED-SMOKE-MATRIX validator')
    sys.exit(1)
print('[PASS] PROJECT-TRAINING-VISUAL-PREVIEW-LOCAL-DUMMY-SEED-SMOKE-MATRIX validator')
sys.exit(0)
