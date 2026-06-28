"""FIX 543 — Validator statico per il fix `SERVER_REQUIRED` da useServerScope
non pronto.

Verifica STATICA che `frontend/app/(tabs)/battle.tsx`:

  1. Legga `loading`, `isReady`, `refreshToken` dall'hook `useServerScope`
     (con alias `serverScopeLoading`, `serverScopeReady`,
     `serverScopeRefreshToken`).
  2. NON mostri `SERVER_REQUIRED` prima di aver controllato
     `serverScopeLoading` / `serverScopeReady`: il guard di readiness deve
     PRECEDERE il check `!selected_server_id` sia in `loadData()` sia nel
     render branch.
  3. Il `useFocusEffect/useCallback` includa `selected_server_id` e
     `serverScopeRefreshToken` fra le dipendenze.
  4. Chiami `/api/user/heroes?server_id=...` (owned roster endpoint).
  5. NON usi `/api/heroes` come fallback owned roster.
  6. Nessun backend modificato.
  7. Nessun file fuori scope modificato.
  8. Nessun endpoint mutativo aggiunto:
     - POST /api/team/save-formation (pre-esistente accettato, NON nuovo)
     - POST /api/psp/ensure
     - POST /api/psp/starter/claim
     - POST /api/battle/simulate

Exit code 0 = PASS. Exit code != 0 = FAIL.
"""

from __future__ import annotations

import fnmatch
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BATTLE_TSX = ROOT / "frontend" / "app" / "(tabs)" / "battle.tsx"

ALLOWED_PATTERNS = [
    "frontend/app/(tabs)/battle.tsx",
    "backend/scripts/validate_fix_team_server_required_scope_ready.py",
    "docs/divine/543_FIX_TEAM_SERVER_REQUIRED_SCOPE_READY.md",
]

AUTO_GENERATED_IGNORE_PATTERNS = [
    ".emergent/emergent.yml",
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
    "frontend/app/pre-battle-lobby.tsx",
    "frontend/app/combat.tsx",
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
    if not BATTLE_TSX.exists():
        print(f"FAIL: {BATTLE_TSX} mancante", file=sys.stderr)
        return 2
    src = BATTLE_TSX.read_text(encoding="utf-8")
    failures: list[str] = []

    # 1) Destructuring di loading/isReady/refreshToken da useServerScope.
    required_substrings = [
        ("alias loading", "loading: serverScopeLoading"),
        ("alias isReady", "isReady: serverScopeReady"),
        ("alias refreshToken", "refreshToken: serverScopeRefreshToken"),
        ("call useServerScope()", "useServerScope()"),
        ("guard in loadData", "if (serverScopeLoading || !serverScopeReady)"),
        ("server_id query param call", "/api/user/heroes?server_id=${encodeURIComponent(selected_server_id)}"),
    ]
    for desc, needle in required_substrings:
        if needle not in src:
            failures.append(f"MISSING: {desc} (`{needle}`)")

    # 2) Il guard scope-ready deve precedere il check SERVER_REQUIRED in
    #    loadData() E il branch `if (!selected_server_id)` del render.
    guard_pos = src.find("if (serverScopeLoading || !serverScopeReady)")
    server_required_pos = src.find("'SERVER_REQUIRED'")
    if guard_pos < 0 or server_required_pos < 0:
        failures.append(
            "Guard scope-ready o token SERVER_REQUIRED non trovati"
        )
    elif not (guard_pos < server_required_pos):
        failures.append(
            "Il guard `serverScopeLoading/serverScopeReady` deve PRECEDERE "
            "il setRosterDiag con `SERVER_REQUIRED` in loadData()"
        )

    # Render branch: il guard scope-ready deve precedere
    # `if (!selected_server_id)` nel return. NB: `if (!selected_server_id) {`
    # compare più volte nel file (loadData, saveTeam, render branch); il
    # render branch è quello che ritorna JSX <LinearGradient ...>, identificato
    # dal commento "stato server-required (no fallback account-wide)".
    render_guard_pos = src.find(
        "if (serverScopeLoading || !serverScopeReady || loading) return"
    )
    render_branch_anchor = src.find(
        "stato server-required (no fallback account-wide)"
    )
    if render_guard_pos < 0 or render_branch_anchor < 0:
        failures.append(
            "Render gate scope-ready o anchor del render branch SERVER_REQUIRED non trovati"
        )
    elif not (render_guard_pos < render_branch_anchor):
        failures.append(
            "Il render gate `serverScopeLoading/serverScopeReady` deve "
            "PRECEDERE il render branch `Pre-QA Stabilization 115C — stato server-required`"
        )

    # 3) useFocusEffect/useCallback deps: deve includere selected_server_id
    #    e serverScopeRefreshToken (e ideal: serverScopeLoading + Ready).
    focus_match = re.search(
        r"useFocusEffect\(\s*useCallback\(\s*\(\)\s*=>\s*\{[^}]*loadData\(\);?[^}]*\},\s*\[(?P<deps>[^\]]*)\]\s*\)\s*,\s*\)",
        src,
        re.DOTALL,
    )
    if not focus_match:
        failures.append(
            "Pattern useFocusEffect(useCallback(... loadData(); ..., [deps])) non trovato"
        )
    else:
        deps = focus_match.group("deps")
        for needed in (
            "selected_server_id",
            "serverScopeRefreshToken",
            "serverScopeLoading",
            "serverScopeReady",
        ):
            if needed not in deps:
                failures.append(
                    f"useFocusEffect deps deve includere `{needed}` (attuali: {deps.strip()})"
                )

    # 4+5) Endpoint roster owned: deve usare /api/user/heroes (con server_id),
    #      NON /api/heroes come fallback owned roster.
    if "/api/user/heroes" not in src:
        failures.append("battle.tsx deve usare `/api/user/heroes` come endpoint owned roster")
    if re.search(r"apiCall(WithMeta)?\(\s*['\"]/api/heroes['\"]", src):
        failures.append(
            "battle.tsx NON deve usare `/api/heroes` come fallback owned roster"
        )

    # 8) Nessun NUOVO endpoint mutativo. POST /api/team/save-formation è
    # pre-esistente (non rimosso, non modificato dal fix).
    forbidden_endpoints_new = [
        "/api/psp/ensure",
        "/api/psp/starter/claim",
        "/api/battle/simulate",
    ]
    for ep in forbidden_endpoints_new:
        if ep in src:
            failures.append(
                f"battle.tsx NON deve referire `{ep}` (vietato in scope FIX 543)"
            )

    # 6+7) Scope drift: solo i file in ALLOWED_PATTERNS modificati.
    changed = get_changed_files()
    relevant = [p for p in changed if not is_auto_generated(p)]
    forbidden_touched = [p for p in relevant if p in EXPLICIT_FORBIDDEN]
    out_of_scope = [p for p in relevant if not is_allowed(p)]

    if forbidden_touched or out_of_scope:
        if forbidden_touched:
            for p in forbidden_touched:
                failures.append(f"File esplicitamente vietato toccato: {p}")
        if out_of_scope:
            for p in out_of_scope:
                failures.append(f"File fuori scope toccato: {p}")

    if failures:
        print("FIX 543 — VALIDATOR (team_server_required_scope_ready): FAIL", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("FIX 543 — VALIDATOR (team_server_required_scope_ready): PASS")
    print(f"  file: {BATTLE_TSX.relative_to(ROOT)}")
    print(f"  file modificati in scope ({len(relevant)}):")
    for p in relevant:
        print(f"    + {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
