#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_85_psp_onboarding/v110_pack_85_psp_onboarding_summary_v1.json')))
l = d.get('live_readiness_update', {})
assert l.get('new_server_onboarding_path_live') is True
for k in ('reward_live','progress_live','ledger_live','battle_engine_authoritative_live','release_readiness_claimed'):
    assert l.get(k) is False, f'{k} must be false'
print('[v110 PACK_85_LIVE_READINESS_UPDATE] OK onboarding_path_live=true reward/progress/ledger live=false release_readiness=false')
