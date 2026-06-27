"""HOTFIX E — Validator 1/4: TeamFormation V1 Contract centralizzato.

Verifica STATICA (no runtime, no DB) che:

  1. esista `backend/helpers/team_formation_contract.py` con i simboli
     richiesti dal contratto V1;
  2. il contratto esponga la forma canonica
     `{user_hero_id, canonical_id, col, row}` e i 11 blocker codes
     richiesti dal prompt;
  3. `backend/routes/v96_team_formation.py` importi e usi il contratto:
     - `normalize_team_formation_to_v1` per GET get-formation;
     - `validate_v1_team_for_save` per POST save-formation;
     - `TeamSlotV1` Pydantic model con `user_hero_id` + `canonical_id`.
  4. il save NON accetta più il vecchio model `TeamSlot{hero_id, col, row}`;
  5. il cap dim `TEAM_FORMATION_V1_MAX_MEMBERS = 6` è invariato (no aumento).

Exit code 0 = PASS. Exit code != 0 = FAIL con motivo.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PY = ROOT / "backend" / "helpers" / "team_formation_contract.py"
ROUTE_PY = ROOT / "backend" / "routes" / "v96_team_formation.py"

REQUIRED_CONTRACT_SYMBOLS = (
    "TEAM_FORMATION_CONTRACT_VERSION",
    "TEAM_FORMATION_V1_MAX_MEMBERS",
    "normalize_slot_to_v1",
    "normalize_team_formation_to_v1",
    "validate_v1_team_for_save",
    "slot_index_to_grid",
)

REQUIRED_BLOCKER_CODES = (
    "TEAM_FORMATION_V1_REQUIRED",
    "TEAM_FORMATION_USER_HERO_ID_REQUIRED",
    "TEAM_FORMATION_CANONICAL_ID_REQUIRED",
    "TEAM_FORMATION_OWNED_HERO_NOT_FOUND",
    "TEAM_FORMATION_SERVER_SCOPE_MISMATCH",
    "TEAM_FORMATION_CANONICAL_MISMATCH",
    "TEAM_FORMATION_DUPLICATE_USER_HERO",
    "TEAM_FORMATION_DUPLICATE_CELL",
    "TEAM_FORMATION_TOO_MANY_MEMBERS",
    "TEAM_FORMATION_LEGACY_AMBIGUOUS",
)


def main() -> int:
    failures: list[str] = []

    if not CONTRACT_PY.exists():
        print(f"FAIL: contratto mancante {CONTRACT_PY}", file=sys.stderr)
        return 2
    contract_src = CONTRACT_PY.read_text(encoding="utf-8")

    for sym in REQUIRED_CONTRACT_SYMBOLS:
        if sym not in contract_src:
            failures.append(f"MISSING simbolo nel contratto: `{sym}`")
    for code in REQUIRED_BLOCKER_CODES:
        if code not in contract_src:
            failures.append(f"MISSING blocker code: `{code}`")

    # Cap 6 confermato (no inflation).
    if "TEAM_FORMATION_V1_MAX_MEMBERS = 6" not in contract_src:
        failures.append(
            "TEAM_FORMATION_V1_MAX_MEMBERS != 6 (HOTFIX E non deve aumentare il cap)"
        )

    # Forma canonica V1 esposta.
    for k in ("user_hero_id", "canonical_id", "col", "row"):
        if f'"{k}"' not in contract_src and f"'{k}'" not in contract_src:
            failures.append(f"MISSING chiave canonica V1: `{k}`")

    if not ROUTE_PY.exists():
        failures.append("backend/routes/v96_team_formation.py mancante")
        return 1
    route_src = ROUTE_PY.read_text(encoding="utf-8")

    if "from helpers.team_formation_contract import" not in route_src:
        failures.append(
            "v96_team_formation.py non importa il contratto centralizzato"
        )
    if "normalize_team_formation_to_v1" not in route_src:
        failures.append(
            "v96_team_formation.py non chiama `normalize_team_formation_to_v1` "
            "(get-formation deve normalizzare a V1 on-read)"
        )
    if "validate_v1_team_for_save" not in route_src:
        failures.append(
            "v96_team_formation.py non chiama `validate_v1_team_for_save` "
            "nel POST save-formation"
        )
    if "class TeamSlotV1" not in route_src:
        failures.append(
            "v96_team_formation.py non definisce il Pydantic model `TeamSlotV1` "
            "con `user_hero_id` + `canonical_id`"
        )
    # Il vecchio model TeamSlot{hero_id, col, row} NON deve più esistere.
    if "class TeamSlot(BaseModel):" in route_src and "TeamSlotV1" not in route_src:
        failures.append(
            "v96_team_formation.py contiene ANCORA il vecchio model `TeamSlot` "
            "senza il rimpiazzo V1"
        )

    if failures:
        print("HOTFIX E — VALIDATOR 1 (teamformation_v1_contract): FAIL", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("HOTFIX E — VALIDATOR 1 (teamformation_v1_contract): PASS")
    print(f"  contratto: {CONTRACT_PY.relative_to(ROOT)}")
    print(f"  blocker codes: {len(REQUIRED_BLOCKER_CODES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
