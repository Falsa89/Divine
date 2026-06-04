#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v78 Track D — PvE Reward Claim Canary Runner."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e:
        ERR.append(f"unreadable:{p}:{e}")
        return None

def main():
    runner = ROOT / "backend/scripts/pve_reward_claim_canary_runner_v1.py"
    dry = _load(ROOT / "data/design/economy/pve_reward_claim_canary_dry_run_result_v1.json")
    apply_or_blocked = _load(ROOT / "data/design/economy/pve_reward_claim_canary_apply_or_blocked_result_v1.json")
    marker = _load(ROOT / "data/design/economy/pve_reward_claim_canary_runner_marker_v1.json")
    if not runner.exists():
        ERR.append("missing:runner_script")
    else:
        src = runner.read_text(encoding="utf-8")
        # Vietati veri statement di import dei file critici (non semplici menzioni in stringhe/commenti)
        import re as _re
        forbidden_import_patterns = [
            (r"^\s*import\s+battle_engine\b", "battle_engine"),
            (r"^\s*from\s+battle_engine\b", "battle_engine"),
            (r"^\s*from\s+backend\.battle_engine\b", "battle_engine"),
            (r"^\s*from\s+backend\.server\b", "backend.server"),
            (r"^\s*import\s+server\b", "server"),
        ]
        for pat, label in forbidden_import_patterns:
            if _re.search(pat, src, flags=_re.MULTILINE):
                ERR.append(f"runner.forbidden_import:{label}")
        if "APPLY_FLAG_VALUE" not in src or "YES_I_UNDERSTAND" not in src:
            ERR.append("runner.missing_apply_flag_guard")
        if "PVE_REWARD_CLAIM_CANARY_APPLY" not in src:
            ERR.append("runner.missing_apply_env_var")
    if dry is None:
        ERR.append("missing:dry_run_result")
    else:
        if dry.get("mode") != "dry-run":
            ERR.append("dry.mode_invalid")
        if dry.get("applied") is not False:
            ERR.append("dry.applied_not_false")
        if dry.get("db_writes", 1) != 0:
            ERR.append("dry.db_writes_nonzero")
    if apply_or_blocked is None:
        ERR.append("missing:apply_or_blocked_result")
    else:
        # nello stato corrente, atteso blocked
        if apply_or_blocked.get("applied") is not False:
            ERR.append("apply_or_blocked.applied_not_false_in_current_env")
        if apply_or_blocked.get("db_writes", 1) != 0:
            ERR.append("apply_or_blocked.db_writes_nonzero")
        if apply_or_blocked.get("verdict_local") != "PVE_REWARD_CLAIM_CANARY_BLOCKED_NOT_APPLIED_SAFE":
            ERR.append("apply_or_blocked.verdict_invalid")
    if marker is None:
        ERR.append("missing:runner_marker")
    if ERR:
        print("FAIL pve_reward_claim_canary_runner:", "; ".join(ERR))
        return 1
    print("PASS pve_reward_claim_canary_runner")
    return 0

if __name__ == "__main__":
    sys.exit(main())
