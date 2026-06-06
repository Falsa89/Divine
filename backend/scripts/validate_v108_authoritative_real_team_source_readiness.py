#!/usr/bin/env python3
import json,os,sys
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d=json.load(open(os.path.join(ROOT,"data","design","authoritative_live_preconditions","v108_authoritative_real_team_source_readiness_v1.json")))
assert d.get("full_6_slot_team_supported") is True
assert d.get("team_server_scoped") is False
assert d.get("heroes_canonical_and_belong_to_account") is True
assert d.get("legacy_heroes_can_leak_into_team") is False
assert d.get("server_id_filter_actually_applied_on_team_load") is False
assert d.get("forbidden_markers_used_anywhere_as_real") is False
assert d.get("live_ready") is False
for k in ("fake_team_as_real","runtime_team_migration","fake_PASS","validator_weakening","release_readiness_claimed"):
    assert d.get("safety_flags",{}).get(k) is False
print("[v108_AUTHORITATIVE_REAL_TEAM_SOURCE_READINESS] OK live_ready=false reasons_documented")
sys.exit(0)
