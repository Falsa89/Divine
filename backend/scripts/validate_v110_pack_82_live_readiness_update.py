#!/usr/bin/env python3
# Pack 82 - Track 8: live readiness update.
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_pack_82_psp_dual_read_compat/v110_pack_82_psp_dual_read_compat_summary_v1.json')
d = json.load(open(S))
lr = d.get('live_readiness_update', {})
for k in ('reward_live','progress_live','ledger_live','battle_engine_authoritative_live','release_readiness_claimed'):
    assert lr.get(k) is False, f'{k} must be false'
print('[v110 PACK_82_LIVE_READINESS_UPDATE] OK reward_live=false progress_live=false ledger_live=false release_readiness=false')
