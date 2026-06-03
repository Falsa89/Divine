#!/usr/bin/env python3
"""v62 Rollup validator."""
from __future__ import annotations
import os, sys, hashlib, subprocess, json
ROOT='/app'
SUITE=os.path.join(ROOT,'backend/scripts/run_hero_skill_kit_validator_suite.py')
ROLL=os.path.join(ROOT,'data/design/release_acceleration/mega_release_acceleration_11_v62_rollup_marker_v1.json')
PACK='MEGA_RELEASE_ACCELERATION_11_PREVIEW_TO_RUNTIME_RUNNER_PLAN_AND_FULL_COVERAGE_ROLLUP_SUPER_PACK_v62'
TAG='PUBLIC_SYNC_TAG_v62_MEGA_RELEASE_ACCELERATION_11_PREVIEW_TO_RUNTIME_RUNNER_PLAN'
TUPLES=[
    "'PROJECT-VISUAL-BATTLE-RUNNER-RUNTIME-SHELL-PLAN'",
    "'PROJECT-PREVIEW-TO-RUNTIME-TRANSITION-PLAN'",
    "'PROJECT-VISUAL-PREVIEW-FULL-COVERAGE-ROLLUP'",
    "'PROJECT-PER-MODE-RUNTIME-READINESS-MATRIX'",
    "'PROJECT-RUNTIME-RUNNER-PAYLOAD-v1-DRAFT-AND-ROLLBACK-PLAN'",
    "'PROJECT-PREVIEW-TO-RUNTIME-RUNNER-PLAN-READINESS-MATRIX'",
    "'MEGA-RELEASE-ACCELERATION-11-v62-ROLLUP'",
]
INV={
    'backend/battle_engine.py':'151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env':'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py':'893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx':'54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx':'45fcc9890b6b128c37088bc33aa54caf',
}
PREF={
    'frontend/app/combat.tsx':'fc792a05b2ada6e677d80400732ae5c3',
    'frontend/app/story.tsx':'8520627b4e63f86821d73d8d3880bac3',
    'backend/server.py':'055df030553f4791e8cac14254f1b148',
}
DEPS=[
    'validate_visual_battle_runner_runtime_shell_plan_v1.py',
    'validate_preview_to_runtime_transition_plan_v1.py',
    'validate_visual_preview_full_coverage_rollup_v1.py',
    'validate_per_mode_runtime_readiness_matrix_v1.py',
    'validate_runtime_runner_payload_v1_draft_and_rollback_plan_v1.py',
    'validate_preview_to_runtime_runner_plan_readiness_matrix_v1.py',
]
DOCS=[
    'docs/divine/365_VISUAL_BATTLE_RUNNER_RUNTIME_SHELL_PLAN.md',
    'docs/divine/366_PREVIEW_TO_RUNTIME_TRANSITION_PLAN.md',
    'docs/divine/367_VISUAL_PREVIEW_FULL_COVERAGE_ROLLUP.md',
    'docs/divine/368_PER_MODE_RUNTIME_READINESS_MATRIX.md',
    'docs/divine/369_RUNTIME_RUNNER_PAYLOAD_v1_DRAFT_AND_ROLLBACK_PLAN.md',
    'docs/divine/370_PREVIEW_TO_RUNTIME_RUNNER_PLAN_READINESS_QA.md',
    'docs/divine/371_MEGA_RELEASE_ACCELERATION_11_PREVIEW_TO_RUNTIME_RUNNER_PLAN_v62.md',
]
F=[]
def f(m): F.append(m)
for rel,exp in INV.items():
    p=os.path.join(ROOT,rel)
    if not os.path.exists(p): f(f'[1] missing {rel}'); continue
    h=hashlib.md5(open(p,'rb').read()).hexdigest()
    if h!=exp: f(f'[1] MD5 drift {rel}: got {h}')
for rel,exp in PREF.items():
    p=os.path.join(ROOT,rel)
    if not os.path.exists(p): f(f'[1b] missing {rel}'); continue
    h=hashlib.md5(open(p,'rb').read()).hexdigest()
    if h!=exp: f(f'[1b] preferred drift {rel}: got {h}')
