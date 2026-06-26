"""HOTFIX B — Validator 1/3: API Error Contract.

Verifica STATICA (no runtime, no DB, no network) che
`frontend/utils/api.ts` esponga il contratto richiesto da HOTFIX B:

  1. classe `ApiError` esportata;
  2. `ApiError` preserva: status, data, detail, code, headers, diagnostics;
  3. funzione `apiCallWithMeta` esportata;
  4. estrazione case-insensitive degli header diagnostici:
     x-blocker, x-roster-count, x-psp-lookup-mode, x-server-scope;
  5. `apiCall` su risposta non-ok lancia `ApiError` (non plain `Error`);
  6. backward-compat: `apiCall` resta esportata.

Exit code 0 = PASS. Exit code != 0 = FAIL con motivo.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
API_TS = ROOT / "frontend" / "utils" / "api.ts"

REQUIRED_CHECKS = [
    # (description, substring/predicate)
    ("export class ApiError", "export class ApiError"),
    ("ApiError preserva status", "this.status = status"),
    ("ApiError preserva data", "this.data = data"),
    ("ApiError preserva detail", "this.detail = detail"),
    ("ApiError preserva code", "this.code = code"),
    ("ApiError preserva headers", "this.headers = headers"),
    ("ApiError preserva diagnostics", "this.diagnostics = extractDiagnostics"),
    ("export apiCallWithMeta", "export async function apiCallWithMeta"),
    ("export apiCall (backward-compat)", "export async function apiCall"),
    ("apiCall lancia ApiError (non Error)", "throw new ApiError"),
    ("estrazione X-Blocker header", "x-blocker"),
    ("estrazione X-Roster-Count header", "x-roster-count"),
    ("estrazione X-PSP-Lookup-Mode header", "x-psp-lookup-mode"),
    ("estrazione X-Server-Scope header", "x-server-scope"),
]

FORBIDDEN_REGRESSIONS = [
    # Pattern che indicano regressione al vecchio comportamento.
    ("apiCall NON deve lanciare plain Error", "throw new Error("),
]


def main() -> int:
    if not API_TS.exists():
        print(f"FAIL: file mancante {API_TS}", file=sys.stderr)
        return 2
    src = API_TS.read_text(encoding="utf-8")
    failures: list[str] = []

    for desc, needle in REQUIRED_CHECKS:
        if needle not in src:
            failures.append(f"MISSING: {desc} (atteso `{needle}`)")

    for desc, needle in FORBIDDEN_REGRESSIONS:
        if needle in src:
            failures.append(f"REGRESSION: {desc} (trovato `{needle}`)")

    # Controllo aggiuntivo: ApiError deve estendere Error.
    if "class ApiError extends Error" not in src:
        failures.append("MISSING: ApiError deve estendere Error")

    if failures:
        print("HOTFIX B — VALIDATOR 1 (api_error_contract): FAIL", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("HOTFIX B — VALIDATOR 1 (api_error_contract): PASS")
    print(f"  file analizzato: {API_TS.relative_to(ROOT)}")
    print(f"  check superati:  {len(REQUIRED_CHECKS) + 1}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
