#!/usr/bin/env python3
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(R, "data/design/v110_psp_migration/v110_rollback_plan_status_v1.json")
S = os.path.join(R, "backend/scripts/rollback_v110_psp_migration_gated.py")
assert os.path.isfile(S), "rollback script missing"
src = open(S).read()
for flag in ("V110_PSP_ROLLBACK", "V110_BACKUP_RESTORE_CONFIRMED", "V110_USER_EXPLICIT_ROLLBACK_APPROVAL"):
    assert flag in src, f"rollback script missing flag {flag}"
assert os.path.isfile(P), "rollback status JSON missing"
d = json.load(open(P))
assert d.get("rollback_executed") is False, "ROLLBACK must NOT be executed"
assert d.get("db_writes") == 0
assert d.get("status") in ("ROLLBACK_SKIPPED_GATED", "ROLLBACK_NOT_IMPLEMENTED_IN_V110_PREP_PACK")
rf = set(d.get("required_flags", []))
assert {"V110_PSP_ROLLBACK", "V110_BACKUP_RESTORE_CONFIRMED", "V110_USER_EXPLICIT_ROLLBACK_APPROVAL"}.issubset(rf)
for k in ("db_write", "rollback_executed", "fake_PASS"):
    assert d.get("safety_flags", {}).get(k) is False, f"rollback safety {k}"
print(f"[v110 ROLLBACK_SCRIPT_GATED_NOT_EXECUTED] OK status={d['status']} rollback_executed=false db_writes=0")
