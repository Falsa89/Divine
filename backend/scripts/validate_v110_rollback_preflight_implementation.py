#!/usr/bin/env python3
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, "backend/scripts/rollback_v110_psp_migration_gated.py")
P = os.path.join(R, "data/design/v110_psp_apply_preflight/v110_rollback_preflight_status_v1.json")
assert os.path.isfile(S), "rollback script missing"
src = open(S).read()
for flag in ("V110_PSP_ROLLBACK", "V110_BACKUP_RESTORE_CONFIRMED", "V110_USER_EXPLICIT_ROLLBACK_APPROVAL", "V110_PRODUCTION_DB_EXPLICIT_APPROVAL"):
    assert flag in src, f"rollback script missing flag {flag}"
for token in ("--dry-run", "--plan-only", "--execute", "--from-backup", "restore_from_mongodump", "migration_source", "audit_log"):
    assert token in src, f"rollback script missing impl token {token}"
assert os.path.isfile(P), "rollback status JSON missing"
d = json.load(open(P))
assert d.get("rollback_executed") is False
assert d.get("db_writes") == 0
assert d.get("implementation_real") is True
assert d.get("status") in ("ROLLBACK_SKIPPED_GATED", "ROLLBACK_REFUSED_BY_V110_APPLY_PREFLIGHT_PACK", "PLAN_BUILT_ONLY_NO_WRITE", "DRY_RUN_NO_WRITE", "REFUSED_EXECUTE_FLAG_REQUIRED", "ROLLBACK_REFUSED_NO_BACKUPS_AVAILABLE", "ROLLBACK_REFUSED_PRODUCTION_WITHOUT_EXPLICIT_APPROVAL")
for k in ("db_write", "rollback_executed", "fake_PASS"):
    assert d.get("safety_flags", {}).get(k) is False
print(f"[v110 ROLLBACK_PREFLIGHT_IMPLEMENTATION] OK status={d['status']} implementation_real=true rollback_executed=false")
