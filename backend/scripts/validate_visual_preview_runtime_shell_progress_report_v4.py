#!/usr/bin/env python3
"""Validator: PROJECT-VISUAL-PREVIEW-RUNTIME-SHELL-PROGRESS-REPORT-v4 (v59 Track F).

Verifica progress report v4 (8 modi snapshot + payload contract):
- boss=local_dummy_seed_wired_v59, tower=local_dummy_seed_wired_v59
- visual_battle_runner_payload_contract=design_only_v0
- material_raid=alpha_loop_closed_v53, training=local_dummy_seed_wired_v56,
  story/event/arena=preview_shell_v58, guild_war unchanged
- db_writes=0, no runtime use
No fake PASS. No validator weakening.
"""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
PACK = 'MEGA_RELEASE_ACCELERATION_8_LOCAL_TIMELINE_AND_RUNNER_PAYLOAD_CONTRACT_BATCH_PACK_v59'
TAG = 'PUBLIC_SYNC_TAG_v59_MEGA_RELEASE_ACCELERATION_8_LOCAL_TIMELINE_AND_RUNNER_PAYLOAD_CONTRACT_BATCH'
REPORT = os.path.join(ROOT, 'data/design/release_acceleration/visual_preview_runtime_shell_progress_report_v4.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/visual_preview_runtime_shell_progress_v4_marker_v1.json')

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(REPORT):
    fail(f'missing report: {REPORT}')
else:
    r = json.load(open(REPORT))
    if r.get('version') != 'visual_preview_runtime_shell_progress_report_v4': fail('report.version mismatch')
    if r.get('pack') != PACK: fail('report.pack mismatch')
    if r.get('public_sync_tag') != TAG: fail('report.public_sync_tag mismatch')
    for k, v in (('db_writes',0),('battle_engine_runtime_used',False),
                 ('story_runtime_used',False),('tower_runtime_used',False),
                 ('event_runtime_used',False),('arena_runtime_used',False),
                 ('boss_runtime_used',False),
                 ('reward_grant_enabled',False),('live_claim_enabled',False)):
        if r.get(k) != v: fail(f'report.{k} != {v} (got {r.get(k)})')
    ms = r.get('modes_status') or {}
    expected = {
        'material_raid':'alpha_loop_closed_v53',
        'training':'local_dummy_seed_wired_v56',
        'boss':'local_dummy_seed_wired_v59',
        'story':'preview_shell_v58',
        'tower':'local_dummy_seed_wired_v59',
        'event':'preview_shell_v58',
        'arena':'preview_shell_v58',
        'guild_war':'autoresolve_with_replay_link_exception_unchanged',
        'visual_battle_runner_payload_contract':'design_only_v0',
    }
    for k, v in expected.items():
        if ms.get(k) != v: fail(f'report.modes_status.{k} != {v} (got {ms.get(k)})')
    nra = r.get('next_recommended_after_batch') or []
    for n in ('visual_battle_runner_router_adapter_preview','event_local_dummy_seed_wiring',
              'arena_local_dummy_seed_wiring','material_raid_claim_safety_hardening_v2_preview_only'):
        if n not in nra: fail(f'report.next_recommended_after_batch missing {n}')
    da = (r.get('director_approvals') or {}).get('not_approved') or []
    for n in ('B8','live_economy','db_writes','reward_grant','battle_engine_runtime'):
        if n not in da: fail(f'report.director_approvals.not_approved missing {n}')

if not os.path.exists(MARKER):
    fail(f'missing marker: {MARKER}')
else:
    mk = json.load(open(MARKER))
    if mk.get('marker_version') != 'visual_preview_runtime_shell_progress_v4_marker_v1': fail('marker.version mismatch')
    for k, v in (('pack',PACK),('public_sync_tag',TAG),('db_writes',0),
                 ('battle_engine_runtime_used',False),('reward_grant_enabled',False),
                 ('live_claim_enabled',False),('story_runtime_used',False),
                 ('tower_runtime_used',False),('event_runtime_used',False),
                 ('arena_runtime_used',False),('boss_runtime_used',False),
                 ('validator_weakening',False),('fake_pass',False)):
        if mk.get(k) != v: fail(f'marker.{k} != {v} (got {mk.get(k)})')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-VISUAL-PREVIEW-RUNTIME-SHELL-PROGRESS-REPORT-v4')
    sys.exit(1)
print('[PASS] PROJECT-VISUAL-PREVIEW-RUNTIME-SHELL-PROGRESS-REPORT-v4')
sys.exit(0)
