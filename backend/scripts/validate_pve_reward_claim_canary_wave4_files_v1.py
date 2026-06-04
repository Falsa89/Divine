#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v82 Track B — Wave4 Files."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []
STAGING = ROOT / "data/canary_staging"

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    manifest = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave4_files_manifest_v1.json")
    marker = _load(ROOT / "data/design/economy/pve_reward_claim_canary_wave4_files_marker_v1.json")
    if manifest is None: ERR.append("missing:manifest")
    if marker is None: ERR.append("missing:marker")
    for f in ("wave4_allowlist_v1.json", "wave4_reward_fixtures_v1.json", "wave4_plan_v1.json"):
        if not (STAGING / f).exists(): ERR.append(f"missing_wave4_file:{f}")
    allowlist = _load(STAGING / "wave4_allowlist_v1.json")
    if allowlist:
        users = allowlist.get("allowlist", [])
        if not users or len(users) > 8 or any("@" in u for u in users):
            ERR.append("allowlist.invalid_or_pii")
        if allowlist.get("alias_only") is not True: ERR.append("allowlist.alias_only_not_true")
    fixtures = _load(STAGING / "wave4_reward_fixtures_v1.json")
    if fixtures:
        if fixtures.get("non_premium_only") is not True:
            ERR.append("fixtures.non_premium_only_not_true")
        forbidden = {"premium_currency", "gacha_currency", "event_currency",
                     "arena_points", "arena_ranking_reward", "vip_points", "battle_pass_xp"}
        for fname, payload in fixtures.get("fixtures", {}).items():
            for k in payload.keys():
                if k in forbidden:
                    ERR.append(f"fixtures.{fname}.forbidden_key:{k}")
        caps = fixtures.get("caps", {})
        for k, expected_max in (("gold", 500), ("account_exp", 50), ("hero_exp", 100), ("basic_material", 3)):
            if caps.get(k) != expected_max: ERR.append(f"fixtures.cap.{k}_mismatch")
        if len(fixtures.get("valid_routes", [])) != 8:
            ERR.append("fixtures.valid_routes_not_8")
    plan = _load(STAGING / "wave4_plan_v1.json")
    if plan:
        if len(plan.get("plan", [])) != 8: ERR.append("plan.entries_not_8")
    if ERR:
        print("FAIL pve_reward_claim_canary_wave4_files:", "; ".join(ERR)); return 1
    print("PASS pve_reward_claim_canary_wave4_files"); return 0

if __name__ == "__main__": sys.exit(main())
