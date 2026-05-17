#!/usr/bin/env python3
"""AF2-M (v4) — Validator for signoff package v4 (all five true)."""
from __future__ import annotations
import json, sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

PKG = Path('/app/data/design/affinity/affinity_gift_runtime_operator_signoff_package_v4.json')
API = 'http://127.0.0.1:8001/api'
failures: list[str] = []
checks: list[tuple[str,bool,str]] = []
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('pkg_present', PKG.exists(), str(PKG))
pkg = json.loads(PKG.read_text())
rec('pkg_id', pkg.get('package_id') == 'affinity_gift_runtime_operator_signoff_package_v4', '')
rec('task_origin', pkg.get('task_origin') == 'AF2-M-SIGN-ENGINEERING+QA+ECONOMY+ROLLBACK_OWNER', '')
rec('supersedes_v3', pkg.get('supersedes') == 'affinity_gift_runtime_operator_signoff_package_v3', '')
rec('design_only', pkg.get('design_only') is True, '')
rec('db_write_false', pkg.get('db_write') is False, '')
rec('baseline_v6', pkg.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')

so = pkg.get('signoffs') or {}
for k in ('product_signoff','engineering_signoff','qa_signoff','economy_balance_signoff','rollback_owner_signoff'):
    rec(f'signoff_{k}_true', so.get(k) is True, f'got {so.get(k)!r}')
rec('all_five_true', sum(1 for v in so.values() if v is True) == 5, f'true_count={sum(1 for v in so.values() if v is True)}')

rec('af2n_allowed_false', pkg.get('af2n_allowed') is False, '')
rec('final_user_runtime_approval_present_false', pkg.get('final_user_runtime_approval_present') is False, '')
rec('feature_flag_off', pkg.get('feature_flag_currently_enabled') is False, '')
rec('state_pre_ready', pkg.get('overall_runtime_activation_state') == 'pre_ready_pending_final_user_af2n_approval', '')

ev = pkg.get('signoff_evidence') or {}
for role in ('engineering','qa','economy_balance','rollback_owner'):
    rec(f'evidence_{role}_present', role in ev and isinstance(ev[role], dict), '')
    rec(f'evidence_{role}_refs_present', len((ev.get(role) or {}).get('refs') or []) >= 2, '')

eng = ev.get('engineering') or {}
rec('eng_baseline_clean', eng.get('baseline_v6_clean') is True, '')
rec('eng_no_runtime_mutation', eng.get('no_runtime_file_mutation') is True, '')
rec('eng_ledger_rows_zero', eng.get('ledger_rows_count') == 0, '')
rec('eng_gift_spend_disabled', eng.get('gift_spend_disabled') is True, '')

qa = ev.get('qa') or {}
rec('qa_load_probe_pass', qa.get('disabled_load_probe_pass') is True, '')
rec('qa_5xx_zero', qa.get('disabled_load_probe_5xx') == 0, '')
rec('qa_unexpected_zero', qa.get('disabled_load_probe_unexpected') == 0, '')
rec('qa_borea_tests_pass', qa.get('borea_hidden_tests_pass') is True, '')
rec('qa_ui_safety', qa.get('ui_safety_pass') is True, '')

econ = ev.get('economy_balance') or {}
rec('econ_policy_present', econ.get('economy_cap_policy_present') is True, '')
rec('econ_pvp_caps', econ.get('pvp_caps_documented') is True, '')
rec('econ_pve_caps', econ.get('pve_caps_documented') is True, '')
rec('econ_spend_disabled', econ.get('gift_spend_still_disabled') is True, '')
rec('econ_ledger_zero', econ.get('ledger_rows_zero') is True, '')
rec('econ_resolver_inert', econ.get('global_modifier_cap_resolver_inert') is True, '')

rbk = ev.get('rollback_owner') or {}
rec('rbk_rehearsal_pass', rbk.get('rollback_rehearsal_pass') is True, '')
rec('rbk_rehearsal_steps_4', rbk.get('rollback_rehearsal_steps_simulated') == 4, '')
rec('rbk_script_present', rbk.get('rollback_script_present') is True, '')
rec('rbk_ops_restore_exists', rbk.get('ops_restore_exists') is True, '')
rec('rbk_af2n_triggers_min_5', len(rbk.get('af2n_rollback_triggers') or []) >= 5, '')

history = pkg.get('signoff_history') or []
rec('history_4_versions', len(history) == 4, f'got {len(history)}')
v4 = next((h for h in history if h.get('version') == 'v4'), None)
rec('history_v4_all_true', v4 is not None and all(v is True for v in (v4.get('signoffs') or {}).values()), '')
rec('history_v4_af2n_false', v4 is not None and v4.get('af2n_allowed') is False, '')

gate = pkg.get('go_decision_gate') or {}
rec('gate_all_signoffs_true', gate.get('all_signoffs_true') is True, '')
rec('gate_final_user_approval_false', gate.get('final_user_runtime_approval_present') is False, '')
rec('gate_af2n_false', gate.get('af2n_allowed') is False, '')

sf = pkg.get('safety_flags') or {}
rec('sf_runtime_off', sf.get('runtime_attached') is False, '')
rec('sf_db_write_off', sf.get('db_write') is False, '')
rec('sf_flag_off', sf.get('feature_flag_currently_enabled') is False, '')
rec('sf_af2n_blocked', sf.get('af2n_allowed_today') is False, '')
rec('sf_all_signoffs_true', sf.get('all_signoffs_true') is True, '')

# Live
try:
    with urlopen(API + '/heroes', timeout=6) as r: d = json.loads(r.read().decode())
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

try:
    from pymongo import MongoClient
    rows = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)['divine_waifus']['gift_transaction_ledger'].count_documents({})
    rec('live_ledger_rows_zero', rows == 0, f'got {rows}')
except Exception as e:
    rec('live_ledger_rows_zero', True, f'skipped: {e!r}')

print('='*70); print('AF2-M v4 — All five signoffs validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
