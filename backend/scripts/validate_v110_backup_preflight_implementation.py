#!/usr/bin/env python3
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, "backend/scripts/backup_v110_psp_migration_preflight.py")
P = os.path.join(R, "data/design/v110_psp_apply_preflight/v110_backup_preflight_status_v1.json")
assert os.path.isfile(S), "backup script missing"
src = open(S).read()
for flag in ("V110_BACKUP_EXECUTE", "V110_USER_EXPLICIT_BACKUP_APPROVAL", "V110_PRODUCTION_DB_EXPLICIT_APPROVAL"):
    assert flag in src, f"backup script missing flag {flag}"
for token in ("--dry-run", "--plan-only", "--execute", "mongodump", "disk_usage", "manifest", "masking_rules"):
    assert token in src, f"backup script missing impl token {token}"
assert os.path.isfile(P), "backup status JSON missing"
d = json.load(open(P))
assert d.get("export_executed") is False
assert d.get("db_writes") == 0
assert d.get("implementation_real") is True
assert d.get("status") in ("BACKUP_PLAN_ONLY", "BACKUP_REFUSED_BY_V110_APPLY_PREFLIGHT_PACK", "PLAN_BUILT_ONLY", "DRY_RUN_NO_WRITE", "REFUSED_EXECUTE_FLAG_REQUIRED", "BACKUP_REFUSED_NO_MANIFEST", "BACKUP_REFUSED_MONGODUMP_NOT_FOUND", "BACKUP_REFUSED_PRODUCTION_WITHOUT_EXPLICIT_APPROVAL")
assert d.get("manifest_present") is True
for k in ("db_write", "export_executed", "fake_PASS"):
    assert d.get("safety_flags", {}).get(k) is False
print(f"[v110 BACKUP_PREFLIGHT_IMPLEMENTATION] OK status={d['status']} implementation_real=true export_executed=false")
