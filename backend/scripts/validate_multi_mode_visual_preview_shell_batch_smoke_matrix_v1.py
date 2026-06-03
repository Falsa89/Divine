#!/usr/bin/env python3
"""Validator: PROJECT-MULTI-MODE-VISUAL-PREVIEW-SHELL-BATCH-SMOKE-MATRIX (v58 Track D).

Verifica QA smoke matrix unificata multi-mode (story/tower/event/arena):
 - presenza file design JSON
 - >= 20 flussi, severity P0/P1/P2/P3
 - flags forbidden tutti False
 - db_writes=0
 - marker di Track D presente e coerente
No fake PASS. No validator weakening.
"""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
PACK = 'MEGA_RELEASE_ACCELERATION_7_MULTI_MODE_VISUAL_PREVIEW_SHELL_BATCH_PACK_v58'
TAG = 'PUBLIC_SYNC_TAG_v58_MEGA_RELEASE_ACCELERATION_7_MULTI_MODE_VISUAL_PREVIEW_SHELL_BATCH'
MATRIX = os.path.join(ROOT, 'data/design/qa/multi_mode_visual_preview_shell_batch_smoke_matrix_v1.json')
MARKER = os.path.join(ROOT, 'data/design/qa/multi_mode_visual_preview_shell_batch_smoke_matrix_marker_v1.json')
FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(MATRIX):
    fail(f'missing matrix: {MATRIX}')
else:
    mx = json.load(open(MATRIX))
    if mx.get('version') != 'multi_mode_visual_preview_shell_batch_smoke_matrix_v1': fail('matrix.version mismatch')
    if mx.get('pack') != PACK: fail('matrix.pack mismatch')
    if mx.get('public_sync_tag') != TAG: fail('matrix.public_sync_tag mismatch')
    if mx.get('db_writes') != 0: fail('matrix.db_writes != 0')
    flows = mx.get('flows') or []
    if len(flows) < 20:
        fail(f'matrix.flows count too low: {len(flows)} (expected >=20)')
    sevs = {f.get('severity') for f in flows}
    for s in ('P0','P1','P2','P3'):
        if s not in sevs: fail(f'matrix.flows missing severity {s}')
    fb = mx.get('forbidden') or {}
    for k in ('claim_button_present','db_writes_nonzero','backend_fetch_present',
              'battle_engine_called','story_tsx_modified','story_battle_endpoint_called',
              'battle_simulate_endpoint_called','guild_war_policy_regression',
              'validator_weakening','fake_pass'):
        if fb.get(k) is not False: fail(f'matrix.forbidden.{k} != False (got {fb.get(k)})')

if not os.path.exists(MARKER):
    fail(f'missing matrix marker: {MARKER}')
else:
    mk = json.load(open(MARKER))
    if mk.get('marker_version') != 'multi_mode_visual_preview_shell_batch_smoke_matrix_marker_v1': fail('matrix marker version mismatch')
    if mk.get('pack') != PACK: fail('matrix marker pack mismatch')
    if mk.get('public_sync_tag') != TAG: fail('matrix marker tag mismatch')
    if mk.get('db_writes') != 0: fail('matrix marker db_writes != 0')
    if mk.get('claim_button_present') is not False: fail('matrix marker claim_button_present != False')
    if mk.get('battle_engine_called') is not False: fail('matrix marker battle_engine_called != False')
    if mk.get('backend_fetch_present') is not False: fail('matrix marker backend_fetch_present != False')
    if mk.get('story_tsx_modified') is not False: fail('matrix marker story_tsx_modified != False')
    if mk.get('guild_war_policy_regression') is not False: fail('matrix marker guild_war_policy_regression != False')
    if mk.get('validator_weakening') is not False: fail('matrix marker validator_weakening != False')
    if mk.get('fake_pass') is not False: fail('matrix marker fake_pass != False')
    sev = mk.get('severity_levels') or []
    for s in ('P0','P1','P2','P3'):
        if s not in sev: fail(f'matrix marker missing severity {s}')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-MULTI-MODE-VISUAL-PREVIEW-SHELL-BATCH-SMOKE-MATRIX')
    sys.exit(1)
print('[PASS] PROJECT-MULTI-MODE-VISUAL-PREVIEW-SHELL-BATCH-SMOKE-MATRIX')
sys.exit(0)
