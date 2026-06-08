#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_psp_normalization_execute/v110_psp_normalization_execute_summary_v1.json')))
p = d.get('pin_verification', {})
assert p.get('all_pins_match') is True
assert p.get('mapping_hash_pin_match') is True
assert p.get('backup_manifest_hash_pin_match') is True
assert p.get('rollback_plan_pin_match') is True
assert p.get('target_db_match') is True
assert p.get('mapping_hash_pin_passed') == p.get('mapping_hash_pin_expected')
assert p.get('backup_manifest_hash_pin_passed') == p.get('backup_manifest_hash_pin_expected')
assert p.get('rollback_plan_pin_passed') == p.get('rollback_plan_pin_expected')
assert 'v110_psp_user_id_normalization_' in p.get('batch_id_used', '')
print('[v110 PACK_84_PIN_VERIFICATION] OK all_pins_match commit_pinned batch_id_present target_db=divine_waifus')
