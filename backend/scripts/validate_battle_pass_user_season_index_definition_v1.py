#!/usr/bin/env python3
"""
V8 BLOCK_B validator (read-only).

Verifica:
- plan JSON integrity + verdict
- index canonical definition (name, fields, unique)
- coerenza con signoff V6 BLOCK_A (BP_D1/D3/D4)
- dry-run script presente, gated, non auto-run
- nessun DB write / create_index call

Exit 0 PASS / 1 FAIL.
"""
import json
import sys
from pathlib import Path

PLAN = Path("/app/data/design/server_lifecycle/battle_pass_user_season_index_definition_v1.json")
DRY_RUN_SCRIPT = Path("/app/backend/scripts/prepare_battle_pass_user_season_index_dry_run_v1.py")
V6_SIGNOFF = Path("/app/data/design/server_lifecycle/battle_pass_bp_d1_d3_d4_signoff_record_v1.json")
V4_MARKER = Path("/app/data/design/system_safety/v4_battle_pass_technical_hardening_marker.json")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not PLAN.exists():
        fail(f"missing plan: {PLAN}")
    m = json.loads(PLAN.read_text(encoding="utf-8"))

    if m.get("verdict") != "BLOCK_B_BATTLE_PASS_INDEX_USER_SEASON_READY":
        fail(f"unexpected verdict: {m.get('verdict')}")
    if m.get("runtime_patch_applied") is not False:
        fail("runtime_patch_applied must be False")
    if m.get("db_index_created") is not False:
        fail("db_index_created must be False")
    if m.get("db_writes_executed") != 0:
        fail("db_writes_executed must be 0")

    idx = m.get("index_canonical_definition", {})
    if idx.get("name") != "idx_battle_pass_user_season":
        fail(f"unexpected index name: {idx.get('name')}")
    if idx.get("collection") != "battle_pass":
        fail(f"unexpected collection: {idx.get('collection')}")
    if idx.get("unique") is not True:
        fail("index must be unique")
    fields = [f.get("field") for f in idx.get("fields", [])]
    if fields != ["user_id", "season"]:
        fail(f"index fields must be ['user_id', 'season'], got {fields}")
    if not idx.get("deferred_to_pack"):
        fail("index must declare deferred_to_pack")

    if not DRY_RUN_SCRIPT.exists():
        fail(f"dry-run script missing: {DRY_RUN_SCRIPT}")
    src = DRY_RUN_SCRIPT.read_text(encoding="utf-8")
    if "V8_BLOCK_B_APPLY" not in src:
        fail("dry-run script missing gating env V8_BLOCK_B_APPLY")
    if "APPLY_REFUSED_NO_PACK_AUTHORIZATION" not in src:
        fail("dry-run script missing apply guard 'APPLY_REFUSED_NO_PACK_AUTHORIZATION'")
    if "NOT EXECUTED" not in src:
        fail("dry-run script missing explicit 'NOT EXECUTED' contract in output")

    # Upstream cross-references
    if not V6_SIGNOFF.exists():
        fail(f"V6 BLOCK_A signoff record missing: {V6_SIGNOFF}")
    if not V4_MARKER.exists():
        fail(f"V4 BLOCK_A marker missing (needed for R4 history): {V4_MARKER}")

    # Coherence with signoff
    coh = m.get("coherence_with_signoff", {})
    for k in ("BP_D1_ACCOUNT_WIDE", "BP_D3_ACCOUNT_WIDE_ONCE", "BP_D4_GLOBAL_SEASON",
              "v7_block_b_setoninsert_doc_shape"):
        if not coh.get(k) or "compatible" not in str(coh.get(k)).lower():
            fail(f"coherence_with_signoff.{k} must declare 'compatible'")

    # Forbidden scope
    forb = m.get("forbidden_in_block_b_respected", {})
    for k in ("live_db_index_creation", "db_migration_backfill", "battle_pass_behavior_change",
              "reward_premium_change", "pricing_currency_change", "runtime_route_mutation"):
        if forb.get(k) is not False:
            fail(f"forbidden_in_block_b_respected.{k} must be False")

    print("[PASS] V8 BLOCK_B index definition canonical OK; dry-run gated; signoff coherence verified")
    sys.exit(0)


if __name__ == "__main__":
    main()
