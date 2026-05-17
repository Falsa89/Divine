#!/usr/bin/env python3
"""SAFETY-ROLLUP-G — Validator for rollup v7 (post AF2-N canary)."""
from __future__ import annotations
import json, sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

R = Path('/app/data/design/system_safety/collection_affinity_runtime_activation_readiness_rollup_v7.json')
API = 'http://127.0.0.1:8001/api'
failures=[]; checks=[]
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('rollup_present', R.exists(), str(R))
r = json.loads(R.read_text())
rec('id', r.get('report_id') == 'collection_affinity_runtime_activation_readiness_rollup_v7', '')
rec('task', r.get('task_origin') == 'SAFETY-ROLLUP-G', '')
rec('supersedes_v6', r.get('supersedes') == 'collection_affinity_runtime_activation_readiness_rollup_v6', '')
rec('design_only_false', r.get('design_only') is False, '')
rec('runtime_attached_canary_only', r.get('runtime_attached_canary_only') is True, '')
rec('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
for k in ('product_signoff','engineering_signoff','qa_signoff','economy_balance_signoff','rollback_owner_signoff'):
    rec(f'{k}_true', r.get(k) is True, '')
rec('all_5_signoffs_true', r.get('all_5_operator_signoffs_true') is True, '')
rec('final_user_approval_present', r.get('final_user_runtime_approval_present') is True, '')
rec('af2n_executed', r.get('AF2N_executed') is True, '')
rec('af2n_mode_canary', r.get('AF2N_mode') == 'controlled_canary_allowlist', '')
rec('af2n_canary_pass', r.get('AF2N_canary_status') == 'PASS', '')
rec('broad_rollout_off', r.get('AF2N_broad_rollout_authorized') is False, '')
rec('decision_canary_only', r.get('go_no_go_decision') == 'CANARY_ONLY_NO_BROAD_ROLLOUT', '')
rec('state_canary_active', r.get('overall_runtime_activation_state') == 'canary_active_no_broad_rollout', '')
rec('feature_flag_on', r.get('feature_flag_currently_enabled') is True, '')
rec('ledger_within_cap', r.get('ledger_row_count_within_cap') is True, '')
rec('rollback_script_ready', r.get('af2n_canary_rollback_script_ready') is True, '')
rec('rollback_executed_false', r.get('rollback_executed') is False, '')

subs = r.get('subsystems') or {}
rec('sub_axis_go', (subs.get('axis_layer') or {}).get('status') == 'GO', '')
rec('sub_ops_go', (subs.get('ops_layer') or {}).get('status') == 'GO', '')
rec('sub_idem_verified', (subs.get('idempotency_contract') or {}).get('status') == 'LIVE_VERIFIED', '')
rec('sub_signoff_all_true', (subs.get('operator_signoff_v4') or {}).get('status') == 'ALL_TRUE', '')
rec('sub_final_user', (subs.get('final_user_approval') or {}).get('status') == 'PRESENT', '')
rec('sub_af2n_active', (subs.get('af2n_canary') or {}).get('status') == 'ACTIVE_PASS', '')
rec('sub_af2n_rollback_ready', (subs.get('af2n_rollback') or {}).get('status') == 'READY', '')
rec('sub_battle_no_go', (subs.get('battle_runtime') or {}).get('status') == 'NO_GO', '')
rec('sub_borea_go', (subs.get('borea_layer') or {}).get('status') == 'GO', '')

trig = r.get('abort_triggers_status') or []
rec('triggers_min_5', len(trig) >= 5, '')
rec('no_trigger_fired', all(t.get('triggered') is False for t in trig), '')

st = r.get('runtime_status_at_completion') or {}
rec('rs_heroes_100', st.get('api_heroes_count') == 100, '')
rec('rs_borea_invisible', st.get('borea_visible_in_heroes') is False, '')
rec('rs_spend_default_423', st.get('gift_spend_default_status') == 423, '')
rec('rs_spend_borea_404', st.get('gift_spend_borea_status') == 404, '')
rec('rs_spend_canary_200', st.get('gift_spend_canary_status') == 200, '')
rec('rs_no_inventory_mut', st.get('ledger_inventory_mutation_count') == 0, '')
rec('rs_no_points_mut', st.get('ledger_affinity_points_mutation_count') == 0, '')
rec('rs_no_buffs', st.get('ledger_buffs_activation_count') == 0, '')
rec('rs_no_battle_wire', st.get('ledger_battle_wiring_count') == 0, '')
rec('rs_no_borea_hero', st.get('ledger_borea_hero_count') == 0, '')

rec('invariants_min_10', len(r.get('invariants_currently_holding') or []) >= 10, '')
rec('no_go_reasons_min_3', len(r.get('runtime_no_go_reasons') or []) >= 3, '')

sf = r.get('safety_flags') or {}
rec('sf_canary_only', sf.get('runtime_attached_canary_only') is True, '')
rec('sf_broad_rollout_off', sf.get('broad_rollout_authorized') is False, '')
rec('sf_battle_off', sf.get('battle_runtime_attached') is False, '')
rec('sf_combat_off', sf.get('applied_to_combat') is False, '')
rec('sf_inventory_off', sf.get('inventory_mutation_enabled') is False, '')
rec('sf_points_off', sf.get('affinity_points_mutation_enabled') is False, '')
rec('sf_buffs_off', sf.get('buffs_enabled') is False, '')
rec('sf_borea_blocked', sf.get('hidden_aliases_blocked') == ['borea','greek_borea','primordial_gaia'], '')

# Live verification
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
rec('live_non_allowlist_423', _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'greek_zeus','quantity':1,'idempotency_key':'randomidem9999','user_id':'random_user_xxx'}) == 423, '')
rec('live_borea_404', _post('/affinity/gift-spend', {'gift_id':'x','hero_id':'borea','quantity':1,'idempotency_key':'abcd1234efgh','user_id':'user_canary_001'}) == 404, '')

print('='*70); print('SAFETY-ROLLUP-G — v7 Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
