#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v85 Track C — Approval Workflow + Checksum Sequence (design-only)."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    wf = _load(ROOT / "data/design/economy/pve_reward_claim_live_db_canary_apply_approval_workflow_v1.json")
    cs = _load(ROOT / "data/design/economy/pve_reward_claim_live_db_canary_apply_checksum_sequence_v1.json")
    for name, obj in (("wf", wf), ("cs", cs)):
        if obj is None: ERR.append(f"missing:{name}")
    if wf:
        if wf.get("design_only") is not True: ERR.append("wf.design_only_not_true")
        if wf.get("dual_human_approval_required") is not True: ERR.append("wf.dual_human_approval_required_not_true")
        if wf.get("checksum_required") is not True: ERR.append("wf.checksum_required_not_true")
        if wf.get("forbid_self_approval") is not True: ERR.append("wf.forbid_self_approval_not_true")
        if wf.get("db_writes") != 0: ERR.append("wf.db_writes_not_0")
        if wf.get("endpoint_implemented") is not False: ERR.append("wf.endpoint_implemented_not_false")
        if wf.get("applies_to_live") is not False: ERR.append("wf.applies_to_live_not_false")
        roles = set(wf.get("approval_roles", []))
        for r in ("release_owner", "security_owner"):
            if r not in roles: ERR.append(f"wf.missing_role:{r}")
        names = {s.get("name") for s in wf.get("steps", [])}
        for req in ("submit_canary_apply_request", "static_validation_md5_invariants",
                    "static_validation_suite_runner_zero_required_fail",
                    "dry_run_simulator_pass", "second_human_approval",
                    "step_up_admin_auth_challenge", "kill_switch_pre_engage_acknowledged",
                    "final_go_decision", "future_pack_required_for_actual_apply"):
            if req not in names: ERR.append(f"wf.missing_step:{req}")
        halts = set(wf.get("halt_conditions", []))
        for req in ("md5_invariants_changed", "suite_required_fail_gt_0",
                    "dry_run_pass_false", "checksum_mismatch",
                    "single_human_only", "step_up_auth_missing",
                    "kill_switch_engaged", "approval_window_expired"):
            if req not in halts: ERR.append(f"wf.missing_halt:{req}")
    if cs:
        if cs.get("design_only") is not True: ERR.append("cs.design_only_not_true")
        if cs.get("checksum_algorithm") != "sha256": ERR.append("cs.checksum_algorithm_not_sha256")
        if cs.get("db_writes") != 0: ERR.append("cs.db_writes_not_0")
        if cs.get("endpoint_implemented") is not False: ERR.append("cs.endpoint_implemented_not_false")
        steps = {s.get("step") for s in cs.get("sequence", [])}
        for req in ("submit", "second_approval", "step_up_auth", "final_go"):
            if req not in steps: ERR.append(f"cs.missing_step:{req}")
        if cs.get("mismatch_action") != "halt": ERR.append("cs.mismatch_action_not_halt")
    if ERR:
        print("FAIL pve_reward_claim_live_db_canary_apply_approval_workflow:", "; ".join(ERR)); return 1
    print("PASS pve_reward_claim_live_db_canary_apply_approval_workflow"); return 0

if __name__ == "__main__": sys.exit(main())
