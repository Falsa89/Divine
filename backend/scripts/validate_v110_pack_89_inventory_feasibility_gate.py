#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_89_inventory_psp_scoped/v110_pack_89_inventory_feasibility_gate_v1.json')))
assert d.get('feasibility_decision') == 'PROMOTE_RUNTIME'
c = d.get('feasibility_criteria', {})
for k in ('schema_already_has_server_id','no_migration_needed','no_backfill_needed','no_db_writes_required_in_promotion','smoke_e2e_runtime_verified_strict_server_scope','smoke_e2e_runtime_verified_no_account_wide_leak','smoke_e2e_runtime_verified_filter_applied_true_only_in_strict_path'):
    assert c.get(k) is True
print('[v110 PACK_89_INVENTORY_FEASIBILITY_GATE] OK feasibility_decision=PROMOTE_RUNTIME criteria_complete')
