#!/usr/bin/env python3
"""AF2-L-K6-LIVE-PREP2 — Result validator."""
from __future__ import annotations
import json, sys
from pathlib import Path

R = Path('/app/data/design/affinity/affinity_gift_spend_k6_live_prep2_result_v1.json')
failures=[]; checks=[]
def rec(n, ok, note=''):
    checks.append((n, ok, note))
    if not ok: failures.append(f'{n}: {note}')

rec('present', R.exists(), str(R))
r = json.loads(R.read_text())
rec('id', r.get('result_id') == 'affinity_gift_spend_k6_live_prep2_result_v1', '')
rec('task', r.get('task_origin') == 'AF2-L-K6-LIVE-PREP2', '')
rec('runtime_canary_only', r.get('runtime_attached_canary_only') is True, '')
rec('db_write_false', r.get('db_write') is False, '')
rec('baseline_v6', r.get('baseline_anchor') == 'hero_skill_kit_catalog_baseline_rm134b_axispatch_v6', '')
rec('5xx_zero', r.get('total_5xx', 99) == 0, '')
rec('unexpected_zero', r.get('unexpected_total', 99) == 0, '')
rec('duplicate_inserted_zero', r.get('duplicate_inserted_total', 99) == 0, '')
rec('ledger_unchanged', r.get('ledger_row_count_unchanged') is True,
    f"before={r.get('ledger_row_count_before')} after={r.get('ledger_row_count_after')}")
rec('rounds_per_label_min_50', r.get('rounds_per_label', 0) >= 50, '')
rec('total_requests_min_500', r.get('total_requests', 0) >= 500, '')

by = r.get('by_label') or {}
for lbl in ('empty', 'no_idem', 'malformed_idem', 'negative_qty', 'huge_qty',
            'borea', 'greek_borea', 'primordial_gaia', 'idempotent_replay'):
    rec(f'label_present:{lbl}', lbl in by, '')
    if lbl in by:
        rec(f'label_no_unexpected:{lbl}', not by[lbl].get('unexpected_codes'), f"got={by[lbl].get('unexpected_codes')}")

reg = r.get('regression_gets') or {}
for ep in ('/affinity/gifts', '/affinity/gift-spend/canary-status', '/heroes',
           '/affinity/gifts/by-element/dark/by-faction/greek',
           '/affinity/gifts/by-element/dark/by-faction/borea'):
    rec(f'reg_ok:{ep}', (reg.get(ep) or {}).get('ok') is True, f"got={reg.get(ep)}")

sf = r.get('safety_flags') or {}
rec('sf_canary_only', sf.get('runtime_attached_canary_only') is True, '')
rec('sf_broad_off', sf.get('broad_rollout_authorized') is False, '')
rec('sf_inventory_off', sf.get('inventory_mutation_enabled') is False, '')
rec('sf_battle_off', sf.get('battle_runtime_attached') is False, '')
rec('sf_combat_off', sf.get('applied_to_combat') is False, '')

print('='*70); print('AF2-L-K6-LIVE-PREP2 — Validator'); print('='*70)
for n, ok, note in checks:
    print(f'  [{ "OK" if ok else "X" }] {n} {("- " + note) if note and not ok else ""}')
print('-'*70); print(f'checks={len(checks)} passed={sum(1 for _,o,_ in checks if o)} failed={len(failures)}')
print('Overall: PASS' if not failures else 'Overall: FAIL')
sys.exit(0 if not failures else 1)
