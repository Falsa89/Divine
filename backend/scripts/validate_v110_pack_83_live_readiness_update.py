#!/usr/bin/env python3
# Pack 83 - Track L: live readiness update.
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_psp_normalization_preflight/v110_psp_normalization_preflight_summary_v1.json')
d = json.load(open(S))
lr = d.get('live_readiness_update', {})
assert lr.get('physical_normalization_ready') is True, 'preflight green -> physical_normalization_ready=true'
assert lr.get('physical_normalization_executed') is False
assert lr.get('dual_read_compat_active') is True
for k in ('reward_live','progress_live','legacy_cleanup_executed','release_readiness_claimed'):
    assert lr.get(k) is False, f'{k} must be false'
print('[v110 PACK_83_LIVE_READINESS_UPDATE] OK normalization_ready=true executed=false dual_read=active reward/progress live=false release_readiness=false')
