#!/usr/bin/env python3
"""PROJECT_H Track G validator — final artifact approval gate + import readiness."""
import json, sys
from pathlib import Path

MARKER = Path('/app/data/design/artifacts/project_h_artifact_final_approval_gate_and_import_readiness_v1.json')
REQUIRED_GATE_IDS = {'USER_APPROVAL', 'ECONOMY_APPROVAL_SUMMON_FRAGMENT_SOURCE', 'BALANCE_APPROVAL_CAPS', 'QA_APPROVAL_NO_LIVE_LEAK'}
INERT_STATUSES = {'draft', 'design_only', 'frozen'}


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f'missing marker {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_G_ARTIFACT_FINAL_APPROVAL_GATE_READY_PENDING_USER': fail('verdict mismatch')
    for k in ('artifact_live_bonus_active', 'artifact_summon_behavior_active', 'artifact_import_live_active'):
        if m.get(k) is not False: fail(f'{k} must be False')
    if m.get('current_prompt_explicit_user_approval_message_detected') is not False:
        fail('current_prompt_explicit_user_approval_message_detected must be False in this pack')
    gates = m.get('approval_gates', [])
    if len(gates) != 4: fail('expected 4 approval gates')
    if {g.get('gate_id') for g in gates} != REQUIRED_GATE_IDS: fail('gate_id set mismatch')
    for g in gates:
        if g.get('state') != 'PENDING': fail(f'gate {g.get("gate_id")} must be PENDING')
        if g.get('signature') is not None: fail(f'gate {g.get("gate_id")} signature must be null')
    if not m.get('exact_future_approval_message_for_user_gate'):
        fail('exact_future_approval_message_for_user_gate must be a non-empty string')
    cands = m.get('five_design_only_candidates', [])
    if len(cands) != 5: fail('expected 5 design-only candidates')
    for c in cands:
        st = c.get('status', 'draft')
        if st not in INERT_STATUSES: fail(f'candidate {c.get("artifact_id")} status not inert: {st}')
        if c.get('is_equipment') is True or c.get('occupies_gear_slot') is True or c.get('is_divine_weapon') is True:
            fail(f'candidate {c.get("artifact_id")} flagged as equipment-like')
    forb = m.get('forbidden_in_track_g_respected', {})
    for k in ('artifact_live_bonus', 'artifact_summon_behavior', 'artifact_import_live_activation', 'gacha_rate_pity_change', 'frontend', 'db_writes', 'equipment_semantics'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_g.{k} must be False')
    print('[PASS] PROJECT_H Track G artifact final approval gate READY (PENDING_USER): 4 PENDING gates; 5 inert non-equipment candidates; exact USER approval message defined')
    sys.exit(0)

if __name__ == '__main__': main()
