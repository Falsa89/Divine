#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_97_daily_login_claim_frontend_unlock/v110_pack_97_kill_switch_and_flags_v1.json')))
assert d['global_kill_switch_default'] is False
assert d['daily_kill_switch_default'] is False
assert d['and_logic_required'] is True
assert d['smoke_lifecycle']['verified_in_smoke'] is True
assert d['frontend_ui_flag_default'] == 'false'
print('[v110 PACK_97_KILL_SWITCH_AND_FLAGS] OK both_default_off AND_logic frontend_default_off lifecycle_verified')
