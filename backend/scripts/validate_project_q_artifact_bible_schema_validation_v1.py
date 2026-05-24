#!/usr/bin/env python3
"""PROJECT_Q Track B validator — artifact bible schema validation.

Verifica che lo schema esista, contenga i campi richiesti, gli enum noti e gli hard invariants;
e che il marker dichiari schema_self_check_pass == true. No DB writes, no runtime touch.
"""
import json, sys
from pathlib import Path

M = Path('/app/data/design/artifacts/project_q_artifact_bible_schema_validation_v1.json')
REQUIRED_FIELDS = {'artifact_id', 'name', 'rarity', 'linked_faction', 'collection_category', 'obtainment_source'}
REQUIRED_INVARIANTS = (
    'is_equipment == false',
    'occupies_gear_slot == false',
    'is_divine_weapon == false',
    'global_roster_account_bonus.value_pct <= 5.0',
)


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main() -> None:
    if not M.exists():
        fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_B_ARTIFACT_BIBLE_SCHEMA_VALIDATION_READY':
        fail(f'verdict mismatch: {m.get("verdict")}')
    schema_ref = Path(m.get('schema_ref') or '')
    if not schema_ref.exists():
        fail(f'schema_ref missing on disk: {schema_ref}')
    declared_fields = set(m.get('required_fields_present') or [])
    missing = REQUIRED_FIELDS - declared_fields
    if missing:
        fail(f'required_fields_present missing: {sorted(missing)}')
    invs = m.get('hard_invariants_in_schema') or []
    for req in REQUIRED_INVARIANTS:
        if req not in invs:
            fail(f'missing invariant: {req}')
    if m.get('schema_self_check_pass') is not True:
        fail('schema_self_check_pass must be True')
    print('[PASS] PROJECT_Q Track B schema validation READY — required fields + invariants declared')
    sys.exit(0)


if __name__ == '__main__':
    main()
