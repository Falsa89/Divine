#!/usr/bin/env python3
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(R, "data/design/v110_psp_migration/v110_apply_status_v1.json")
S = os.path.join(R, "backend/scripts/apply_v110_psp_migration_gated.py")
assert os.path.isfile(S), "apply script missing"
src = open(S).read()
for flag in ("V110_PSP_APPLY", "V110_BACKUP_CONFIRMED", "V110_STAGING_DB_CONFIRMED", "V110_USER_EXPLICIT_DB_WRITE_APPROVAL", "V110_ROLLBACK_PLAN_CONFIRMED"):
    assert flag in src, f"apply script missing flag {flag}"
assert os.path.isfile(P), "apply status JSON missing (run apply_v110_psp_migration_gated.py first)"
d = json.load(open(P))
assert d.get("apply_executed") is False, "APPLY must NOT be executed"
assert d.get("db_writes") == 0
assert d.get("status") in ("APPLY_SKIPPED_GATED", "APPLY_NOT_IMPLEMENTED_IN_V110_PREP_PACK")
rf = set(d.get("required_flags", []))
assert {"V110_PSP_APPLY", "V110_BACKUP_CONFIRMED", "V110_STAGING_DB_CONFIRMED", "V110_USER_EXPLICIT_DB_WRITE_APPROVAL", "V110_ROLLBACK_PLAN_CONFIRMED"}.issubset(rf)
for k in ("db_write", "destructive_migration", "apply_executed", "fake_PASS"):
    assert d.get("safety_flags", {}).get(k) is False, f"apply safety {k}"
print(f"[v110 APPLY_SCRIPT_GATED_NOT_EXECUTED] OK status={d['status']} apply_executed=false db_writes=0")
