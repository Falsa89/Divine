"""HOTFIX B — Validator 3/3: No Scope Drift.

Verifica che i file modificati dal working tree rispetto a HEAD siano
ESCLUSIVAMENTE quelli autorizzati per HOTFIX B. Qualsiasi file extra
(es. `backend/server.py`, `frontend/app/(tabs)/servers.tsx`,
`frontend/app/pre-battle-lobby.tsx`, `backend/routes/v96_team_formation.py`)
provoca FAIL.

Allowed scope (deve essere un superset esatto dei file toccati):

  frontend/utils/api.ts
  frontend/app/(tabs)/battle.tsx
  frontend/app/(tabs)/heroes.tsx
  backend/scripts/validate_hotfix_b_api_error_contract.py
  backend/scripts/validate_hotfix_b_blocker_visibility.py
  backend/scripts/validate_hotfix_b_no_scope_drift.py
  docs/divine/537_HOTFIX_B_API_ERROR_CONTRACT*.md

Exit code 0 = PASS. Exit code != 0 = FAIL (scope drift).
"""

from __future__ import annotations

import fnmatch
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ALLOWED_PATTERNS = [
    "frontend/utils/api.ts",
    "frontend/app/(tabs)/battle.tsx",
    "frontend/app/(tabs)/heroes.tsx",
    "backend/scripts/validate_hotfix_b_api_error_contract.py",
    "backend/scripts/validate_hotfix_b_blocker_visibility.py",
    "backend/scripts/validate_hotfix_b_no_scope_drift.py",
    "docs/divine/537_HOTFIX_B_API_ERROR_CONTRACT*.md",
]

# File auto-generati a runtime dai validator Pack (output JSON di report).
# Non sono source-change e non rientrano nello scope guard: vengono riemessi
# ogni volta che la suite Pack 127-133 viene eseguita. Ignorati esplicitamente.
AUTO_GENERATED_IGNORE_PATTERNS = [
    "backend/scripts/reports/*.json",
    "backend/scripts/reports/**/*.json",
]


def is_allowed(path: str) -> bool:
    return any(fnmatch.fnmatch(path, pat) for pat in ALLOWED_PATTERNS)


def is_auto_generated(path: str) -> bool:
    return any(fnmatch.fnmatch(path, pat) for pat in AUTO_GENERATED_IGNORE_PATTERNS)


def get_changed_files() -> list[str]:
    """Ritorna l'elenco di file modificati nel working tree (modificati,
    aggiunti, untracked) rispetto a HEAD. Non include rename old-paths."""
    files: set[str] = set()

    # Modified vs HEAD (tracked).
    res = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=str(ROOT), capture_output=True, text=True, check=False,
    )
    for line in res.stdout.splitlines():
        line = line.strip()
        if line:
            files.add(line)

    # Untracked.
    res2 = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=str(ROOT), capture_output=True, text=True, check=False,
    )
    for line in res2.stdout.splitlines():
        line = line.strip()
        if line:
            files.add(line)

    return sorted(files)


def main() -> int:
    changed = get_changed_files()
    # Filtra auto-generated (report JSON dei validator Pack) prima del check.
    ignored = [p for p in changed if is_auto_generated(p)]
    relevant = [p for p in changed if not is_auto_generated(p)]
    out_of_scope = [p for p in relevant if not is_allowed(p)]

    if out_of_scope:
        print("HOTFIX B — VALIDATOR 3 (no_scope_drift): FAIL", file=sys.stderr)
        print("  Scope drift rilevato. File modificati fuori scope:", file=sys.stderr)
        for p in out_of_scope:
            print(f"    - {p}", file=sys.stderr)
        print("  Allowed patterns:", file=sys.stderr)
        for pat in ALLOWED_PATTERNS:
            print(f"    + {pat}", file=sys.stderr)
        return 1

    print("HOTFIX B — VALIDATOR 3 (no_scope_drift): PASS")
    print(f"  File modificati in scope ({len(relevant)}):")
    for p in relevant:
        print(f"    + {p}")
    if ignored:
        print(f"  File auto-generati ignorati ({len(ignored)}):")
        for p in ignored:
            print(f"    ~ {p}")
    if not relevant:
        print("  (working tree pulito vs HEAD — nessun file di scope modificato)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
