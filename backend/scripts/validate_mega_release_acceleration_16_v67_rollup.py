#!/usr/bin/env python3
"""v67 Rollup validator."""
from __future__ import annotations
import os, sys, hashlib, subprocess, json
ROOT='/app'
SUITE=os.path.join(ROOT,'backend/scripts/run_hero_skill_kit_validator_suite.py')
ROLL=os.path.join(ROOT,'data/design/release_acceleration/mega_release_acceleration_16_v67_rollup_marker_v1.json')
PACK='MEGA_RELEASE_ACCELERATION_16_STORY_RUNTIME_ADAPTER_WIDEN_AND_IDEMPOTENCY_SIMULATION_PACK_v67'
TAG='PUBLIC_SYNC_TAG_v67_MEGA_RELEASE_ACCELERATION_16_STORY_RUNTIME_ADAPTER_WIDEN_IDEMPOTENCY'
TUPLES=[
    "'PROJECT-STORY-ALPHA-NODES-002-003-PAYLOAD'",
    "'PROJECT-STORY-RUNTIME-PREVIEW-WIDENING'",
    "'PROJECT-STORY-CLEAR-IDEMPOTENCY-SIMULATOR'",
    "'PROJECT-STORY-CLEAR-REPLAY-LEDGER-DRY-RUN'",
    "'PROJECT-STORY-CLEAR-ROLLBACK-OBSERVATION'",
    "'PROJECT-STORY-RUNTIME-ADAPTER-WIDEN-IDEMPOTENCY-QA'",
    "'MEGA-RELEASE-ACCELERATION-16-v67-ROLLUP'",
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
    'validate_story_alpha_nodes_002_003_payload_v1.py',
    'validate_story_runtime_preview_widening_v1.py',
    'validate_story_clear_idempotency_simulator_v1.py',
    'validate_story_clear_replay_ledger_dry_run_v1.py',
    'validate_story_clear_rollback_observation_v1.py',
    'validate_story_runtime_adapter_widen_idempotency_qa_v1.py',
]
DOCS=[
    'docs/divine/399_STORY_ALPHA_NODES_002_003_FIXTURE_AND_PAYLOAD.md',
    'docs/divine/400_STORY_RUNTIME_PREVIEW_WIDENING.md',
    'docs/divine/401_STORY_CLEAR_IDEMPOTENCY_DRY_RUN_SIMULATOR.md',
    'docs/divine/402_STORY_CLEAR_REPLAY_AND_LEDGER_DRY_RUN.md',
    'docs/divine/403_STORY_CLEAR_ROLLBACK_OBSERVATION_SIMULATION.md',
    'docs/divine/404_STORY_RUNTIME_ADAPTER_WIDEN_IDEMPOTENCY_QA.md',
    'docs/divine/405_MEGA_RELEASE_ACCELERATION_16_STORY_RUNTIME_ADAPTER_WIDEN_IDEMPOTENCY_v67.md',
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
        ('marker_version','mega_release_acceleration_16_v67_rollup_marker_v1'),
        ('pack',PACK),('public_sync_tag',TAG),
        ('server_py_changed',False),('battle_engine_changed',False),
        ('combat_tsx_changed',False),('story_tsx_changed',False),
        ('material_raid_preview_changed',False),
        ('character_bible_changed',False),('final_numbers_changed',False),
        ('db_writes',0),('real_db_writes',0),
        ('mongo_url_used',False),('pymongo_used',False),
        ('motor_used',False),('redis_used',False),('filesystem_writes',0),
        ('reward_grant_enabled',False),('materials_granted',False),
        ('inventory_mutation',False),('wallet_mutation',False),
        ('runtime_runner_created',False),('runtime_activation_enabled',False),
        ('story_runtime_authoritative',False),('story_permanent_progress',False),
        ('story_reward_grant',False),('battle_engine_runtime',False),
        ('frontend_changes_in_v67',True),
        ('home_menu_mandatory_routing',False),('asset_copy_or_import',False),
        ('validator_weakening',False),('fake_pass',False),
    ):
        if m.get(k)!=v: f(f'[5] rollup marker {k}!={v} (got {m.get(k)})')
    if m.get('tracks')!=['A','B','C','D','E','F','G']: f('[5] rollup tracks mismatch')
    exp_t=['PROJECT-STORY-ALPHA-NODES-002-003-PAYLOAD',
           'PROJECT-STORY-RUNTIME-PREVIEW-WIDENING',
           'PROJECT-STORY-CLEAR-IDEMPOTENCY-SIMULATOR',
           'PROJECT-STORY-CLEAR-REPLAY-LEDGER-DRY-RUN',
           'PROJECT-STORY-CLEAR-ROLLBACK-OBSERVATION',
           'PROJECT-STORY-RUNTIME-ADAPTER-WIDEN-IDEMPOTENCY-QA',
           'MEGA-RELEASE-ACCELERATION-16-v67-ROLLUP']
    if m.get('suite_tuples')!=exp_t: f('[5] rollup suite_tuples mismatch')
    mb=m.get('md5_invariants') or {}
    for rel,exp in INV.items():
        if mb.get(rel)!=exp: f(f'[5] rollup md5_invariants {rel}!={exp}')
if F:
    for x in F: print('FAIL:',x)
    print('[FAIL] MEGA_RELEASE_ACCELERATION_16_v67_ROLLUP validator'); sys.exit(1)
print('[PASS] MEGA_RELEASE_ACCELERATION_16_v67_ROLLUP validator'); sys.exit(0)
