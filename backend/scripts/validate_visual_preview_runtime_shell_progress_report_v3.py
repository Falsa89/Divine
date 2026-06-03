#!/usr/bin/env python3
"""Validator: PROJECT-VISUAL-PREVIEW-RUNTIME-SHELL-PROGRESS-REPORT-v3 (v58 Track E).

Verifica:
 - progress report v3 snapshot stato 8 modalita
 - story/tower/event/arena -> preview_shell_v58
 - material_raid alpha_loop_closed_v53, training local_dummy_seed_wired_v56,
   boss preview_shell_v57, guild_war autoresolve+replay_link unchanged
 - db_writes=0, battle_engine_runtime_used=false, reward_grant_enabled=false
 - marker Track E presente e coerente
No fake PASS. No validator weakening.
"""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
PACK = 'MEGA_RELEASE_ACCELERATION_7_MULTI_MODE_VISUAL_PREVIEW_SHELL_BATCH_PACK_v58'
TAG = 'PUBLIC_SYNC_TAG_v58_MEGA_RELEASE_ACCELERATION_7_MULTI_MODE_VISUAL_PREVIEW_SHELL_BATCH'
REPORT = os.path.join(ROOT, 'data/design/release_acceleration/visual_preview_runtime_shell_progress_report_v3.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/visual_preview_runtime_shell_progress_v3_marker_v1.json')

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(REPORT):
    fail(f'missing progress report v3: {REPORT}')
else:
    r = json.load(open(REPORT))
    if r.get('version') != 'visual_preview_runtime_shell_progress_report_v3': fail('report.version mismatch')
    if r.get('pack') != PACK: fail('report.pack mismatch')
    if r.get('public_sync_tag') != TAG: fail('report.public_sync_tag mismatch')
    for k, v in (('db_writes',0),('battle_engine_runtime_used',False),
                 ('story_runtime_used',False),('tower_runtime_used',False),
                 ('event_runtime_used',False),('arena_runtime_used',False),
                 ('reward_grant_enabled',False),('live_claim_enabled',False)):
        if r.get(k) != v: fail(f'report.{k} != {v} (got {r.get(k)})')
    ms = r.get('modes_status') or {}
    expected = {
        'material_raid':'alpha_loop_closed_v53',
        'training':'local_dummy_seed_wired_v56',
        'boss':'preview_shell_v57',
        'story':'preview_shell_v58',
        'tower':'preview_shell_v58',
        'event':'preview_shell_v58',
        'arena':'preview_shell_v58',
        'guild_war':'autoresolve_with_replay_link_exception_unchanged',
    }
    for k, v in expected.items():
        if ms.get(k) != v: fail(f'report.modes_status.{k} != {v} (got {ms.get(k)})')
    nra = r.get('next_recommended_after_batch') or []
    for n in ('visual_battle_runner_payload_contract_v0','boss_local_timeline_wiring',
              'tower_local_dummy_seed_wiring','material_raid_claim_safety_hardening_v2_preview_only'):
        if n not in nra: fail(f'report.next_recommended_after_batch missing {n}')
    da = (r.get('director_approvals') or {}).get('not_approved') or []
    for n in ('B8','live_economy','db_writes','reward_grant','battle_engine_runtime'):
        if n not in da: fail(f'report.director_approvals.not_approved missing {n}')

if not os.path.exists(MARKER):
    fail(f'missing progress v3 marker: {MARKER}')
else:
    mk = json.load(open(MARKER))
    if mk.get('marker_version') != 'visual_preview_runtime_shell_progress_v3_marker_v1': fail('progress marker version mismatch')
    if mk.get('pack') != PACK: fail('progress marker pack mismatch')
    if mk.get('public_sync_tag') != TAG: fail('progress marker tag mismatch')
    for k, v in (('db_writes',0),('battle_engine_runtime_used',False),
                 ('reward_grant_enabled',False),('live_claim_enabled',False),
                 ('story_runtime_used',False),('tower_runtime_used',False),
                 ('event_runtime_used',False),('arena_runtime_used',False),
                 ('validator_weakening',False),('fake_pass',False)):
        if mk.get(k) != v: fail(f'progress marker.{k} != {v} (got {mk.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-VISUAL-PREVIEW-RUNTIME-SHELL-PROGRESS-REPORT-v3')
    sys.exit(1)
print('[PASS] PROJECT-VISUAL-PREVIEW-RUNTIME-SHELL-PROGRESS-REPORT-v3')
sys.exit(0)
