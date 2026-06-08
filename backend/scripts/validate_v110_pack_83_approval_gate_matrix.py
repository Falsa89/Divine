#!/usr/bin/env python3
# Pack 83 - Track H: approval gate matrix.
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
m = json.load(open(os.path.join(R, 'data/design/v110_psp_normalization_preflight/v110_psp_normalization_approval_gate_matrix_v1.json')))
assert m.get('current_approval_present') is False
assert m.get('execute_allowed') is False
assert m.get('physical_normalization_executed_during_pack_83') is False
assert m.get('production_db_writes_during_pack_83') == 0
flags = m.get('required_future_flags', [])
for must in ('--execute', '--approval-string AUTORIZZO_V110_PSP_USER_ID_PHYSICAL_NORMALIZATION_SU_DIVINE_WAIFUS', '--mapping-hash-pin', '--backup-manifest-hash-pin', '--rollback-plan-pin', '--commit-hash-pin', '--target-db divine_waifus', '--batch-id'):
    assert any(must in f for f in flags), f'required flag missing: {must}'
assert m.get('mapping_hash_pin_expected') == '1fe15c3a8d953bf9c9c9c6c3bbc0a301dba58d1ccbc77ac5f597b9d6d8daf166'
assert m.get('backup_manifest_hash_pin_expected') == 'e12b15aa0e45c3a388310b74b8d24473affde0697282d7f30d8781554986b4a2'
assert m.get('rollback_plan_pin_expected') == '8573794d23492f0315cb3517a3f50733f90d18ff328ed7412b270d0d3c01b293'
cl = m.get('operator_checklist', [])
assert len(cl) >= 8, f'operator_checklist too short: {len(cl)}'
es = m.get('emergency_stop', {})
assert es.get('abort_action', '').startswith('REFUSED')
print('[v110 PACK_83_APPROVAL_GATE_MATRIX] OK current_approval=false execute_allowed=false hashes_pinned operator_checklist>=8 emergency_stop_present')
