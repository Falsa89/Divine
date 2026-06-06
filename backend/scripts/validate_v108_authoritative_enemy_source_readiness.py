#!/usr/bin/env python3
import json,os,sys
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(ROOT,"data","design","authoritative_live_preconditions","v108_authoritative_enemy_source_readiness_v1.json")))
modes=d.get("per_mode",[])
assert len(modes)>=5
for m in modes:
    assert m.get("random_placeholder_player_facing") is False, f"mode {m.get('mode')} has random/placeholder player-facing"
assert d.get("placeholder_alpha_player_facing_modes")==[]
assert d.get("random_generate_enemy_player_facing_modes")==[]
assert d.get("boss_schema_ready") is True
assert d.get("live_ready") is False
for k in ("random_enemy_player_facing","placeholder_alpha_enemy_player_facing","fake_PASS","validator_weakening","release_readiness_claimed"):
    assert d.get("safety_flags",{}).get(k) is False
print("[v108_AUTHORITATIVE_ENEMY_SOURCE_READINESS] OK modes>=5 no_random_no_placeholder live_ready=false")
sys.exit(0)
