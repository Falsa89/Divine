#!/usr/bin/env python3
"""Validator: PROJECT-ROUTER-ADAPTER-PREVIEW-HARDENING (v61 Track C)."""
from __future__ import annotations
import os, sys, re, json

ROOT = '/app'
PACK = 'MEGA_RELEASE_ACCELERATION_10_STORY_TIMELINE_ROUTER_HARDENING_RUNTIME_GATE_SUPER_PACK_v61'
TAG = 'PUBLIC_SYNC_TAG_v61_MEGA_RELEASE_ACCELERATION_10_STORY_TIMELINE_ROUTER_HARDENING_RUNTIME_GATE'
CONTRACT = os.path.join(ROOT, 'data/design/release_acceleration/visual_battle_runner_router_adapter_hardening_contract_v1.json')
VAL = os.path.join(ROOT, 'data/design/release_acceleration/visual_battle_runner_payload_adapter_validation_rules_v1.json')
MARKER = os.path.join(ROOT, 'data/design/release_acceleration/router_adapter_preview_hardening_marker_v1.json')
ROUTER = os.path.join(ROOT, 'frontend/app/visual-battle-preview-router.tsx')

FAILS = []
def fail(m): FAILS.append(m)

if not os.path.exists(CONTRACT): fail('missing contract')
else:
    c = json.load(open(CONTRACT))
    if c.get('version') != 'visual_battle_runner_router_adapter_hardening_contract_v1': fail('contract.version')
    if c.get('extends') != 'visual_battle_runner_router_adapter_preview_contract_v1': fail('contract.extends')
    if c.get('adapter_preview_version') != 'adapter_preview_v61': fail('contract.adapter_preview_version')
    if c.get('contract_version') != 'visual_battle_runner_payload_v0': fail('contract.contract_version')
    req = c.get('required_fields_for_payload_like_ready') or []
    for f in ('mode','battle_seed_preview'):
        if f not in req: fail(f'contract.required_fields missing {f}')
    sv = c.get('adapter_status_values') or []
    for s in ('payload_like_ready','missing_required_fields'):
        if s not in sv: fail(f'contract.adapter_status_values missing {s}')
    pms = c.get('per_mode_state_display') or {}
    for m, st in (('material_raid','alpha_loop_closed_v53'),('training','local_dummy_seed_wired_v56'),
                  ('boss','local_dummy_seed_wired_v59'),('tower','local_dummy_seed_wired_v59'),
                  ('event','local_dummy_seed_wired_v60'),('arena','local_dummy_seed_wired_v60'),
                  ('story','local_dummy_seed_wired_v61')):
        if pms.get(m) != st: fail(f'contract.per_mode_state_display.{m} != {st}')

if not os.path.exists(VAL): fail('missing validation rules')
else:
    v = json.load(open(VAL))
    if v.get('version') != 'visual_battle_runner_payload_adapter_validation_rules_v1': fail('val.version')
    if v.get('db_writes') != 0: fail('val.db_writes')
    rules = v.get('rules') or []
    if len(rules) < 5: fail(f'val.rules count too low: {len(rules)}')

if not os.path.exists(ROUTER): fail('missing router')
else:
    src = open(ROUTER).read()
    if 'adapter_preview_v61' not in src: fail('router missing adapter_preview_v61')
    if 'visual_battle_runner_payload_v0' not in src: fail('router missing contract_version reference')
    if 'adapter_status: payload_like_ready' not in src: fail('router missing payload_like_ready status')
    if 'adapter_status: missing_required_fields' not in src: fail('router missing missing_required_fields status')
    if 'missing_fields' not in src: fail('router missing missing_fields display')
    if 'Per-mode state' not in src: fail('router missing Per-mode state block')
    if 'local_dummy_seed_wired_v61' not in src: fail('router missing story v61 state')
    # ensure existing mode blocks preserved
    for m in ('training','boss','story','tower','event','arena'):
        if f"mode === '{m}'" not in src: fail(f'regression: missing mode block {m}')
    for pat, desc in [
        (r"from\s+['\"][^'\"]*combat['\"]", 'combat import'),
        (r"from\s+['\"]\.\./story['\"]", 'parent story import'),
        (r'react-native-reanimated', 'reanimated'),
        (r'\bfetch\s*\(', 'fetch call'),
        (r'\baxios\b', 'axios'),
        (r"['\"`(]/api/", '/api/ use'),
        (r'battle_engine\s*\(', 'battle_engine call'),
        (r"from\s+['\"][^'\"]*battle_engine", 'battle_engine import'),
        (r'>\s*Claim\s*<', 'Claim CTA'),
    ]:
        if re.search(pat, src): fail(f'router forbidden {desc}')

if not os.path.exists(MARKER): fail('missing marker')
else:
    mk = json.load(open(MARKER))
    if mk.get('marker_version') != 'router_adapter_preview_hardening_marker_v1': fail('marker.version')
    for k, v in (('pack',PACK),('public_sync_tag',TAG),
                 ('adapter_preview_version','adapter_preview_v61'),
                 ('design_only',True),('adapter_preview_only',True),
                 ('runtime_runner_created',False),('backend_used',False),
                 ('battle_engine_runtime_used',False),('db_writes',0),
                 ('validator_weakening',False),('fake_pass',False)):
        if mk.get(k) != v: fail(f'marker.{k} != {v}')

if FAILS:
    for f in FAILS: print('FAIL:', f)
    print('[FAIL] PROJECT-ROUTER-ADAPTER-PREVIEW-HARDENING'); sys.exit(1)
print('[PASS] PROJECT-ROUTER-ADAPTER-PREVIEW-HARDENING'); sys.exit(0)
