"""
RM1.12 — Character Bible validation (CLI).
Esegue validate_character_bible() e stampa un report. Read-only,
nessuna mutazione DB.

Uso:
    cd /app/backend && python3 scripts/validate_character_bible.py
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from data.character_bible import (
    validate_character_bible,
    CHARACTER_BIBLE,
    LAUNCH_BASE_HERO_IDS,
    EXTRA_PREMIUM_HERO_IDS,
    CHARACTER_BIBLE_BY_ID,
)


def main() -> int:
    print("=" * 78)
    print(" Divine Waifus — Character Bible validation (RM1.12)")
    print("=" * 78)

    res = validate_character_bible()
    counts = res["counts"]

    print(f"\n Total entries:           {counts['total']}")
    print(f" launch_base:             {counts['launch_base']}")
    print(f" launch_extra_premium:    {counts['launch_extra_premium']}")
    print(f"\n Per-rarity (launch_base):")
    for r, n in counts["per_rarity_launch_base"].items():
        print(f"   {r}*: {n}")

    print(f"\n LAUNCH_BASE_HERO_IDS sample (first 5): {LAUNCH_BASE_HERO_IDS[:5]}")
    print(f" EXTRA_PREMIUM_HERO_IDS:                  {EXTRA_PREMIUM_HERO_IDS}")

    borea = CHARACTER_BIBLE_BY_ID.get("greek_borea")
    if borea:
        print("\n Borea entry:")
        for k, v in borea.items():
            print(f"   {k:<18s} {v}")

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
