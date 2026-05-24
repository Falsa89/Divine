#!/usr/bin/env python3
"""PROJECT_I Track E validator — AF2-N approval signatures + canary plan."""
import json, sys
from pathlib import Path

MARKER = Path('/app/data/design/system_safety/project_i_af2n_approval_signatures_and_canary_plan_v1.json')
REQUIRED_GATE_IDS = {'OPS_APPROVAL', 'ALERT_SINK_CONFIGURED', 'DASHBOARD_DATA_SOURCE_CONFIGURED', 'NO_SECRET_LEAKAGE', 'ROLLBACK_NO_OP_PATH'}


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f'missing marker {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') not in ('TRACK_E_AF2N_APPROVAL_SIGNATURES_RECORDED_PARTIAL_OR_COMPLETE', 'TRACK_E_AF2N_APPROVAL_SIGNATURES_PENDING'):
        fail('verdict mismatch')
    if m.get('external_calls_made') != 0: fail('external_calls_made must be 0')
    detected = m.get('prompt_exact_approval_texts_detected', {})
    if set(detected.keys()) != REQUIRED_GATE_IDS: fail('detected keys must match REQUIRED_GATE_IDS')
    gates = m.get('approval_gates', [])
    if {g.get('gate_id') for g in gates} != REQUIRED_GATE_IDS: fail('gate_id set mismatch')
    # Honest gating: a gate may be SIGNED only if its exact text is detected=true
    for g in gates:
        gid = g.get('gate_id')
        state = g.get('state')
        if state == 'SIGNED' and detected.get(gid) is not True:
            fail(f'gate {gid} SIGNED but exact text not detected (would be fake PASS)')
        if state == 'PENDING' and (g.get('signature') is not None or g.get('signed_at_iso') is not None or g.get('signed_by') is not None):
            fail(f'PENDING gate {gid} must have null signature/signed_at_iso/signed_by')
    plan = m.get('canary_provisioning_plan', [])
    if len(plan) < 6: fail('canary_provisioning_plan must have at least 6 steps')
    forb = m.get('forbidden_in_track_e_respected', {})
    for k in ('external_service_calls', 'af2n_runtime_mutation', 'public_spend_ui'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_e.{k} must be False')
    print(f'[PASS] PROJECT_I Track E AF2-N approval signatures OK (verdict={m.get("verdict")}); 0 external calls; honest gating')
    sys.exit(0)

if __name__ == '__main__': main()
