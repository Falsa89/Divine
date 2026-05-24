#!/usr/bin/env python3
"""PROJECT_G Track H validator — artifact approval gate signature template.

Verifies:
  * marker present with verdict TRACK_H_ARTIFACT_APPROVAL_GATE_SIGNATURE_READY_PENDING_USER
  * 4 approval gates present and all PENDING (signature=null, signed_at_iso=null, signed_by=null)
  * signature_template defines signing_rule + user_approval_required_message_template
  * 5 design-only candidates listed and inert (no live/active status)
  * current_prompt_explicit_user_approval_message_detected == False
  * artifact_live_bonus_active / artifact_summon_behavior_active / artifact_import_live_active all False
"""
import json, sys
from pathlib import Path

MARKER = Path('/app/data/design/artifacts/project_g_artifact_approval_gate_signature_pack_v1.json')
REQUIRED_GATE_IDS = {'USER_APPROVAL', 'ECONOMY_APPROVAL_SUMMON_FRAGMENT_SOURCE', 'BALANCE_APPROVAL_CAPS', 'QA_APPROVAL_NO_LIVE_LEAK'}
INERT_STATUSES = {'draft', 'design_only', 'frozen'}
LIVE_FORBIDDEN = {'live', 'released', 'active', 'production'}


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f'marker missing {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_H_ARTIFACT_APPROVAL_GATE_SIGNATURE_READY_PENDING_USER': fail('verdict mismatch')
    if m.get('artifact_live_bonus_active') is not False: fail('artifact_live_bonus_active must be False')
    if m.get('artifact_summon_behavior_active') is not False: fail('artifact_summon_behavior_active must be False')
    if m.get('artifact_import_live_active') is not False: fail('artifact_import_live_active must be False')
    if m.get('current_prompt_explicit_user_approval_message_detected') is not False:
        fail('current_prompt_explicit_user_approval_message_detected must be False in this pack')
    gates = m.get('approval_gates', [])
    if len(gates) != 4: fail(f'expected 4 approval gates, got {len(gates)}')
    if {g.get('gate_id') for g in gates} != REQUIRED_GATE_IDS:
        fail('gate_id set mismatch')
    for g in gates:
        if g.get('state') != 'PENDING': fail(f'gate {g.get("gate_id")} must be PENDING')
        if g.get('signature') is not None: fail(f'gate {g.get("gate_id")} signature must be null')
        if g.get('signed_at_iso') is not None: fail(f'gate {g.get("gate_id")} signed_at_iso must be null')
        if g.get('signed_by') is not None: fail(f'gate {g.get("gate_id")} signed_by must be null')
    tpl = m.get('signature_template', {})
    if 'signing_rule' not in tpl: fail('signature_template missing signing_rule')
    if 'user_approval_required_message_template' not in tpl: fail('signature_template missing user_approval_required_message_template')
    cands = m.get('five_design_only_candidates', [])
    if len(cands) != 5: fail(f'expected 5 design-only candidates, got {len(cands)}')
    for c in cands:
        st = c.get('status', 'draft')
        if st in LIVE_FORBIDDEN: fail(f'candidate {c.get("artifact_id")} LIVE forbidden status: {st}')
        if st not in INERT_STATUSES: fail(f'candidate {c.get("artifact_id")} status not inert: {st}')
    forb = m.get('forbidden_in_track_h_respected', {})
    for k in ('artifact_live_bonus', 'artifact_summon_behavior', 'gacha_rate_pity_change', 'frontend', 'db_writes', 'equipment_semantics'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_h.{k} must be False')
    print('[PASS] PROJECT_G Track H artifact approval gate signature READY (PENDING_USER): 4 PENDING gates; signature template defined; 5 inert candidates; no live activation')
    sys.exit(0)

if __name__ == '__main__': main()
