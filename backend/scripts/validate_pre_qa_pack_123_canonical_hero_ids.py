#!/usr/bin/env python3
"""
Pack 123 — Validator: canonical hero IDs must exist in roster.

Verifica che TUTTI i preview hero IDs dichiarati in
`frontend/src/utils/previewBattleTeam.ts` esistano nel roster canonico
`data/design/heroes_master.json`. Fallisce se anche un solo id e' mancante,
e' Borea, e' 6* premium, e' hidden o e' un placeholder.

NO DB write, NO runtime mutation.

Exit code: 0 = pass, 1 = fail.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
UTIL_FILE = REPO_ROOT / "frontend" / "src" / "utils" / "previewBattleTeam.ts"
ROSTER_FILE = REPO_ROOT / "data" / "design" / "heroes_master.json"

FORBIDDEN_KEYWORDS = ["borea", "hidden", "placeholder", "test_only", "internal"]


def fail(msg: str) -> None:
    print(f"FAIL  {msg}")


def ok(msg: str) -> None:
    print(f"OK    {msg}")


def extract_hero_ids(src: str) -> list[str]:
    # Match `hero_id: '...'` or `hero_id: "..."`
    return re.findall(r"hero_id:\s*['\"]([^'\"]+)['\"]", src)


def main() -> int:
    errors: list[str] = []

    if not UTIL_FILE.exists():
        errors.append(f"missing util file: {UTIL_FILE}")
        return _emit(errors, [])

    if not ROSTER_FILE.exists():
        errors.append(f"missing roster file: {ROSTER_FILE}")
        return _emit(errors, [])

    util_src = UTIL_FILE.read_text(encoding="utf-8")
    ids = extract_hero_ids(util_src)
    if not ids:
        errors.append("no hero_id entries found in previewBattleTeam.ts")
        return _emit(errors, [])

    if len(ids) < 6:
        errors.append(f"only {len(ids)} preview hero ids declared (need >=6 for 6v6 team)")

    roster_data = json.loads(ROSTER_FILE.read_text(encoding="utf-8"))
    heroes = roster_data.get("heroes", [])
    by_id = {h["id"]: h for h in heroes if isinstance(h, dict) and h.get("id")}

    for hid in ids:
        if hid not in by_id:
            errors.append(f"hero_id `{hid}` NOT found in heroes_master.json (roster canonico)")
            continue
        h = by_id[hid]
        # Forbidden keywords
        lower = hid.lower()
        for kw in FORBIDDEN_KEYWORDS:
            if kw in lower:
                errors.append(f"hero_id `{hid}` contains forbidden keyword `{kw}`")
        # 6* premium check
        if h.get("rarity") == 6:
            errors.append(f"hero_id `{hid}` is 6* (premium) — vietato per preview launch-safe")
        # Must be launch_base (not launch_extra_premium)
        if h.get("release_group") not in ("launch_base", None):
            errors.append(
                f"hero_id `{hid}` release_group=`{h.get('release_group')}` — solo launch_base ammessi"
            )
        # Borea explicit
        name_lower = str(h.get("name", "")).lower()
        if "borea" in name_lower or "borea" in lower:
            errors.append(f"hero_id `{hid}` (name=`{h.get('name')}`) — Borea esplicitamente VIETATO")
        else:
            ok(f"hero_id canonico OK: {hid} ({h.get('name')} - {h.get('rarity')}* - {h.get('role')})")

    # Verify role coverage (6v6 composition)
    if len(ids) >= 6:
        roles_found = set()
        for hid in ids:
            h = by_id.get(hid)
            if h:
                roles_found.add(h.get("role"))
        required_roles = {"Tank", "DPS Melee", "DPS Ranged", "Mage AoE", "Support / Buffer", "Healer"}
        missing = required_roles - roles_found
        if missing:
            errors.append(f"missing role coverage: {sorted(missing)}")
        else:
            ok(f"role coverage complete: {sorted(roles_found & required_roles)}")

    return _emit(errors, ids)


def _emit(errors: list[str], ids: list[str]) -> int:
    print()
    print("=" * 72)
    print("Pack 123 — canonical hero IDs validation")
    print("=" * 72)
    report = {
        "pack": "PRE_QA_PACK_123_CANONICAL_HERO_IDS",
        "validator": "validate_pre_qa_pack_123_canonical_hero_ids",
        "status": "PASS" if not errors else "FAIL",
        "hero_ids_checked": ids,
        "errors": errors,
    }
    out_dir = REPO_ROOT / "backend" / "scripts" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "pack_123_canonical_hero_ids_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    if errors:
        print(f"FAIL  {len(errors)} errors:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"PASS  {len(ids)} preview hero ids verified canonical")
    return 0


if __name__ == "__main__":
    sys.exit(main())
