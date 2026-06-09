#!/usr/bin/env python3
import os, json
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, 'data/design/v110_pack_95_reward_ledger_story_write_legacy_guards/v110_pack_95_frontend_consumer_guard_v1.json')))
assert d.get('no_false_success_on_blocker') is True
assert d.get('no_silent_s1_for_server_bound_paths') is True
sb = d.get('story_battle_frontend_consumer') or {}
assert sb.get('frontend_unlock_strict_promotion_in_pack_95') is False
print('[v110 PACK_95_FRONTEND_CONSUMER_GUARD] OK no_false_success no_silent_s1 frontend_promotion_deferred')
