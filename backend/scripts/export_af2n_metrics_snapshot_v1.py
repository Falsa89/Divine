#!/usr/bin/env python3
"""
V6 BLOCK_B AF2-N metrics snapshot export script (non-runtime, on-demand).

Reads AF2-N metric values via GET-only API calls and produces a JSONL snapshot in
/app/data/design/system_safety/af2n_metrics_snapshot.jsonl.

Does NOT run as a daemon. Does NOT poll. Does NOT write to DB/Redis.
Does NOT emit metrics to any external collector.

Usage:
  python3 /app/backend/scripts/export_af2n_metrics_snapshot_v1.py

Exit 0 OK / 1 partial failure (some metrics unreachable, snapshot still written)
"""
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE_URL = "http://localhost:8001"
OUT = Path("/app/data/design/system_safety/af2n_metrics_snapshot.jsonl")


def http_get_json(path: str) -> tuple[int, object]:
    try:
        with urllib.request.urlopen(BASE_URL + path, timeout=3.0) as r:
            return r.status, json.loads(r.read().decode("utf-8", "ignore"))
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception:
        return -1, None


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def emit_record(records: list, family: str, name: str, value, source: str, labels: dict | None = None) -> None:
    if value is None:
        return
    rec = {
        "timestamp_utc": now(),
        "metric_family": family,
        "metric_name": name,
        "value": value,
        "source": source,
    }
    if labels:
        rec["labels"] = labels
    records.append(rec)


def main() -> None:
    records: list[dict] = []
    partial_failures = 0

    # canary family
    code, status = http_get_json("/api/affinity/gift-spend/canary-status")
    if code == 200 and isinstance(status, dict):
        emit_record(records, "canary", "af2n_canary_allowlist_size", status.get("canary_allowlist_size"), "/api/affinity/gift-spend/canary-status")
        emit_record(records, "canary", "af2n_canary_ledger_cap", status.get("canary_ledger_cap"), "/api/affinity/gift-spend/canary-status")
        emit_record(records, "ledger", "af2n_ledger_total_rows", status.get("ledger_total_rows"), "/api/affinity/gift-spend/canary-status")
        emit_record(records, "rate_limit", "af2n_feature_flag_currently_enabled", int(bool(status.get("feature_flag_currently_enabled"))), "/api/affinity/gift-spend/canary-status")
        emit_record(records, "inventory_writes", "af2n_inventory_mutation_enabled", int(bool(status.get("inventory_mutation_enabled"))), "/api/affinity/gift-spend/canary-status")
        emit_record(records, "affinity_gain", "af2n_affinity_points_mutation_enabled", int(bool(status.get("affinity_points_mutation_enabled"))), "/api/affinity/gift-spend/canary-status")
    else:
        partial_failures += 1

    # heroes count snapshot (sanity)
    code, body = http_get_json("/api/heroes")
    if code == 200 and isinstance(body, list):
        emit_record(records, "canary", "backend_heroes_count", len(body), "/api/heroes")
    else:
        partial_failures += 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"[OK] V6 BLOCK_B export wrote {len(records)} records to {OUT}; partial_failures={partial_failures}")
    sys.exit(0 if partial_failures == 0 else 1)


if __name__ == "__main__":
    main()
