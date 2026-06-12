#!/usr/bin/env python3
import os, json
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
path = os.path.join(R, 'data/design/v110_pack_107_arena_pvp_guild_events_server_scope_guards/v110_pack_107_runtime_smoke_e2e_result_v1.json')
assert os.path.exists(path), 'pack 107 smoke result missing'
d = json.load(open(path))
assert d['real_smoke_executed'] is True, f'smoke not green: {d.get("required_missing")}'
assert d['arena_server_scope_ready'] is True
assert d['pvp_server_scope_ready'] is True
assert d['guild_server_scope_audit_honest_blocker'] is True
assert d['event_server_scope_ready'] is True
assert d['rewards_state_all_deferred_ledger_gated_off'] is True
assert d['s1_s2_isolation_verified'] is True
assert d['no_users_gold_gems_experience_mutation'] is True
assert d['no_arena_pvp_guild_event_battlepass_afk_reward_live'] is True
assert d['no_reward_live_general'] is True
assert d['release_readiness_claimed'] is False
for required in ('health_default_off','arena_pvp_guild_event_preflight_ok','server_id_required','s1_s2_isolated_preflight','guild_legacy_audit_honest','no_battlepass_event_afk_pvp_guild_arena_routes','users_invariant','pack_91_106_preserved'):
    assert d['proofs'].get(required) is True, f'missing proof: {required}'
print('[v110 PACK_107_RUNTIME_SMOKE_E2E] OK arena_pvp_event_ready guild_audit_honest rewards_deferred S1_S2_isolated no_users_mutation pack_91_106_preserved')
