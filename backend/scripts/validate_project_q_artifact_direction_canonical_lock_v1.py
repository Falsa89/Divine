#!/usr/bin/env python3
"""PROJECT_Q Track A validator — artifact direction canonical lock.

Verifica che gli Artifact siano dichiarati 'account-wide / roster-wide collectibles'
e NON equipaggiamento, NON gear slot, NON divine weapon / unique weapon.
Non tocca il DB, non esegue import live.
"""
import json, sys
from pathlib import Path

M = Path('/app/data/design/artifacts/project_q_artifact_direction_canonical_lock_v1.json')
REQUIRED_INVARIANTS = (
    'is_equipment == false',
    'occupies_gear_slot == false',
    'is_divine_weapon == false',
    'global_roster_account_bonus.value_pct <= 5.0',
    "obtainment_source != 'hero_summon_banner'",
)


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main() -> None:
    if not M.exists():
        fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_A_ARTIFACT_DIRECTION_CANONICAL_LOCK_READY':
        fail(f'verdict mismatch: {m.get("verdict")}')
    lock = m.get('canonical_lock') or {}
    if 'account-wide' not in (lock.get('artifacts_are') or '').lower() and 'roster-wide' not in (lock.get('artifacts_are') or '').lower():
        fail('canonical_lock.artifacts_are must declare account-wide / roster-wide collectibles')
    are_not = [str(x).lower() for x in (lock.get('artifacts_are_NOT') or [])]
    for forbidden in ('equipment', 'hero gear slot', 'divine weapon', 'unique 6-star weapon'):
        if not any(forbidden in x for x in are_not):
            fail(f'canonical_lock.artifacts_are_NOT must include: {forbidden}')
    invs = m.get('hard_invariants_locked') or []
    for req in REQUIRED_INVARIANTS:
        if req not in invs:
            fail(f'missing invariant: {req}')
    # Direction file must exist on disk
    ref = Path(m.get('canonical_direction_v1_ref') or '')
    if not ref.exists():
        fail(f'canonical_direction_v1_ref missing on disk: {ref}')
    print('[PASS] PROJECT_Q Track A direction canonical lock READY — artifacts account/roster-wide, NOT equipment / gear / divine weapon')
    sys.exit(0)


if __name__ == '__main__':
    main()
