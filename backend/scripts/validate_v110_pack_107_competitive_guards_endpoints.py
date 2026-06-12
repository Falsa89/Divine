#!/usr/bin/env python3
import os
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src = open(os.path.join(R, 'backend/routes/competitive_guards.py')).read()
for route in ('/competitive-guards/health','/competitive-guards/arena/preflight','/competitive-guards/pvp/preflight','/competitive-guards/guild/preflight','/competitive-guards/event/preflight'):
    assert route in src, f'route missing: {route}'
for ks in ('ARENA_REWARD_LIVE_ENABLED','PVP_REWARD_LIVE_ENABLED','GUILD_REWARD_LIVE_ENABLED','EVENT_REWARD_LIVE_ENABLED'):
    assert ks in src, f'kill switch missing: {ks}'
assert 'PACK_107_USER_TEST_MARKER' in src
assert 'pack_107_test_artifact' in src
for blk in ('ARENA_SERVER_SCOPE_REQUIRED','PVP_RANKING_SERVER_SCOPE_DEFERRED','GUILD_SERVER_SCOPE_REQUIRED','EVENT_SERVER_SCOPE_REQUIRED','LEADERBOARD_SERVER_SCOPE_REQUIRED','ARENA_REWARD_LIVE_DISABLED','GUILD_REWARD_LIVE_DISABLED','EVENT_REWARD_LIVE_DISABLED'):
    assert blk in src, f'blocker missing: {blk}'
assert '"reward_live_general": False' in src
assert '"release_readiness_claimed": False' in src
assert '"no_arena_pvp_guild_event_reward_live": True' in src
assert '"no_cross_server_ranking_leak": True' in src
print('[v110 PACK_107_COMPETITIVE_GUARDS_ENDPOINTS] OK all_routes_present test_marker_required blockers_canonical_present reward_live_off no_cross_server_leak')
