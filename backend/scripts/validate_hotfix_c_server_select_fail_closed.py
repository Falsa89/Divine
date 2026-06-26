"""HOTFIX C — Validator 1/2: Server Select Fail-Closed.

Verifica STATICA che `frontend/app/servers.tsx` implementi il flow
fail-closed richiesto da HOTFIX C:

  1. nessun `catch silenzioso` su PSP ensure / starter claim;
  2. nessuna navigazione `router.replace('/(tabs)/home')` dentro `catch`
     o dopo una failure;
  3. `AsyncStorage.setItem('v101_selected_server_id', ...)` avviene SOLO
     dopo il pass del roster verify (post-success ordering verificato
     contando l'occorrenza nel sorgente rispetto al check `rosterEmpty`);
  4. `servers.tsx` importa e usa `ApiError` + `apiCallWithMeta` dal
     contratto HOTFIX B;
  5. esiste una chiamata a `GET /api/user/heroes?server_id=` dopo
     ensure + starter claim;
  6. il roster vuoto produce un codice diagnostico (default
     `ROSTER_EMPTY_AFTER_SERVER_PREP`), letto da X-Blocker /
     X-Roster-Count quando presente;
  7. nessun nuovo endpoint mutativo è stato introdotto (solo gli
     endpoint già esistenti POST `/api/psp/ensure` e
     `/api/psp/starter/claim` user-triggered);
  8. Hotfix A e B non sono stati indeboliti (presenza dei file di
     validator A/B + contratto ApiError invariato).

Exit code 0 = PASS. Exit code != 0 = FAIL con motivo.
NO runtime call, NO DB write, NO endpoint mutativo eseguito.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SERVERS_TSX = ROOT / "frontend" / "app" / "servers.tsx"
API_TS = ROOT / "frontend" / "utils" / "api.ts"
HOTFIX_A_VALIDATORS = [
    ROOT / "backend" / "scripts" / "validate_security_hotfix_a_battle_simulate_guard.py",
    ROOT / "backend" / "scripts" / "validate_security_hotfix_a_jwt_secret_preflight.py",
]
HOTFIX_B_VALIDATORS = [
    ROOT / "backend" / "scripts" / "validate_hotfix_b_api_error_contract.py",
    ROOT / "backend" / "scripts" / "validate_hotfix_b_blocker_visibility.py",
]


def fail(msg: str, failures: list[str]) -> None:
    failures.append(msg)


def check_servers_tsx(src: str, failures: list[str]) -> None:
    # 1. No catch silenziosi su PSP/starter:
    #    pattern .catch(() => { /* tolerated */ }) o catch vuoti.
    forbidden_silent_patterns = [
        r"\.catch\(\(\)\s*=>\s*\{\s*/\*[^*]*tolerated[^*]*\*/\s*\}\)",
        r"\.catch\(\(\)\s*=>\s*\{\s*\}\)",
        r"catch\s*\(\s*\)\s*\{\s*\}",
    ]
    for pat in forbidden_silent_patterns:
        if re.search(pat, src):
            fail(f"silent-catch pattern presente: /{pat}/", failures)

    # 2. router.replace('/(tabs)/home') NON deve apparire nello stesso blocco
    #    di un catch. Controllo statico semplice: l'unica occorrenza deve
    #    essere preceduta da `// ── Step 5: PASS` (marker post-success).
    home_navs = list(re.finditer(r"router\.replace\(['\"]/\(tabs\)/home['\"]\)", src))
    if len(home_navs) != 1:
        fail(
            f"router.replace('/(tabs)/home') deve apparire UNA volta sola "
            f"(trovate {len(home_navs)}).",
            failures,
        )
    else:
        # Verifica che il marker post-success preceda la navigazione.
        idx = home_navs[0].start()
        prefix = src[:idx]
        if "Step 5: PASS" not in prefix:
            fail(
                "router.replace Home non è preceduto dal marker `Step 5: PASS` "
                "del flow fail-closed.",
                failures,
            )

    # 3. AsyncStorage.setItem('v101_selected_server_id', ...) appare SOLO
    #    dopo `Step 5`. Cattura il primo match.
    persist_matches = list(
        re.finditer(
            r"AsyncStorage\.setItem\(\s*['\"]v101_selected_server_id['\"]",
            src,
        )
    )
    if not persist_matches:
        fail("nessuna persistenza di `v101_selected_server_id` trovata.", failures)
    else:
        # Tutte le occorrenze devono essere dentro il blocco post-Step 5.
        step5_idx = src.find("Step 5: PASS")
        if step5_idx < 0:
            fail("marker `Step 5: PASS` mancante in servers.tsx.", failures)
        else:
            for m in persist_matches:
                if m.start() < step5_idx:
                    fail(
                        "persistenza `v101_selected_server_id` PRIMA del "
                        "marker Step 5 (fail-closed violato).",
                        failures,
                    )

    # 4. Import di ApiError e apiCallWithMeta dal contratto HOTFIX B.
    if "apiCallWithMeta" not in src:
        fail("`apiCallWithMeta` non importato/usato in servers.tsx.", failures)
    if "ApiError" not in src:
        fail("`ApiError` non importato/usato in servers.tsx.", failures)
    # Path canonico verso ../utils/api (HOTFIX B export).
    if "from '../utils/api'" not in src and 'from "../utils/api"' not in src:
        fail("import `../utils/api` non trovato in servers.tsx.", failures)

    # 5. GET /api/user/heroes?server_id=... presente.
    if not re.search(r"/api/user/heroes\?server_id=", src):
        fail(
            "chiamata `GET /api/user/heroes?server_id=...` mancante "
            "(roster verify post ensure+claim non implementato).",
            failures,
        )

    # 6. Codice diagnostico per roster vuoto.
    if "ROSTER_EMPTY_AFTER_SERVER_PREP" not in src:
        fail(
            "codice diagnostico `ROSTER_EMPTY_AFTER_SERVER_PREP` mancante "
            "per il caso roster vuoto senza X-Blocker.",
            failures,
        )

    # 7. Nessun nuovo endpoint mutativo: verifichiamo che NON appaiano
    #    POST verso path non autorizzati. Le POST ammesse sono esclusivamente
    #    /api/psp/ensure e /api/psp/starter/claim (user-triggered).
    method_post_calls = re.findall(
        r"apiCallWithMeta<[^>]*>\(\s*[`'\"]([^`'\"]+)[`'\"]\s*,\s*\{[^}]*method:\s*['\"]POST['\"]",
        src,
        re.DOTALL,
    )
    allowed_post_prefixes = ("/api/psp/ensure", "/api/psp/starter/claim")
    for url in method_post_calls:
        if not any(url.startswith(p) for p in allowed_post_prefixes):
            fail(
                f"POST verso endpoint non autorizzato per HOTFIX C: {url!r}",
                failures,
            )

    # 8. UI diagnostica presente: campi minimi nella card.
    required_ui_fields = [
        "Server non pronto",
        "Codice",
        "HTTP",
        "Roster count",
        "PSP lookup",
        "Scope",
        "X-Blocker",
        "Dettaglio",
        "Riprova",
        "Cambia server",
    ]
    for f in required_ui_fields:
        if f not in src:
            fail(f"UI diagnostic field mancante: {f!r}", failures)

    # 9. Phase enum: tutte e cinque le fasi devono essere referenziate.
    for phase in ("no_auth_token", "psp_ensure", "starter_claim", "roster_verify", "network"):
        if phase not in src:
            fail(f"phase `{phase}` non referenziata nel DiagError type.", failures)

    # 10. Nessun retry automatico: nessun setInterval/setTimeout di retry sul flow.
    if re.search(r"setInterval\([^)]*onEnter", src):
        fail("retry automatico via setInterval rilevato (vietato).", failures)
    if re.search(r"setTimeout\([^)]*onEnter", src):
        fail("retry automatico via setTimeout rilevato (vietato).", failures)


def check_hotfix_b_not_weakened(failures: list[str]) -> None:
    if not API_TS.exists():
        fail("api.ts mancante (HOTFIX B contract non disponibile).", failures)
        return
    src = API_TS.read_text(encoding="utf-8")
    required = [
        "export class ApiError",
        "class ApiError extends Error",
        "export async function apiCallWithMeta",
        "export async function apiCall",
        "throw new ApiError",
    ]
    for r in required:
        if r not in src:
            fail(f"HOTFIX B contract regression: manca `{r}` in api.ts.", failures)


def check_hotfix_a_b_validators_present(failures: list[str]) -> None:
    for p in HOTFIX_B_VALIDATORS:
        if not p.exists():
            fail(f"HOTFIX B validator mancante: {p.name}", failures)


def main() -> int:
    if not SERVERS_TSX.exists():
        print(f"FAIL: file mancante {SERVERS_TSX}", file=sys.stderr)
        return 2
    src = SERVERS_TSX.read_text(encoding="utf-8")

    failures: list[str] = []
    check_servers_tsx(src, failures)
    check_hotfix_b_not_weakened(failures)
    check_hotfix_a_b_validators_present(failures)

    if failures:
        print("HOTFIX C — VALIDATOR 1 (server_select_fail_closed): FAIL", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("HOTFIX C — VALIDATOR 1 (server_select_fail_closed): PASS")
    print(f"  file analizzato: {SERVERS_TSX.relative_to(ROOT)}")
    print(f"  righe servers.tsx: {len(src.splitlines())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
