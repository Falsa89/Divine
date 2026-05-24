#!/usr/bin/env python3
"""PROJECT_E Track F validator: AF2-N dashboard provisioning drill (offline)."""
import json, sys
from pathlib import Path

MARKER = Path("/app/data/design/system_safety/project_e_af2n_dashboard_provisioning_drill_v1.json")
TEMPLATES = Path("/app/ops/grafana/templates")
REQUIRED_TEMPLATES = ("af2n_datasource.yaml.template", "af2n_dashboard_provisioning.yaml.template", "af2n_alerts.yaml.template")


def fail(m): print(f"[FAIL] {m}"); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f"missing {MARKER}")
    m = json.loads(MARKER.read_text())
    if m.get("verdict") != "TRACK_F_AF2N_DASHBOARD_PROVISIONING_DRILL_READY": fail("verdict mismatch")
    if m.get("external_service_calls") != 0: fail("external_service_calls must be 0")
    if m.get("af2n_runtime_flip") is not False: fail("af2n_runtime_flip must be False")
    steps = m.get("drill_steps_executed_locally", [])
    if len(steps) != 5: fail(f"drill must have 5 steps, got {len(steps)}")
    for s in steps:
        if s.get("external_call") is not False: fail(f"step {s.get('name')} external_call must be False")
    forb = m.get("forbidden_in_track_f_respected", {})
    for k in ("external_calls", "af2n_runtime_mutation", "public_spend_ui", "stack_g_changes"):
        if forb.get(k) is not False: fail(f"forbidden_in_track_f.{k} must be False")
    for t in REQUIRED_TEMPLATES:
        if not (TEMPLATES / t).exists(): fail(f"template missing: {t}")
    print("[PASS] PROJECT_E Track F AF2-N dashboard provisioning drill OK: 5 steps offline; 0 external calls; 3 templates present")
    sys.exit(0)

if __name__ == "__main__": main()
