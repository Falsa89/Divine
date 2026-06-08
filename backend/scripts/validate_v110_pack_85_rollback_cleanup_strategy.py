#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_85_psp_onboarding/v110_pack_85_psp_onboarding_summary_v1.json')))
rb = d.get('rollback_cleanup_strategy', {})
assert '_slc_psp_created_by_pack' in rb.get('fresh_start_psp_identifiable_via', '')
assert 'v110_pack_85_psp_onboarding_new_server_fresh_start' in rb.get('fresh_start_psp_identifiable_via', '')
assert rb.get('safe_to_keep_in_production') is True
assert rb.get('no_data_loss_risk') is True
print('[v110 PACK_85_ROLLBACK_CLEANUP_STRATEGY] OK fresh_start_psp_identifiable_via_marker safe_to_keep no_data_loss_risk')
