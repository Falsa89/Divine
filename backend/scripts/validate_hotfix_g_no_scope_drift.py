"""HOTFIX G — Validator 4/4: No Scope Drift.

Allowed scope:

  frontend/app/pre-battle-lobby.tsx
  frontend/app/combat.tsx
  backend/scripts/validate_hotfix_g_frontend_lobby_to_combat_v1_payload.py
  backend/scripts/validate_hotfix_g_combat_requires_v1_preview.py
  backend/scripts/validate_hotfix_g_no_live_battle_or_reward_path.py
  backend/scripts/validate_hotfix_g_no_scope_drift.py
  data/design/system_safety/hotfix_g_*.json
  docs/divine/542_HOTFIX_G_FRONTEND_LOBBY_COMBAT_V1*.md

Exit code 0 = PASS. Exit code != 0 = FAIL.
"""

from __future__ import annotations

import fnmatch
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ALLOWED_PATTERNS = [
    "frontend/app/pre-battle-lobby.tsx",
    "frontend/app/combat.tsx",
    "backend/scripts/validate_hotfix_g_frontend_lobby_to_combat_v1_payload.py",
    "backend/scripts/validate_hotfix_g_combat_requires_v1_preview.py",
    "backend/scripts/validate_hotfix_g_no_live_battle_or_reward_path.py",
    "backend/scripts/validate_hotfix_g_no_scope_drift.py",
    "data/design/system_safety/hotfix_g_*.json",
    "docs/divine/542_HOTFIX_G_FRONTEND_LOBBY_COMBAT_V1*.md",
]

AUTO_GENERATED_IGNORE_PATTERNS = [
    "backend/scripts/reports/*.json",
    "backend/scripts/reports/**/*.json",
]

EXPLICIT_FORBIDDEN = [
    "backend/battle_engine.py",
    "backend/server.py",
    "backend/helpers/real_player_snapshot.py",
    "backend/helpers/jwt_secret_preflight.py",
    "backend/helpers/team_formation_contract.py",
    "backend/helpers/starter_roster_contract.py",
    "backend/routes/v96_auth.py",
    "backend/routes/v96_team_formation.py",
    "backend/routes/v130_lobby_launch_context.py",
    "backend/routes/v131_combat_preview.py",
    "frontend/utils/api.ts",
    "frontend/app/servers.tsx",
    "frontend/app/(tabs)/battle.tsx",
    "frontend/app/(tabs)/heroes.tsx",
    "data/design/heroes_master.json",
    "backend/data/character_bible.py",
]


def is_allowed(path: str) -> bool:
    return any(fnmatch.fnmatch(path, pat) for pat in ALLOWED_PATTERNS)


def is_auto_generated(path: str) -> bool:
    return any(fnmatch.fnmatch(path, pat) for pat in AUTO_GENERATED_IGNORE_PATTERNS)


def get_changed_files() -> list[str]:
    files: set[str] = set()
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
    return sorted(files)


def main() -> int:
    changed = get_changed_files()
    ignored = [p for p in changed if is_auto_generated(p)]
    relevant = [p for p in changed if not is_auto_generated(p)]
    forbidden_touched = [p for p in relevant if p in EXPLICIT_FORBIDDEN]
    out_of_scope = [p for p in relevant if not is_allowed(p)]

    if forbidden_touched or out_of_scope:
        print("HOTFIX G — VALIDATOR 4 (no_scope_drift): FAIL", file=sys.stderr)
        if forbidden_touched:
            print("  File esplicitamente vietati toccati:", file=sys.stderr)
            for p in forbidden_touched:
                print(f"    ! {p}", file=sys.stderr)
        if out_of_scope:
            print("  File fuori scope:", file=sys.stderr)
            for p in out_of_scope:
                print(f"    - {p}", file=sys.stderr)
        print("  Allowed patterns:", file=sys.stderr)
        for pat in ALLOWED_PATTERNS:
            print(f"    + {pat}", file=sys.stderr)
        return 1

    print("HOTFIX G — VALIDATOR 4 (no_scope_drift): PASS")
    print(f"  File modificati in scope ({len(relevant)}):")
    for p in relevant:
        print(f"    + {p}")
    if ignored:
        print(f"  File auto-generati ignorati ({len(ignored)}):")
        for p in ignored:
            print(f"    ~ {p}")
    if not relevant:
        print("  (working tree pulito vs HEAD)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
