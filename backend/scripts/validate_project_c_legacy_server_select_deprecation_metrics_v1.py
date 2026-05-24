#!/usr/bin/env python3
"""PROJECT_C Track G validator (read-only).

Verifica il design metrics + log archival per `POST /api/server/select` legacy.
Nessun emitter runtime atteso in V_C.

Exit 0 PASS / 1 FAIL.
"""
import json
import sys
from pathlib import Path

MARKER = Path("/app/data/design/system_safety/project_c_legacy_server_select_deprecation_metrics_v1.json")
UPSTREAM = Path("/app/data/design/system_safety/v7_economy_server_select_deprecation_marker.json")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not MARKER.exists():
        fail(f"missing {MARKER}")
    m = json.loads(MARKER.read_text())
    if m.get("verdict") != "TRACK_G_LEGACY_SERVER_SELECT_DEPRECATION_METRICS_DESIGN_READY":
        fail(f"verdict mismatch: {m.get('verdict')}")
    if m.get("runtime_patch_applied") is not False:
        fail("runtime_patch_applied must be False")
    if m.get("route_behavior_mutated") is not False:
        fail("route_behavior_mutated must be False")
    if m.get("db_writes_executed") != 0:
        fail("db_writes_executed must be 0")
    md = m.get("metrics_design", {})
    if md.get("metric_count") != 3:
        fail("metric_count must be 3")
    metrics = md.get("metrics", [])
    if len(metrics) != 3:
        fail("metrics list must have 3 entries")
    expected_names = {
        "divine_legacy_server_select_calls_total",
        "divine_legacy_server_select_deprecation_log_emit_total",
        "divine_legacy_server_select_unique_users_24h",
    }
    got_names = {x.get("metric_name") for x in metrics}
    if got_names != expected_names:
        fail(f"metric names mismatch: got {got_names}")
    for x in metrics:
        if x.get("emitter") != "deferred_to_metrics_block_v_d":
            fail(f"metric {x.get('metric_name')} emitter must be deferred_to_metrics_block_v_d")
    if md.get("prometheus_compatible") is not True:
        fail("prometheus_compatible must be True")
    if md.get("af2n_pipeline_compatible") is not True:
        fail("af2n_pipeline_compatible must be True")
    arch = m.get("log_archival_design", {})
    if arch.get("archived_in_v_c") is not False:
        fail("log archival must NOT be active in V_C")
    kill = m.get("kill_switch_strategy", {})
    if not all(k in kill for k in ("phase_1_v_d", "phase_2_v_e", "phase_3_v_f", "phase_4_v_g")):
        fail("kill_switch_strategy must declare 4 phases")
    forb = m.get("forbidden_in_track_g_respected", {})
    for k in ("server_select_behavior_change", "users_server_backfill", "db_migration", "battle_mutation", "af2n_runtime_flip", "metric_emitter_runtime_wiring"):
        if forb.get(k) is not False:
            fail(f"forbidden_in_track_g.{k} must be False")
    if not UPSTREAM.exists():
        fail("upstream V7 BLOCK_A deprecation marker missing")
    print("[PASS] PROJECT_C Track G legacy server select deprecation metrics DESIGN OK: 3 metrics + archival design + 4-phase kill-switch; no runtime wiring")
    sys.exit(0)


if __name__ == "__main__":
    main()
