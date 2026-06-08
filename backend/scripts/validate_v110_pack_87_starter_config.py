#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_87_server_scoped_starter_flow/v110_pack_87_starter_config_v1.json')))
assert d.get('starter_set_id') == 'pack_87_default_starter_set'
assert d.get('server_scoped') is True
assert d.get('claim_once_per_server') is True
assert d.get('allow_duplicate_on_same_server') is False
assert d.get('no_equipment') is True
assert d.get('no_currency') is True
assert d.get('no_inventory_reward') is True
assert d.get('no_story_reward') is True
assert d.get('no_player_level_mutation') is True
assert d.get('no_s1_to_s2_copy') is True
assert d.get('no_overwrite_existing_team') is True
assert d.get('team_init_only_if_empty') is True
assert d.get('premium') is False
assert d.get('max_rarity_allowed') == 2
hero_ids = d.get('hero_ids', [])
assert len(hero_ids) == 3
for h in hero_ids:
    assert h.get('initial_level') == 1
    assert h.get('initial_exp') == 0
    assert h.get('premium') is False
blockers = d.get('audit_blockers_when_violated', [])
for expected in ('STARTER_ROSTER_NOT_CATALOGED','STARTER_ROSTER_HIGH_RARITY','STARTER_ROSTER_PREMIUM_FORBIDDEN'):
    assert expected in blockers, f'audit blocker missing: {expected}'
print('[v110 PACK_87_STARTER_CONFIG] OK 3_heroes_low_rarity_non_premium claim_once_per_server team_init_only_if_empty no_equipment no_currency no_story_reward audit_blockers_defined')
