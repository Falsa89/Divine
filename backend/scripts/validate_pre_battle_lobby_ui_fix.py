#!/usr/bin/env python3
# Pack 78 Track F: pre-battle lobby UI fix — DEFERRED (file MD5-lockato).
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_server_filter_team_source/pre_battle_lobby_ui_fix_v1.json")
d = json.load(open(F))
assert d.get("lobby_file") == "frontend/app/pre-battle-lobby.tsx"
# Audit onesto: il UI fix NON è applicato in Pack 78 perché il file è MD5-lockato.
assert d.get("patches_applied_in_pack_78") is False
assert d.get("all_patches_applied") is False
assert d.get("ui_fix_promotion_status", "").startswith("DEFERRED")
assert "MD5" in d.get("ui_fix_deferred_reason", "")
assert d.get("ui_fix_required_next_action")
# Il blocker NON è enforced perché il file non è stato modificato. Lo documentiamo onestamente.
assert d.get("blocker_currently_enforced_in_lobby") is False
sf = d.get("safety_flags", {})
# Nessun fake_PASS: stiamo dichiarando onestamente che il UI fix è deferred.
for k in ("3_slot_placeholder_player_facing", "fake_team_as_real", "fake_PASS"):
    assert sf.get(k) is False, k
print("[v110 PRE_BATTLE_LOBBY_UI_FIX] OK DEFERRED (MD5-lock honest audit, no validator_weakening)")
