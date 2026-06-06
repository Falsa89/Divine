#!/usr/bin/env python3
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, "data", "design", "authoritative_runtime", "v108_authoritative_runtime_idempotency_ledger_dryrun_contract_v1.json")
d = json.load(open(P))
idem = d.get("idempotency", {})
assert idem.get("key_field_in_request") == "idempotency_key"
assert idem.get("key_field_in_result_envelope") == "idempotency_key"
assert idem.get("required_in_staging") is False
assert idem.get("required_when_reward_live_or_progress_live") is True
led = d.get("ledger", {})
assert led.get("writes_in_this_pack") == 0
assert led.get("db_collections_touched") == []
rl = d.get("reward_progress_live_block_in_staging", {})
assert rl.get("reward_live", {}).get("http") == 423
assert rl.get("reward_live", {}).get("code") == "BATTLE_RESULT_REWARD_LIVE_FORBIDDEN"
assert rl.get("progress_live", {}).get("code") == "BATTLE_RESULT_PROGRESS_LIVE_FORBIDDEN"
print("[v108_AUTHORITATIVE_RUNTIME IDEMPOTENCY_LEDGER_DRYRUN] OK ledger_writes=0 idempotency_future_required")
sys.exit(0)
