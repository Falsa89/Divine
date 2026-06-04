#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v84 Track C — Live DB Dry-Run Fixtures."""
import json, sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []

def _load(p):
    try: return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e: ERR.append(f"unreadable:{p}:{e}"); return None

def main():
    fx = _load(ROOT / "data/canary_staging/live_db_dry_run_fixtures_v1.json")
    if fx is None: ERR.append("missing:fixtures"); print("FAIL pve_reward_claim_live_db_dry_run_fixtures:", "; ".join(ERR)); return 1
    if fx.get("alias_only") is not True: ERR.append("fixtures.alias_only_not_true")
    if fx.get("pii") is not False: ERR.append("fixtures.pii_not_false")
    users = fx.get("users", [])
    if not users: ERR.append("fixtures.users_empty")
    for u in users:
        uid = u.get("user_id_hash", "")
        if not uid.startswith("sha256:"): ERR.append(f"fixtures.user_id_hash_invalid:{uid}")
        if "@" in uid: ERR.append(f"fixtures.user_id_hash_pii:{uid}")
    claims = fx.get("claims", [])
    if not claims or len(claims) < 1: ERR.append("fixtures.claims_empty")
    allowed = {"gold", "account_exp", "hero_exp", "basic_material"}
    forb = set(fx.get("forbidden_reward_keys", []))
    for k in ("premium_currency", "arena_ranking_reward", "gacha_currency", "event_currency",
              "arena_points", "vip_points", "battle_pass_xp"):
        if k not in forb: ERR.append(f"fixtures.forbidden_keys.missing:{k}")
    for c in claims:
        for k in c.get("reward_preview", {}).keys():
            if k not in allowed:
                ERR.append(f"fixtures.claim_reward_invalid_key:{c.get('claim_id')}:{k}")
    neg = fx.get("negative_cases", [])
    expected_neg = {"non_allowlisted_user", "premium_currency", "arena_ranking_reward",
                    "over_cap_reward", "malformed_route", "real_account_id", "kill_switch_engaged"}
    got = {n.get("name") for n in neg}
    for e in expected_neg:
        if e not in got: ERR.append(f"fixtures.missing_negative_case:{e}")
    caps = fx.get("caps", {})
    for k, exp in (("gold", 500), ("account_exp", 50), ("hero_exp", 100), ("basic_material", 3)):
        if caps.get(k) != exp: ERR.append(f"fixtures.cap.{k}_mismatch")
    if len(fx.get("valid_routes", [])) != 8:
        ERR.append("fixtures.valid_routes_not_8")
    if ERR:
        print("FAIL pve_reward_claim_live_db_dry_run_fixtures:", "; ".join(ERR)); return 1
    print("PASS pve_reward_claim_live_db_dry_run_fixtures"); return 0

if __name__ == "__main__": sys.exit(main())
