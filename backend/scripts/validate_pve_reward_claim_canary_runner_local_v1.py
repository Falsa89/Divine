#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v79 Track C — Runner Local Staging Mode."""
import json, sys, re
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
    marker = _load(ROOT / "data/design/economy/pve_reward_claim_canary_runner_local_marker_v1.json")
    if not runner.exists():
        ERR.append("missing:runner")
    else:
        src = runner.read_text(encoding="utf-8")
        # Must support local staging mode
        if "LOCAL_FILE_STAGING" not in src:
            ERR.append("runner.missing_local_file_staging_mode")
        if "PVE_REWARD_CLAIM_CANARY_MODE" not in src:
            ERR.append("runner.missing_mode_env_var")
        if "--local-apply" not in src:
            ERR.append("runner.missing_local_apply_arg")
        if "--local-preflight" not in src:
            ERR.append("runner.missing_local_preflight_arg")
        if "--local-rollback-drill" not in src:
            ERR.append("runner.missing_rollback_drill_arg")
        # Forbidden imports
        forbidden_imports = [
            (r"^\s*import\s+pymongo\b", "pymongo"),
            (r"^\s*from\s+pymongo\b", "pymongo"),
            (r"^\s*import\s+motor\b", "motor"),
            (r"^\s*from\s+motor\b", "motor"),
            (r"^\s*import\s+redis\b", "redis"),
            (r"^\s*from\s+redis\b", "redis"),
            (r"^\s*import\s+battle_engine\b", "battle_engine"),
            (r"^\s*from\s+battle_engine\b", "battle_engine"),
        ]
        for pat, label in forbidden_imports:
            if re.search(pat, src, flags=re.MULTILINE):
                ERR.append(f"runner.forbidden_import:{label}")
        # MONGO_URL usage check (string literal allowed in comment? Be safe.)
        if re.search(r"\bMONGO_URL\b", src):
            ERR.append("runner.uses_MONGO_URL")
    if marker is None:
        ERR.append("missing:marker")
    if ERR:
        print("FAIL pve_reward_claim_canary_runner_local:", "; ".join(ERR))
        return 1
    print("PASS pve_reward_claim_canary_runner_local")
    return 0

if __name__ == "__main__":
    sys.exit(main())
