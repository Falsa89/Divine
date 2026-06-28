"""HOTFIX G — Validator 3/4: nessun live battle / reward path attivato dal
frontend in scope HOTFIX G.

Verifica STATICA che, nei file di scope HOTFIX G
(`frontend/app/pre-battle-lobby.tsx`, `frontend/app/combat.tsx`):

  1. NON sia stato AGGIUNTO un nuovo call `/api/battle/simulate` (il
     riferimento legacy in `combat.tsx` resta gated dai precedenti
     HOTFIX A + v115E LEGACY_COMBAT_ENTRY_BLOCKED_PRE_QA, in branch
     non raggiungibile sotto PREVIEW_REWARD_LOCK_ACTIVE).
  2. In `pre-battle-lobby.tsx` NON ci siano riferimenti a
     `/api/battle/simulate` (vietato HOTFIX G).
  3. NON siano introdotti nuovi endpoint mutativi:
     - POST /api/team/save-formation
     - POST /api/psp/starter/claim
     - POST /api/battle/simulate
  4. Non siano introdotti grant runtime nuovi nei file di scope HOTFIX G:
     `grant_reward`, `grant_exp`, `grant_gold`, `grant_drop`,
     `grant_affinity_runtime` (`grantAffinity()` esistente in combat.tsx
     resta gated da `if (!PREVIEW_REWARD_LOCK_ACTIVE)`).
  5. Nel ramo PREVIEW_REWARD_LOCK_ACTIVE di `combat.tsx`:
     - non viene chiamato `refreshUser()`;
     - non viene chiamato `grantAffinity(`.
  6. Il file `frontend/utils/api.ts` non è stato toccato (ApiError contract
     HOTFIX B preservato).
  7. Hotfix A invariant: il backend `battle_simulate_guard` non è
     stato indebolito (verifica out-of-scope se file presente,
     comunque la lobby/combat non lo richiamano).

Exit code 0 = PASS. Exit code != 0 = FAIL.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOBBY_TSX = ROOT / "frontend" / "app" / "pre-battle-lobby.tsx"
COMBAT_TSX = ROOT / "frontend" / "app" / "combat.tsx"
API_TS = ROOT / "frontend" / "utils" / "api.ts"

FORBIDDEN_ENDPOINTS_LOBBY = (
    "/api/battle/simulate",
    "/api/team/save-formation",
    "/api/psp/starter/claim",
)

FORBIDDEN_GRANT_TOKENS = (
    "grant_reward(",
    "grant_exp(",
    "grant_gold(",
    "grant_drop(",
    "grant_account_exp(",
    "grant_affinity_runtime(",
)


def main() -> int:
    for f in (LOBBY_TSX, COMBAT_TSX):
        if not f.exists():
            print(f"FAIL: {f} mancante", file=sys.stderr)
            return 2
    lobby_src = LOBBY_TSX.read_text(encoding="utf-8")
    combat_src = COMBAT_TSX.read_text(encoding="utf-8")
    failures: list[str] = []

    # 1+2: lobby non deve riferire endpoint vietati.
    for ep in FORBIDDEN_ENDPOINTS_LOBBY:
        if ep in lobby_src:
            failures.append(
                f"pre-battle-lobby.tsx contiene endpoint vietato `{ep}` (HOTFIX G)"
            )

    # 3: nuovi endpoint mutativi vietati in entrambi i file di scope.
    for ep in ("/api/team/save-formation", "/api/psp/starter/claim"):
        if ep in combat_src:
            failures.append(
                f"combat.tsx contiene endpoint vietato `{ep}` (HOTFIX G)"
            )

    # Il riferimento RUNTIME a `/api/battle/simulate` in combat.tsx (es.
    # `apiCall('/api/battle/simulate'`) è accettato SOLO se preceduto dai
    # guard LEGACY_COMBAT_ENTRY_BLOCKED_PRE_QA + PREVIEW_REWARD_LOCK_ACTIVE
    # (early-return). Ignoriamo i riferimenti in commenti / stringhe non
    # apiCall (es. log diagnostici).
    api_call_simulate = re.search(
        r"""apiCall\(\s*['"]/api/battle/simulate['"]""",
        combat_src,
    )
    if api_call_simulate:
        sim_pos = api_call_simulate.start()
        guard_legacy_pos = combat_src.find("LEGACY_COMBAT_ENTRY_BLOCKED_PRE_QA")
        guard_preview_pos = combat_src.find("PREVIEW_REWARD_LOCK_ACTIVE")
        if guard_legacy_pos < 0 or guard_preview_pos < 0:
            failures.append(
                "combat.tsx chiama apiCall('/api/battle/simulate') ma manca uno dei guard fail-closed precedenti"
            )
        else:
            if not (guard_legacy_pos < sim_pos and guard_preview_pos < sim_pos):
                failures.append(
                    "combat.tsx: i guard LEGACY_COMBAT_ENTRY_BLOCKED_PRE_QA e PREVIEW_REWARD_LOCK_ACTIVE devono precedere apiCall('/api/battle/simulate')"
                )
        # Inoltre l'apiCall a simulate deve trovarsi DOPO la return della
        # branch PREVIEW_REWARD_LOCK_ACTIVE (verificato dalla presenza di
        # `if (PREVIEW_REWARD_LOCK_ACTIVE) {` con `return;` prima della call).
        preview_branch_pos = combat_src.find("if (PREVIEW_REWARD_LOCK_ACTIVE) {")
        if preview_branch_pos < 0 or not (preview_branch_pos < sim_pos):
            failures.append(
                "combat.tsx: branch `if (PREVIEW_REWARD_LOCK_ACTIVE)` deve precedere apiCall('/api/battle/simulate')"
            )

    # 4: grant tokens vietati nei file di scope HOTFIX G.
    for tok in FORBIDDEN_GRANT_TOKENS:
        if tok in lobby_src:
            failures.append(f"pre-battle-lobby.tsx contiene grant token vietato `{tok}`")
        if tok in combat_src:
            failures.append(f"combat.tsx contiene grant token vietato `{tok}`")

    # 5: nel branch PREVIEW_REWARD_LOCK_ACTIVE, refreshUser/grantAffinity devono
    # restare gated. Verifica che ogni `refreshUser()` chiamato dopo l'header
    # del file sia preceduto entro 200 char da `!PREVIEW_REWARD_LOCK_ACTIVE`.
    for token in ("refreshUser();", "grantAffinity("):
        for m in re.finditer(re.escape(token), combat_src):
            start = max(0, m.start() - 200)
            window = combat_src[start:m.start()]
            if "!PREVIEW_REWARD_LOCK_ACTIVE" not in window:
                # ammissibile se è la definizione (function grantAffinity = ...)
                if token == "grantAffinity(" and "const grantAffinity = async" in combat_src[start:m.end()+10]:
                    continue
                failures.append(
                    f"combat.tsx: `{token}` non gated da `!PREVIEW_REWARD_LOCK_ACTIVE` (pos {m.start()})"
                )

    # 6: api.ts non deve essere modificato. Static check: contiene marker ApiError
    # introdotto in HOTFIX B.
    if API_TS.exists():
        api_src = API_TS.read_text(encoding="utf-8")
        if "class ApiError" not in api_src and "ApiError" not in api_src:
            failures.append(
                "frontend/utils/api.ts: marker ApiError (HOTFIX B) assente, file potenzialmente alterato"
            )
    else:
        # api.ts assente è anomalo ma non bloccante per HOTFIX G in modo diretto.
        pass

    # 7: marker Hotfix A backend (best-effort, file out-of-scope per modifiche).
    battle_engine = ROOT / "backend" / "battle_engine.py"
    if battle_engine.exists():
        be_src = battle_engine.read_text(encoding="utf-8", errors="ignore")
        if "BATTLE_SIMULATE_LIVE_ENABLED" not in be_src:
            failures.append(
                "backend/battle_engine.py: marker BATTLE_SIMULATE_LIVE_ENABLED (Hotfix A) assente — invariant rotta"
            )

    if failures:
        print("HOTFIX G — VALIDATOR 3 (no_live_battle_or_reward_path): FAIL", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("HOTFIX G — VALIDATOR 3 (no_live_battle_or_reward_path): PASS")
    print("  file: frontend/app/pre-battle-lobby.tsx, frontend/app/combat.tsx")
    return 0


if __name__ == "__main__":
    sys.exit(main())
