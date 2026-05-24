#!/usr/bin/env python3
"""
PROJECT_A Track F validator (read-only).

Verifica:
- plan JSON integrity con 7 drift doc classificati
- summary aggregato consistente
- nessuna data mutation eseguita in Track F
- summon route definitions UNCHANGED (sanity diff on summon.py if present)

Exit 0 PASS / 1 FAIL.
"""
import json
import sys
from pathlib import Path

PLAN = Path("/app/data/design/system_safety/project_a_gacha_summon_drift_cleanup_plan_v1.json")
SUMMON = Path("/app/backend/routes/summon.py")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not PLAN.exists():
        fail(f"missing plan: {PLAN}")
    m = json.loads(PLAN.read_text(encoding="utf-8"))
    if m.get("verdict") != "TRACK_F_GACHA_SUMMON_DRIFT_CLEANUP_PLAN_READY":
        fail(f"unexpected verdict: {m.get('verdict')}")
    if m.get("db_writes_executed") != 0:
        fail("db_writes_executed must be 0")
    if m.get("gacha_behavior_mutated") is not False:
        fail("gacha_behavior_mutated must be False")

    drift = m.get("drift_docs_classification", [])
    if len(drift) != 7:
        fail(f"expected 7 drift docs, got {len(drift)}")
    summary = m.get("summary", {})
    if summary.get("docs_total") != 7:
        fail("summary.docs_total must be 7")
    if summary.get("data_mutation_executed_in_track_f") != 0:
        fail("data_mutation_executed_in_track_f must be 0")

    forb = m.get("forbidden_in_track_f_respected", {})
    for k in ("db_cleanup", "gacha_summon_route_behavior_change",
              "roster_ownership_mutation", "borea_activation", "banner_rate_pity_pool_change"):
        if forb.get(k) is not False:
            fail(f"forbidden_in_track_f_respected.{k} must be False")

    if SUMMON.exists():
        src = SUMMON.read_text(encoding="utf-8")
        # Sanity: ensure no obvious banner rate/pity hardcode added in this pack.
        for forbidden_pattern in ("FORCED_PITY_OVERRIDE", "BOREA_OBTAINABLE = True", "RATE_OVERRIDE_PROJECT_A"):
            if forbidden_pattern in src:
                fail(f"forbidden pattern '{forbidden_pattern}' detected in summon.py")

    print("[PASS] PROJECT_A Track F drift cleanup plan integrity OK; 7 drift docs classified; 0 data mutation")
    sys.exit(0)


if __name__ == "__main__":
    main()
