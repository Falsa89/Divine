#!/usr/bin/env python3
"""PROJECT_I Track F validator — artifact approval signatures + import canary plan."""
import json, sys
from pathlib import Path

MARKER = Path('/app/data/design/artifacts/project_i_artifact_approval_signatures_and_import_canary_plan_v1.json')
REQUIRED_GATE_IDS = {'USER_APPROVAL', 'ECONOMY_APPROVAL_SUMMON_FRAGMENT_SOURCE', 'BALANCE_APPROVAL_CAPS', 'QA_APPROVAL_NO_LIVE_LEAK'}


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f'missing marker {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') not in ('TRACK_F_ARTIFACT_APPROVAL_SIGNATURES_RECORDED_PARTIAL_OR_COMPLETE', 'TRACK_F_ARTIFACT_APPROVAL_SIGNATURES_PENDING'):
        fail('verdict mismatch')
    for k in ('artifact_live_bonus_active', 'artifact_summon_behavior_active', 'artifact_import_live_active'):
        if m.get(k) is not False: fail(f'{k} must be False')
    detected = m.get('prompt_exact_approval_texts_detected', {})
    if set(detected.keys()) != REQUIRED_GATE_IDS: fail('detected keys mismatch')
    gates = m.get('approval_gates', [])
    if {g.get('gate_id') for g in gates} != REQUIRED_GATE_IDS: fail('gate_id set mismatch')
    for g in gates:
        gid = g.get('gate_id')
        state = g.get('state')
        if state == 'SIGNED' and detected.get(gid) is not True:
            fail(f'gate {gid} SIGNED but exact text not detected (would be fake PASS)')
        if state == 'PENDING' and (g.get('signature') is not None or g.get('signed_at_iso') is not None or g.get('signed_by') is not None):
            fail(f'PENDING gate {gid} must have null signature/signed_at_iso/signed_by')
    plan = m.get('import_canary_plan', [])
    if len(plan) < 5: fail('import_canary_plan must have at least 5 steps')
    forb = m.get('forbidden_in_track_f_respected', {})
    for k in ('artifact_live_bonus', 'artifact_summon_behavior', 'artifact_import_live_activation', 'gacha_rate_pity_change', 'frontend', 'db_writes', 'equipment_semantics'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_f.{k} must be False')
    print(f'[PASS] PROJECT_I Track F artifact approval signatures OK (verdict={m.get("verdict")}); honest gating; no live bonus/summon/import')
    sys.exit(0)

if __name__ == '__main__': main()
