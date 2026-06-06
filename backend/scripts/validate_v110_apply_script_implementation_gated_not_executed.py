#!/usr/bin/env python3
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, "backend/scripts/apply_v110_psp_migration_gated.py")
P = os.path.join(R, "data/design/v110_psp_apply_preflight/v110_apply_script_implementation_status_v1.json")
assert os.path.isfile(S), "apply script missing"
src = open(S).read()
for flag in ("V110_PSP_APPLY", "V110_BACKUP_CONFIRMED", "V110_STAGING_DB_CONFIRMED", "V110_USER_EXPLICIT_DB_WRITE_APPROVAL", "V110_ROLLBACK_PLAN_CONFIRMED", "V110_PRODUCTION_DB_EXPLICIT_APPROVAL"):
    assert flag in src, f"apply script missing flag {flag}"
for token in ("--dry-run", "--plan-only", "--execute", "--target-server-id", "--limit", "_build_plan", "backup_marker_check", "contract_present", "rollback_script_present"):
    assert token in src, f"apply script missing impl token {token}"
assert os.path.isfile(P), "apply status JSON missing"
d = json.load(open(P))
assert d.get("apply_executed") is False
assert d.get("db_writes") == 0
assert d.get("implementation_real") is True
assert d.get("status") in ("APPLY_SKIPPED_GATED", "APPLY_REFUSED_BY_V110_APPLY_PREFLIGHT_PACK", "PLAN_BUILT_ONLY_NO_WRITE", "DRY_RUN_NO_WRITE", "REFUSED_EXECUTE_FLAG_REQUIRED", "APPLY_REFUSED_NO_BACKUP", "APPLY_REFUSED_NO_ROLLBACK_SCRIPT", "APPLY_REFUSED_NO_CONTRACT", "APPLY_REFUSED_PRODUCTION_WITHOUT_EXPLICIT_APPROVAL")
rf = set(d.get("required_flags", []))
assert {"V110_PSP_APPLY", "V110_BACKUP_CONFIRMED", "V110_STAGING_DB_CONFIRMED", "V110_USER_EXPLICIT_DB_WRITE_APPROVAL", "V110_ROLLBACK_PLAN_CONFIRMED"}.issubset(rf)
for k in ("db_write", "destructive_migration", "apply_executed", "premium_grant", "currency_duplication", "fake_PASS", "release_readiness_claimed"):
    assert d.get("safety_flags", {}).get(k) is False
print(f"[v110 APPLY_SCRIPT_IMPLEMENTATION_GATED_NOT_EXECUTED] OK status={d['status']} implementation_real=true apply_executed=false")
