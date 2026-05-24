#!/usr/bin/env python3
"""PROJECT_G Track F validator — AF2-N dashboard provisioning approval gate.

Verifies:
  * marker present with verdict TRACK_F_AF2N_DASHBOARD_PROVISIONING_APPROVAL_GATE_READY
  * 5 approval gates declared (OPS, ALERT_SINK_CONFIGURED, DATA_SOURCE_CONFIGURED, NO_SECRET_LEAKAGE, ROLLBACK_NO_OP_PATH); all PENDING
  * external_calls_made == 0
  * local templates inert
  * upstream phase3 marker present
"""
import json, sys
from pathlib import Path

MARKER = Path('/app/data/design/system_safety/project_g_af2n_dashboard_provisioning_approval_gate_v1.json')
UPSTREAM = '/app/data/design/system_safety/project_f_af2n_dashboard_provisioning_phase3_dryrun_v1.json'
REQUIRED_GATE_IDS = {'OPS_APPROVAL', 'ALERT_SINK_CONFIGURED', 'DASHBOARD_DATA_SOURCE_CONFIGURED', 'NO_SECRET_LEAKAGE', 'ROLLBACK_NO_OP_PATH'}


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f'missing marker {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_F_AF2N_DASHBOARD_PROVISIONING_APPROVAL_GATE_READY': fail('verdict mismatch')
    if m.get('external_calls_made') != 0: fail('external_calls_made must be 0')
    if m.get('runtime_changes_applied') is not False: fail('runtime_changes_applied must be False')
    if m.get('local_templates_inert') is not True: fail('local_templates_inert must be True')
    gates = m.get('approval_gates', [])
    if len(gates) != 5: fail(f'expected 5 approval gates, got {len(gates)}')
    gate_ids = {g.get('gate_id') for g in gates}
    if gate_ids != REQUIRED_GATE_IDS: fail(f'gate_id set mismatch: extra={sorted(gate_ids - REQUIRED_GATE_IDS)} missing={sorted(REQUIRED_GATE_IDS - gate_ids)}')
    for g in gates:
        if g.get('state') != 'PENDING': fail(f'gate {g.get("gate_id")} state must be PENDING')
        if g.get('required') is not True: fail(f'gate {g.get("gate_id")} required must be True')
    forb = m.get('forbidden_in_track_f_respected', {})
    for k in ('external_service_calls', 'af2n_runtime_mutation', 'public_spend_ui', 'stack_g_change'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_f.{k} must be False')
    if not Path(UPSTREAM).exists(): fail(f'upstream phase3 marker missing: {UPSTREAM}')
    print('[PASS] PROJECT_G Track F AF2-N dashboard provisioning approval gate READY: 5 PENDING gates; 0 external calls; templates inert')
    sys.exit(0)

if __name__ == '__main__': main()
