#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v83 Track F — Live DB Design Contract (design-only)."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    contract = _load(ROOT / "data/design/economy/pve_reward_claim_live_db_design_contract_v1.json")
    marker = _load(ROOT / "data/design/economy/pve_reward_claim_live_db_design_contract_marker_v1.json")

    for name, obj in (("contract", contract), ("marker", marker)):
        if obj is None: ERR.append(f"missing:{name}")

    if contract:
        if contract.get("design_only") is not True: ERR.append("contract.design_only_not_true")
        if contract.get("live_db_apply_allowed") is not False: ERR.append("contract.live_db_apply_allowed_not_false")
        if contract.get("endpoint_implemented") is not False: ERR.append("contract.endpoint_implemented_not_false")
        if contract.get("db_writes") != 0: ERR.append("contract.db_writes_not_0")
        if contract.get("live_reward_grant") is not False: ERR.append("contract.live_reward_grant_not_false")
        sec = contract.get("sections", {})
        for required_section in ("db_transaction_policy", "real_account_allowlist_schema",
                                 "auth_guard", "endpoint_contract", "rollback_script",
                                 "observation_sink", "kill_switch", "manual_approval_for_apply"):
            if required_section not in sec: ERR.append(f"contract.section_missing:{required_section}")
        ec = sec.get("endpoint_contract", {})
        if ec.get("status") != "DESIGN_ONLY_NOT_IMPLEMENTED":
            ERR.append("contract.endpoint_contract.status_not_design_only")
        if not isinstance(ec.get("reason_codes"), list) or len(ec.get("reason_codes", [])) < 5:
            ERR.append("contract.endpoint_contract.reason_codes_insufficient")
        rs = sec.get("rollback_script", {})
        if rs.get("status") != "DESIGN_ONLY_NOT_CREATED":
            ERR.append("contract.rollback_script.status_not_design_only")
        ks = sec.get("kill_switch", {})
        if not ks.get("flag") or not ks.get("trigger_value"):
            ERR.append("contract.kill_switch_invalid")
        if ks.get("on_engage_reject_all") is not True:
            ERR.append("contract.kill_switch.on_engage_reject_all_not_true")
        ma = sec.get("manual_approval_for_apply", {})
        if ma.get("required") is not True or ma.get("checksum_required") is not True:
            ERR.append("contract.manual_approval_invalid")

    if marker:
        if marker.get("design_only") is not True: ERR.append("marker.design_only_not_true")
        if marker.get("live_db_apply_allowed") is not False: ERR.append("marker.live_db_apply_allowed_not_false")
        if marker.get("endpoint_implemented") is not False: ERR.append("marker.endpoint_implemented_not_false")
        if marker.get("db_writes") != 0: ERR.append("marker.db_writes_not_0")

    # Verifica che NESSUNA route/endpoint sia stato registrato in server.py o routes/
    server_py = ROOT / "backend/server.py"
    if server_py.exists():
        src = server_py.read_text(encoding="utf-8")
        if "/api/pve/reward/claim" in src:
            ERR.append("server_py.contains_pve_reward_claim_route")

    if ERR:
        print("FAIL pve_reward_claim_live_db_design_contract:", "; ".join(ERR)); return 1
    print("PASS pve_reward_claim_live_db_design_contract"); return 0

if __name__ == "__main__": sys.exit(main())
