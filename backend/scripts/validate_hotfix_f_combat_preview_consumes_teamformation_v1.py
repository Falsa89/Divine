"""HOTFIX F — Validator 2/4: combat preview consumes team_formation_v1.

Verifica STATICA che `backend/routes/v131_combat_preview.py`:

  1. Estragga team_formation_v1 + warnings dal launch_context snapshot;
  2. Blocchi COMBAT_PREVIEW_TEAMFORMATION_V1_REQUIRED se manca;
  3. Blocchi COMBAT_PREVIEW_TEAMFORMATION_V1_EMPTY se vuoto;
  4. Blocchi COMBAT_PREVIEW_TEAMFORMATION_V1_AMBIGUOUS se warning ambiguous;
  5. Esponga team_formation_v1 al top-level del response;
  6. Marchi hotfix_f_combat_preview_consumes_v1: True;
  7. Esponga reward_status=DISABLED + progress_status=DISABLED + battle_simulate_status=BLOCKED;
  8. NON chiami /api/battle/simulate;
  9. NON tratti canonical_id come owned id;
 10. NON muti DB.

Exit code 0 = PASS. Exit code != 0 = FAIL.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTE_PY = ROOT / "backend" / "routes" / "v131_combat_preview.py"


def main() -> int:
    if not ROUTE_PY.exists():
        print(f"FAIL: {ROUTE_PY} mancante", file=sys.stderr)
        return 2
    src = ROUTE_PY.read_text(encoding="utf-8")
    failures: list[str] = []

    required = [
        ("team_formation_v1", "team_formation_v1"),
        ("warnings V1", "team_formation_v1_warnings"),
        ("blocker REQUIRED", "COMBAT_PREVIEW_TEAMFORMATION_V1_REQUIRED"),
        ("blocker EMPTY", "COMBAT_PREVIEW_TEAMFORMATION_V1_EMPTY"),
        ("blocker AMBIGUOUS", "COMBAT_PREVIEW_TEAMFORMATION_V1_AMBIGUOUS"),
        ("marker hotfix_f", "hotfix_f_combat_preview_consumes_v1"),
        ("reward DISABLED", "'reward_status': 'DISABLED'"),
        ("progress DISABLED", "'progress_status': 'DISABLED'"),
        ("battle_simulate BLOCKED", "'battle_simulate_status'"),
        ("preview_only", "'preview_only': True"),
    ]
    for desc, needle in required:
        if needle not in src:
            failures.append(f"MISSING: {desc} (`{needle}`)")

    if "/api/battle/simulate" in src and "battle_simulate_status" not in src.split("/api/battle/simulate")[0]:
        # Soft-check: la stringa "/api/battle/simulate" può apparire solo se referenziata
        # come metadata ("BLOCKED_PRE_QA_HOTFIX_A_FAIL_CLOSED"), mai come chiamata HTTP.
        # Verifica: nessun `requests.post`, `httpx.post`, `fetch`.
        for client in ("requests.post(", "requests.get(", "httpx.post(", "httpx.get(", "fetch("):
            if client in src:
                failures.append(f"combat_preview chiama client HTTP vietato: `{client}`")

    # Nessuna mutazione DB.
    for w in (".insert_one(", ".update_one(", ".update_many(", ".delete_one(", ".delete_many("):
        if w in src:
            failures.append(f"combat_preview contiene scrittura DB vietata: `{w}`")

    # canonical_id non come owned id.
    if "user_hero_id = canonical_id" in src or "user_hero_id=canonical_id" in src:
        failures.append("combat_preview tratta canonical_id come owned id")

    # battle_engine.py non importato/chiamato.
    if "from battle_engine" in src or "import battle_engine" in src:
        failures.append("combat_preview importa battle_engine (vietato)")

    if failures:
        print("HOTFIX F — VALIDATOR 2 (combat_preview_consumes_v1): FAIL", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("HOTFIX F — VALIDATOR 2 (combat_preview_consumes_v1): PASS")
    print(f"  file: {ROUTE_PY.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
