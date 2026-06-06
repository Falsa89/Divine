#!/usr/bin/env python3
"""v108_AUTHORITATIVE_PRE - Track H reward/progress/idempotency preflight."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "data", "design", "authoritative_pre", "v108_authoritative_pre_reward_progress_idempotency_preflight_v1.json")
d = json.load(open(P))
ff = d.get("feature_flags", {})
for k in ("REWARD_LIVE_ENABLED","PROGRESS_LIVE_ENABLED","BATTLE_LAUNCH_AUTHORITATIVE_ENABLED","SERVER_SCOPED_RUNTIME_ENABLED"):
    assert ff.get(k) is False, f"{k} must be false"
assert d.get("reward_live_endpoint_block", {}).get("block_code") == "BATTLE_INSTANCE_REWARD_LIVE_FORBIDDEN"
assert d.get("progress_live_endpoint_block", {}).get("block_code") == "BATTLE_INSTANCE_PROGRESS_LIVE_FORBIDDEN"
assert d.get("db_writes_observed") == 0
assert d.get("reward_progress_write_attempts_observed") == 0
idem = d.get("idempotency", {})
assert idem.get("required_in_authoritative_pre") is False
assert idem.get("future_required_when_reward_live_or_progress_live_enabled") is True
print("[v108_AUTHORITATIVE_PRE REWARD_PROGRESS_IDEMPOTENCY] OK all_flags_off blocks_defined idempotency_future_documented")
sys.exit(0)
