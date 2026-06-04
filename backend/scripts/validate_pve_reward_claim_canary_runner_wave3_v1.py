#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v81 Track C — Runner Wave3 Mode."""
import json, sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    runner = ROOT / "backend/scripts/pve_reward_claim_canary_runner_v1.py"
    marker = _load(ROOT / "data/design/economy/pve_reward_claim_canary_runner_wave3_marker_v1.json")
    if not runner.exists(): ERR.append("missing:runner")
    else:
        src = runner.read_text(encoding="utf-8")
        for needle in ("--wave3-preflight", "--wave3-apply", "--wave3-observe", "--wave3-rollback-drill",
                       "PVE_REWARD_CLAIM_CANARY_WAVE3", "LOCAL_FILE_STAGING",
                       "VALID_WAVE3_ROUTES", "malformed_route"):
            if needle not in src: ERR.append(f"runner.missing_token:{needle}")
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
        if re.search(r"\bMONGO_URL\b", src): ERR.append("runner.uses_MONGO_URL")
    if marker is None: ERR.append("missing:marker")
    if ERR:
        print("FAIL pve_reward_claim_canary_runner_wave3:", "; ".join(ERR)); return 1
    print("PASS pve_reward_claim_canary_runner_wave3"); return 0

if __name__ == "__main__": sys.exit(main())
