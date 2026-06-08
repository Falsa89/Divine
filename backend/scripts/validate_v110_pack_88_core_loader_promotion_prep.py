#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_88_team_formation_strict_server_scope/v110_pack_88_core_loader_promotion_prep_v1.json')))
assert d.get('prep_only_no_runtime_promotion') is True
assert d.get('explicit_no_false_readiness') is True
assert d.get('explicit_no_filter_applied_emitted_in_this_pack') is True
assert d.get('explicit_no_schema_migration_in_this_pack') is True
assert d.get('explicit_no_runtime_writes_in_this_pack') is True
loaders = d.get('loaders', [])
expected = {'/api/inventory','/api/currencies','/api/story/progress','/api/user/equipment'}
found = {l.get('loader') for l in loaders}
assert expected.issubset(found), f'missing loaders: {expected-found}'
for l in loaders:
    assert l.get('runtime_promoted_in_this_pack') is False, f"loader {l.get('loader')} runtime_promoted_in_this_pack must be false"
    blocks = l.get('blockers_for_psp_scope', [])
    assert isinstance(blocks, list) and len(blocks) >= 2, f'{l.get("loader")} blockers list must be documented'
    assert l.get('staged_plan') or l.get('backup_rollback'), 'staged_plan or backup_rollback required per loader'
print('[v110 PACK_88_CORE_LOADER_PROMOTION_PREP] OK 4_loaders_documented_no_runtime_promotion no_false_readiness no_schema_migration no_filter_applied_emitted')
