#!/usr/bin/env python3
"""PROJECT_C Track F validator (read-only).

Verifica che i 3 template Grafana siano stati emessi in `/app/ops/grafana/templates/`
senza nessun secret bakato, e che il marker JSON dichiari `production_apply_status=DESIGNED_NOT_AUTHORIZED`.

Exit 0 PASS / 1 FAIL.
"""
import json
import sys
from pathlib import Path

MARKER = Path("/app/data/design/system_safety/project_c_af2n_dashboard_provision_ops_v1.json")
TEMPLATES_DIR = Path("/app/ops/grafana/templates")
REQUIRED_TEMPLATES = [
    "af2n_datasource.yaml.template",
    "af2n_dashboard_provisioning.yaml.template",
    "af2n_alerts.yaml.template",
]
REQUIRED_PLACEHOLDERS = [
    "${AF2N_METRICS_DS_URL}",
    "${AF2N_METRICS_DS_TOKEN}",
    "${AF2N_PAGER_TOKEN}",
    "${AF2N_SMTP_PASSWORD}",
    "${AF2N_SLACK_WEBHOOK_URL}",
    "${GRAFANA_PROVISIONING_PATH}",
]
# Pattern che indicherebbero secrets reali bakati (semplice euristica)
LIKELY_SECRET_PATTERNS = ["-----BEGIN", "ghp_", "glpat-", "AKIA", "xoxb-", "slack.com/services/T0"]


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def main() -> None:
    if not MARKER.exists():
        fail(f"missing marker {MARKER}")
    m = json.loads(MARKER.read_text())
    if m.get("verdict") != "TRACK_F_AF2N_DASHBOARD_PROVISION_OPS_TEMPLATES_READY":
        fail(f"verdict mismatch: {m.get('verdict')}")
    if m.get("runtime_patch_applied") is not False:
        fail("runtime_patch_applied must be False")
    if m.get("external_service_calls") != 0:
        fail("external_service_calls must be 0")
    if m.get("production_apply_status") != "DESIGNED_NOT_AUTHORIZED":
        fail("production_apply_status must be DESIGNED_NOT_AUTHORIZED")
    if m.get("all_templates_inert_no_secret_baked") is not True:
        fail("all_templates_inert_no_secret_baked must be True")
    forb = m.get("forbidden_in_track_f_respected", {})
    for k in ("af2n_runtime_mutation", "external_service_integration", "public_spend_ui", "stack_g_changes", "af2n_public_rollout"):
        if forb.get(k) is not False:
            fail(f"forbidden_in_track_f.{k} must be False")
    if not TEMPLATES_DIR.exists():
        fail(f"templates dir missing: {TEMPLATES_DIR}")
    for t in REQUIRED_TEMPLATES:
        p = TEMPLATES_DIR / t
        if not p.exists():
            fail(f"missing template {p}")
        src = p.read_text()
        for pattern in LIKELY_SECRET_PATTERNS:
            if pattern in src:
                fail(f"template {t} contains likely-secret pattern: {pattern}")
    # Verifica che ogni placeholder canonico appaia in almeno uno dei template
    combined = "\n".join((TEMPLATES_DIR / t).read_text() for t in REQUIRED_TEMPLATES)
    for ph in REQUIRED_PLACEHOLDERS:
        if ph not in combined:
            fail(f"placeholder {ph} not present in any template")
    print("[PASS] PROJECT_C Track F AF2-N dashboard provisioning OPS OK: 3 templates, no secrets baked, DESIGNED_NOT_AUTHORIZED")
    sys.exit(0)


if __name__ == "__main__":
    main()
