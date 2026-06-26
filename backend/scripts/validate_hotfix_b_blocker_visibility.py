"""HOTFIX B — Validator 2/3: Blocker Visibility nei tab Heroes e Battle.

Verifica STATICA che `frontend/app/(tabs)/heroes.tsx` e
`frontend/app/(tabs)/battle.tsx` non mascherino più gli errori come
"team vuoto" generico, ma espongano i diagnostici richiesti:

  - import `apiCallWithMeta` e `ApiError` da `../../utils/api`;
  - usano `apiCallWithMeta` per il roster reader server-scoped;
  - hanno uno state diagnostic (rosterDiag o equivalente) che cattura
    status/diagnostics/error_code/error_detail;
  - l'empty state UI menziona almeno: blocker, server_scope,
    psp_lookup_mode, roster_count (X-* headers diagnostici).

Exit code 0 = PASS. Exit code != 0 = FAIL con motivo.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGETS = {
    "heroes": ROOT / "frontend" / "app" / "(tabs)" / "heroes.tsx",
    "battle": ROOT / "frontend" / "app" / "(tabs)" / "battle.tsx",
}

PER_FILE_REQUIRED = [
    # description, needle
    ("import apiCallWithMeta", "apiCallWithMeta"),
    ("import ApiError", "ApiError"),
    ("import ApiDiagnostics", "ApiDiagnostics"),
    ("usa apiCallWithMeta nel loader", "apiCallWithMeta"),
    ("state diagnostic (rosterDiag)", "rosterDiag"),
    ("setRosterDiag (writer)", "setRosterDiag"),
    ("catch instanceof ApiError", "instanceof ApiError"),
    ("UI mostra blocker", "blocker"),
    ("UI mostra server_scope", "server_scope"),
    ("UI mostra psp_lookup_mode", "psp_lookup_mode"),
    ("UI mostra roster_count", "roster_count"),
    ("UI mostra HTTP status", "HTTP "),
]

FORBIDDEN_REGRESSIONS = [
    # Catch silenzioso = regressione.
    ("catch silenzioso `catch(e){}`", "catch(e){}"),
    ("catch silenzioso `catch (e) {}`", "catch (e) {}"),
]


def check_file(label: str, path: Path) -> list[str]:
    failures: list[str] = []
    if not path.exists():
        failures.append(f"[{label}] file mancante: {path}")
        return failures
    src = path.read_text(encoding="utf-8")
    for desc, needle in PER_FILE_REQUIRED:
        if needle not in src:
            failures.append(f"[{label}] MISSING: {desc} (atteso `{needle}`)")
    for desc, needle in FORBIDDEN_REGRESSIONS:
        if needle in src:
            failures.append(f"[{label}] REGRESSION: {desc}")
    return failures


def main() -> int:
    all_failures: list[str] = []
    for label, path in TARGETS.items():
        all_failures.extend(check_file(label, path))

    if all_failures:
        print("HOTFIX B — VALIDATOR 2 (blocker_visibility): FAIL", file=sys.stderr)
        for f in all_failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("HOTFIX B — VALIDATOR 2 (blocker_visibility): PASS")
    for label, path in TARGETS.items():
        print(f"  {label}: {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
