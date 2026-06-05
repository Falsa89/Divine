#!/usr/bin/env python3
"""v107A — Frontend loader server_id propagation validator."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(ROOT, 'data', 'design', 'server_scope', 'v107a_frontend_loader_server_id_propagation_result_v1.json')
if not os.path.isfile(p): print('FAIL \u2014 file missing'); sys.exit(1)
d = json.load(open(p, 'r', encoding='utf-8'))
hook = os.path.join(ROOT, 'frontend', 'src', 'hooks', 'useServerScope.ts')
if not os.path.isfile(hook): print('FAIL \u2014 useServerScope.ts missing'); sys.exit(1)
helper = os.path.join(ROOT, 'frontend', 'src', 'battle_launch', 'buildLaunchContext.ts')
if not os.path.isfile(helper): print('FAIL \u2014 buildLaunchContext.ts missing'); sys.exit(1)
if d.get('adoption_status') != 'HELPER_AVAILABLE_LOADERS_NOT_YET_PROPAGATING': print('FAIL \u2014 adoption_status wrong'); sys.exit(1)
if len(d.get('loaders_should_propagate_server_id') or []) < 10: print('FAIL \u2014 loaders_should_propagate < 10'); sys.exit(1)
if not d.get('banner_obligation_active', False): print('FAIL \u2014 banner_obligation_active must be true'); sys.exit(1)
if d.get('banner_token') != 'SERVER_DATA_ISOLATION_BACKEND_PENDING': print('FAIL \u2014 banner_token wrong'); sys.exit(1)
saf = d.get('safety') or {}
for k in ('new_player_facing_feature','combat_tsx_changes','fake_PASS','validator_weakening'):
    if saf.get(k, True): print(f'FAIL \u2014 safety.{k} must be false'); sys.exit(1)
print('PASS \u2014 v107A frontend loader server_id propagation (hook + helper present, banner obligation active)')
sys.exit(0)
