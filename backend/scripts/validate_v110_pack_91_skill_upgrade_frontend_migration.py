#!/usr/bin/env python3
import os, json, subprocess
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_91_inventory_frontend_consumer_and_smoke/v110_pack_91_skill_upgrade_frontend_migration_v1.json')))
assert d.get('runtime_frontend_caller_present') is False
assert d.get('deferred') is True
# Static guarantee: NO frontend caller exists for skill upgrade endpoints
fe_root = os.path.join(R, 'frontend')
found = []
for dp, _, files in os.walk(fe_root):
    if 'node_modules' in dp: continue
    for fn in files:
        if not fn.endswith(('.ts','.tsx','.js','.jsx')): continue
        try:
            txt = open(os.path.join(dp,fn)).read()
        except Exception:
            continue
        if '/api/hero/skill-upgrade' in txt or '/api/hero/skills-upgrade' in txt:
            found.append(os.path.join(dp,fn))
assert not found, f'unexpected skill-upgrade frontend caller(s) present: {found}'
print('[v110 PACK_91_SKILL_UPGRADE_FRONTEND_MIGRATION] OK no_runtime_caller honest_documentation backend_ready_for_future_consumer')
