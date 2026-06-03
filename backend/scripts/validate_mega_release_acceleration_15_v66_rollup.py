#!/usr/bin/env python3
"""v66 Rollup validator."""
from __future__ import annotations
import os, sys, hashlib, subprocess, json
ROOT='/app'
SUITE=os.path.join(ROOT,'backend/scripts/run_hero_skill_kit_validator_suite.py')
ROLL=os.path.join(ROOT,'data/design/release_acceleration/mega_release_acceleration_15_v66_rollup_marker_v1.json')
PACK='MEGA_RELEASE_ACCELERATION_15_STORY_RUNTIME_ADAPTER_AND_FIRST_NODE_ALPHA_SUPER_PACK_v66'
TAG='PUBLIC_SYNC_TAG_v66_MEGA_RELEASE_ACCELERATION_15_STORY_RUNTIME_ADAPTER_AND_FIRST_NODE_ALPHA'
TUPLES=[
    "'PROJECT-STORY-RUNTIME-ADAPTER-v1-CONTRACT'",
    "'PROJECT-STORY-FIRST-NODE-ALPHA-FIXTURE-AND-PAYLOAD'",
    "'PROJECT-STORY-FIRST-NODE-RUNTIME-PREVIEW-SCREEN'",
    "'PROJECT-STORY-RESULT-REWARD-PROGRESS-PREVIEW-BOUNDARY'",
    "'PROJECT-STORY-ANTI-DOUBLE-CLEAR-IDEMPOTENCY-DESIGN'",
    "'PROJECT-STORY-RUNTIME-ADAPTER-FIRST-NODE-ALPHA-QA-AND-PROGRESS-v10'",
    "'MEGA-RELEASE-ACCELERATION-15-v66-ROLLUP'",
]
INV={
    'backend/battle_engine.py':'151ca35ad3bc35f0a6209cb3744ed440',
    'backend/.env':'ff60bbb79efa329b71aa8ed351ea89b3',
    'backend/routes/artifacts.py':'893f244d85fd45cbe825996463995293',
    'frontend/app/battlepass.tsx':'54568b8cb75a07033f78ef6593aba839',
    'frontend/app/vip.tsx':'45fcc9890b6b128c37088bc33aa54caf',
}
PREF={
    'backend/server.py':'055df030553f4791e8cac14254f1b148',
    'frontend/app/combat.tsx':'fc792a05b2ada6e677d80400732ae5c3',
    'frontend/app/story.tsx':'8520627b4e63f86821d73d8d3880bac3',
    'backend/routes/material_raid_preview.py':'38c7c89f89e1669ac46438a03f318a75',
}
DEPS=[
    'validate_story_runtime_adapter_v1_contract.py',
    'validate_story_first_node_alpha_fixture_and_payload_v1.py',
    'validate_story_first_node_runtime_preview_screen_v1.py',
    'validate_story_result_reward_progress_preview_boundary_v1.py',
    'validate_story_anti_double_clear_idempotency_design_v1.py',
    'validate_story_runtime_adapter_first_node_alpha_qa_and_progress_v10_v1.py',
]
DOCS=[
    'docs/divine/392_STORY_RUNTIME_ADAPTER_v1_CONTRACT.md',
    'docs/divine/393_STORY_FIRST_NODE_ALPHA_FIXTURE_AND_PAYLOAD.md',
    'docs/divine/394_STORY_FIRST_NODE_RUNTIME_PREVIEW_SCREEN.md',
    'docs/divine/395_STORY_RESULT_REWARD_PROGRESS_PREVIEW_BOUNDARY.md',
    'docs/divine/396_STORY_ANTI_DOUBLE_CLEAR_IDEMPOTENCY_DESIGN.md',
    'docs/divine/397_STORY_RUNTIME_ADAPTER_FIRST_NODE_ALPHA_QA_AND_PROGRESS_v10.md',
    'docs/divine/398_MEGA_RELEASE_ACCELERATION_15_STORY_RUNTIME_ADAPTER_AND_FIRST_NODE_ALPHA_v66.md',
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
        ('marker_version','mega_release_acceleration_15_v66_rollup_marker_v1'),
        ('pack',PACK),('public_sync_tag',TAG),
        ('server_py_changed',False),('battle_engine_changed',False),
        ('combat_tsx_changed',False),('story_tsx_changed',False),
        ('material_raid_preview_changed',False),
        ('character_bible_changed',False),('final_numbers_changed',False),
        ('db_writes',0),('real_db_writes',0),('mongo_url_used',False),
        ('pymongo_used',False),('motor_used',False),('redis_used',False),
        ('filesystem_writes',0),
        ('reward_grant_enabled',False),('reward_grant_executed',False),
        ('materials_granted',False),('inventory_mutation',False),
        ('wallet_mutation',False),
        ('home_menu_mandatory_routing',False),('asset_copy_or_import',False),
        ('validator_weakening',False),('fake_pass',False),
        ('runtime_runner_created',False),('runtime_activation_enabled',False),
        ('story_runtime_authoritative',False),('story_permanent_progress',False),
        ('story_reward_grant',False),
        ('frontend_changes_in_v66',True),
    ):
        if m.get(k)!=v: f(f'[5] rollup marker {k}!={v} (got {m.get(k)})')
    if m.get('tracks')!=['A','B','C','D','E','F','G']: f('[5] rollup tracks mismatch')
    exp_t=['PROJECT-STORY-RUNTIME-ADAPTER-v1-CONTRACT',
           'PROJECT-STORY-FIRST-NODE-ALPHA-FIXTURE-AND-PAYLOAD',
           'PROJECT-STORY-FIRST-NODE-RUNTIME-PREVIEW-SCREEN',
           'PROJECT-STORY-RESULT-REWARD-PROGRESS-PREVIEW-BOUNDARY',
           'PROJECT-STORY-ANTI-DOUBLE-CLEAR-IDEMPOTENCY-DESIGN',
           'PROJECT-STORY-RUNTIME-ADAPTER-FIRST-NODE-ALPHA-QA-AND-PROGRESS-v10',
           'MEGA-RELEASE-ACCELERATION-15-v66-ROLLUP']
    if m.get('suite_tuples')!=exp_t: f('[5] rollup suite_tuples mismatch')
    mb=m.get('md5_invariants') or {}
    for rel,exp in INV.items():
        if mb.get(rel)!=exp: f(f'[5] rollup md5_invariants {rel}!={exp}')
    fcs=m.get('frontend_changes_scope') or []
    if 'frontend/app/story-first-node-runtime-preview.tsx' not in fcs:
        f('[5] rollup frontend_changes_scope missing the new screen')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] MEGA_RELEASE_ACCELERATION_15_v66_ROLLUP validator'); sys.exit(1)
print('[PASS] MEGA_RELEASE_ACCELERATION_15_v66_ROLLUP validator'); sys.exit(0)
