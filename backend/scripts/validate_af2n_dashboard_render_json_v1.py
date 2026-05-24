#!/usr/bin/env python3
"""
V8 BLOCK_C validator (read-only).

Verifica lo schema del rendered dashboard JSON:
- 8 panel canonici con id 1..8 e panel_id P1..P8
- 5 alert rules A1..A5 con panel_ref
- 4 panel v8_signoff_gating=true (P1, P2, P5, P6)
- placeholders datasource presenti (no live connections)
- daemon_required=false
- forbidden scope rispettato
- upstream template V7 BLOCK_D presente

Exit 0 PASS / 1 FAIL.
"""
import json
import sys
from pathlib import Path

RENDER = Path("/app/data/design/system_safety/af2n_observability_dashboard_render_v1.json")
UPSTREAM_TEMPLATE = Path("/app/data/design/system_safety/af2n_observability_dashboard_template_v1.json")

EXPECTED_PANEL_IDS = {"P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"}
EXPECTED_ALERT_IDS = {"A1", "A2", "A3", "A4", "A5"}
EXPECTED_SIGNOFF_GATING = {"P1", "P2", "P5", "P6"}


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not RENDER.exists():
        fail(f"missing render: {RENDER}")
    if not UPSTREAM_TEMPLATE.exists():
        fail(f"upstream V7 template missing: {UPSTREAM_TEMPLATE}")

    m = json.loads(RENDER.read_text(encoding="utf-8"))
    if m.get("verdict") != "BLOCK_C_AF2N_DASHBOARD_RENDER_JSON_READY":
        fail(f"unexpected verdict: {m.get('verdict')}")
    if m.get("runtime_patch_applied") is not False:
        fail("runtime_patch_applied must be False")
    if m.get("daemon_required") is not False:
        fail("daemon_required must be False")
    if m.get("external_service_connections") not in (None, []):
        fail("external_service_connections must be empty")

    dash = m.get("dashboard", {})
    panels = dash.get("panels", [])
    if len(panels) != 8:
        fail(f"expected 8 panels, got {len(panels)}")
    panel_ids = {p.get("panel_id") for p in panels}
    if panel_ids != EXPECTED_PANEL_IDS:
        fail(f"panel_ids mismatch: {panel_ids}")

    gating = {p.get("panel_id") for p in panels if p.get("v8_signoff_gating") is True}
    if gating != EXPECTED_SIGNOFF_GATING:
        fail(f"v8 signoff gating panels mismatch: got {gating}, expected {EXPECTED_SIGNOFF_GATING}")

    alerts = dash.get("alert_rules", [])
    if len(alerts) != 5:
        fail(f"expected 5 alert rules, got {len(alerts)}")
    alert_ids = {a.get("id") for a in alerts}
    if alert_ids != EXPECTED_ALERT_IDS:
        fail(f"alert ids mismatch: {alert_ids}")
    for a in alerts:
        if not a.get("panel_ref"):
            fail(f"alert {a.get('id')} missing panel_ref")

    placeholders = m.get("placeholders_required_for_runtime_provisioning", [])
    if not any("af2n_metrics_ds" in p for p in placeholders):
        fail("missing af2n_metrics_ds placeholder")

    # Forbidden scope.
    forb = m.get("forbidden_in_block_c_respected", {})
    for k in ("af2n_runtime_mutation", "dashboard_daemon", "external_service_connection",
              "public_spend_ui", "stack_g_changes"):
        if forb.get(k) is not False:
            fail(f"forbidden_in_block_c_respected.{k} must be False")

    print("[PASS] V8 BLOCK_C dashboard render schema OK (8 panels, 5 alerts, 4 gating, 0 daemons, 0 ext connections)")
    sys.exit(0)


if __name__ == "__main__":
    main()
