#!/usr/bin/env python3
import os, json, re
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_92_core_server_scope/v110_pack_92_frontend_server_id_sweep_v1.json')))
assert d.get('sweep_completed') is True
assert d.get('inventory_pack_91_caveat_resolved') is True
assert d.get('silent_s1_fallback') is False
assert d.get('account_wide_fallback_for_server_bound_data') is False
for f in d.get('frontend_files_migrated', []):
    fp = os.path.join(R, f); assert os.path.exists(fp), f
    src = open(fp).read()
    assert 'useServerScope' in src, f'no useServerScope in {f}'
    assert 'selected_server_id' in src, f'no selected_server_id in {f}'
    # Each migrated file must include at least one server_id query string
    assert 'server_id=' in src, f'no server_id query in {f}'
print(f'[v110 PACK_92_FRONTEND_SERVER_ID_SWEEP] OK files_migrated={len(d["frontend_files_migrated"])} sweep_completed no_silent_s1')
