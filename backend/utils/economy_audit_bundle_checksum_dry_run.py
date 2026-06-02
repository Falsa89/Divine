"""economy_audit_bundle_checksum_dry_run.py

v48 — Track A
Audit Bundle Checksum (DRY-RUN, in-memory only, deterministic).

Computes a deterministic SHA-256 checksum of the consolidated audit bundle
covering economy safety packs v37-v47:
- design markers (data/design/economy_safety/*.json)
- contract designs (data/design/economy_safety/*.json non-marker)
- validators (backend/scripts/validate_*.py related to safety packs)
- routes (backend/routes/*_safety_preview.py)
- utils (backend/utils/economy_*.py)
- docs (docs/divine/2*.md for indexes 254-281)

Strict properties:
- Read-only filesystem access (no writes).
- NO DB writes. NO Redis. NO persistent runtime ledger.
- No live apply. No mutation. No reward grant.
- Returns a deterministic checksum (sort path lexicographic, normalize
  line endings to LF).

Public API:
- build_audit_bundle_checksum() -> dict
- build_config_block()          -> dict
- _test_reset()                 -> None
"""
from __future__ import annotations

import hashlib
import os
from typing import Any, Dict, List

CONTRACT_VERSION = "economy_audit_bundle_checksum_dry_run_v1"
DRY_RUN_ONLY = True
DB_WRITES = 0
PERSISTED = False
LIVE_APPLY_ALLOWED = False
LIVE_ENFORCEMENT_ENABLED = False
PREVIEW_REQUEST_BLOCKED = False

ROOT = "/app"

# Sorted, deterministic, exhaustive list patterns (relative to /app).
_BUNDLE_DIRS = [
    ("data/design/economy_safety", lambda n: n.endswith(".json")),
    ("backend/utils", lambda n: n.startswith("economy_") and n.endswith(".py")),
    ("backend/routes", lambda n: n.endswith("_safety_preview.py")),
    ("backend/scripts", lambda n: n.startswith("validate_") and (
        "economy_safety" in n or "client_idem_key" in n or "observability" in n or
        "material_raid_canary" in n or "replay_conflict" in n or "all_family_canary" in n or
        "telemetry_alerting" in n or "signoff_promotion" in n or "go_no_go" in n or
        "alert_history" in n or "rollback_runbook" in n or "pre_live_audit" in n or
        "audit_bundle_checksum" in n or "final_go_no_go" in n or
        "live_apply_decision_log" in n or "expo_watcher_enospc" in n
    ) and n.endswith(".py")),
    ("docs/divine", lambda n: n.endswith(".md") and any(
        n.startswith(f"{i}_") for i in range(254, 290)
    )),
]


def _collect_files() -> List[str]:
    found: List[str] = []
    for rel_dir, predicate in _BUNDLE_DIRS:
        abs_dir = os.path.join(ROOT, rel_dir)
        if not os.path.isdir(abs_dir):
            continue
        try:
            entries = sorted(os.listdir(abs_dir))
        except Exception:
            continue
        for name in entries:
            if not predicate(name):
                continue
            full = os.path.join(abs_dir, name)
            if not os.path.isfile(full):
                continue
            rel = os.path.relpath(full, ROOT)
            found.append(rel)
    return sorted(found)


def _hash_file(abs_path: str) -> str:
    h = hashlib.sha256()
    try:
        with open(abs_path, "rb") as fh:
            data = fh.read()
        # Normalize CRLF -> LF for determinism
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        h.update(data)
    except Exception:
        return ""
    return h.hexdigest()


def build_audit_bundle_checksum() -> Dict[str, Any]:
    """Deterministic SHA-256 checksum over the consolidated v37-v47 bundle."""
    files = _collect_files()
    per_file: List[Dict[str, Any]] = []
    missing: List[str] = []
    rolling = hashlib.sha256()
    for rel in files:
        full = os.path.join(ROOT, rel)
        if not os.path.exists(full):
            missing.append(rel)
            continue
        fh = _hash_file(full)
        if not fh:
            missing.append(rel)
            continue
        per_file.append({"path": rel, "sha256": fh})
        rolling.update(rel.encode("utf-8"))
        rolling.update(b"\x00")
        rolling.update(fh.encode("ascii"))
        rolling.update(b"\n")
    overall = rolling.hexdigest()
    return {
        "enabled": True,
        "contract_version": CONTRACT_VERSION,
        "dry_run_only": DRY_RUN_ONLY,
        "checksum_sha256": overall,
        "file_count": len(per_file),
        "included_files": [p["path"] for p in per_file],
        "missing_files": missing,
        "per_file_sha256_count": len(per_file),
        "db_writes": DB_WRITES,
        "persisted": PERSISTED,
        "live_apply_allowed": LIVE_APPLY_ALLOWED,
        "live_enforcement_enabled": LIVE_ENFORCEMENT_ENABLED,
        "preview_request_blocked": PREVIEW_REQUEST_BLOCKED,
        "read_only": True,
        "external_sink_used": False,
        "alert_dispatched": False,
    }


def build_config_block() -> Dict[str, Any]:
    return {
        "enabled": True,
        "contract_version": CONTRACT_VERSION,
        "dry_run_only": DRY_RUN_ONLY,
        "db_writes": DB_WRITES,
        "persisted": PERSISTED,
        "live_apply_allowed": LIVE_APPLY_ALLOWED,
        "live_enforcement_enabled": LIVE_ENFORCEMENT_ENABLED,
        "preview_request_blocked": PREVIEW_REQUEST_BLOCKED,
        "read_only": True,
        "external_sink_used": False,
        "alert_dispatched": False,
    }


def _test_reset() -> None:
    """No-op: utility is stateless."""
    return None
