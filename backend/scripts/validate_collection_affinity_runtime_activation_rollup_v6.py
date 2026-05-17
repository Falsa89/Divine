#!/usr/bin/env python3
"""SAFETY-ROLLUP-F — Validator for rollup v6."""
from __future__ import annotations
import json, sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

R = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v6.json')
API = 'http://127.0.0.1:8001/api'
failures: list[str] = []
checks: list[tuple[str,bool,str]] = []
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('rollup_present', R.exists(), str(R))
r = json.loads(R.read_text())
rec('id_v6', r.get('report_id') == 'collection_affinity_runtime_activation_readiness_rollup_v6', '')
rec('task', r.get('task_origin') == 'SAFETY-ROLLUP-F', '')
rec('supersedes_v5', r.get('supersedes') == 'collection_affinity_runtime_activation_readiness_rollup_v5', '')
rec('design_only', r.get('design_only') is True, '')
rec('db_write_false', r.get('db_write') is False, '')
rec('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')

for k in ('product_signoff','engineering_signoff','qa_signoff','economy_balance_signoff','rollback_owner_signoff'):
    rec(f'{k}_true', r.get(k) is True, '')
rec('all_operator_signoffs_true', r.get('all_operator_signoffs_true') is True, '')
rec('operator_signoff_ready', r.get('operator_signoff_ready') is True, '')
rec('final_user_approval_required', r.get('final_user_runtime_approval_required') is True, '')
rec('final_user_approval_present_false', r.get('final_user_runtime_approval_present') is False, '')
rec('af2n_allowed_false', r.get('AF2N_allowed') is False, '')
rec('overall_runtime_ready_false', r.get('overall_runtime_activation_ready') is False, '')
rec('state_ready_pending', r.get('overall_runtime_activation_state') == 'ready_pending_final_user_runtime_approval', '')
rec('gift_spend_disabled', r.get('gift_spend_currently_disabled') is True, '')
rec('go_no_go_runtime', r.get('go_no_go_decision') == 'NO_GO_RUNTIME', '')
rec('axis_layer_go', r.get('axis_layer_decision') == 'GO_AXIS', '')
for k in ('ledger_schema_ready','ledger_row_count_zero','axis_layer_ready','ops_layer_ready',
          'stack_g_preconnection_ready','k6_live_prep_pass','migration_applied'):
    rec(f'{k}_true', r.get(k) is True, '')
rec('supervisor_wiring_state_known',
    r.get('supervisor_wiring_state') in ('READY_NOT_APPLIED','APPLIED'), f'got {r.get("supervisor_wiring_state")}')

subs = r.get('subsystems') or {}
rec('sub_axis_go', (subs.get('axis_layer') or {}).get('status') == 'GO', '')
rec('sub_ops_go', (subs.get('ops_layer') or {}).get('status') == 'GO', '')
rec('sub_migration_applied', (subs.get('migration_commit') or {}).get('status') == 'APPLIED_ZERO_ROWS', '')
rec('sub_load_full_pass', (subs.get('load_probe_full') or {}).get('status') == 'PASS', '')
rec('sub_k6_live_pass', (subs.get('k6_live_prep') or {}).get('status') == 'PASS', '')
rec('sub_signoff_all_true', (subs.get('operator_signoff_v4') or {}).get('status') == 'ALL_TRUE', '')
rec('sub_stack_g_ready', (subs.get('stack_g_preconnection') or {}).get('status') == 'READY_NOT_WIRED', '')
rec('sub_af2n_ready_no_go', (subs.get('af2n_go_nogo_package') or {}).get('status') == 'READY_NO_GO', '')
rec('sub_battle_no_go', (subs.get('battle_runtime') or {}).get('status') == 'NO_GO', '')
rec('sub_borea_go', (subs.get('borea_layer') or {}).get('status') == 'GO', '')

rec('no_go_reasons_min_5', len(r.get('runtime_no_go_reasons') or []) >= 5, '')
rec('af2n_blockers_min_3', len(r.get('AF2N_blockers') or []) >= 3, '')
rec('invariants_min_10', len(r.get('invariants_currently_holding') or []) >= 10, '')

# Live
try:
    with urlopen(API + '/heroes', timeout=6) as resp: d = json.loads(resp.read().decode())
    heroes = d if isinstance(d, list) else (d.get('heroes') or [])
    rec('live_heroes_100', len(heroes) == 100, f'got {len(heroes)}')
    ids = {h.get('id') for h in heroes if isinstance(h, dict)}
    rec('live_borea_hidden', not (ids & {'borea','greek_borea','primordial_gaia'}), '')
except Exception as e:
    rec('live_heroes_100', False, f'{e!r}')

def _post(p, b):
    req = Request(API+p, data=json.dumps(b).encode(), method='POST', headers={'Content-Type':'application/json'})
    try:
        with urlopen(req, timeout=6) as r: return r.status
    except HTTPError as e: return e.code
    except URLError: return -1
rec('live_gift_spend_423', _post('/affinity/gift-spend', {}) == 423, '')
rec('live_gift_spend_borea_404', _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'abcd1234'}) == 404, '')

print('='*70); print('SAFETY-ROLLUP-F — v6 Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
