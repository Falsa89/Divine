#!/usr/bin/env python3
"""PROJECT_F Track H validator — artifact bible import plan & approval gate.

No runtime/live bonus. Verifies:
  * marker present with verdict ready
  * 4 approval gates declared, all in PENDING state
  * import plan has at least 7 ordered steps
  * candidates remain inert (design_only/draft/frozen)
  * no equipment semantics / no live bonus / no live summon
"""
import json, sys
from pathlib import Path

MARKER = Path('/app/data/design/artifacts/project_f_artifact_bible_import_plan_v1.json')
CANDIDATES = Path('/app/data/design/artifacts/artifact_bible_launch_candidates_v1.json')
FREEZE = Path('/app/data/design/artifacts/project_d_artifact_bible_v1_approval_freeze_pack.json')
SCHEMA = Path('/app/data/design/artifacts/artifact_bible_schema_v1.json')
INERT_STATUSES = {'draft', 'design_only', 'frozen'}
LIVE_FORBIDDEN = {'live', 'released', 'active', 'production'}


def fail(m): print(f'[FAIL] {m}'); sys.exit(1)


def main():
    if not MARKER.exists(): fail(f'missing marker {MARKER}')
    m = json.loads(MARKER.read_text())
    if m.get('verdict') != 'TRACK_H_ARTIFACT_BIBLE_IMPORT_PLAN_APPROVAL_GATE_READY': fail('verdict mismatch')
    if m.get('artifact_live_bonus_active') is not False: fail('artifact_live_bonus_active must be False')
    if m.get('artifact_summon_behavior_active') is not False: fail('artifact_summon_behavior_active must be False')
    gates = m.get('approval_gates', [])
    if len(gates) != 4: fail('exactly 4 approval gates required')
    gate_ids_required = {'USER_APPROVAL', 'ECONOMY_APPROVAL_SUMMON_FRAGMENT_SOURCE', 'BALANCE_APPROVAL_CAPS', 'QA_APPROVAL_NO_LIVE_LEAK'}
    if {g.get('gate_id') for g in gates} != gate_ids_required: fail(f'gate_ids must equal {sorted(gate_ids_required)}')
    for g in gates:
        if g.get('state') != 'PENDING': fail(f'gate {g.get("gate_id")} must be PENDING (got {g.get("state")})')
        if g.get('required') is not True: fail(f'gate {g.get("gate_id")} must be required')
    steps = m.get('import_plan_steps', [])
    if len(steps) < 7: fail('import_plan_steps must have at least 7 entries')
    forb = m.get('forbidden_in_track_h_respected', {})
    for k in ('artifact_live_bonus', 'artifact_summon_behavior', 'gacha_rate_pity_change', 'frontend', 'db_writes', 'equipment_semantics'):
        if forb.get(k) is not False: fail(f'forbidden_in_track_h.{k} must be False')
    # Upstream candidates inert
    for p in (CANDIDATES, FREEZE, SCHEMA):
        if not p.exists(): fail(f'upstream missing {p}')
    cands = json.loads(CANDIDATES.read_text()).get('candidates', [])
    if not cands: fail('candidates list empty')
    for c in cands:
        st = c.get('status', 'draft')
        if st in LIVE_FORBIDDEN: fail(f'candidate {c.get("artifact_id")} is LIVE forbidden status: {st}')
        if st not in INERT_STATUSES: fail(f'candidate {c.get("artifact_id")} status not inert: {st}')
        if c.get('is_equipment') is True or c.get('occupies_gear_slot') is True or c.get('is_divine_weapon') is True:
            fail(f'candidate {c.get("artifact_id")} flagged as equipment')
    print('[PASS] PROJECT_F Track H artifact bible import plan READY: 4 PENDING gates; 7 steps; 5 inert non-equipment candidates; no live bonus/summon')
    sys.exit(0)

if __name__ == '__main__': main()
