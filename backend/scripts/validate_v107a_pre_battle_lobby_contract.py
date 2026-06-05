#!/usr/bin/env python3
"""v107A — Pre-battle-lobby contract producer validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'battle_launch', 'v107a_pre_battle_lobby_contract_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
if d.get('status') != 'CONTRACT_PRODUCER_HELPER_INTRODUCED': print('FAIL \u2014 status wrong'); sys.exit(1)
helper = os.path.join(ROOT, d.get('helper_module',''))
if not os.path.isfile(helper): print(f'FAIL \u2014 helper file missing: {helper}'); sys.exit(1)
content = open(helper, 'r', encoding='utf-8').read()
for token in ('buildLaunchContext','validateLaunchContext','BattleLaunchContractV1','server_id_required','idempotency_key_required_for_live_gated_or_live'):
    if token not in content: print(f'FAIL \u2014 helper missing token: {token}'); sys.exit(1)
fields = set(d.get('contract_v1_fields_supported') or [])
required_fields = {'server_id','mode','encounter_id','player_team_snapshot','enemy_source_type','enemy_source_id','reward_policy','progress_policy','battle_engine_mode','idempotency_key'}
missing = required_fields - fields
if missing: print(f'FAIL \u2014 contract fields missing {missing}'); sys.exit(1)
def_vals = d.get('default_field_values') or {}
if def_vals.get('reward_policy') != 'preview': print('FAIL \u2014 default reward_policy must be preview'); sys.exit(1)
if def_vals.get('progress_policy') != 'preview': print('FAIL \u2014 default progress_policy must be preview'); sys.exit(1)
if def_vals.get('battle_engine_mode') != 'preview': print('FAIL \u2014 default battle_engine_mode must be preview'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('new_player_facing_feature','combat_tsx_changes','fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
print('PASS \u2014 v107A pre-battle-lobby contract producer (helper introduced, contract v1 supported)')
sys.exit(0)
