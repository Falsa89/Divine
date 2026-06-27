"""HOTFIX E — Validator 3/4: real_player_snapshot alignment al V1.

Verifica STATICA che `backend/helpers/real_player_snapshot.py`:

  1. importi `normalize_team_formation_to_v1` dal contratto centralizzato;
  2. costruisca `uh_ids` ESCLUSIVAMENTE dai `user_hero_id` di team_formation
     V1 normalizzata (no più `entry.get('user_hero_id') or entry.get('hero_id')`
     che trattava canonical_id come owned id);
  3. la mappa `slot_by_uh_id` derivi dalla forma V1 (no più `entry.get('hero_id')`
     come owned id);
  4. NON faccia DB writes (find/update_one/insert_one/delete_one assenti
     nel path snapshot).
  5. esponga `team_formation_v1` + `team_formation_v1_warnings` nello
     snapshot output per visibility downstream (combat preview / lobby).

Exit code 0 = PASS. Exit code != 0 = FAIL.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNAP_PY = ROOT / "backend" / "helpers" / "real_player_snapshot.py"


def main() -> int:
    if not SNAP_PY.exists():
        print(f"FAIL: {SNAP_PY} mancante", file=sys.stderr)
        return 2
    src = SNAP_PY.read_text(encoding="utf-8")
    failures: list[str] = []

    # 1. Import del contratto centralizzato (preferito) o riferimento al
    #    helper di normalizzazione.
    if "from helpers.team_formation_contract import" not in src and \
       "normalize_team_formation_to_v1" not in src:
        failures.append(
            "real_player_snapshot non importa/usa `normalize_team_formation_to_v1`"
        )

    # 2. NON deve più costruire uh_ids con `entry.get('hero_id')` come
    #    owned id (il pattern pre-V1 ambiguo è bandito).
    legacy_pattern = re.search(
        r"entry\.get\(\s*['\"]user_hero_id['\"]\s*\)\s*or\s*entry\.get\(\s*['\"]hero_id['\"]\s*\)",
        src,
    )
    if legacy_pattern:
        failures.append(
            "regressione: real_player_snapshot usa ancora "
            "`entry.get('user_hero_id') or entry.get('hero_id')` per uh_ids "
            "(canonical_id trattato come owned id — violazione contratto V1)"
        )

    # 3. Costruzione lookup map V1-aware presente (owned_by_user_hero_id).
    if "owned_by_user_hero_id" not in src:
        failures.append(
            "real_player_snapshot non costruisce lookup map `owned_by_user_hero_id` "
            "per la disambiguazione legacy"
        )

    # 4. NESSUNA mutazione DB nel modulo snapshot (read-only).
    forbidden_writes = (
        ".insert_one(", ".insert_many(",
        ".update_one(", ".update_many(",
        ".delete_one(", ".delete_many(",
        ".replace_one(", ".bulk_write(",
    )
    for w in forbidden_writes:
        if w in src:
            failures.append(f"real_player_snapshot contiene scrittura DB vietata: `{w}`")

    # 5. Esposizione team_formation_v1 + warnings.
    if "'team_formation_v1'" not in src and '"team_formation_v1"' not in src:
        failures.append(
            "snapshot output non espone `team_formation_v1` per downstream visibility"
        )
    if "team_formation_v1_warnings" not in src:
        failures.append(
            "snapshot output non espone `team_formation_v1_warnings`"
        )

    if failures:
        print("HOTFIX E — VALIDATOR 3 (snapshot_alignment): FAIL", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("HOTFIX E — VALIDATOR 3 (snapshot_alignment): PASS")
    print(f"  file: {SNAP_PY.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
