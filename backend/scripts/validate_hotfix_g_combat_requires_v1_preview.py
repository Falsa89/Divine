"""HOTFIX G — Validator 2/4: combat.tsx legge e richiede team_formation_v1 dal
launch_context (fail-closed, no fake team locale, no canonical-as-owned).

Verifica STATICA che `frontend/app/combat.tsx`:

  1. Definisca il type `HotfixFLaunchContextV1Slot` con campi
     user_hero_id / canonical_id / col / row.
  2. Parsifichi il router param `launch_context` come JSON (NON usi solo
     `previewContextFromParams` per V1, NON usi `parseLaunchContextFromParams`
     che NON espone V1).
  3. Estragga `team_formation_v1`, `team_formation_v1_warnings` e
     `team_formation_v1_size` dal payload JSON parsato.
  4. Emetta i blocker:
     - FRONTEND_COMBAT_TEAMFORMATION_V1_REQUIRED
     - FRONTEND_COMBAT_TEAMFORMATION_V1_AMBIGUOUS
     - FRONTEND_COMBAT_TEAMFORMATION_V1_SIZE_MISMATCH
     - FRONTEND_COMBAT_TEAMFORMATION_V1_CANONICAL_AS_OWNED
  5. Early-return su blocker (NIENTE `buildPreviewCombatSnapshot`,
     NIENTE `/api/battle/simulate`, NIENTE reward) e setti
     `setPhase('preview_locked'` come fallback diagnostico.
  6. Non costruisca owned id da canonical_id (`user_hero_id = canonical_id`
     vietato).
  7. Mantenga PREVIEW_REWARD_LOCK_ACTIVE come gate per le mutazioni.

Exit code 0 = PASS. Exit code != 0 = FAIL.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMBAT_TSX = ROOT / "frontend" / "app" / "combat.tsx"


def main() -> int:
    if not COMBAT_TSX.exists():
        print(f"FAIL: {COMBAT_TSX} mancante", file=sys.stderr)
        return 2
    src = COMBAT_TSX.read_text(encoding="utf-8")
    failures: list[str] = []

    required_substrings = [
        ("type V1 slot", "HotfixFLaunchContextV1Slot"),
        ("parse launch_context", "hotfixGRawLaunchContext"),
        ("JSON.parse(rawLc)", "JSON.parse(rawLc)"),
        ("read team_formation_v1", "hotfixGRawLaunchContext?.team_formation_v1"),
        ("read team_formation_v1_warnings", "hotfixGRawLaunchContext?.team_formation_v1_warnings"),
        ("read team_formation_v1_size", "hotfixGRawLaunchContext?.team_formation_v1_size"),
        ("blocker REQUIRED", "FRONTEND_COMBAT_TEAMFORMATION_V1_REQUIRED"),
        ("blocker AMBIGUOUS", "FRONTEND_COMBAT_TEAMFORMATION_V1_AMBIGUOUS"),
        ("blocker SIZE_MISMATCH", "FRONTEND_COMBAT_TEAMFORMATION_V1_SIZE_MISMATCH"),
        ("blocker CANONICAL_AS_OWNED", "FRONTEND_COMBAT_TEAMFORMATION_V1_CANONICAL_AS_OWNED"),
        ("early return preview_locked", "setPhase('preview_locked'"),
        ("PREVIEW_REWARD_LOCK_ACTIVE gate", "PREVIEW_REWARD_LOCK_ACTIVE"),
        ("warn legacy ambiguous detect", "TEAM_FORMATION_LEGACY_AMBIGUOUS"),
    ]
    for desc, needle in required_substrings:
        if needle not in src:
            failures.append(f"MISSING: {desc} (`{needle}`)")

    # Ordering: il blocker guard DEVE precedere `buildPreviewCombatSnapshot` nella
    # branch PREVIEW_REWARD_LOCK_ACTIVE. Verifichiamo che la prima occorrenza
    # del token blocker REQUIRED preceda la prima occorrenza di
    # `buildPreviewCombatSnapshot(previewCtxLocal)`.
    pos_blocker = src.find("FRONTEND_COMBAT_TEAMFORMATION_V1_REQUIRED")
    pos_snap = src.find("buildPreviewCombatSnapshot(previewCtxLocal)")
    if pos_blocker < 0 or pos_snap < 0:
        failures.append("Guard ordering non verificabile (token assenti)")
    elif not (pos_blocker < pos_snap):
        failures.append(
            "Il guard V1 fail-closed deve PRECEDERE `buildPreviewCombatSnapshot`"
        )

    # Early-return: dopo il blocker DEVE esserci un `return;` prima di `snap`.
    # Cerchiamo che fra la posizione del blocker `hotfixGV1Blocker` e
    # `const snap = buildPreviewCombatSnapshot` ci sia un `return;`.
    m_block_if = src.find("if (hotfixGV1Blocker)")
    m_snap_decl = src.find("const snap = buildPreviewCombatSnapshot(previewCtxLocal);")
    if m_block_if < 0 or m_snap_decl < 0:
        failures.append("Branch `if (hotfixGV1Blocker)` o `const snap = ...` mancante")
    else:
        between = src[m_block_if:m_snap_decl]
        if "return;" not in between:
            failures.append(
                "Manca `return;` dentro `if (hotfixGV1Blocker)` prima di `const snap = buildPreviewCombatSnapshot`"
            )

    # canonical_id NON deve essere usato come owned id.
    forbidden_assignments = [
        r"user_hero_id\s*[:=]\s*canonical_id",
        r"const\s+ownedKey\s*=\s*String\(\s*[a-zA-Z_]+\.canonical_id\b",
    ]
    for pat in forbidden_assignments:
        if re.search(pat, src):
            failures.append(
                f"canonical_id usato come owned id (pattern proibito: `{pat}`)"
            )

    if failures:
        print("HOTFIX G — VALIDATOR 2 (combat_requires_v1_preview): FAIL", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("HOTFIX G — VALIDATOR 2 (combat_requires_v1_preview): PASS")
    print(f"  file: {COMBAT_TSX.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
