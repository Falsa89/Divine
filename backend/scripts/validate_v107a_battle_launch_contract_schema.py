#!/usr/bin/env python3
"""v107A — Battle Launch Contract schema validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'battle_launch', 'battle_launch_contract_schema_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
req = set(d.get('required') or [])
required_min = {'server_id','mode','encounter_id','enemy_source_type','enemy_source_id','reward_policy','progress_policy','battle_engine_mode'}
missing = required_min - req
if missing: print(f'FAIL \u2014 required missing {missing}'); sys.exit(1)
props = d.get('properties') or {}
mode_enum = (props.get('mode') or {}).get('enum') or []
for m in ('story','tower','arena','training','boss','raid','event','guild_war','guild_raid','world_boss'):
    if m not in mode_enum: print(f'FAIL \u2014 mode enum missing {m}'); sys.exit(1)
es_enum = (props.get('enemy_source_type') or {}).get('enum') or []
for e in ('authored','player_team','bot_team','boss','training_preset','event_preset'):
    if e not in es_enum: print(f'FAIL \u2014 enemy_source enum missing {e}'); sys.exit(1)
for key in ('reward_policy','progress_policy'):
    pol = (props.get(key) or {}).get('enum') or []
    for v in ('none','preview','live_gated','live'):
        if v not in pol: print(f'FAIL \u2014 {key} enum missing {v}'); sys.exit(1)
em = (props.get('battle_engine_mode') or {}).get('enum') or []
for v in ('preview','authoritative'):
    if v not in em: print(f'FAIL \u2014 battle_engine_mode enum missing {v}'); sys.exit(1)
if len(d.get('validation_rules') or []) < 3: print('FAIL \u2014 validation_rules < 3'); sys.exit(1)
if len(d.get('feature_flag_coercions') or {}) < 3: print('FAIL \u2014 feature_flag_coercions < 3'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('no_db_writes_in_v107a','no_reward_grant','no_progress_write'):
    if not saf.get(k, False): print(f'FAIL \u2014 safety.{k} must be true'); sys.exit(1)
for k in ('fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
print('PASS \u2014 v107A battle launch contract schema (10 modes, 6 enemy sources, 4 reward/progress, 2 engine modes)')
sys.exit(0)
