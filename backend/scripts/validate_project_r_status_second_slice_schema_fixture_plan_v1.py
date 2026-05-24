#!/usr/bin/env python3
"""PROJECT_R Track C validator — schema + fixture plan.

Verifica required fields nello schema design e che le canonical fixtures siano coerenti
con il scope (Track A) e i caps (Track B). is_runtime_active deve essere false ovunque.
"""
import json, sys
from pathlib import Path

M = Path('/app/data/design/status_effects/project_r_status_second_slice_schema_fixture_plan_v1.json')
REQUIRED_FIELDS = {'status_id', 'family', 'stat_target', 'sign', 'duration_rounds', 'stacking_rule', 'caps', 'source', 'mode_constraints', 'is_runtime_active'}
ALLOWED_FAMILIES = {'debuff_offensive', 'debuff_defensive', 'speed_up', 'speed_down'}
ALLOWED_STAT_TARGETS = {'atk_pct', 'def_pct', 'speed_pct', 'crit_pct'}


def fail(msg: str) -> None:
    print(f'[FAIL] {msg}')
    sys.exit(1)


def main() -> None:
    if not M.exists():
        fail(f'marker missing: {M}')
    m = json.loads(M.read_text())
    if m.get('verdict') != 'TRACK_C_STATUS_SECOND_SLICE_SCHEMA_AND_FIXTURE_PLAN_READY':
        fail(f'verdict mismatch: {m.get("verdict")}')
    required = set(m.get('required_fields') or [])
    missing = REQUIRED_FIELDS - required
    if missing:
        fail(f'required_fields missing: {sorted(missing)}')
    fixtures = m.get('canonical_fixtures') or []
    if not fixtures or len(fixtures) != int(m.get('fixture_count', -1)):
        fail('fixture_count != len(canonical_fixtures)')
    seen_ids = set()
    for fx in fixtures:
        for k in REQUIRED_FIELDS:
            if k not in fx:
                fail(f'fixture {fx.get("status_id")} missing field: {k}')
        sid = fx['status_id']
        if not sid.startswith('st_'):
            fail(f'bad status_id prefix: {sid}')
        if sid in seen_ids:
            fail(f'duplicate status_id: {sid}')
        seen_ids.add(sid)
        if fx['family'] not in ALLOWED_FAMILIES:
            fail(f'{sid}: family not allowed: {fx["family"]}')
        if fx['stat_target'] not in ALLOWED_STAT_TARGETS:
            fail(f'{sid}: stat_target not allowed: {fx["stat_target"]}')
        if fx.get('is_runtime_active') is not False:
            fail(f'{sid}: is_runtime_active must be False (design-only)')
        if not (1 <= int(fx.get('duration_rounds', 0)) <= 6):
            fail(f'{sid}: duration_rounds out of [1,6]')
    if m.get('resolver_implemented') is not False:
        fail('resolver_implemented must be False in design-only')
    if m.get('db_writes') is not False:
        fail('db_writes must be False')
    print(f'[PASS] PROJECT_R Track C schema + fixture plan READY — {len(fixtures)} canonical fixtures, design-only, no resolver impl')
    sys.exit(0)


if __name__ == '__main__':
    main()
