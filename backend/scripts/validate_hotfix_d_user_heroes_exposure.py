"""HOTFIX D — Validator 2/3: `/api/user/heroes` exposure.

Verifica STATICA (no runtime, no DB) che il route GET `/api/user/heroes`
in `backend/server.py` mantenga il contratto headers diagnostici Hotfix B/C
e applichi il fallback `hero_class` dal contratto starter per gli starter
canonici quando il catalog `db.heroes` espone l'eroe con `hero_class`
mancante (o non lo espone affatto).

Controlli:

  1. headers diagnostici Hotfix B presenti su path server-scoped:
     X-Blocker, X-Roster-Count, X-PSP-Lookup-Mode, X-Server-Scope.
  2. import `is_starter_id` + `starter_fallback_exposure` dal contratto.
  3. backfill `hero_class` solo se mancante (no overwrite).
  4. esposizione di starter posseduti anche se NON nel catalog
     (`elif _hd_is_starter_id(...)`) con fallback dal contratto.
  5. header `X-Starter-Fallback-Applied` per QA visibility.
  6. NESSUNA chiamata a `/api/heroes` per popolare il roster.
  7. NESSUNA mutazione DB nel path GET.
  8. blocker `PLAYER_SERVER_PROFILE_REQUIRED` preservato.

Exit code 0 = PASS. Exit code != 0 = FAIL con motivo.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SERVER_PY = ROOT / "backend" / "server.py"

REQUIRED_DIAGNOSTIC_HEADERS = (
    "X-Blocker",
    "X-Roster-Count",
    "X-PSP-Lookup-Mode",
    "X-Server-Scope",
)


def main() -> int:
    if not SERVER_PY.exists():
        print(f"FAIL: {SERVER_PY} mancante", file=sys.stderr)
        return 2
    src = SERVER_PY.read_text(encoding="utf-8")
    failures: list[str] = []

    # Estraggo il body del route GET /api/user/heroes con limite preciso:
    # termina al prossimo decoratore `@app.` (route o evento) O al prossimo
    # section divider `# ===` a inizio riga. `re.M` per match line-anchored.
    m_start = re.search(r'@app\.get\(\s*"/api/user/heroes"\s*\)', src)
    if not m_start:
        print("FAIL: decoratore `/api/user/heroes` non trovato.", file=sys.stderr)
        return 2
    start = m_start.start()
    after = src[start + 1 :]
    candidates: list[int] = []
    m_route = re.search(r"^@app\.", after, re.M)
    if m_route:
        candidates.append(m_route.start())
    m_section = re.search(r"^# =====", after, re.M)
    if m_section:
        candidates.append(m_section.start())
    if candidates:
        end = min(candidates) + start + 1
    else:
        end = len(src)
    block = src[start:end]

    # 1) Headers diagnostici Hotfix B+C presenti.
    for h in REQUIRED_DIAGNOSTIC_HEADERS:
        if h not in block:
            failures.append(f"header diagnostico `{h}` mancante in /api/user/heroes")

    # 2) Import del contratto nel block (HOTFIX D).
    if "from helpers.starter_roster_contract import" not in block:
        failures.append(
            "/api/user/heroes non importa il contratto starter "
            "(`from helpers.starter_roster_contract import ...`)"
        )
    for sym in ("is_starter_id", "starter_fallback_exposure"):
        if sym not in block:
            failures.append(f"/api/user/heroes non usa `{sym}` dal contratto")

    # 3) Backfill condizionato (no overwrite). Verifica pattern
    #    `if not merged.get(...)` dopo il loop di backfill.
    if "if not merged.get(" not in block:
        failures.append(
            "/api/user/heroes non rispetta il vincolo `no overwrite` "
            "sul backfill hero_class (manca `if not merged.get(...)`)"
        )

    # 4) Esposizione fallback per starter NON nel catalog (elif branch).
    if "elif _hd_is_starter_id(" not in block and "elif is_starter_id(" not in block:
        failures.append(
            "/api/user/heroes non espone starter canonici posseduti quando "
            "manca il catalog (manca branch `elif is_starter_id(...)`)"
        )

    # 5) Header `X-Starter-Fallback-Applied`.
    if "X-Starter-Fallback-Applied" not in block:
        failures.append("/api/user/heroes non emette `X-Starter-Fallback-Applied`")

    # 6) NESSUNA chiamata a /api/heroes per popolare /api/user/heroes.
    # Strip line-end comments (`# ...`) prima del check, così i commenti
    # di sicurezza tipo "# NESSUN /api/heroes usage" non producono falso
    # positivo. Manteniamo le stringhe letterali nel codice attivo.
    block_no_comments = re.sub(r"#[^\n]*", "", block)
    if "/api/heroes" in block_no_comments:
        failures.append(
            "/api/user/heroes non deve riferire `/api/heroes` (proibito dal prompt)"
        )

    # 7) NESSUNA mutazione DB nel path GET.
    forbidden_writes = (
        ".insert_one(", ".insert_many(",
        ".update_one(", ".update_many(",
        ".delete_one(", ".delete_many(",
        ".replace_one(", ".bulk_write(",
    )
    for w in forbidden_writes:
        if w in block:
            failures.append(f"/api/user/heroes contiene scrittura DB vietata: `{w}`")

    # 8) Blocker PSP preservato.
    if "PLAYER_SERVER_PROFILE_REQUIRED" not in block:
        failures.append(
            "/api/user/heroes non emette `PLAYER_SERVER_PROFILE_REQUIRED` "
            "quando PSP manca (regressione fail-closed)"
        )

    if failures:
        print("HOTFIX D — VALIDATOR 2 (user_heroes_exposure): FAIL", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("HOTFIX D — VALIDATOR 2 (user_heroes_exposure): PASS")
    print(f"  blocco analizzato: /api/user/heroes ({end - start} char)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
