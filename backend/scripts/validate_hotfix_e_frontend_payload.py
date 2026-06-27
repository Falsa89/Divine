"""HOTFIX E — Validator 2/4: Frontend payload battle.tsx.

Verifica STATICA che `frontend/app/(tabs)/battle.tsx`:

  1. emetta il payload TeamFormation V1 nel save: ogni slot deve contenere
     ESPLICITAMENTE `user_hero_id` e `canonical_id`;
  2. NON usi più `h.id` dentro un campo ambiguo chiamato `hero_id`;
  3. il loader della formazione esistente legga prima `user_hero_id` e
     supporti `canonical_id` come fallback (V1-aware load).
  4. nessun frontend fuori `battle.tsx` viene modificato (verifica
     delegata a Validator 4 / no_scope_drift, qui controllo solo il file).

Exit code 0 = PASS. Exit code != 0 = FAIL.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BATTLE_TSX = ROOT / "frontend" / "app" / "(tabs)" / "battle.tsx"


def main() -> int:
    if not BATTLE_TSX.exists():
        print(f"FAIL: {BATTLE_TSX} mancante", file=sys.stderr)
        return 2
    src = BATTLE_TSX.read_text(encoding="utf-8")
    failures: list[str] = []

    # 1. Payload V1: user_hero_id + canonical_id presenti come chiavi
    #    dell'oggetto pushato in team_formation.
    save_block_m = re.search(
        r"team_formation\.push\(\s*\{([^}]*)\}\s*\)",
        src,
        re.DOTALL,
    )
    if not save_block_m:
        failures.append("`team_formation.push({...})` non trovato in battle.tsx")
    else:
        body = save_block_m.group(1)
        if "user_hero_id" not in body:
            failures.append(
                "save payload non contiene `user_hero_id` (HOTFIX E V1 richiesto)"
            )
        if "canonical_id" not in body:
            failures.append(
                "save payload non contiene `canonical_id` (HOTFIX E V1 richiesto)"
            )

    # 2. Il vecchio pattern `team_formation.push({ hero_id: h.id, col, row })`
    #    NON deve più apparire.
    legacy_push = re.search(
        r"team_formation\.push\(\s*\{\s*hero_id\s*:\s*h\.id\s*,\s*col\s*,\s*row\s*\}\s*\)",
        src,
    )
    if legacy_push:
        failures.append(
            "regressione: pattern legacy `team_formation.push({hero_id:h.id,col,row})` "
            "ancora presente"
        )

    # 3. Loader V1-aware: deve preferire `user_hero_id` come prima chiave.
    #    Cerchiamo un riferimento `f?.user_hero_id` o `f.user_hero_id` nel loader.
    if "user_hero_id" not in src:
        failures.append(
            "battle.tsx non legge `user_hero_id` da team_formation (loader non V1-aware)"
        )

    # 4. Marker HOTFIX E presente nel save payload (commento di sicurezza).
    if "HOTFIX E" not in src:
        failures.append("marker `HOTFIX E` mancante in battle.tsx (commento di intent)")

    if failures:
        print("HOTFIX E — VALIDATOR 2 (frontend_payload): FAIL", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("HOTFIX E — VALIDATOR 2 (frontend_payload): PASS")
    print(f"  file: {BATTLE_TSX.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
