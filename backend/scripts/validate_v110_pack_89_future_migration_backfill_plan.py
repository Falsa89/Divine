#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_89_inventory_psp_scoped/v110_pack_89_future_migration_backfill_plan_v1.json')))
assert d.get('future_migration_needed') is False
assert d.get('future_backfill_needed') is False
plan = d.get('future_write_paths_promotion_plan', [])
assert len(plan) >= 2
for p in plan:
    assert 'AUTORIZZO' in p.get('future_authorization_string', '')
print('[v110 PACK_89_FUTURE_MIGRATION_BACKFILL_PLAN] OK no_migration_needed future_write_paths_planned_with_authorization_strings')
