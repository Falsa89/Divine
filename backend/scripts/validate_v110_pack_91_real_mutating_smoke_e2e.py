#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
p = os.path.join(R, 'data/design/v110_pack_91_inventory_frontend_consumer_and_smoke/v110_pack_91_real_mutating_smoke_e2e_result_v1.json')
assert os.path.exists(p), 'real mutating smoke result missing — run smoke_v110_pack_91_inventory_mutating_e2e.py first'
d = json.load(open(p))
assert d.get('real_mutating_smoke_executed') is True, d
proofs = d.get('proofs', {})
required = [
    'register_ok','server_id_required_on_buy','psp_required_on_buy',
    'ensure_psp_a_ok','ensure_psp_b_ok','mark_pack_91_ok',
    'buy_on_a_ok','inventory_a_sees_item','inventory_b_no_leak',
    'use_exp_b_blocked_no_item','cleanup_ok',
]
for k in required:
    assert proofs.get(k) is True, f'proof {k} missing/false: {proofs.get(k)}'
assert d.get('test_artifact_marker') == 'pack_91_test_artifact'
assert str(d.get('test_user_email_pattern','')).startswith('pack91_test_user_')
print('[v110 PACK_91_REAL_MUTATING_SMOKE_E2E] OK real_mutating_smoke_executed buy_on_a_ok no_leak_on_b cleanup_executed marked_test_artifacts_only')
