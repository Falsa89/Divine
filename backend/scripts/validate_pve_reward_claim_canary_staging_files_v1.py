#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validator v79 Track B — Staging Files (allowlist, fixtures, ledger, etc.)."""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ERR = []
STAGING = ROOT / "data/canary_staging"

def _load(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e:
        ERR.append(f"unreadable:{p}:{e}")
        return None

def main():
    manifest = _load(ROOT / "data/design/economy/pve_reward_claim_canary_staging_files_manifest_v1.json")
    marker = _load(ROOT / "data/design/economy/pve_reward_claim_canary_staging_files_marker_v1.json")
    for f in ("README.md", "allowlist_v1.json", "reward_fixtures_v1.json",
              "local_ledger_v1.json", "rollback_tokens_v1.json", "observation_log_v1.json"):
        if not (STAGING / f).exists():
            ERR.append(f"missing_staging_file:{f}")
    if manifest is None: ERR.append("missing:manifest")
    if marker is None: ERR.append("missing:marker")
    allowlist = _load(STAGING / "allowlist_v1.json")
    if allowlist:
        users = allowlist.get("allowlist", [])
        if not users or len(users) > 5 or any("@" in u for u in users):
            ERR.append("allowlist.invalid_or_pii")
        if allowlist.get("alias_only") is not True:
            ERR.append("allowlist.alias_only_not_true")
    fixtures = _load(STAGING / "reward_fixtures_v1.json")
    if fixtures:
        if fixtures.get("non_premium_only") is not True:
            ERR.append("fixtures.non_premium_only_not_true")
        forbidden = {"premium_currency", "gacha_currency", "event_currency",
                     "arena_points", "vip_points", "battle_pass_xp"}
        for fname, payload in fixtures.get("fixtures", {}).items():
            for k in payload.keys():
                if k in forbidden:
                    ERR.append(f"fixtures.{fname}.forbidden_key:{k}")
        caps = fixtures.get("caps", {})
        for k, expected_max in (("gold", 500), ("account_exp", 50),
                                ("hero_exp", 100), ("basic_material", 3)):
            if caps.get(k) != expected_max:
                ERR.append(f"fixtures.cap.{k}_mismatch")
    ledger = _load(STAGING / "local_ledger_v1.json")
    if ledger:
        if ledger.get("canary") is not True:
            ERR.append("ledger.canary_not_true")
        if ledger.get("isolated_from_live") is not True:
            ERR.append("ledger.isolated_from_live_not_true")
        for e in ledger.get("entries", []):
            payload = e.get("reward_payload_summary", {})
            for k in payload.keys():
                if k in ("premium_currency", "gacha_currency", "event_currency",
                         "arena_points", "vip_points", "battle_pass_xp"):
                    ERR.append(f"ledger.entry.forbidden_key:{k}")
    if ERR:
        print("FAIL pve_reward_claim_canary_staging_files:", "; ".join(ERR))
        return 1
    print("PASS pve_reward_claim_canary_staging_files")
    return 0

if __name__ == "__main__":
    sys.exit(main())
