#!/usr/bin/env python3
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sot = os.path.join(R, 'docs/divine/110_ARENA_PVP_GUILD_EVENTS_SERVER_SCOPE_GUARDS_SOT.md')
assert os.path.exists(sot)
src = open(sot).read()
for kw in ('arena','pvp','guild','event','ARENA_SERVER_SCOPE_REQUIRED','PVP_RANKING_SERVER_SCOPE_DEFERRED','GUILD_SERVER_SCOPE_REQUIRED','EVENT_SERVER_SCOPE_REQUIRED','LEADERBOARD_SERVER_SCOPE_REQUIRED','ARENA_REWARD_LIVE_DISABLED','GUILD_REWARD_LIVE_DISABLED','EVENT_REWARD_LIVE_DISABLED','reward_live_general=false','release_readiness_claimed=false','AUDIT_LEGACY_NOT_SERVER_SCOPED','READY_GATED_REWARDS_DEFERRED'):
    assert kw in src, f'SOT missing: {kw}'
print('[v110 PACK_107_SOT] OK doc_present_all_canonical_keywords_present')
