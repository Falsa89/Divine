#!/usr/bin/env python3
# Pack 81 - Track 8: story progress loader scoping (honest deferral).
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_pack_81_user_heroes_server_scope/v110_pack_81_user_heroes_server_scope_summary_v1.json')
d = json.load(open(S))
sp = d.get('core_loader_promotion_batch', {}).get('story_progress', {})
assert sp.get('filter_applied') is False
assert sp.get('promotion_status', '').startswith('DEFERRED')
assert 'reason' in sp and sp['reason']
print('[v110 PACK_81_STORY_PROGRESS_LOADER_SCOPING] OK story_progress=DEFERRED honest reason_documented')
