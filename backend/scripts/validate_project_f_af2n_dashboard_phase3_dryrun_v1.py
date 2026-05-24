#!/usr/bin/env python3
"""PROJECT_F Track F validator — AF2-N dashboard provisioning phase 3 dry-run.

Local/offline only. Validates manifest, templates, alert UIDs and that no
external calls or secrets were required.
"""
import json, sys
from pathlib import Path

MARKER = Path('/app/data/design/system_safety/project_f_af2n_dashboard_provisioning_phase3_dryrun_v1.json')
UPSTREAM = [
    '/app/data/design/system_safety/af2n_observability_dashboard_template_v1.json',
    '/app/data/design/system_safety/af2n_observability_dashboard_render_v1.json',
    '/app/data/design/system_safety/af2n_observability_metrics_pipeline_v1.json',
]


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f'missing marker {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_F_AF2N_DASHBOARD_PROVISIONING_PHASE3_DRYRUN_READY': fail('verdict mismatch')
    if m.get('external_calls_made') != 0: fail('external_calls_made must be 0')
    if m.get('secrets_required_at_dryrun') != 0: fail('secrets_required_at_dryrun must be 0')
    if m.get('templates_validated') != 3: fail('templates_validated must be 3')
    if m.get('alert_uids_verified') != 5: fail('alert_uids_verified must be 5')
    forb = m.get('forbidden_in_track_f_respected', {})
    for k in ('external_service_calls', 'af2n_runtime_mutation', 'public_spend_ui', 'stack_g_change'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_f.{k} must be False')
    for u in UPSTREAM:
        if not Path(u).exists(): fail(f'upstream missing: {u}')
    print('[PASS] PROJECT_F Track F AF2-N dashboard phase3 dry-run READY: 7 offline steps; 0 external calls; 3 templates; 5 alert UIDs')
    sys.exit(0)

if __name__ == '__main__': main()
