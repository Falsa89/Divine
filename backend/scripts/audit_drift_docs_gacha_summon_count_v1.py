#!/usr/bin/env python3
"""
BLOCK_B audit validator (MEGA_COMBO_SLC_ACCELERATION_V1).

Read-only check: verifica che il marker di housekeeping drift docs gacha/summon
sia presente e che la regola canonical sia documentata. NON esegue query DB,
NON corregge nessun drift doc.

Il conteggio effettivo in DB sara' gestito in un futuro Batch-3 dedicato.

Exit codes:
  0 -> PASS
  1 -> FAIL
"""
import json
import sys
from pathlib import Path

MARKER = Path("/app/data/design/system_safety/gacha_summon_drift_docs_housekeeping_v1.json")
REPORT = Path("/app/docs/divine/115B_GACHA_SUMMON_DRIFT_DOCS_HOUSEKEEPING.md")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not MARKER.exists():
        fail(f"missing marker: {MARKER}")
    if not REPORT.exists():
        fail(f"missing report: {REPORT}")

    m = json.loads(MARKER.read_text(encoding="utf-8"))

    if m.get("verdict") != "BLOCK_B_DRIFT_DOCS_HOUSEKEEPING_READY":
        fail(f"unexpected verdict: {m.get('verdict')}")
    if m.get("runtime_patch_applied") is not False:
        fail("runtime_patch_applied must be false")
    if m.get("db_writes_executed") != 0:
        fail("db_writes_executed must be 0")

    summary = m.get("drift_docs_summary", {})
    if summary.get("total_known_drift_docs") != 7:
        fail(f"expected 7 known drift docs, got {summary.get('total_known_drift_docs')}")
    if summary.get("non_blocking") is not True:
        fail("drift docs must be marked non_blocking")

    rule = m.get("housekeeping_canonical_rule", {})
    if rule.get("rule_id") != "DRIFT_DOCS_GACHA_SUMMON_KNOWN_NONBLOCKING_V1":
        fail("canonical rule id missing or wrong")
    if rule.get("max_allowed_drift_count") != 7:
        fail("max_allowed_drift_count baseline must be 7")

    origin = m.get("origin_routes", [])
    if len(origin) < 2:
        fail("expected at least 2 origin routes (gacha/pull + gacha/pull10)")

    print("[PASS] BLOCK_B drift docs housekeeping artifact integrity OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
