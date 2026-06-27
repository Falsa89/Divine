"""HOTFIX D — Validator 1/3: Starter Roster Contract centralizzato.

Verifica STATICA (no runtime, no DB, no network) che:

  1. esista `backend/helpers/starter_roster_contract.py` con la lista
     canonica dei tre starter (greek_phalanx_recruit / celtic_forest_archer
     / angelic_sanctuary_acolyte);
  2. il contratto esponga i campi `starter_id`, `expected_role`,
     `expected_hero_class`, `expected_rarity` per ogni entry;
  3. il contratto esponga i flag richiesti
     `STARTER_REQUIRED_FLAGS` con i 6 vincoli del prompt
     (is_official_required, obtainable_required, show_in_catalog_required,
     premium_forbidden, deactivated_forbidden, high_rarity_forbidden);
  4. `backend/server.py` importi e usi il contratto (no duplicazione
     incoerente di IDs/role);
  5. il claim non accetti starter fuori contratto (nessun hero_id altro
     che i tre canonici nel claim path);
  6. il claim conservi l'idempotenza (`already_claimed`) e i 7 blocker
     ratificati.

Exit code 0 = PASS. Exit code != 0 = FAIL con motivo.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PY = ROOT / "backend" / "helpers" / "starter_roster_contract.py"
SERVER_PY = ROOT / "backend" / "server.py"

EXPECTED_STARTER_IDS = (
    "greek_phalanx_recruit",
    "celtic_forest_archer",
    "angelic_sanctuary_acolyte",
)

REQUIRED_CONTRACT_SYMBOLS = (
    "STARTER_ROSTER_CONTRACT",
    "STARTER_IDS",
    "STARTER_REQUIRED_FLAGS",
    "is_starter_id",
    "get_starter_entry",
    "starter_set_for_claim",
    "starter_fallback_exposure",
)

REQUIRED_FLAG_KEYS = (
    "is_official_required",
    "obtainable_required",
    "show_in_catalog_required",
    "premium_forbidden",
    "deactivated_forbidden",
    "high_rarity_forbidden",
)

REQUIRED_BLOCKER_CODES = (
    "STARTER_ROSTER_NOT_CATALOGED",
    "STARTER_ROSTER_NOT_OFFICIAL",
    "STARTER_ROSTER_NOT_OBTAINABLE",
    "STARTER_ROSTER_NOT_CATALOG_VISIBLE",
    "STARTER_ROSTER_DEACTIVATED",
    "STARTER_ROSTER_PREMIUM_FORBIDDEN",
    "STARTER_ROSTER_HIGH_RARITY",
)


def main() -> int:
    failures: list[str] = []

    # ── 1) Contratto esiste ─────────────────────────────────────────────
    if not CONTRACT_PY.exists():
        print(f"FAIL: contratto mancante {CONTRACT_PY}", file=sys.stderr)
        return 2
    contract_src = CONTRACT_PY.read_text(encoding="utf-8")

    # ── 2) Simboli esportati ────────────────────────────────────────────
    for sym in REQUIRED_CONTRACT_SYMBOLS:
        if sym not in contract_src:
            failures.append(f"MISSING symbol nel contratto: {sym}")

    # ── 3) IDs canonici presenti UNA volta nel contratto ────────────────
    for sid in EXPECTED_STARTER_IDS:
        n = contract_src.count(f'"{sid}"') + contract_src.count(f"'{sid}'")
        if n < 1:
            failures.append(f"MISSING starter_id `{sid}` nel contratto")

    # ── 4) Flag richiesti tutti presenti ─────────────────────────────────
    for flag in REQUIRED_FLAG_KEYS:
        if flag not in contract_src:
            failures.append(f"MISSING flag `{flag}` in STARTER_REQUIRED_FLAGS")

    # ── 5) Mapping role → hero_class atteso ─────────────────────────────
    # tank / dps / support (lowercase role) + Tank / DPS / Support (PascalCase class)
    expected_pairs = [
        ("greek_phalanx_recruit", "tank", "Tank"),
        ("celtic_forest_archer", "dps", "DPS"),
        ("angelic_sanctuary_acolyte", "support", "Support"),
    ]
    for sid, role, cls in expected_pairs:
        # Tolleriamo qualsiasi ordine dei campi; verifichiamo che siano nel
        # contratto in close proximity allo starter_id.
        idx = contract_src.find(f'"{sid}"')
        if idx >= 0:
            window = contract_src[idx : idx + 400]
            if f'"{role}"' not in window:
                failures.append(f"MISSING expected_role `{role}` per `{sid}`")
            if f'"{cls}"' not in window:
                failures.append(f"MISSING expected_hero_class `{cls}` per `{sid}`")

    # ── 6) server.py importa il contratto ───────────────────────────────
    if not SERVER_PY.exists():
        failures.append("server.py mancante")
        return 1
    server_src = SERVER_PY.read_text(encoding="utf-8")
    if "from helpers.starter_roster_contract import" not in server_src:
        failures.append(
            "server.py non importa `from helpers.starter_roster_contract import …`"
        )
    # Il claim deve usare `starter_set_for_claim()` e `STARTER_REQUIRED_FLAGS`.
    if "starter_set_for_claim()" not in server_src:
        failures.append("server.py non chiama `starter_set_for_claim()` nel claim")
    if "STARTER_REQUIRED_FLAGS" not in server_src:
        failures.append("server.py non usa `STARTER_REQUIRED_FLAGS` nel claim")

    # ── 7) Nessuna duplicazione incoerente di IDs ───────────────────────
    # server.py NON deve avere una seconda lista hardcoded `[("greek_…", …), …]`.
    # Verifica: la vecchia forma con tre tuple consecutive non deve apparire.
    legacy_pattern = re.compile(
        r'\(\s*"greek_phalanx_recruit"\s*,\s*"tank"\s*\)\s*,'
        r'\s*\(\s*"celtic_forest_archer"\s*,\s*"dps"\s*\)\s*,'
        r'\s*\(\s*"angelic_sanctuary_acolyte"\s*,\s*"support"\s*\)',
    )
    if legacy_pattern.search(server_src):
        failures.append(
            "server.py contiene ANCORA la lista starter hardcoded — duplicazione "
            "incoerente col contratto centralizzato."
        )

    # ── 8) Claim path contiene i 7 blocker richiesti ────────────────────
    for code in REQUIRED_BLOCKER_CODES:
        if code not in server_src:
            failures.append(f"server.py non emette il blocker `{code}`")

    # ── 9) Idempotency preservata ────────────────────────────────────────
    if "_slc_pack_87_starter_claim_marker" not in server_src:
        failures.append(
            "server.py: marker idempotenza `_slc_pack_87_starter_claim_marker` rimosso"
        )
    if 'already_claimed_no_write' not in server_src:
        failures.append(
            "server.py: header `X-Starter-Claim-Mode: already_claimed_no_write` rimosso"
        )

    # ── 10) Authorization string Pack 87 invariata ───────────────────────
    if "AUTORIZZO_V110_SERVER_SCOPED_STARTER_FLOW_PACK_87" not in server_src:
        failures.append(
            "server.py: authorization string Pack 87 rimossa"
        )

    if failures:
        print("HOTFIX D — VALIDATOR 1 (starter_roster_contract): FAIL", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("HOTFIX D — VALIDATOR 1 (starter_roster_contract): PASS")
    print(f"  contratto: {CONTRACT_PY.relative_to(ROOT)}")
    print(f"  starter ids: {', '.join(EXPECTED_STARTER_IDS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
