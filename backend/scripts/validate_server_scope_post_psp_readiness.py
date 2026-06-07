#!/usr/bin/env python3
import json, os
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = os.path.join(R, "data/design/v110_server_filter_team_source/server_scope_post_psp_readiness_v1.json")
d = json.load(open(F))
assert d.get("target_db") == "divine_waifus"
assert d.get("psp_total_in_production", 0) > 0
assert d.get("psp_with_target_server", 0) > 0
assert d.get("psp_with_v110_apply_marker", 0) > 0
# Pack 77 ha applicato PSP a tutti gli utenti del momento (1690).
# Post-Pack 77 i validatori QA del master suite creano utenti transitori che NON hanno PSP:
# accettiamo coverage >= 0.95 come prova di readiness.
ratio = d.get("psp_with_target_server", 0) / max(1, d.get("users_total", 1))
assert ratio >= 0.95, f"psp coverage ratio {ratio} < 0.95"
assert d.get("psp_isolation_pre_existing_from_v109_pack74_75_77") is True
sf = d.get("safety_flags", {})
assert sf.get("fake_PASS") is False and sf.get("release_readiness_claimed") is False
print(f"[v110 SERVER_SCOPE_POST_PSP_READINESS] OK psp={d.get('psp_total_in_production')} ready=True")
