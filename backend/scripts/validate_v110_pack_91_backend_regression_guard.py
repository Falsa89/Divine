#!/usr/bin/env python3
import os, json, hashlib
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_91_inventory_frontend_consumer_and_smoke/v110_pack_91_backend_regression_guard_v1.json')))
assert d.get('backend_items_py_md5_unchanged') is True
assert d.get('hardcoded_s1_in_writes') is False
assert d.get('false_filter_applied_true') is False
assert d.get('server_id_required_on_writes') is True
for k in ('pack_89_get_inventory_strict_preserved','pack_90_buy_strict_preserved','pack_90_use_exp_strict_preserved','pack_90_skill_upgrade_strict_preserved'):
    assert d.get(k) is True, k
m = hashlib.md5(open(os.path.join(R, 'backend/routes/items.py'),'rb').read()).hexdigest()
assert m == d.get('backend_items_py_md5'), f'items.py md5 drift: {m}'
print(f'[v110 PACK_91_BACKEND_REGRESSION_GUARD] OK items.py_md5={m[:12]} pack_89_90_preserved no_hardcoded_s1 server_id_required_on_writes')
