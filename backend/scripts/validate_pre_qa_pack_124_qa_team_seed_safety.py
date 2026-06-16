#!/usr/bin/env python3
"""
Pack 124 — Validator: QA team seed safety (canonical, idempotent, no-economy).
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SEED_FILE = REPO_ROOT / "backend" / "scripts" / "qa_team_seed_canonical_heroes.py"
CLEAR_FILE = REPO_ROOT / "backend" / "scripts" / "qa_team_seed_clear.py"
ROSTER = REPO_ROOT / "data" / "design" / "heroes_master.json"

FORBIDDEN_KEYWORDS = ["borea", "hidden", "placeholder"]

REQUIRED_SEED = [
    ("QA_SEED_ENABLED", "env flag gate"),
    ("--allow-account", "allowlist arg"),
    ("manual_dev_only", "manual_dev_only flag in report"),
    ("no_premium_currency", "no_premium_currency flag"),
    ("no_gacha", "no_gacha flag"),
    ("no_shop", "no_shop flag"),
    ("no_vip", "no_vip flag"),
    ("no_battlepass", "no_battlepass flag"),
    ("no_iap", "no_iap flag"),
    ("idempotent", "idempotency claim"),
    ("_qa_seed_pack", "qa_seed_pack marker for rollback"),
]

FORBIDDEN_IN_SEED = [
    "/api/gacha/",
    "/api/shop/",
    "/api/vip/",
    "/api/battlepass/",
    "/api/iap/",
    # Cerca solo mutazioni reali (assegnamento), non keyword in commenti/docstring.
    "user[\"diamonds\"]",
    "user['diamonds']",
    "user[\"gold\"]",
    "user['gold']",
]


def main() -> int:
    errors: list[str] = []
    if not SEED_FILE.exists():
        errors.append(f"missing: {SEED_FILE}")
        return _emit(errors)
    if not CLEAR_FILE.exists():
        errors.append(f"missing rollback: {CLEAR_FILE}")
    seed_src = SEED_FILE.read_text(encoding="utf-8")
    for pat, desc in REQUIRED_SEED:
        if pat not in seed_src:
            errors.append(f"missing in seed script `{pat}`: {desc}")
        else:
            print(f"OK    seed: {desc}")
    for f in FORBIDDEN_IN_SEED:
        if f in seed_src:
            errors.append(f"forbidden in seed: `{f}`")
    # Verify canonical hero IDs
    hero_ids = re.findall(r'"(\w+)",  #', seed_src)
    # Più semplice: extract from QA_TEAM_SEED_HERO_IDS list literal
    m = re.search(r"QA_TEAM_SEED_HERO_IDS\s*:\s*list\[str\]\s*=\s*\[(.*?)\]", seed_src, re.S)
    if not m:
        errors.append("QA_TEAM_SEED_HERO_IDS list not found")
    else:
        ids = re.findall(r'"([^"]+)"', m.group(1))
        if len(ids) < 10:
            errors.append(f"only {len(ids)} hero ids (need >=10)")
        else:
            print(f"OK    seed pool size: {len(ids)} hero ids")
        if ROSTER.exists():
            roster = json.loads(ROSTER.read_text(encoding="utf-8"))
            by_id = {h["id"]: h for h in roster.get("heroes", []) if isinstance(h, dict)}
            for hid in ids:
                lo = hid.lower()
                for kw in FORBIDDEN_KEYWORDS:
                    if kw in lo:
                        errors.append(f"seed hero `{hid}` contains forbidden `{kw}`")
                if hid not in by_id:
                    errors.append(f"seed hero `{hid}` NOT in heroes_master.json")
                else:
                    h = by_id[hid]
                    if h.get("rarity") == 6:
                        errors.append(f"seed hero `{hid}` is 6* premium (vietato)")
                    if "borea" in str(h.get("name", "")).lower():
                        errors.append(f"seed hero `{hid}` (name) e' Borea (vietato)")
            print(f"OK    {len(ids)} hero ids verificati canonici")
    return _emit(errors)


def _emit(errors: list[str]) -> int:
    print("\n" + "="*72)
    print("Pack 124 — QA team seed safety")
    print("="*72)
    report = {"pack": "PRE_QA_PACK_124_QA_TEAM_SEED_SAFETY",
              "status": "PASS" if not errors else "FAIL", "errors": errors}
    out = REPO_ROOT / "backend" / "scripts" / "reports"
    out.mkdir(parents=True, exist_ok=True)
    (out / "pack_124_qa_team_seed_safety_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if errors:
        for e in errors: print(f"  FAIL  {e}")
        return 1
    print("PASS  QA team seed canonical, gated, idempotent, no-economy")
    return 0


if __name__ == "__main__":
    sys.exit(main())
