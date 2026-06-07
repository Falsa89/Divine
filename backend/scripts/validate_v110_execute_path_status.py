#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(R, "data/design/v110_psp_apply_staging_execute/v110_execute_path_status_v1.json")))
assert d.get("execute_path_enabled_safely") is True
assert d.get("hard_stop_in_original_pack71_script_intact") is True, "pack71 hard-stop MUST remain intact"
assert d.get("original_apply_script_unchanged")
guards = d.get("hard_guards_in_new_script", [])
assert len(guards) >= 5, f"new script must have at least 5 hard guards, got {len(guards)}"
for k in ("production_apply_path_unlocked", "hard_stop_pack71_modified", "fake_PASS"):
    assert d.get("safety_flags", {}).get(k) is False
print(f"[v110 EXECUTE_PATH_STATUS] OK hard_guards={len(guards)} pack71_hard_stop_intact=true")
