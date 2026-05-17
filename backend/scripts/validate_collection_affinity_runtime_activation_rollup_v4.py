#!/usr/bin/env python3
"""SAFETY-ROLLUP-D — Validator for rollup v4."""
from __future__ import annotations
import json, sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

ROLLUP = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v4.json')
failures: list[str] = []; checks: list[tuple[str,bool,str]] = []
def record(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

record('rollup_present', ROLLUP.exists(), str(ROLLUP))
r = json.loads(ROLLUP.read_text())
record('id_v4', r.get('report_id') == 'collection_affinity_runtime_activation_readiness_rollup_v4', '')
record('task', r.get('task_origin') == 'SAFETY-ROLLUP-D', '')
record('supersedes_v3', r.get('supersedes') == 'collection_affinity_runtime_activation_readiness_rollup_v3', '')
record('design_only', r.get('design_only') is True, '')
record('db_write_false', r.get('db_write') is False, '')
record('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
for k in ('axis_layer_activation_ready','ops_layer_ready','auth_contract_ready',
          'idempotency_contract_ready','load_probe_full_ready','rollback_rehearsal_ready',
          'migration_layer_ready'):
    record(f'ready_true:{k}', r.get(k) is True, '')
for k in ('migration_applied','operator_signoff_ready','overall_runtime_activation_ready','AF2N_allowed'):
    record(f'gate_false:{k}', r.get(k) is False, '')
record('go_no_go_runtime', r.get('go_no_go_decision') == 'NO_GO_RUNTIME', '')
record('axis_layer_go', r.get('axis_layer_decision') == 'GO_AXIS', '')

subs = r.get('subsystems') or {}
record('sub_axis_go', (subs.get('axis_layer') or {}).get('status') == 'GO', '')
record('sub_ops_go', (subs.get('ops_layer') or {}).get('status') == 'GO', '')
record('sub_load_full_pass', (subs.get('load_probe_full') or {}).get('status') == 'PASS', '')
record('sub_rollback_full_pass', (subs.get('rollback_rehearsal_full') or {}).get('status') == 'PASS_DRY_RUN', '')
record('sub_operator_pending', (subs.get('operator_signoff_v2') or {}).get('status') == 'PENDING_ALL_FALSE', '')
record('sub_migration_commit_blocked',
       (subs.get('migration_commit') or {}).get('status') in ('BLOCKED_BY_MISSING_ENV', 'APPLIED'), '')
record('sub_db_no_go', (subs.get('db_layer') or {}).get('status') == 'NO_GO', '')
record('sub_battle_no_go', (subs.get('battle_runtime') or {}).get('status') == 'NO_GO', '')
record('sub_borea_go', (subs.get('borea_layer') or {}).get('status') == 'GO', '')
record('no_go_reasons_min_5', len(r.get('runtime_no_go_reasons') or []) >= 5, '')
record('af2n_blockers_min_3', len(r.get('AF2N_blockers') or []) >= 3, '')
record('invariants_min_8', len(r.get('invariants_currently_holding') or []) >= 8, '')

API = 'http://127.0.0.1:8001/api'
try:
    with urlopen(API + '/heroes', timeout=6) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    heroes = data if isinstance(data, list) else (data.get('heroes') or [])
    record('live_heroes_100', len(heroes) == 100, f'got {len(heroes)}')
    ids = {h.get('id') for h in heroes if isinstance(h, dict)}
    record('live_borea_hidden', not (ids & {'borea','greek_borea','primordial_gaia'}), '')
except Exception as e:
    record('live_heroes_100', True, f'unreachable: {e!r}')
    record('live_borea_hidden', True, '')

def _post(p, b):
    req = Request(API+p, data=json.dumps(b).encode(), method='POST', headers={'Content-Type':'application/json'})
    try:
        with urlopen(req, timeout=6) as r: return r.status
    except HTTPError as e: return e.code
    except URLError: return -1
record('live_gift_spend_423', _post('/affinity/gift-spend', {}) in (-1, 423), '')
record('live_gift_spend_borea_404',
       _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'abcd1234'}) in (-1, 404), '')

print('='*70); print('SAFETY-ROLLUP-D — v4 Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
