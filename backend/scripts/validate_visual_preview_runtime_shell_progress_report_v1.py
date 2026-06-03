#!/usr/bin/env python3
"""Validator: PROJECT-VISUAL-PREVIEW-RUNTIME-SHELL-PROGRESS-REPORT (v56 Track E)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
REPORT = os.path.join(ROOT, 'data/design/release_acceleration/visual_preview_runtime_shell_progress_report_v1.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/visual_preview_runtime_shell_progress_marker_v1.json')
TAG = 'PUBLIC_SYNC_TAG_v56_MEGA_RELEASE_ACCELERATION_5_TRAINING_VISUAL_PREVIEW_LOCAL_DUMMY_SEED'

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(REPORT): fail('missing report')
else:
    r = json.load(open(REPORT))
    if r.get('public_sync_tag') != TAG: fail('report public_sync_tag mismatch')
    if r.get('db_writes') != 0: fail('report db_writes != 0')
    if r.get('battle_engine_runtime_used') is not False: fail('report battle_engine_runtime_used != false')
    if r.get('reward_grant_enabled') is not False: fail('report reward_grant_enabled != false')
    ms = r.get('modes_status') or {}
    if ms.get('material_raid') != 'alpha_loop_closed_v53': fail('report material_raid mismatch')
    if ms.get('training') != 'local_dummy_seed_wired_v56': fail('report training != local_dummy_seed_wired_v56')
    for mode in ('story','boss','tower','event','arena'):
        if ms.get(mode) != 'design_only_runtime_deferred': fail(f'report {mode} not design_only_runtime_deferred')
    if ms.get('guild_war') != 'autoresolve_with_replay_link_exception_unchanged': fail('report guild_war policy mismatch')
    nxt = set(r.get('next_recommended_mode_after_training') or [])
    if 'boss_visual_preview_route' not in nxt and 'story_visual_preview_contract_to_deeplink' not in nxt:
        fail('report next_recommended_mode_after_training missing both options')

if not os.path.exists(MARKER): fail('missing marker')
else:
    m = json.load(open(MARKER))
    for k, v in (
        ('marker_version','visual_preview_runtime_shell_progress_marker_v1'),
        ('track','E'),
        ('public_sync_tag',TAG),
        ('db_writes',0),
        ('battle_engine_runtime_used',False),
        ('reward_grant_enabled',False),
        ('validator_weakening',False),
        ('fake_pass',False),
    ):
        if m.get(k) != v: fail(f'marker {k} != {v} (got {m.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-VISUAL-PREVIEW-RUNTIME-SHELL-PROGRESS-REPORT validator')
    sys.exit(1)
print('[PASS] PROJECT-VISUAL-PREVIEW-RUNTIME-SHELL-PROGRESS-REPORT validator')
sys.exit(0)
