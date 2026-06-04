#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v85 Track F — Design Drill (kill_switch + rollback_chain) + v86 Gate."""
import json, sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    drill_script = ROOT / "backend/scripts/pve_reward_claim_live_db_canary_apply_design_drill_v1.py"
    if not drill_script.exists(): ERR.append("missing:drill_script")
    else:
        src = drill_script.read_text(encoding="utf-8")
        for pat, label in [
            (r"^\s*import\s+pymongo\b", "pymongo"),
            (r"^\s*from\s+pymongo\b", "pymongo"),
            (r"^\s*import\s+motor\b", "motor"),
            (r"^\s*from\s+motor\b", "motor"),
            (r"^\s*import\s+redis\b", "redis"),
            (r"^\s*from\s+redis\b", "redis"),
            (r"^\s*import\s+battle_engine\b", "battle_engine"),
            (r"^\s*from\s+battle_engine\b", "battle_engine"),
        ]:
            if re.search(pat, src, flags=re.MULTILINE):
                ERR.append(f"drill.forbidden_import:{label}")
        if re.search(r"\bMONGO_URL\b", src): ERR.append("drill.uses_MONGO_URL")
        for needle in ("drill_kill_switch", "drill_rollback_chain", "build_v86_gate"):
            if needle not in src: ERR.append(f"drill.missing_token:{needle}")
    ks = _load(ROOT / "data/design/economy/pve_reward_claim_live_db_canary_apply_kill_switch_drill_result_v1.json")
    rb = _load(ROOT / "data/design/economy/pve_reward_claim_live_db_canary_apply_rollback_chain_drill_result_v1.json")
    rollup = _load(ROOT / "data/design/economy/pve_reward_claim_live_db_canary_apply_drill_rollup_v1.json")
    gate = _load(ROOT / "data/design/economy/pve_reward_claim_v86_gate_v1.json")
    for name, obj in (("ks", ks), ("rb", rb), ("rollup", rollup), ("gate", gate)):
        if obj is None: ERR.append(f"missing:{name}")
    if ks:
        if ks.get("all_engage_window_claims_rejected") is not True: ERR.append("ks.engage_not_reject_all")
        if ks.get("single_approval_disengage_rejected") is not True: ERR.append("ks.single_disengage_not_rejected")
        if ks.get("dual_approval_disengage_allowed") is not True: ERR.append("ks.dual_disengage_not_allowed")
        if ks.get("db_writes") != 0: ERR.append("ks.db_writes_not_0")
        if ks.get("endpoint_implemented") is not False: ERR.append("ks.endpoint_implemented_not_false")
        if ks.get("design_only") is not True: ERR.append("ks.design_only_not_true")
    if rb:
        if rb.get("all_chain_approved") is not True: ERR.append("rb.chain_not_approved")
        if rb.get("all_negatives_halted") is not True: ERR.append("rb.negatives_not_all_halted")
        if rb.get("db_rollback") is not False: ERR.append("rb.db_rollback_not_false")
        if rb.get("db_writes") != 0: ERR.append("rb.db_writes_not_0")
        if rb.get("endpoint_implemented") is not False: ERR.append("rb.endpoint_implemented_not_false")
        if rb.get("design_only") is not True: ERR.append("rb.design_only_not_true")
    if rollup:
        if rollup.get("design_only") is not True: ERR.append("rollup.design_only_not_true")
        if rollup.get("db_writes") != 0: ERR.append("rollup.db_writes_not_0")
        if rollup.get("endpoint_implemented") is not False: ERR.append("rollup.endpoint_implemented_not_false")
    if gate:
        if gate.get("design_drill_pass") is not True: ERR.append("gate.design_drill_pass_not_true")
        if gate.get("live_db_apply_allowed") is not False: ERR.append("gate.live_db_apply_allowed_not_false")
        if gate.get("endpoint_implemented") is not False: ERR.append("gate.endpoint_implemented_not_false")
        if gate.get("db_writes") != 0: ERR.append("gate.db_writes_not_0")
        if gate.get("manual_approval_required_for_future_apply") is not True: ERR.append("gate.manual_approval_not_true")
        if gate.get("checksum_required_for_future_apply") is not True: ERR.append("gate.checksum_not_true")
        if gate.get("step_up_auth_required_for_future_apply") is not True: ERR.append("gate.step_up_not_true")
        if not gate.get("v86_recommendation"): ERR.append("gate.v86_recommendation_missing")
    if ERR:
        print("FAIL pve_reward_claim_live_db_canary_apply_drill:", "; ".join(ERR)); return 1
    print("PASS pve_reward_claim_live_db_canary_apply_drill"); return 0

if __name__ == "__main__": sys.exit(main())
