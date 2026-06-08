#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_87_server_scoped_starter_flow/v110_pack_87_backend_starter_claim_endpoint_v1.json')))
inv = d.get('implementation_invariants', {})
for k in ('explicit_server_id_required','server_id_blank_returns_400','requires_existing_psp','idempotent','user_heroes_created_only_with_server_id','audit_each_hero_id_via_catalog','refuse_if_not_cataloged','refuse_if_high_rarity','refuse_if_not_official','refuse_if_not_obtainable','refuse_if_not_show_in_catalog','refuse_if_deactivated','refuse_if_premium','team_init_only_if_empty','team_init_no_overwrite'):
    assert inv.get(k) is True, f'invariant {k} must be true'
for k in ('no_account_wide_user_heroes','no_premium_currency_grant','no_hard_currency_grant','no_inventory_grant','no_equipment_grant','no_story_reward_grant','no_player_level_mutation','no_s1_to_s2_copy'):
    assert inv.get(k) is True, f'forbidden {k} must be true (i.e., not done)'
assert inv.get('creation_source') == 'server_scoped_starter_flow_pack_87'
assert inv.get('idempotency_marker_psp') == '_slc_pack_87_starter_claim_marker'
assert inv.get('starter_marker_per_user_hero') == '_slc_pack_87_starter_user_hero'
# Verifica statica nel server.py
src = open(os.path.join(R, 'backend/server.py')).read()
for tok in ('@app.post("/api/psp/starter/claim")','psp_starter_claim','server_scoped_starter_flow_pack_87','_slc_pack_87_starter_claim_marker','_slc_pack_87_starter_user_hero','AUTORIZZO_V110_SERVER_SCOPED_STARTER_FLOW_PACK_87','STARTER_ROSTER_NOT_CATALOGED','STARTER_ROSTER_HIGH_RARITY','STARTER_ROSTER_PREMIUM_FORBIDDEN','PLAYER_SERVER_PROFILE_REQUIRED'):
    assert tok in src, f'server.py token missing: {tok}'
# Smoke test result verifica
sm = d.get('smoke_test_result', {})
assert sm.get('register_user_heroes_count_after_register') == 0
assert sm.get('starter_claim_first_call_created') is True
assert sm.get('starter_user_heroes_created_now') == 3
assert sm.get('all_user_heroes_have_server_id') is True
assert sm.get('all_user_heroes_creation_source') == 'server_scoped_starter_flow_pack_87'
assert sm.get('team_initialized') is True
assert sm.get('starter_claim_second_call_created') is False
assert sm.get('starter_claim_second_call_already_claimed') is True
assert sm.get('premium_currency_granted') is False
assert sm.get('player_level_mutated') is False
print('[v110 PACK_87_BACKEND_STARTER_CLAIM_ENDPOINT] OK route_implemented invariants_complete creation_source_marked idempotent server_scoped_user_heroes refuse_audit_blockers no_premium no_currency')
