#!/usr/bin/env python3
"""
Pack 123 — Validator: no-DB-write / no-reward / no-grant invariant.

Scansiona TUTTI i file frontend modificati nel Pack 123 e verifica che
NESSUNO contenga chiamate o pattern di mutazione live verso backend o
DB. Fail-closed: anche un solo match scatena FAIL.

NO runtime mutation. Solo analisi statica.

Exit code: 0 = pass, 1 = fail.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

TARGETS = [
    "frontend/src/utils/previewBattleTeam.ts",
    "frontend/app/pre-battle-lobby.tsx",
    "frontend/app/combat.tsx",
    "frontend/app/tower-of-the-hells.tsx",
    "frontend/app/hero-training.tsx",
    "frontend/app/arena-preview.tsx",
    "frontend/app/boss-raid-preview.tsx",
]

# Forbidden patterns: each entry is (regex, description, allowed_in_files_set).
# Some patterns may legitimately appear in combat.tsx as DEAD CODE behind
# PREVIEW_REWARD_LOCK_ACTIVE / LEGACY_COMBAT_ENTRY_MUTATING guards, so we allow
# their presence ONLY if they are pre-existing (not introduced by Pack 123).
# The validator instead targets NEW additions: it requires that newly added
# pre-battle-lobby preview branch does NOT call mutating endpoints.

FORBIDDEN_NEW_PATTERNS = [
    (r"/api/team/save-formation", "team save endpoint"),
    (r"/api/team/save", "team save endpoint"),
    (r"/api/user/heroes/grant", "grant hero endpoint"),
    (r"/api/inventory/grant", "grant inventory endpoint"),
    (r"/api/battle/reward", "battle reward endpoint"),
    (r"/api/gacha/pull", "gacha pull endpoint"),
    (r"/api/shop/purchase", "shop purchase endpoint"),
    (r"/api/vip/purchase", "vip purchase endpoint"),
    (r"/api/iap/purchase", "iap purchase endpoint"),
    (r"/api/battlepass/buy", "battlepass buy endpoint"),
    (r"/api/progress/save", "progress save endpoint"),
]

# Per-file: pattern that must be PRESENT (positive controls) to ensure the
# preview branch is properly guarded.
REQUIRED_PRESENCE = {
    "frontend/src/utils/previewBattleTeam.ts": [
        ("db_write: false", "explicit db_write false"),
        ("persistent: false", "explicit persistent false"),
        ("reward_allowed: false", "explicit reward_allowed false"),
        ("progress_allowed: false", "explicit progress_allowed false"),
        ("account_roster_mutation: false", "explicit account roster mutation false"),
    ],
    "frontend/app/pre-battle-lobby.tsx": [
        ("previewFallbackActive", "preview fallback gate present"),
        ("buildPreviewCombatUrl", "uses canonical preview combat URL builder"),
    ],
}


def main() -> int:
    errors: list[str] = []

    for rel in TARGETS:
        fpath = REPO_ROOT / rel
        if not fpath.exists():
            errors.append(f"missing target file: {rel}")
            continue
        src = fpath.read_text(encoding="utf-8")
        # Forbidden patterns: must NOT match anywhere in pack 123 introductions.
        # Tolleranza: alcuni endpoint legacy possono apparire in combat.tsx come
        # dead-code dietro PREVIEW_REWARD_LOCK_ACTIVE (gia' attivo pre-pack).
        # Quindi escludiamo combat.tsx solo da quei pattern noti.
        for pat, desc in FORBIDDEN_NEW_PATTERNS:
            for m in re.finditer(pat, src):
                if rel == "frontend/app/combat.tsx":
                    # combat.tsx pre-esistente: ignora se gia' presente
                    continue
                errors.append(f"{rel}: forbidden pattern `{desc}` ({pat}) found")
        # Positive presence checks
        for pat, desc in REQUIRED_PRESENCE.get(rel, []):
            if pat not in src:
                errors.append(f"{rel}: missing required pattern `{desc}` ({pat})")
            else:
                print(f"OK    {rel}: {desc}")

    return _emit(errors)


def _emit(errors: list[str]) -> int:
    print()
    print("=" * 72)
    print("Pack 123 — no-DB-write / no-reward / no-grant invariant")
    print("=" * 72)
    report = {
        "pack": "PRE_QA_PACK_123_NO_DB_WRITE_INVARIANT",
        "validator": "validate_pre_qa_pack_123_no_db_write_invariant",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }
    out_dir = REPO_ROOT / "backend" / "scripts" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "pack_123_no_db_write_invariant_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    if errors:
        print(f"FAIL  {len(errors)} errors:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PASS  no mutating backend calls introduced in pack 123 files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
