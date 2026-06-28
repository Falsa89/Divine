"""HOTFIX F — Validator 1/4: lobby launch context consumes team_formation_v1.

Verifica STATICA che `backend/routes/v130_lobby_launch_context.py`:

  1. Estragga `team_formation_v1` + `team_formation_v1_warnings` dallo snapshot;
  2. Blocchi `LOBBY_TEAMFORMATION_V1_REQUIRED` se manca;
  3. Blocchi `LOBBY_TEAMFORMATION_V1_EMPTY` se vuoto;
  4. Blocchi `LOBBY_TEAMFORMATION_V1_AMBIGUOUS` se warning ambiguous presente;
  5. Esponga `team_formation_v1` al top-level del response;
  6. Marchi `hotfix_f_lobby_consumes_v1: True`;
  7. Non chiami `/api/battle/simulate` né muti DB;
  8. Non tratti `canonical_id` come owned id.

Exit code 0 = PASS. Exit code != 0 = FAIL.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTE_PY = ROOT / "backend" / "routes" / "v130_lobby_launch_context.py"


def main() -> int:
    if not ROUTE_PY.exists():
        print(f"FAIL: {ROUTE_PY} mancante", file=sys.stderr)
        return 2
    src = ROUTE_PY.read_text(encoding="utf-8")
    failures: list[str] = []

    required = [
        ("estrae team_formation_v1", "team_formation_v1"),
        ("estrae warnings V1", "team_formation_v1_warnings"),
        ("blocker REQUIRED", "LOBBY_TEAMFORMATION_V1_REQUIRED"),
        ("blocker EMPTY", "LOBBY_TEAMFORMATION_V1_EMPTY"),
        ("blocker AMBIGUOUS", "LOBBY_TEAMFORMATION_V1_AMBIGUOUS"),
        ("marker hotfix_f", "hotfix_f_lobby_consumes_v1"),
    ]
    for desc, needle in required:
        if needle not in src:
            failures.append(f"MISSING: {desc} (`{needle}`)")

    # Nessuna chiamata a /api/battle/simulate dal route lobby.
    if "/api/battle/simulate" in src:
        failures.append(
            "lobby route NON deve riferire `/api/battle/simulate` (vietato HOTFIX F)"
        )

    # Nessuna mutazione DB.
    for w in (".insert_one(", ".update_one(", ".update_many(", ".delete_one(", ".delete_many("):
        if w in src:
            failures.append(f"lobby route contiene scrittura DB vietata: `{w}`")

    # canonical_id NON deve essere usato come owned id.
    # Pattern proibito: `owned_id = ... canonical_id ...` o `user_hero_id = ... canonical_id`.
    if "user_hero_id = canonical_id" in src or "user_hero_id=canonical_id" in src:
        failures.append(
            "lobby route tratta canonical_id come owned id (violazione contratto V1)"
        )

    if failures:
        print("HOTFIX F — VALIDATOR 1 (lobby_consumes_v1): FAIL", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("HOTFIX F — VALIDATOR 1 (lobby_consumes_v1): PASS")
    print(f"  file: {ROUTE_PY.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
