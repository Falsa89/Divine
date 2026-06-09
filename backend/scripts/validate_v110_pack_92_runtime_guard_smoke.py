#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(R, 'data/design/v110_pack_92_core_server_scope/v110_pack_92_runtime_guard_smoke_result_v1.json')
assert os.path.exists(p), 'runtime guard smoke result missing — run smoke_v110_pack_92_runtime_guard_e2e.py first'
d = json.load(open(p))
assert d.get('real_smoke_executed') is True
assert d.get('read_only') is True
proofs = d.get('proofs', {})
required = [
    'register_ok','ensure_psp_a_ok','mark_pack_92_ok',
    'wallet_split_real_filter','wallet_unknown_server_blocker_honest','wallet_legacy_path_flagged',
    'story_psp_real_filter','story_unknown_server_blocker_honest','story_legacy_path_flagged',
    'equipment_honest_deferred_blocker','equipment_legacy_path_flagged',
    'pack_91_inventory_preserved','pack_90_buy_strict_preserved',
    'user_heroes_strict_psp','cleanup_ok',
]
for k in required:
    assert proofs.get(k) is True, f'proof {k} missing/false: {proofs.get(k)}'
assert d.get('test_artifact_marker') == 'pack_92_test_artifact'
print('[v110 PACK_92_RUNTIME_GUARD_SMOKE] OK loader_guards_safe wallet_split_real story_psp_real equipment_deferred_blocker pack_91_preserved cleanup_executed')
