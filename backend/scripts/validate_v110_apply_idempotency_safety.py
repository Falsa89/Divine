#!/usr/bin/env python3
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_preflight/v110_apply_idempotency_safety_v1.json")))
idem = d.get("idempotency_strategy", {})
assert idem.get("unique_key") == ["user_id", "server_id"]
assert idem.get("upsert_operation") is True
assert idem.get("second_run_inserts_zero_new_psp") is True
assert idem.get("second_run_updates_only_non_destructive_fields") is True
prot = set(idem.get("destructive_fields_protected_on_collision", []))
for f in ("player_level", "player_exp", "soft_currencies", "selected_team_id", "story_progress", "server_created_at", "created_at"):
    assert f in prot, f"destructive field protection {f}"
rr = d.get("re_run_safety", {})
assert rr.get("crash_in_middle_safe") is True
assert rr.get("resume_via_audit_log_marker") is True
assert rr.get("abort_signal_safe") is True
forbid = set(d.get("forbidden_on_rerun", []))
for f in ("duplicate_psp_creation", "player_level_overwrite", "soft_currency_double_grant", "premium_balance_modification"):
    assert f in forbid, f"rerun forbid {f}"
assert d.get("verified_in_this_pack") is False
assert d.get("applied_in_this_pack") is False
assert d.get("db_writes_in_this_pack") == 0
for k in ("duplicate_psp", "premium_grant", "currency_duplication", "fake_PASS"):
    assert d.get("safety_flags", {}).get(k) is False
print("[v110 APPLY_IDEMPOTENCY_SAFETY] OK unique_key=(user_id,server_id) destructive_protected re_run_safe")
