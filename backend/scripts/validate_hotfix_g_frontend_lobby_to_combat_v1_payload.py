"""HOTFIX G — Validator 1/4: pre-battle-lobby propaga team_formation_v1 nel
launch_context verso /combat.

Verifica STATICA che `frontend/app/pre-battle-lobby.tsx`:

  1. Definisca state HOTFIX G per V1 slots + warnings.
  2. Inserisca `team_formation_v1`, `team_formation_v1_warnings`,
     `team_formation_v1_size` nell'oggetto `launchContext` che viene
     JSON-stringified nel router params verso `/combat`.
  3. Marchi `hotfix_g_frontend_v1_propagation: true`.
  4. Implementi guard fail-closed PRIMA di `router.push`:
     - blocker FRONTEND_LOBBY_TEAMFORMATION_V1_REQUIRED (missing/empty)
     - blocker FRONTEND_LOBBY_TEAMFORMATION_V1_AMBIGUOUS (ambiguous)
  5. Mantenga `user_hero_id` come owned id primario (NON tratti
     `canonical_id` come owned id: pattern `user_hero_id = canonical_id`
     deve essere assente).
  6. Non aggiunga chiamate a endpoint mutativi:
     - POST /api/team/save-formation
     - POST /api/psp/starter/claim
     - POST /api/battle/simulate

Exit code 0 = PASS. Exit code != 0 = FAIL.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOBBY_TSX = ROOT / "frontend" / "app" / "pre-battle-lobby.tsx"


def main() -> int:
    if not LOBBY_TSX.exists():
        print(f"FAIL: {LOBBY_TSX} mancante", file=sys.stderr)
        return 2
    src = LOBBY_TSX.read_text(encoding="utf-8")
    failures: list[str] = []

    required_substrings = [
        ("state V1 slots", "hotfixGTeamV1"),
        ("state V1 warnings", "hotfixGTeamV1Warnings"),
        ("payload team_formation_v1", "team_formation_v1: hotfixGTeamV1"),
        ("payload team_formation_v1_warnings", "team_formation_v1_warnings: hotfixGTeamV1Warnings"),
        ("payload team_formation_v1_size", "team_formation_v1_size: hotfixGTeamV1.length"),
        ("marker hotfix_g", "hotfix_g_frontend_v1_propagation: true"),
        ("blocker REQUIRED", "FRONTEND_LOBBY_TEAMFORMATION_V1_REQUIRED"),
        ("blocker AMBIGUOUS", "FRONTEND_LOBBY_TEAMFORMATION_V1_AMBIGUOUS"),
        ("set state V1 da fetch", "setHotfixGTeamV1("),
        ("warning legacy ambiguous detect", "TEAM_FORMATION_LEGACY_AMBIGUOUS"),
        ("launch_context query param wiring", "launch_context="),
    ]
    for desc, needle in required_substrings:
        if needle not in src:
            failures.append(f"MISSING: {desc} (`{needle}`)")

    # Guard fail-closed: il blocker deve precedere `router.push(target` nello
    # stesso flusso `startBattle`. Verifichiamo che entrambi i token blocker
    # siano referenziati nel file e che appaiano PRIMA dell'ultima
    # occorrenza di `router.push(target` (regex multilinea).
    m_required_pos = src.find("FRONTEND_LOBBY_TEAMFORMATION_V1_REQUIRED")
    m_ambiguous_pos = src.find("FRONTEND_LOBBY_TEAMFORMATION_V1_AMBIGUOUS")
    m_push_pos = src.rfind("router.push(target")
    if m_required_pos < 0 or m_ambiguous_pos < 0 or m_push_pos < 0:
        failures.append(
            "Blocker guard ordering non verificabile (token assenti o router.push assente)"
        )
    else:
        if not (m_required_pos < m_push_pos and m_ambiguous_pos < m_push_pos):
            failures.append(
                "Guard fail-closed deve precedere `router.push(target` nel flusso startBattle"
            )

    # canonical_id NON deve essere usato come owned id. Cerchiamo pattern
    # ovvi che invertano la priorità (assegnamento di canonical_id a
    # user_hero_id).
    forbidden_assignments = [
        r"user_hero_id\s*[:=]\s*canonical_id",
        r"const\s+ownedKey\s*=\s*String\(\s*e\.canonical_id",
    ]
    for pat in forbidden_assignments:
        if re.search(pat, src):
            failures.append(
                f"canonical_id usato come owned id (pattern proibito: `{pat}`)"
            )

    # Endpoint mutativi NON devono essere aggiunti in scope HOTFIX G.
    # NOTE: Pack 86 defensive ensure `/api/psp/ensure` è pre-esistente
    # (idempotente backend-side). I seguenti devono restare ASSENTI.
    forbidden_endpoints = [
        "/api/team/save-formation",
        "/api/psp/starter/claim",
        "/api/battle/simulate",
    ]
    for ep in forbidden_endpoints:
        if ep in src:
            failures.append(
                f"pre-battle-lobby NON deve riferire `{ep}` (vietato HOTFIX G)"
            )

    # Niente `apiCall(` mutativo aggiunto: la lobby fa solo GET /api/team/get-formation
    # e GET /api/user/heroes. Verifichiamo che eventuali fetch POST non riguardino
    # endpoint vietati. Controllo grezzo: ogni `method: 'POST'` deve essere
    # accompagnato da `/api/psp/ensure` (Pack 86 baseline pre-esistente) e
    # NON da uno dei forbidden_endpoints sopra.
    post_block_pattern = re.compile(
        r"method:\s*'POST'(?P<body>.*?)\n\s*\)", re.DOTALL
    )
    for m in post_block_pattern.finditer(src):
        block = m.group(0)
        if any(ep in block for ep in forbidden_endpoints):
            failures.append(
                "trovato blocco POST con endpoint mutativo vietato (HOTFIX G)"
            )

    if failures:
        print("HOTFIX G — VALIDATOR 1 (frontend_lobby_to_combat_v1_payload): FAIL", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("HOTFIX G — VALIDATOR 1 (frontend_lobby_to_combat_v1_payload): PASS")
    print(f"  file: {LOBBY_TSX.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
