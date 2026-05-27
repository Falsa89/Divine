#!/usr/bin/env python3
"""
PROJECT_ARTIFACT_INVENTORY_GATED_IMPORT — safe-default migration runner.

DEFAULT MODE: dry-run / no-op / read-only.
LIVE MODE: requires BOTH explicit env markers + explicit CLI flag.

This script is NEVER executed from server startup, supervisord, or cron.
It must be invoked manually from a shell.

Usage:
    python3 backend/scripts/artifact_inventory_gated_import_apply.py
        --dry-run                          (default; no DB op)

    python3 backend/scripts/artifact_inventory_gated_import_apply.py
        --apply --i-understand-this-will-write
        # Requires env:
        #   PROJECT_ARTIFACT_INVENTORY_LIVE_APPROVAL=true
        #   ARTIFACT_INVENTORY_RUNTIME_ENABLED=true_explicit

    python3 backend/scripts/artifact_inventory_gated_import_apply.py
        --rollback --i-understand-this-will-write
        # Same env markers required; emits compensating ledger entries only.

Exit codes:
    0  -> dry-run completed OK, or apply/rollback completed OK
    2  -> apply/rollback requested but live markers absent -> REFUSED, no DB op
    3  -> apply/rollback requested but --i-understand-this-will-write missing
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path("/app")
BIBLE_PATH = ROOT / "data/design/artifacts/artifact_bible_launch_draft_v1.json"
PREVIEW_PATH = ROOT / "data/design/artifacts/preview/artifact_preview_dataset_v1.json"
MAPPING_PATH = ROOT / "data/design/artifacts/gated_import/artifact_import_source_target_mapping_v1.json"

TARGET_COLLECTIONS = [
    "artifact_catalog_snapshot",
    "user_artifact_inventory",
    "artifact_inventory_ledger",
    "artifact_collection_state",
    "artifact_idempotency_registry",
]

LIVE_MARKER_APPROVAL_KEY = "PROJECT_ARTIFACT_INVENTORY_LIVE_APPROVAL"
LIVE_MARKER_RUNTIME_KEY = "ARTIFACT_INVENTORY_RUNTIME_ENABLED"
LIVE_MARKER_APPROVAL_VAL = "true"
LIVE_MARKER_RUNTIME_VAL = "true_explicit"

# Invarianti che il runner verifica prima di qualsiasi azione.
EXPECTED_INVARIANTS = {
    "backend/battle_engine.py": "151ca35ad3bc35f0a6209cb3744ed440",
    "backend/.env": "ff60bbb79efa329b71aa8ed351ea89b3",
}


def md5_of(rel_path: str) -> str:
    return hashlib.md5((ROOT / rel_path).read_bytes()).hexdigest()


def check_invariants() -> dict:
    drift = {}
    for rel, expected in EXPECTED_INVARIANTS.items():
        actual = md5_of(rel)
        drift[rel] = {"expected": expected, "actual": actual, "ok": actual == expected}
    return drift


def check_live_markers() -> dict:
    """Read live markers from process env. Optionally also from backend/.env
    file as backup, but ONLY env (live process) is considered authoritative."""
    approval = os.environ.get(LIVE_MARKER_APPROVAL_KEY, "")
    runtime = os.environ.get(LIVE_MARKER_RUNTIME_KEY, "")
    return {
        LIVE_MARKER_APPROVAL_KEY: approval,
        LIVE_MARKER_RUNTIME_KEY: runtime,
        "approval_ok": approval == LIVE_MARKER_APPROVAL_VAL,
        "runtime_ok": runtime == LIVE_MARKER_RUNTIME_VAL,
        "both_ok": (approval == LIVE_MARKER_APPROVAL_VAL
                    and runtime == LIVE_MARKER_RUNTIME_VAL),
    }


def load_bible_rows():
    with BIBLE_PATH.open("r", encoding="utf-8") as f:
        bible = json.load(f)
    rows = bible.get("artifacts", [])
    return bible.get("bible_version"), rows


def build_catalog_snapshot_docs(bible_version, bible_rows):
    docs = []
    for r in bible_rows:
        row_md5 = hashlib.md5(
            json.dumps(r, sort_keys=True).encode("utf-8")
        ).hexdigest()
        docs.append({
            "artifact_id": r["artifact_id"],
            "bible_version": bible_version,
            "release_status": r["release_status"],
            "gameplay_status": r["gameplay_status"],
            "category": r["category"],
            "rarity_band": r["rarity_band"],
            "associated_hero_id": r.get("associated_hero_id"),
            "associated_character_status": r.get("associated_character_status", "none"),
            "display_name_it": r["display_name_it"],
            "display_name_en": r["display_name_en"],
            "snapshot_md5": row_md5,
        })
    return docs


def dry_run_report():
    """Print a human-friendly + machine-readable report. NO DB op."""
    inv = check_invariants()
    markers = check_live_markers()
    bible_version, bible_rows = load_bible_rows()
    snapshot_docs = build_catalog_snapshot_docs(bible_version, bible_rows)

    report = {
        "mode": "dry_run",
        "live_markers": markers,
        "verdict": (
            "READY_TO_APPLY_LIVE_MARKERS_PRESENT" if markers["both_ok"]
            else "READY_NOT_APPLIED_MISSING_LIVE_MARKERS"
        ),
        "invariants": inv,
        "target_collections_status": {
            c: "would_be_created_or_noop_if_exists" for c in TARGET_COLLECTIONS
        },
        "catalog_snapshot_rows_that_would_be_inserted": len(snapshot_docs),
        "bible_version_pinned": bible_version,
        "canary_grants_planned": 0,
        "db_writes_performed": 0,
        "db_collections_created": 0,
        "indexes_created": 0,
        "grants_emitted": 0,
        "revokes_emitted": 0,
    }
    print(json.dumps(report, indent=2))
    return report


def refuse_apply(reason: str, exit_code: int):
    """Print a refusal envelope and exit without ANY DB op."""
    print(json.dumps({
        "mode": "refused",
        "verdict": "PROJECT_ARTIFACT_INVENTORY_GATED_IMPORT_BLOCKED_UNAUTHORIZED_APPLY_ATTEMPT",
        "reason": reason,
        "db_writes_performed": 0,
        "db_collections_created": 0,
    }, indent=2))
    sys.exit(exit_code)


def apply_live(rollback: bool = False):
    """
    Placeholder live path. Even when both live markers are present, this
    function intentionally does NOT touch MongoDB in this pack: it returns a
    verdict requesting an explicit follow-up pack to perform the live write.
    The actual write would happen only in a future Stage 7 pack with double
    signoff. This preserves zero-mutation safety even if someone accidentally
    sets the env markers locally.
    """
    inv = check_invariants()
    drift = {k: v for k, v in inv.items() if not v["ok"]}
    if drift:
        print(json.dumps({
            "mode": "refused",
            "verdict": "PROJECT_ARTIFACT_INVENTORY_GATED_IMPORT_BLOCKED_INVARIANT_DRIFT",
            "drift": drift,
            "db_writes_performed": 0,
        }, indent=2))
        sys.exit(4)
    print(json.dumps({
        "mode": "apply" if not rollback else "rollback",
        "verdict": "PROJECT_ARTIFACT_INVENTORY_GATED_IMPORT_LIVE_APPROVAL_RECEIVED_DEFERRED_TO_NEXT_PACK",
        "reason": "Live markers detected, but live writes require Stage 7 PROJECT_ARTIFACT_INVENTORY_LIVE_ACTIVATION_SIGNOFF_PACK. No DB write performed in this Stage 6 runner.",
        "db_writes_performed": 0,
        "db_collections_created": 0,
        "grants_emitted": 0,
        "revokes_emitted": 0,
    }, indent=2))
    sys.exit(0)


def main():
    ap = argparse.ArgumentParser(description="Artifact Inventory gated-import runner (safe by default).")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", default=True, help="default: dry-run, no DB op")
    g.add_argument("--apply", action="store_true", help="attempt live apply (requires markers + flag)")
    g.add_argument("--rollback", action="store_true", help="attempt rollback via compensating ledger entries")
    ap.add_argument(
        "--i-understand-this-will-write",
        action="store_true",
        help="explicit human ack required when --apply or --rollback is set",
    )
    args = ap.parse_args()

    if args.apply or args.rollback:
        markers = check_live_markers()
        if not markers["both_ok"]:
            refuse_apply(
                reason=(
                    f"Live markers missing: "
                    f"{LIVE_MARKER_APPROVAL_KEY}={markers[LIVE_MARKER_APPROVAL_KEY]!r}, "
                    f"{LIVE_MARKER_RUNTIME_KEY}={markers[LIVE_MARKER_RUNTIME_KEY]!r}. "
                    "Refusing all DB operations."
                ),
                exit_code=2,
            )
        if not args.i_understand_this_will_write:
            refuse_apply(
                reason="--apply/--rollback requested but --i-understand-this-will-write flag is missing.",
                exit_code=3,
            )
        apply_live(rollback=args.rollback)
        return

    # Default: dry-run
    dry_run_report()


if __name__ == "__main__":
    main()
