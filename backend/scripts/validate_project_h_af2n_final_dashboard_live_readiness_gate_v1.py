#!/usr/bin/env python3
"""PROJECT_H Track F validator — final AF2-N dashboard live readiness gate."""
import json, sys
from pathlib import Path

MARKER = Path('/app/data/design/system_safety/project_h_af2n_final_dashboard_live_readiness_gate_v1.json')
REQUIRED_GATE_IDS = {'OPS_APPROVAL', 'ALERT_SINK_CONFIGURED', 'DASHBOARD_DATA_SOURCE_CONFIGURED', 'NO_SECRET_LEAKAGE', 'ROLLBACK_NO_OP_PATH'}
EXACT_TEXT_KEYS = (
    'exact_approval_text_for_ops_gate',
    'exact_approval_text_for_alert_sink_gate',
    'exact_approval_text_for_datasource_gate',
    'exact_approval_text_for_no_secret_leakage_gate',
    'exact_approval_text_for_rollback_gate',
)


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f'missing marker {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_F_AF2N_FINAL_DASHBOARD_LIVE_READINESS_GATE_READY': fail('verdict mismatch')
    if m.get('external_calls_made') != 0: fail('external_calls_made must be 0')
    if m.get('runtime_changes_applied') is not False: fail('runtime_changes_applied must be False')
    if m.get('current_prompt_explicit_approval_detected') is not False:
        fail('current_prompt_explicit_approval_detected must be False in this pack')
    gates = m.get('approval_gates', [])
    if {g.get('gate_id') for g in gates} != REQUIRED_GATE_IDS: fail('gate_id set mismatch')
    for g in gates:
        if g.get('state') != 'PENDING': fail(f'gate {g.get("gate_id")} must be PENDING')
        if g.get('required_for_live') is not True: fail(f'gate {g.get("gate_id")} required_for_live must be True')
    for k in EXACT_TEXT_KEYS:
        if not m.get(k): fail(f'missing exact approval text: {k}')
    forb = m.get('forbidden_in_track_f_respected', {})
    for k in ('external_service_calls', 'af2n_runtime_mutation', 'public_spend_ui', 'stack_g_change'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_f.{k} must be False')
    print('[PASS] PROJECT_H Track F AF2-N final dashboard live readiness gate READY: 5 PENDING gates; 5 exact approval texts defined; 0 external calls')
    sys.exit(0)

if __name__ == '__main__': main()