if not os.path.exists(SUITE): f('[2] missing suite')
else:
    sr=open(SUITE).read()
    for t in TUPLES:
        if sr.count(t)!=1: f(f'[2] suite count!=1 for {t} got {sr.count(t)}')
    if TAG not in sr: f(f'[2] suite missing tag {TAG}')
for v in DEPS:
    vp=os.path.join(ROOT,'backend/scripts',v)
    if not os.path.exists(vp): f(f'[3] missing validator {v}'); continue
    r=subprocess.run([sys.executable,vp],capture_output=True,text=True)
    if r.returncode!=0:
        f(f'[3] dep validator {v} rc={r.returncode}'); print(r.stdout[-400:]); print(r.stderr[-400:])
for d in DOCS:
    if not os.path.exists(os.path.join(ROOT,d)): f(f'[4] missing doc {d}')
if not os.path.exists(ROLL): f('[5] missing rollup marker')
else:
    m=json.load(open(ROLL))
    for k,v in (
        ('marker_version','mega_release_acceleration_11_v62_rollup_marker_v1'),
        ('pack',PACK),('public_sync_tag',TAG),
        ('server_py_changed',False),('battle_engine_changed',False),
        ('combat_tsx_changed',False),('story_tsx_changed',False),
        ('battle_simulate_endpoint_changed',False),('story_battle_endpoint_changed',False),
        ('existing_endpoint_paths_changed',False),('existing_feature_flags_changed',False),
        ('existing_default_503_changed',False),('safety_flags_changed',False),
        ('guild_war_policy_changed',False),('guild_war_policy_regression',False),
        ('character_bible_changed',False),('final_numbers_changed',False),
        ('db_writes',0),('real_db_writes',0),('mongo_url_used',False),
        ('pymongo_used',False),('motor_used',False),('redis_used',False),
        ('filesystem_writes',0),('live_apply_allowed',False),
        ('reward_grant_enabled',False),('reward_claim_live',False),
        ('reward_claim_enabled',False),('claim_button_enabled',False),
        ('materials_granted',False),('inventory_mutation',False),
        ('battle_engine_runtime_used',False),('result_authoritative',False),
        ('home_menu_mandatory_routing',False),('asset_copy_or_import',False),
        ('validator_weakening',False),('fake_pass',False),
        ('gate_0_v61_pass',True),('gate_1_v62_validators_pass',True),
        ('runtime_runner_created',False),('runtime_activation_enabled',False),
        ('manual_approval_required',True),('visual_preview_local_layer_complete',True),
        ('frontend_changes_in_v62',False),
    ):
        if m.get(k)!=v: f(f'[5] rollup marker {k}!={v} (got {m.get(k)})')
    if m.get('tracks')!=['A','B','C','D','E','F','G']: f('[5] rollup tracks mismatch')
    exp_t=['PROJECT-VISUAL-BATTLE-RUNNER-RUNTIME-SHELL-PLAN','PROJECT-PREVIEW-TO-RUNTIME-TRANSITION-PLAN',
           'PROJECT-VISUAL-PREVIEW-FULL-COVERAGE-ROLLUP','PROJECT-PER-MODE-RUNTIME-READINESS-MATRIX',
           'PROJECT-RUNTIME-RUNNER-PAYLOAD-v1-DRAFT-AND-ROLLBACK-PLAN',
           'PROJECT-PREVIEW-TO-RUNTIME-RUNNER-PLAN-READINESS-MATRIX',
           'MEGA-RELEASE-ACCELERATION-11-v62-ROLLUP']
    if m.get('suite_tuples')!=exp_t: f('[5] rollup suite_tuples mismatch')
    mb=m.get('md5_invariants') or {}
    for rel,exp in INV.items():
        if mb.get(rel)!=exp: f(f'[5] rollup md5_invariants {rel}!={exp}')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] MEGA_RELEASE_ACCELERATION_11_v62_ROLLUP validator'); sys.exit(1)
print('[PASS] MEGA_RELEASE_ACCELERATION_11_v62_ROLLUP validator'); sys.exit(0)
