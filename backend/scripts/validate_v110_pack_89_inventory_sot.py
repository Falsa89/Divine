#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_89_inventory_psp_scoped/v110_pack_89_inventory_sot_v1.json')))
for k in ('server_scoped','player_facing_read_strict','player_facing_requires_server_id','no_account_wide_fallback_when_server_id_present','no_copy_s1_to_s2','new_server_starts_empty','onboarding_rewards_not_granted_in_this_pack'):
    assert d.get(k) is True, f'{k} must be true'
print('[v110 PACK_89_INVENTORY_SOT] OK server_scoped player_facing_strict no_account_wide_fallback no_copy_s1_to_s2 onboarding_rewards_not_granted')
