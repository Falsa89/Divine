"""HOTFIX F — Validator 3/4: no live battle / no reward path.

Verifica STATICA che HOTFIX F NON abbia introdotto:

  1. nuove chiamate a `/api/battle/simulate` da nessun file di scope;
  2. import di `battle_engine` nei route lobby/combat preview;
  3. mutazioni reward / EXP / gold / progress nei file di scope;
  4. modifiche a `backend/battle_engine.py` (file fuori scope, intoccato);
  5. modifiche a `backend/server.py` (file fuori scope, intoccato);
  6. modifiche a `real_player_snapshot.py` (HOTFIX E re-audited intoccato).

Exit code 0 = PASS. Exit code != 0 = FAIL.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# File di HOTFIX F (scope) da scansionare per pattern proibiti.
SCOPE_FILES = [
    ROOT / "backend" / "routes" / "v130_lobby_launch_context.py",
    ROOT / "backend" / "routes" / "v131_combat_preview.py",
    ROOT / "frontend" / "app" / "pre-battle-lobby.tsx",
    ROOT / "frontend" / "app" / "combat.tsx",
]

# File che HOTFIX F NON deve aver modificato vs HEAD.
INVARIANT_FILES = [
    "backend/battle_engine.py",
    "backend/server.py",
    "backend/helpers/real_player_snapshot.py",
    "backend/helpers/jwt_secret_preflight.py",
    "backend/routes/v96_auth.py",
    "backend/routes/v96_team_formation.py",
    "backend/helpers/team_formation_contract.py",
]

# Pattern di reward/economy/progress mutation vietati nei file di scope.
FORBIDDEN_REWARD_MUTATIONS = (
    "grant_reward(",
    "grant_gold(",
    "grant_exp(",
    "grant_affinity(",
    "grant_hero_exp(",
    "update_gold(",
    "update_exp(",
    "progress_grant(",
    "reward_claim(",
)

# Pattern HTTP mutativo verso battle simulate.
FORBIDDEN_HTTP_CALLS = (
    "requests.post('/api/battle/simulate",
    'requests.post("/api/battle/simulate',
    "httpx.post('/api/battle/simulate",
    'httpx.post("/api/battle/simulate',
)


def get_changed_files() -> set:
    files: set = set()
    res = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=str(ROOT), capture_output=True, text=True, check=False,
    )
    for line in res.stdout.splitlines():
        line = line.strip()
        if line:
            files.add(line)
    res2 = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=str(ROOT), capture_output=True, text=True, check=False,
    )
    for line in res2.stdout.splitlines():
        line = line.strip()
        if line:
            files.add(line)
    return files


def main() -> int:
    failures: list[str] = []
    changed = get_changed_files()

    # 1-2-3. Pattern check sui file di scope HOTFIX F.
    for f in SCOPE_FILES:
        if not f.exists():
            continue
        src = f.read_text(encoding="utf-8")
        rel = str(f.relative_to(ROOT))
        for pat in FORBIDDEN_REWARD_MUTATIONS:
            if pat in src:
                failures.append(f"[{rel}] reward/progress mutation vietata: `{pat}`")
        for pat in FORBIDDEN_HTTP_CALLS:
            if pat in src:
                failures.append(f"[{rel}] HTTP call vietata: `{pat}`")
        if "from battle_engine" in src or "import battle_engine" in src:
            failures.append(f"[{rel}] importa battle_engine (vietato)")

    # 4-5-6. Invariant files: nessun cambio vs HEAD.
    for inv in INVARIANT_FILES:
        if inv in changed:
            failures.append(
                f"INVARIANT VIOLATED: `{inv}` è stato modificato da HOTFIX F (vietato)"
            )

    if failures:
        print("HOTFIX F — VALIDATOR 3 (no_live_battle_or_reward_path): FAIL", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("HOTFIX F — VALIDATOR 3 (no_live_battle_or_reward_path): PASS")
    print(f"  file di scope scansionati: {len(SCOPE_FILES)}")
    print(f"  invariant files preservati: {len(INVARIANT_FILES)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
