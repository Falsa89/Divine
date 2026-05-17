#!/usr/bin/env python3
"""AF2-N GO/NO-GO preflight package validator (NOT a flag-flip)."""
from __future__ import annotations
import json, os, sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

PKG = Path('/app/data/design/affinity/af2n_go_no_go_preflight_package_v1.json')
API = 'http://127.0.0.1:8001/api'

failures: list[str] = []
checks: list[tuple[str,bool,str]] = []
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('pkg_present', PKG.exists(), str(PKG))
p = json.loads(PKG.read_text())
rec('id', p.get('package_id') == 'af2n_go_no_go_preflight_package_v1', '')
rec('design_only', p.get('design_only') is True, '')
rec('runtime_off', p.get('runtime_attached') is False, '')
rec('do_not_execute', p.get('do_not_execute_in_this_task') is True, '')
rec('decision_no_go', p.get('go_no_go_decision_today') == 'NO_GO_PENDING_FINAL_USER_APPROVAL', '')

cs = p.get('current_state') or {}
rec('cs_all_signoffs', cs.get('all_signoffs_true') is True, '')
rec('cs_final_user_present_false', cs.get('final_user_runtime_approval_present') is False, '')
rec('cs_af2n_allowed_false', cs.get('AF2N_allowed') is False, '')
rec('cs_runtime_flag_off', cs.get('AFFINITY_GIFT_RUNTIME_ENABLED_current') is False, '')
rec('cs_ledger_rows_zero', cs.get('ledger_rows') == 0, '')
rec('cs_gift_spend_disabled', cs.get('gift_spend_disabled') is True, '')

gate = p.get('go_gate_required') or []
rec('gate_min_10', len(gate) >= 10, f'got {len(gate)}')
final_user_gate = next((g for g in gate if g.get('id') == 'final_user_runtime_approval_present'), None)
rec('final_user_gate_required', final_user_gate is not None and final_user_gate.get('required') is True, '')
rec('final_user_gate_status_fail', final_user_gate is not None and final_user_gate.get('status_today') == 'FAIL', '')

rec('flip_template_present', isinstance(p.get('runtime_flip_command_template_DO_NOT_EXECUTE'), dict), '')
rec('rollback_template_present', isinstance(p.get('runtime_rollback_command_template'), dict), '')
rec('monitoring_min_5', len(p.get('monitoring_checklist') or []) >= 5, '')
rec('staged_rollout_5', len(p.get('staged_rollout_plan') or []) == 5, '')

sf = p.get('safety_flags') or {}
rec('sf_runtime_off', sf.get('runtime_attached') is False, '')
rec('sf_db_write_off', sf.get('db_write') is False, '')
rec('sf_flag_off', sf.get('feature_flag_currently_enabled') is False, '')
rec('sf_af2n_blocked', sf.get('AF2N_allowed_today') is False, '')
rec('sf_af2n_not_executed', sf.get('af2n_executed_in_this_task') is False, '')

# Live invariants: AF2-N must NOT be active
rec('env_runtime_flag_not_set',
    os.environ.get('AFFINITY_GIFT_RUNTIME_ENABLED', '') == '', f'got {os.environ.get("AFFINITY_GIFT_RUNTIME_ENABLED")!r}')

def _post(p_, b):
    req = Request(API+p_, data=json.dumps(b).encode(), method='POST', headers={'Content-Type':'application/json'})
    try:
        with urlopen(req, timeout=6) as r: return r.status
    except HTTPError as e: return e.code
    except URLError: return -1
rec('live_gift_spend_423', _post('/affinity/gift-spend', {}) == 423, '')
rec('live_gift_spend_borea_404', _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'abcd1234'}) == 404, '')

print('='*70); print('AF2-N GO/NO-GO Preflight Package — Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
