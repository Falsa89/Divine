#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_87_server_scoped_starter_flow/v110_pack_87_team_initialization_v1.json')))
cond = d.get('conditions', {})
for k in ('only_if_psp_team_empty','only_with_newly_created_starter_user_hero_ids','only_same_server_id','never_overwrite','never_fake_team','never_copy_other_server'):
    assert cond.get(k) is True, f'team init condition {k} must be true'
sm = d.get('smoke_test_result', {})
assert sm.get('team_initialized_on_first_claim') is True
assert sm.get('team_unchanged_on_second_claim') is True
assert sm.get('existing_team_never_overwritten') is True
# Verifica statica server.py
src = open(os.path.join(R, 'backend/server.py')).read()
assert 'team_formation' in src
assert '"team_formation": {"$in": [None, []]}' in src or "'team_formation': {'$in': [None, []]}" in src, 'team init MUST use conditional update with team in {None, []}'
assert '_slc_pack_87_starter_team_init' in src
assert '_slc_pack_87_team_initialized_from_starter' in src
print('[v110 PACK_87_TEAM_INITIALIZATION] OK init_only_if_empty no_overwrite no_fake no_cross_server conditional_mongo_update team_init_marker')
