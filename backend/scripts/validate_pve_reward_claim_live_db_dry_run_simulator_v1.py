#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v84 Track D — Live DB Dry-Run Simulator."""
import json, sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    sim = ROOT / "backend/scripts/pve_reward_claim_live_db_dry_run_simulator_v1.py"
    if not sim.exists():
        ERR.append("missing:simulator"); print("FAIL pve_reward_claim_live_db_dry_run_simulator:", "; ".join(ERR)); return 1
    src = sim.read_text(encoding="utf-8")
    # No forbidden imports / references
    forbidden = [
        (r"^\s*import\s+pymongo\b", "pymongo"),
        (r"^\s*from\s+pymongo\b", "pymongo"),
        (r"^\s*import\s+motor\b", "motor"),
        (r"^\s*from\s+motor\b", "motor"),
        (r"^\s*import\s+redis\b", "redis"),
        (r"^\s*from\s+redis\b", "redis"),
        (r"^\s*import\s+battle_engine\b", "battle_engine"),
        (r"^\s*from\s+battle_engine\b", "battle_engine"),
    ]
    for pat, label in forbidden:
        if re.search(pat, src, flags=re.MULTILINE):
            ERR.append(f"simulator.forbidden_import:{label}")
    if re.search(r"\bMONGO_URL\b", src): ERR.append("simulator.uses_MONGO_URL")
    # Required tokens
    for needle in ("dry_run_transaction_policy", "dry_run_auth_guard",
                   "dry_run_endpoint_contract", "dry_run_kill_switch",
                   "dry_run_rollback", "dry_run_observation_sink",
                   "build_v85_gate", "DESIGN_ONLY_NOT_IMPLEMENTED"):
        if needle not in src: ERR.append(f"simulator.missing_token:{needle}")
    # Check outputs produced (after one run)
    rollup = _load(ROOT / "data/design/economy/pve_reward_claim_live_db_dry_run_result_v1.json")
    if rollup is None: ERR.append("missing:rollup_result")
    else:
        if rollup.get("db_writes") != 0: ERR.append("rollup.db_writes_not_0")
        if rollup.get("endpoint_implemented") is not False: ERR.append("rollup.endpoint_implemented_not_false")
        if rollup.get("live_reward_grant") is not False: ERR.append("rollup.live_reward_grant_not_false")
        if rollup.get("dry_run_only") is not True: ERR.append("rollup.dry_run_only_not_true")
        for sec in ("transaction_policy", "auth_guard", "endpoint_contract",
                    "kill_switch", "rollback", "observation_sink"):
            if sec not in rollup: ERR.append(f"rollup.missing_section:{sec}")
    if ERR:
        print("FAIL pve_reward_claim_live_db_dry_run_simulator:", "; ".join(ERR)); return 1
    print("PASS pve_reward_claim_live_db_dry_run_simulator"); return 0

if __name__ == "__main__": sys.exit(main())
