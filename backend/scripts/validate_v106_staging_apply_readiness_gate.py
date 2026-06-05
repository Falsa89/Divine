#!/usr/bin/env python3
"""v106 — Staging apply readiness gate validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'server_scope', 'v106_staging_apply_readiness_gate_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
if d.get('gate_status') not in ('NOT_PASSED_APPLY_GATED_NOT_EXECUTED','PASSED_READY_FOR_STAGING_APPLY'): print(f'FAIL \u2014 invalid gate_status {d.get("gate_status")}'); sys.exit(1)
crit = d.get('criteria') or []
if len(crit) < 10: print(f'FAIL \u2014 criteria < 10 (got {len(crit)})'); sys.exit(1)
required_criteria = {'backup_present','dry_run_pass','rollback_script_present','db_target_staging_only','no_production_env_targeted','user_explicit_approval','monitoring_plan','post_apply_smoke_plan','abort_conditions_documented'}
present = {c.get('criterion') for c in crit}
missing = required_criteria - present
if missing: print(f'FAIL \u2014 criteria missing {missing}'); sys.exit(1)
if len(d.get('abort_conditions') or []) < 5: print('FAIL \u2014 abort_conditions < 5'); sys.exit(1)
if len(d.get('monitoring_plan') or []) < 3: print('FAIL \u2014 monitoring_plan < 3'); sys.exit(1)
if len(d.get('post_apply_smoke_plan') or []) < 2: print('FAIL \u2014 post_apply_smoke_plan < 2'); sys.exit(1)
saf = d.get('safety') or {}
if not saf.get('production_target_forbidden', False): print('FAIL \u2014 safety.production_target_forbidden must be true'); sys.exit(1)
for k in ('fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
print(f"PASS \u2014 v106 staging apply readiness gate ({d.get('gate_status')}, {len(crit)} criteria)")
sys.exit(0)
