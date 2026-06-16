#!/usr/bin/env python3
"""
Pack 125 — Validator: no live unlocks introdotti dal pack 125.
Scansiona tutti i file modificati in Pack 125 e fallisce se contengono
chiamate a reward/gacha/shop/VIP/BP/IAP/live unlock endpoint.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

TARGETS = [
    "frontend/src/utils/previewBattleTeam.ts",
    "frontend/app/combat.tsx",
    "frontend/app/(tabs)/battle.tsx",
    "frontend/components/home/HomeHeroSplash.tsx",
    "backend/routes/v96_team_formation.py",
    "backend/scripts/qa_team_seed_canonical_heroes.py",
    "backend/scripts/qa_team_seed_clear.py",
]

FORBIDDEN = [
    "/api/gacha/pull",
    "/api/gacha/banner",
    "/api/shop/purchase",
    "/api/shop/buy",
    "/api/vip/purchase",
    "/api/battlepass/buy",
    "/api/iap/purchase",
    "/api/iap/redeem",
    "/api/mail/claim",
    "/api/guild/reward",
    "/api/pvp/reward",
    "unlock_borea",
    "grant_borea",
]


def main() -> int:
    errors: list[str] = []
    for rel in TARGETS:
        fpath = REPO_ROOT / rel
        if not fpath.exists():
            print(f"SKIP  {rel} (not present)")
            continue
        src = fpath.read_text(encoding="utf-8")
        for fp in FORBIDDEN:
            # Tollera nei validator stessi (string literal) ed in commenti negative.
            if fp in src:
                # Check if it's in a comment line (best-effort)
                lines_with = [
                    ln for ln in src.split("\n")
                    if fp in ln and not (ln.strip().startswith(("#", "//", "*", '"', "'"))
                                          or "forbidden" in ln.lower()
                                          or "no_" in ln.lower()
                                          or "vietato" in ln.lower())
                ]
                if lines_with:
                    errors.append(f"{rel}: forbidden `{fp}` (not in comment): {lines_with[0][:120]}")
                else:
                    print(f"OK    {rel}: `{fp}` only in comments/negative refs")
            else:
                pass
        print(f"OK    {rel}: scanned")
    return _emit(errors)


def _emit(errors: list[str]) -> int:
    print("\n" + "="*72)
    print("Pack 125 — no live unlocks")
    print("="*72)
    report = {"pack": "PRE_QA_PACK_125_NO_LIVE_UNLOCKS",
              "status": "PASS" if not errors else "FAIL", "errors": errors}
    out = REPO_ROOT / "backend" / "scripts" / "reports"
    out.mkdir(parents=True, exist_ok=True)
    (out / "pack_125_no_live_unlocks_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if errors:
        for e in errors: print(f"  FAIL  {e}")
        return 1
    print("PASS  no live unlocks / reward / gacha / shop / VIP / BP / IAP in Pack 125 changes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
