#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v85 Track E — Step-Up Auth + Endpoint Stub + Rate Limit (design-only)."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    s = _load(ROOT / "data/design/economy/pve_reward_claim_live_db_canary_apply_step_up_auth_endpoint_stub_v1.json")
    if s is None:
        ERR.append("missing:stub"); print("FAIL pve_reward_claim_live_db_canary_apply_step_up_auth_endpoint_stub:", "; ".join(ERR)); return 1
    if s.get("design_only") is not True: ERR.append("design_only_not_true")
    if s.get("endpoint_implemented") is not False: ERR.append("endpoint_implemented_not_false")
    if s.get("db_writes") != 0: ERR.append("db_writes_not_0")
    if s.get("backend_routes_changed") is not False: ERR.append("backend_routes_changed_not_false")
    sua = s.get("step_up_auth", {})
    factors = set(sua.get("factors_required", []))
    if not {"hardware_token", "passkey"}.issubset(factors):
        ERR.append("step_up.factors_insufficient")
    if sua.get("min_factor_count", 0) < 2: ERR.append("step_up.min_factor_count_lt_2")
    if sua.get("server_signed_challenge_required") is not True: ERR.append("step_up.server_signed_not_true")
    if sua.get("deny_anonymous") is not True: ERR.append("step_up.deny_anonymous_not_true")
    if sua.get("deny_single_factor") is not True: ERR.append("step_up.deny_single_factor_not_true")
    if sua.get("deny_replay_within_window") is not True: ERR.append("step_up.deny_replay_not_true")
    ep = s.get("endpoint_stub", {})
    if ep.get("status") != "DESIGN_ONLY_NOT_IMPLEMENTED": ERR.append("endpoint.status_not_design_only")
    if ep.get("hard_block_outside_design") is not True: ERR.append("endpoint.hard_block_outside_design_not_true")
    if len(ep.get("reject_reason_codes", [])) < 8: ERR.append("endpoint.reject_reason_codes_too_few")
    rl = s.get("rate_limit_design", {})
    if rl.get("window_seconds") != 60: ERR.append("rate_limit.window_invalid")
    if rl.get("max_global_attempts", 99) > 10: ERR.append("rate_limit.max_global_attempts_too_high")
    if rl.get("on_breach") != "reject_rate_limited": ERR.append("rate_limit.on_breach_invalid")
    # Cross check con server.py: NESSUNA presenza dell'endpoint stub
    server_py = ROOT / "backend/server.py"
    if server_py.exists():
        src = server_py.read_text(encoding="utf-8")
        if "/api/pve/reward/canary-apply" in src:
            ERR.append("server_py.contains_canary_apply_route")
    if ERR:
        print("FAIL pve_reward_claim_live_db_canary_apply_step_up_auth_endpoint_stub:", "; ".join(ERR)); return 1
    print("PASS pve_reward_claim_live_db_canary_apply_step_up_auth_endpoint_stub"); return 0

if __name__ == "__main__": sys.exit(main())
