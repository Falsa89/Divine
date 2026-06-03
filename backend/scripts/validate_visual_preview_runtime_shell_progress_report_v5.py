#!/usr/bin/env python3
"""Validator: PROJECT-VISUAL-PREVIEW-RUNTIME-SHELL-PROGRESS-REPORT-v5 (v60 Track F)."""
from __future__ import annotations
import os, sys, json

ROOT = '/app'
PACK = 'MEGA_RELEASE_ACCELERATION_9_ROUTER_ADAPTER_EVENT_ARENA_LOCAL_TIMELINE_BATCH_PACK_v60'
TAG = 'PUBLIC_SYNC_TAG_v60_MEGA_RELEASE_ACCELERATION_9_ROUTER_ADAPTER_EVENT_ARENA_LOCAL_TIMELINE_BATCH'
REPORT = os.path.join(ROOT, 'data/design/release_acceleration/visual_preview_runtime_shell_progress_report_v5.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/visual_preview_runtime_shell_progress_v5_marker_v1.json')

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(REPORT):
    fail(f'missing report: {REPORT}')
else:
    r = json.load(open(REPORT))
    if r.get('version') != 'visual_preview_runtime_shell_progress_report_v5': fail('report.version mismatch')
    if r.get('pack') != PACK: fail('report.pack')
    if r.get('public_sync_tag') != TAG: fail('report.tag')
    for k, v in (('db_writes',0),('battle_engine_runtime_used',False),
                 ('story_runtime_used',False),('tower_runtime_used',False),
                 ('event_runtime_used',False),('arena_runtime_used',False),
                 ('boss_runtime_used',False),
                 ('reward_grant_enabled',False),('live_claim_enabled',False)):
        if r.get(k) != v: fail(f'report.{k} != {v}')
    ms = r.get('modes_status') or {}
    expected = {
        'material_raid':'alpha_loop_closed_v53',
        'training':'local_dummy_seed_wired_v56',
        'boss':'local_dummy_seed_wired_v59',
        'story':'preview_shell_v58',
        'tower':'local_dummy_seed_wired_v59',
        'event':'local_dummy_seed_wired_v60',
        'arena':'local_dummy_seed_wired_v60',
        'guild_war':'autoresolve_with_replay_link_exception_unchanged',
        'visual_battle_runner_payload_contract':'design_only_v0',
        'router_adapter_preview':'adapter_preview_v60',
    }
    for k, v in expected.items():
        if ms.get(k) != v: fail(f'report.modes_status.{k} != {v}')
    nra = r.get('next_recommended_after_batch') or []
    for n in ('visual_battle_runner_router_adapter_preview_hardening',
              'material_raid_claim_safety_hardening_v2_preview_only',
              'story_local_dummy_seed_wiring',
              'visual_preview_to_real_runtime_gate_design'):
        if n not in nra: fail(f'report.next_recommended_after_batch missing {n}')
    da = (r.get('director_approvals') or {}).get('not_approved') or []
    for n in ('B8','live_economy','db_writes','reward_grant','battle_engine_runtime'):
        if n not in da: fail(f'report.director_approvals.not_approved missing {n}')

if not os.path.exists(MARKER):
    fail(f'missing marker: {MARKER}')
else:
    mk = json.load(open(MARKER))
    if mk.get('marker_version') != 'visual_preview_runtime_shell_progress_v5_marker_v1': fail('marker.version mismatch')
    for k, v in (('pack',PACK),('public_sync_tag',TAG),('db_writes',0),
                 ('battle_engine_runtime_used',False),('reward_grant_enabled',False),
                 ('live_claim_enabled',False),('story_runtime_used',False),
                 ('tower_runtime_used',False),('event_runtime_used',False),
                 ('arena_runtime_used',False),('boss_runtime_used',False),
                 ('validator_weakening',False),('fake_pass',False)):
        if mk.get(k) != v: fail(f'marker.{k} != {v}')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-VISUAL-PREVIEW-RUNTIME-SHELL-PROGRESS-REPORT-v5'); sys.exit(1)
print('[PASS] PROJECT-VISUAL-PREVIEW-RUNTIME-SHELL-PROGRESS-REPORT-v5'); sys.exit(0)
