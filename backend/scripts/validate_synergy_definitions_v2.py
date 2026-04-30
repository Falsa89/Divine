"""
RM1.14 — Synergy/Faction V2 validation (CLI). Read-only.

Uso:
    cd /app/backend && python3 scripts/validate_synergy_definitions_v2.py
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data.synergy_definitions_v2 import (
    validate_synergy_v2,
    FORMATION_SYNERGY_RULES_V2,
    TEAM_SYNERGY_DEFINITIONS_V2,
    COLLECTION_SYNERGY_DEFINITIONS_V2,
    PLAYER_FACTION_DEFINITIONS_V2,
)


def main() -> int:
    print("=" * 78)
    print(" Divine Waifus — Synergy & Player Faction V2 validation (RM1.14)")
    print("=" * 78)

    res = validate_synergy_v2()
    counts = res["counts"]

    print(f"\n Formation rules:                {counts['formation_rules']}")
    print(f" Team synergies:                 {counts['team_synergies']}")
    print(f" Collection synergies:           {counts['collection_synergies']}")
    print(f" Player factions (total):        {counts['player_factions_total']}")
    print(f"   - allowed_at_onboarding:      {counts['player_factions_onboarding']}")
    print(f"   - internal/hero faction only: {counts['player_factions_internal_only']}")
    print(f"\n All entries disabled?           {counts['all_disabled']}")

    print("\n Formation rule IDs:")
    for r in FORMATION_SYNERGY_RULES_V2:
        print(f"   - {r['id']:<28s} ({r['condition_type']})")

    print("\n Team synergy IDs:")
    for s in TEAM_SYNERGY_DEFINITIONS_V2:
        print(f"   - {s['id']:<48s} ({len(s.get('required_hero_ids', []))} heroes)")

    print("\n Collection synergy IDs:")
    for c in COLLECTION_SYNERGY_DEFINITIONS_V2:
        print(f"   - {c['id']:<48s} ({len(c.get('required_hero_ids', []))} heroes)")

    print("\n Player faction IDs:")
    for f in PLAYER_FACTION_DEFINITIONS_V2:
        flag = "[ONBOARDING]" if f.get("allowed_at_onboarding") else "[internal]"
        print(f"   - {f['id']:<20s} {flag}")

    if res["errors"]:
        print("\n ERRORS:")
        for e in res["errors"]:
            print(f"   - {e}")
    else:
        print("\n ERRORS: none")

    if res["warnings"]:
        print("\n WARNINGS:")
        for w in res["warnings"]:
            print(f"   - {w}")

    print("\n" + ("=" * 78))
    print(f" RESULT: {'PASS' if res['ok'] else 'FAIL'}")
    print("=" * 78)
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
