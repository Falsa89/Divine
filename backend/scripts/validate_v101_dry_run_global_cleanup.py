#!/usr/bin/env python3
"""v101 — Dry-run global cleanup validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT,'data','design','legacy_cleanup','v101_dry_run_global_cleanup_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
with open(p,'r',encoding='utf-8') as f: d = json.load(f)
if not d.get('dry_run_executed', False): print('FAIL \u2014 dry_run_executed not true'); sys.exit(1)
for k in ('accounts_affected','heroes_removed_quarantined_converted','items_removed_quarantined_converted','bot_records_affected','encounter_records_affected','frontend_backend_mock_references_affected','risk_level','rollback_info','apply_blockers'):
    if k not in d: print(f'FAIL \u2014 {k} missing'); sys.exit(1)
if d.get('risk_level') not in ('LOW','MEDIUM','HIGH'): print('FAIL \u2014 risk_level invalid'); sys.exit(1)
if len(d.get('apply_blockers', [])) < 2: print('FAIL \u2014 apply_blockers < 2'); sys.exit(1)
script = os.path.join(ROOT, d.get('dry_run_script',''))
if not os.path.isfile(script): print(f'FAIL \u2014 dry_run_script missing: {script}'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('blind_destructive_reset','delete_without_backup','random_opponent_generation','premium_currency_grant','fake_PASS'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} not false'); sys.exit(1)
print(f"PASS \u2014 v101 dry-run global cleanup (risk={d['risk_level']})")
sys.exit(0)
