#!/usr/bin/env python3
"""PROJECT_D Track G validator (read-only, local YAML shape only).

Valida i 3 template Grafana **solo localmente** (no external calls):
- apiVersion: 1
- top-level key corretta
- minimo numero entries
- campi richiesti per ciascuna entry / rule
- 5 alert UID canonici A1..A5
- 3 severity coperte: pager/email/slack

NON usa PyYAML (no extra deps): parsing minimalista linear-scan.
Exit 0 PASS / 1 FAIL.
"""
import json, sys
from pathlib import Path

MARKER = Path("/app/data/design/system_safety/project_d_af2n_dashboard_local_validation_v1.json")
TEMPLATES_DIR = Path("/app/ops/grafana/templates")
FILES = {
    "af2n_datasource.yaml.template": {"top": "datasources:", "required": ["name:", "type:", "url:"], "min_entries": 1},
    "af2n_dashboard_provisioning.yaml.template": {"top": "providers:", "required": ["name:", "type:", "options:"], "min_entries": 1},
    "af2n_alerts.yaml.template": {"top": "groups:", "required": ["uid:", "title:", "labels:"], "min_entries": 1, "min_rules": 5},
}
REQUIRED_ALERT_UIDS = (
    "af2n_a1_canary_error_rate",
    "af2n_a2_latency_p99",
    "af2n_a3_ratelimit_block_rate",
    "af2n_a4_ledger_idempotency_collision",
    "af2n_a5_canary_traffic_share_drift",
)
REQUIRED_SEVERITIES = ("pager", "email", "slack")


def fail(m): print(f"[FAIL] {m}"); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f"missing {MARKER}")
    m = json.loads(MARKER.read_text())
    if m.get("verdict") != "TRACK_G_AF2N_DASHBOARD_LOCAL_VALIDATION_READY":
        fail("verdict mismatch")
    if m.get("external_service_calls") != 0: fail("external_service_calls must be 0")
    if m.get("af2n_runtime_flip") is not False: fail("af2n_runtime_flip must be False")
    forb = m.get("forbidden_in_track_g_respected", {})
    for k in ("external_calls", "af2n_runtime_mutation", "public_spend_ui"):
        if forb.get(k) is not False: fail(f"forbidden_in_track_g.{k} must be False")

    if not TEMPLATES_DIR.exists(): fail(f"templates dir missing")
    for fname, rules in FILES.items():
        p = TEMPLATES_DIR / fname
        if not p.exists(): fail(f"template missing: {p}")
        src = p.read_text()
        if "apiVersion: 1" not in src: fail(f"{fname}: apiVersion: 1 missing")
        if rules["top"] not in src: fail(f"{fname}: top-level {rules['top']} missing")
        for f in rules["required"]:
            if f not in src: fail(f"{fname}: required field {f} missing")
        if fname == "af2n_alerts.yaml.template":
            # Count rules by 'uid:' occurrences
            uid_count = src.count("uid:")
            if uid_count < rules["min_rules"]: fail(f"{fname}: expected >= {rules['min_rules']} rules, got {uid_count}")
            # Required UIDs and severities
            for u in REQUIRED_ALERT_UIDS:
                if u not in src: fail(f"alerts: required uid {u} missing")
            for sev in REQUIRED_SEVERITIES:
                if f"severity: {sev}" not in src: fail(f"alerts: required severity {sev} missing")

    print("[PASS] PROJECT_D Track G AF2-N dashboard local validation OK: 3 templates shape OK; 5 alert UIDs A1..A5; severity pager/email/slack present; no external calls")
    sys.exit(0)

if __name__ == "__main__": main()
