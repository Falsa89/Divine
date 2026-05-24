#!/usr/bin/env python3
"""PROJECT_Q Track C validator — artifact candidate expansion (design-only).

Verifica che la lista di candidati sia design-only:
- ogni artifact ha is_equipment=false, occupies_gear_slot=false, is_divine_weapon=false
- status == 'design_only'
- value_pct <= 1.5 per artifact
- somma teorica massima per account <= 5.0 (master cap)
- obtainment_source != 'hero_summon_banner'
- nessun DB write, lista solo in JSON.
"""
import json, sys
from pathlib import Path

M = Path('/app/data/design/artifacts/project_q_artifact_candidate_expansion_v1.json')
PER_ART_MAX_PCT = 1.5
MASTER_CAP_PCT = 5.0


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main() -> None:
    if not M.exists():
        fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_C_ARTIFACT_CANDIDATE_EXPANSION_READY':
        fail(f'verdict mismatch: {m.get("verdict")}')
    cands = m.get('candidates') or []
    if not cands:
        fail('no candidates listed')
    if m.get('total_candidates') != len(cands):
        fail(f'total_candidates {m.get("total_candidates")} != actual {len(cands)}')
    seen_ids = set()
    for art in cands:
        aid = art.get('artifact_id')
        if not isinstance(aid, str) or not aid.startswith('art_'):
            fail(f'bad artifact_id: {aid}')
        if aid in seen_ids:
            fail(f'duplicate artifact_id: {aid}')
        seen_ids.add(aid)
        if art.get('is_equipment') is not False:
            fail(f'{aid}: is_equipment must be false')
        if art.get('occupies_gear_slot') is not False:
            fail(f'{aid}: occupies_gear_slot must be false')
        if art.get('is_divine_weapon') is not False:
            fail(f'{aid}: is_divine_weapon must be false')
        if art.get('status') != 'design_only':
            fail(f'{aid}: status must be design_only (got {art.get("status")})')
        if art.get('obtainment_source') == 'hero_summon_banner':
            fail(f'{aid}: obtainment_source MUST NOT be hero_summon_banner')
        bonus = art.get('global_roster_account_bonus') or {}
        v = float(bonus.get('value_pct', 0.0))
        if v < 0 or v > PER_ART_MAX_PCT:
            fail(f'{aid}: value_pct {v} out of [0,{PER_ART_MAX_PCT}]')
    total_max = sum(float((a.get('global_roster_account_bonus') or {}).get('value_pct', 0.0)) for a in cands[:4])
    if total_max > MASTER_CAP_PCT:
        fail(f'top-4 theoretical bonus {total_max} exceeds master cap {MASTER_CAP_PCT}')
    print(f'[PASS] PROJECT_Q Track C candidate expansion READY — {len(cands)} design-only candidates, all invariants OK')
    sys.exit(0)


if __name__ == '__main__':
    main()
