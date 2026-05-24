#!/usr/bin/env python3
# PROJECT_W TRACK A — SECOND SLICE PROD PRECHECK / SIGNATURE GATE
# Read-only validator. Verifica firme prod, stage marker e classificazione ambiente.
# Esce 0 (PASS) anche se il verdict è BLOCKING_MISSING_SIGNATURES, perché il blocco
# è il comportamento ATTESO e corretto per questa modalità (READY_NOT_APPLIED).
import json, sys, hashlib, os
from pathlib import Path

ROOT = Path('/app')
MARKER = ROOT / 'data/design/status_effects/project_w_second_slice_prod_precheck_signature_gate_v1.json'
ENV = ROOT / 'backend/.env'
BATTLE_ENGINE = ROOT / 'backend/battle_engine.py'
BATTLE_ENGINE_MD5_AUTHORIZED = '151ca35ad3bc35f0a6209cb3744ed440'
ENV_MD5_PRE_FLIP_AUTHORIZED = 'ff60bbb79efa329b71aa8ed351ea89b3'

PROD_SIGS = [
    'PROD_ROLLOUT_USER_APPROVAL', 'PROD_ROLLOUT_QA_APPROVAL', 'PROD_ROLLOUT_OPS_APPROVAL',
    'PROD_ROLLOUT_OBSERVABILITY_APPROVAL', 'PROD_ROLLOUT_ROLLBACK_RUNBOOK_APPROVAL',
    'PROD_ROLLOUT_SECURITY_APPROVAL', 'STATUS_RUNTIME_SECOND_SLICE_PROD_OK',
]
STAGE_MARKERS = [
    'STATUS_SECOND_SLICE_PROD_STAGE_1_APPROVAL',
    'STATUS_SECOND_SLICE_PROD_STAGE_5_APPROVAL',
    'STATUS_SECOND_SLICE_PROD_STAGE_25_APPROVAL',
    'STATUS_SECOND_SLICE_PROD_STAGE_100_APPROVAL',
]

def md5(p):
    return hashlib.md5(p.read_bytes()).hexdigest() if p.exists() else None

def main():
    if not MARKER.exists():
        print('[FAIL] missing marker JSON'); return 1
    m = json.loads(MARKER.read_text())
    env_text = ENV.read_text() if ENV.exists() else ''
    present_sigs = [k for k in PROD_SIGS if f'{k}=true' in env_text]
    present_stages = [k for k in STAGE_MARKERS if f'{k}=true' in env_text]
    be = md5(BATTLE_ENGINE)
    env_md5 = md5(ENV)
    # Asserzioni invarianti
    assert be == BATTLE_ENGINE_MD5_AUTHORIZED, f'battle_engine.py md5 drift: {be}'
    assert env_md5 == ENV_MD5_PRE_FLIP_AUTHORIZED, f'.env md5 drift: {env_md5}'
    assert m['flag_flipped'] is False
    assert m['prod_env_touched'] is False
    assert m['db_writes'] is False
    assert m['battle_engine_mutated'] is False
    assert m['env_classification'] in ('NON_PROD_LOCAL_ONLY', 'PROD_CONFIRMED', 'PROD_LIKE_BLOCKED', 'ENV_NOT_PROVEN')
    assert m['env_classification'] != 'PROD_CONFIRMED' or len(present_sigs) == len(PROD_SIGS)
    # Coerenza marker vs realtà
    assert sorted(m['prod_signatures_present']) == sorted(present_sigs)
    assert sorted(m['stage_markers_present']) == sorted(present_stages)
    if len(present_sigs) == len(PROD_SIGS) and m['env_classification'] == 'PROD_CONFIRMED':
        expected = 'TRACK_A_SECOND_SLICE_PROD_PRECHECK_READY_ALL_SIGNATURES_PRESENT'
    elif m['env_classification'] not in ('PROD_CONFIRMED',):
        expected = 'TRACK_A_SECOND_SLICE_PROD_PRECHECK_BLOCKING_MISSING_SIGNATURES'
    else:
        expected = 'TRACK_A_SECOND_SLICE_PROD_PRECHECK_BLOCKING_MISSING_SIGNATURES'
    assert m['verdict'] == expected, f'verdict mismatch: {m["verdict"]} vs {expected}'
    missing = len(PROD_SIGS) - len(present_sigs)
    print(f'[PASS] PROJECT_W Track A precheck GATE — env={m["env_classification"]}, prod_sigs={len(present_sigs)}/{len(PROD_SIGS)}, stage_markers={len(present_stages)}/{len(STAGE_MARKERS)}, missing_sigs={missing} → BLOCKING (correct)')
    return 0

if __name__ == '__main__':
    sys.exit(main())
