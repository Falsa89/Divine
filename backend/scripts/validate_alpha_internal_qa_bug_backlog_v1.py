#!/usr/bin/env python3
# Validator: PROJECT-ALPHA-INTERNAL-QA-BUG-BACKLOG
# Pack: MEGA_RELEASE_ACCELERATION_21_v72
import json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FILES = {
    "backlog": "data/design/qa/alpha_internal_qa_bug_backlog_v1.json",
    "triage": "data/design/qa/alpha_internal_qa_bug_triage_matrix_v1.json",
    "log": "data/design/qa/alpha_internal_qa_no_fix_or_fix_decision_log_v1.json",
    "marker": "data/design/qa/alpha_internal_qa_bug_backlog_marker_v1.json",
}

FINDING_REQUIRED_KEYS = {
    "id", "severity", "route", "file", "evidence_ref",
    "expected", "actual", "recommended_action",
    "safe_to_fix_now", "reason_if_deferred",
}


def main() -> int:
    errors = []
    for k, rel in FILES.items():
        if not os.path.isfile(os.path.join(ROOT, rel)):
            errors.append(f"MISSING_FILE: {k}={rel}")
    if errors:
        for e in errors: print(e)
        return 1

    backlog = json.load(open(os.path.join(ROOT, FILES["backlog"]), "r", encoding="utf-8"))
    findings = backlog.get("findings") or []
    if backlog.get("open_findings_count") != len(findings):
        errors.append("BACKLOG_COUNT_MISMATCH")
    if backlog.get("p0_open") != 0:
        errors.append("BACKLOG_P0_OPEN")
    if backlog.get("p1_open") != 0:
        errors.append("BACKLOG_P1_OPEN")
    if backlog.get("db_writes") != 0:
        errors.append("BACKLOG_BAD_DB_WRITES")
    for f in findings:
        missing = FINDING_REQUIRED_KEYS - set(f.keys())
        if missing:
            errors.append(f"FINDING_MISSING_KEYS: {f.get('id')}: {sorted(missing)}")
        if f.get("severity") not in {"P0", "P1", "P2", "P3"}:
            errors.append(f"FINDING_BAD_SEVERITY: {f.get('id')}")

    triage = json.load(open(os.path.join(ROOT, FILES["triage"]), "r", encoding="utf-8"))
    tbs = triage.get("triage_by_severity") or {}
    for sev in ("P0", "P1", "P2", "P3"):
        if sev not in tbs:
            errors.append(f"TRIAGE_MISSING_SEVERITY: {sev}")
    if tbs.get("P0", {}).get("count") != 0:
        errors.append("TRIAGE_P0_NONZERO")
    if tbs.get("P1", {}).get("count") != 0:
        errors.append("TRIAGE_P1_NONZERO")

    log = json.load(open(os.path.join(ROOT, FILES["log"]), "r", encoding="utf-8"))
    if log.get("all_fixes_preview_only") is not True:
        errors.append("LOG_NOT_PREVIEW_ONLY")
    if log.get("db_writes") != 0:
        errors.append("LOG_BAD_DB_WRITES")
    if log.get("applied_fixes_count") + log.get("deferred_fixes_count") != len(findings):
        errors.append("LOG_COUNT_MISMATCH_VS_BACKLOG")

    marker = json.load(open(os.path.join(ROOT, FILES["marker"]), "r", encoding="utf-8"))
    if marker.get("p0_open") != 0:
        errors.append("MARKER_P0_OPEN")
    if marker.get("p1_open") != 0:
        errors.append("MARKER_P1_OPEN")

    if errors:
        for e in errors: print(e)
        return 1
    print("PROJECT-ALPHA-INTERNAL-QA-BUG-BACKLOG: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
