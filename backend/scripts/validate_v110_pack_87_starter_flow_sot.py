#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Verifica esistenza SOT MD + JSON canon
md = os.path.join(R, 'docs/divine/113_CANON_SERVER_SCOPED_STARTER_FLOW.md')
js = os.path.join(R, 'data/design/v110_pack_87_server_scoped_starter_flow/v110_pack_87_canon_starter_flow_sot_v1.json')
assert os.path.exists(md), f'missing canon MD: {md}'
assert os.path.exists(js), f'missing canon JSON: {js}'
md_src = open(md).read()
for tok in ('Server-Scoped', 'AUTORIZZO_V110_SERVER_SCOPED_STARTER_FLOW_PACK_87', 'claim_once_per_server', 'No account-wide', 'no premium', 'No S1\u2192S2 copy'.replace('\u2192','→'), 'level 1'):
    assert tok.lower() in md_src.lower(), f'canon MD missing token: {tok}'
d = json.load(open(js))
assert d.get('canonical_decision','').lower().find('server-scoped') >= 0
ss = d.get('starter_set', {})
assert ss.get('server_scoped') is True
assert ss.get('claim_once_per_server') is True
assert ss.get('premium') is False
assert ss.get('no_equipment') is True
assert ss.get('no_currency') is True
assert ss.get('no_inventory_reward') is True
assert ss.get('no_story_reward') is True
assert ss.get('no_player_level_mutation') is True
assert ss.get('no_s1_to_s2_copy') is True
assert ss.get('team_init_only_if_empty') is True
hero_ids = ss.get('hero_ids', [])
assert len(hero_ids) == 3, f'starter set must have 3 heroes, got {len(hero_ids)}'
for h in hero_ids:
    assert h.get('initial_level') == 1
    assert h.get('initial_exp') == 0
    assert h.get('premium') is False
forb = d.get('forbidden', {})
for k in ('account_wide_starter','premium_or_borea_or_5star_or_6star','hard_premium_currency','inventory_equipment_story_reward','player_level_mutation','copy_s1_to_s2','overwrite_existing_team','legacy_cleanup','reward_live','progress_live','release_readiness_claim','fake_PASS','validator_weakening'):
    assert forb.get(k) is True, f'forbidden.{k} must be true'
print('[v110 PACK_87_STARTER_FLOW_SOT] OK canon_md_exists canon_json_starter_set_server_scoped claim_once_per_server forbidden_set_complete')
