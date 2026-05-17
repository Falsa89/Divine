#!/usr/bin/env python3
"""SAFETY-ROLLUP-E — Validator for rollup v5."""
from __future__ import annotations
import json, sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

ROLLUP = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v5.json')
API = 'http://127.0.0.1:8001/api'
failures: list[str] = []
checks: list[tuple[str,bool,str]] = []
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('rollup_present', ROLLUP.exists(), str(ROLLUP))
r = json.loads(ROLLUP.read_text())
rec('id_v5', r.get('report_id') == 'collection_affinity_runtime_activation_readiness_rollup_v5', '')
rec('task', r.get('task_origin') == 'SAFETY-ROLLUP-E', '')
rec('supersedes_v4', r.get('supersedes') == 'collection_affinity_runtime_activation_readiness_rollup_v4', '')
rec('design_only', r.get('design_only') is True, '')
rec('db_write_false', r.get('db_write') is False, '')
rec('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
rec('product_signoff_true', r.get('product_signoff') is True, '')
for k in ('engineering_signoff','qa_signoff','economy_balance_signoff','rollback_owner_signoff'):
    rec(f'{k}_false', r.get(k) is False, '')
rec('operator_signoff_ready_false', r.get('operator_signoff_ready') is False, '')
rec('af2n_allowed_false', r.get('AF2N_allowed') is False, '')
rec('overall_runtime_false', r.get('overall_runtime_activation_ready') is False, '')
rec('go_no_go_runtime', r.get('go_no_go_decision') == 'NO_GO_RUNTIME', '')
rec('axis_layer_go', r.get('axis_layer_decision') == 'GO_AXIS', '')
rec('ledger_schema_ready', r.get('ledger_schema_ready') is True, '')
rec('ledger_row_count_zero', r.get('ledger_row_count_zero') is True, '')
rec('axis_layer_ready', r.get('axis_layer_ready') is True, '')
rec('ops_layer_ready', r.get('ops_layer_ready') is True, '')
rec('stack_g_preconnection_ready', r.get('stack_g_preconnection_ready') is True, '')
rec('k6_prep_pass', r.get('k6_prep_probe_pass') is True, '')
rec('migration_applied', r.get('migration_applied') is True, '')
rec('supervisor_wiring_state',
    r.get('supervisor_wiring_state') in ('READY_NOT_APPLIED','APPLIED'), f"got {r.get('supervisor_wiring_state')}")

subs = r.get('subsystems') or {}
rec('sub_axis_go', (subs.get('axis_layer') or {}).get('status') == 'GO', '')
rec('sub_ops_go', (subs.get('ops_layer') or {}).get('status') == 'GO', '')
rec('sub_migration_applied', (subs.get('migration_commit') or {}).get('status') == 'APPLIED_ZERO_ROWS', '')
rec('sub_load_full_pass', (subs.get('load_probe_full') or {}).get('status') == 'PASS', '')
rec('sub_signoff_partial', (subs.get('operator_signoff_v3') or {}).get('status') == 'PARTIAL_PRODUCT_ONLY', '')
rec('sub_stack_g_ready', (subs.get('stack_g_preconnection') or {}).get('status') == 'READY_NOT_WIRED', '')
rec('sub_battle_no_go', (subs.get('battle_runtime') or {}).get('status') == 'NO_GO', '')
rec('sub_borea_go', (subs.get('borea_layer') or {}).get('status') == 'GO', '')

rec('no_go_reasons_min_5', len(r.get('runtime_no_go_reasons') or []) >= 5, '')
rec('af2n_blockers_min_4', len(r.get('AF2N_blockers') or []) >= 4, '')
rec('invariants_min_10', len(r.get('invariants_currently_holding') or []) >= 10, '')

# Live invariants
try:
    with urlopen(API + '/heroes', timeout=6) as resp:
        d = json.loads(resp.read().decode())
    heroes = d if isinstance(d, list) else (d.get('heroes') or [])
    rec('live_heroes_100', len(heroes) == 100, f'got {len(heroes)}')
    ids = {h.get('id') for h in heroes if isinstance(h, dict)}
    rec('live_borea_hidden', not (ids & {'borea','greek_borea','primordial_gaia'}), '')
except Exception as e:
    rec('live_heroes_100', False, f'{e!r}')
    rec('live_borea_hidden', False, f'{e!r}')

def _post(p, b):
    req = Request(API+p, data=json.dumps(b).encode(), method='POST', headers={'Content-Type':'application/json'})
    try:
        with urlopen(req, timeout=6) as r: return r.status
    except HTTPError as e: return e.code
    except URLError: return -1
rec('live_gift_spend_423', _post('/affinity/gift-spend', {}) == 423, '')
rec('live_gift_spend_borea_404', _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'abcd1234'}) == 404, '')

print('='*70); print('SAFETY-ROLLUP-E — v5 Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
