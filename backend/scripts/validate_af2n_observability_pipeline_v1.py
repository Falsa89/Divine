#!/usr/bin/env python3
"""
V5 BLOCK_B AF2-N observability pipeline read-only validator.

Verifies the V5 metrics-pipeline JSON exists with the expected family count and
that the V4 canary report is still referenced. Read-only.

Exit 0 PASS / 1 FAIL.
"""
import json
import sys
from pathlib import Path

PIPELINE = Path("/app/data/design/system_safety/af2n_observability_metrics_pipeline_v1.json")
CANARY_REPORT = Path("/app/data/design/system_safety/af2n_canary_metrics_report_v1.json")

EXPECTED_FAMILIES = {"canary", "ledger", "rate_limit", "inventory_writes", "affinity_gain"}


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not PIPELINE.exists():
        fail(f"missing pipeline JSON: {PIPELINE}")
    if not CANARY_REPORT.exists():
        fail(f"missing V4 canary report reference: {CANARY_REPORT}")

    p = json.loads(PIPELINE.read_text(encoding="utf-8"))
    if p.get("verdict") != "BLOCK_B_AF2N_OBSERVABILITY_PIPELINE_READY":
        fail(f"unexpected verdict: {p.get('verdict')}")
    if p.get("runtime_patch_applied") is not False:
        fail("runtime_patch_applied must be false")

    families = {f.get("family") for f in p.get("metrics_schema", {}).get("metric_families", [])}
    missing = EXPECTED_FAMILIES - families
    if missing:
        fail(f"missing metric families: {sorted(missing)}")

    print(f"[PASS] V5 BLOCK_B observability pipeline: {len(families)} families registered")
    sys.exit(0)


if __name__ == "__main__":
    main()
