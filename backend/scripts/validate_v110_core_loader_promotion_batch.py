#!/usr/bin/env python3
# Pack 80 — Track F: core loader promotion batch (PROMOTED solo se filtrato realmente).
import os, json, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = os.path.join(R, 'data/design/v110_pack_80_lobby_fetch/v110_pack_80_lobby_fetch_summary_v1.json')
d = json.load(open(S))
b = d.get('core_loader_promotion_batch', {})
assert b, 'core_loader_promotion_batch missing'
# team_formation: PROMOSSO
tf = b.get('team_formation', {})
assert tf.get('filter_applied') is True, 'team_formation must be filter_applied=true'
assert tf.get('promotion_status') == 'PROMOTED_REAL_FILTER_APPLIED'
# user_heroes/inventory/currencies/story_progress: DEFERRED honestly
for k in ('user_heroes', 'inventory', 'currencies', 'story_progress'):
    sub = b.get(k, {})
    assert sub.get('filter_applied') is False, f'{k} must declare filter_applied=false (DEFERRED honest)'
    assert (sub.get('promotion_status') or '').startswith('DEFERRED'), f'{k} promotion_status must start with DEFERRED'
    assert 'reason' in sub and sub['reason'], f'{k} missing deferral reason'
assert b.get('false_filter_applied_true_emitted_anywhere') is False
print('[v110 CORE_LOADER_PROMOTION_BATCH] OK team_formation=PROMOTED; user_heroes/inventory/currencies/story_progress=DEFERRED honest')
