#!/usr/bin/env python3
"""
PRE_QA_STABILIZATION_114B_GACHA_COMBAT_LOBBY_GUARD_REPAIR — VALIDATOR
====================================================================

Validator statico per il Pack 114B. Controlla che lo stato del repository
sia coerente con gli assert richiesti dal pack `gacha_combat_lobby_guard_repair`
prima del Final Deep Re-Audit PASS 4.

Tutti i check sono STATICI (regex/grep su file di repo). Nessun DB write,
nessuna chiamata di rete, nessuna mutazione runtime.

Output: stampa OK/FAIL per ogni check + summary finale.
Exit code: 0 se tutti PASS, 1 altrimenti.

Tutti i log sono in italiano (lingua del progetto).
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Utility I/O
# ---------------------------------------------------------------------------
def _read(rel_path: str) -> str:
    p = REPO_ROOT / rel_path
    if not p.exists():
        raise FileNotFoundError(f"File mancante: {rel_path}")
    return p.read_text(encoding="utf-8", errors="strict")


def _find_index(haystack: str, needle: str, start: int = 0) -> int:
    return haystack.find(needle, start)


# ---------------------------------------------------------------------------
# Check definitions
# ---------------------------------------------------------------------------
CHECKS: List[Tuple[str, str]] = []


def _ok(name: str, detail: str = "") -> Tuple[bool, str, str]:
    return (True, name, detail)


def _fail(name: str, detail: str) -> Tuple[bool, str, str]:
    return (False, name, detail)


def check_01_gacha_pull_blocker() -> Tuple[bool, str, str]:
    """server.py /api/gacha/pull contiene il blocker GACHA_LIVE_DISABLED_PRE_QA."""
    src = _read("backend/server.py")
    name = "01_GACHA_PULL_BLOCKER_PRESENT"
    pull_idx = src.find('@app.post("/api/gacha/pull")')
    if pull_idx < 0:
        return _fail(name, "endpoint /api/gacha/pull non trovato")
    # cerca il blocker entro 60 righe
    window = src[pull_idx: pull_idx + 4000]
    if "GACHA_LIVE_DISABLED_PRE_QA" not in window:
        return _fail(name, "blocker GACHA_LIVE_DISABLED_PRE_QA non trovato vicino a /api/gacha/pull")
    if "GACHA_LIVE_ENABLED" not in window:
        return _fail(name, "kill-switch env GACHA_LIVE_ENABLED non referenziato vicino al guard")
    if "raise HTTPException(423" not in window and "HTTPException(\n            423" not in window and "HTTPException(423," not in window:
        return _fail(name, "HTTP 423 non sollevato dal guard")
    return _ok(name, "blocker + kill-switch + HTTP 423 presenti")


def check_02_gacha_pull10_blocker() -> Tuple[bool, str, str]:
    """server.py /api/gacha/pull10 contiene il blocker GACHA_LIVE_DISABLED_PRE_QA."""
    src = _read("backend/server.py")
    name = "02_GACHA_PULL10_BLOCKER_PRESENT"
    pull10_idx = src.find('@app.post("/api/gacha/pull10")')
    if pull10_idx < 0:
        return _fail(name, "endpoint /api/gacha/pull10 non trovato")
    window = src[pull10_idx: pull10_idx + 4000]
    if "GACHA_LIVE_DISABLED_PRE_QA" not in window:
        return _fail(name, "blocker GACHA_LIVE_DISABLED_PRE_QA non trovato vicino a /api/gacha/pull10")
    if "GACHA_LIVE_ENABLED" not in window:
        return _fail(name, "kill-switch env GACHA_LIVE_ENABLED non referenziato vicino al guard")
    return _ok(name, "blocker + kill-switch presenti")


def check_03_guard_precedes_gems_spend() -> Tuple[bool, str, str]:
    """Il guard gacha deve precedere QUALSIASI db.users.update_one(... $inc gems ...) negli handler /pull e /pull10."""
    src = _read("backend/server.py")
    name = "03_GUARD_PRECEDES_GEMS_SPEND"
    for endpoint in ('@app.post("/api/gacha/pull")', '@app.post("/api/gacha/pull10")'):
        ep_idx = src.find(endpoint)
        if ep_idx < 0:
            return _fail(name, f"endpoint {endpoint} non trovato")
        # individua fine handler: prossimo '@app.' o EOF
        next_app = src.find("\n@app.", ep_idx + 1)
        if next_app < 0:
            next_app = len(src)
        body = src[ep_idx:next_app]
        guard_pos = body.find("GACHA_LIVE_DISABLED_PRE_QA")
        if guard_pos < 0:
            return _fail(name, f"guard non trovato nel corpo di {endpoint}")
        # Cerca pattern update_one con $inc gems
        spend_pattern = re.compile(r'db\.users\.update_one\([^)]*\$inc[^)]*gems', re.DOTALL)
        m = spend_pattern.search(body)
        if m and m.start() < guard_pos:
            return _fail(name, f"gems spend ({m.group(0)[:60]}...) precede il guard in {endpoint}")
    return _ok(name, "guard precede ogni gems spend negli handler gacha")


def check_04_guard_precedes_user_heroes_insert() -> Tuple[bool, str, str]:
    """Il guard gacha deve precedere QUALSIASI db.user_heroes.insert_one(...) negli handler."""
    src = _read("backend/server.py")
    name = "04_GUARD_PRECEDES_USER_HEROES_INSERT"
    for endpoint in ('@app.post("/api/gacha/pull")', '@app.post("/api/gacha/pull10")'):
        ep_idx = src.find(endpoint)
        if ep_idx < 0:
            return _fail(name, f"endpoint {endpoint} non trovato")
        next_app = src.find("\n@app.", ep_idx + 1)
        if next_app < 0:
            next_app = len(src)
        body = src[ep_idx:next_app]
        guard_pos = body.find("GACHA_LIVE_DISABLED_PRE_QA")
        if guard_pos < 0:
            return _fail(name, f"guard non trovato nel corpo di {endpoint}")
        insert_pattern = re.compile(r'db\.user_heroes\.insert_one\(')
        for m in insert_pattern.finditer(body):
            if m.start() < guard_pos:
                return _fail(name, f"user_heroes.insert_one precede il guard in {endpoint}")
        # Anche helper _do_gacha_pull e' indirettamente chiamato DOPO il guard: ok.
    return _ok(name, "nessun user_heroes.insert_one precede il guard negli handler gacha")


def check_05_heroes_gacha_duplicate_dead_code() -> Tuple[bool, str, str]:
    """backend/routes/heroes.py: endpoint gacha REGISTRATI restano quarantined/dead-code.

    Il file contiene anche helper privati non collegati a route (es. `_do_gacha_pull`,
    `_legacy_gacha_pull_dead_code`) preservati come reference UNREACHABLE.
    Il check verifica solo che le ROUTE registrate (@router.post) sollevino
    immediatamente HTTPException 423 con blocker GACHA_DUPLICATE_DEAD_CODE_QUARANTINED
    e che NON contengano gems spend o user_heroes insert prima del raise.
    """
    src = _read("backend/routes/heroes.py")
    name = "05_HEROES_GACHA_DUPLICATE_DEAD_CODE"
    if 'GACHA_DUPLICATE_DEAD_CODE_QUARANTINED' not in src:
        return _fail(name, "blocker GACHA_DUPLICATE_DEAD_CODE_QUARANTINED assente")
    # Per ciascun endpoint registrato verifica che il corpo immediato (fino al
    # prossimo @router. o def helper privato `async def _`) sollevi 423 senza side-effect.
    for ep in ('@router.post("/gacha/pull")', '@router.post("/gacha/pull10")'):
        ep_idx = src.find(ep)
        if ep_idx < 0:
            return _fail(name, f"route {ep} non trovata (atteso quarantine marker)")
        # confine: prossimo decoratore o funzione privata (helper) che NON e' route.
        next_router = src.find("\n    @router.", ep_idx + 1)
        next_helper = src.find("\n    async def _", ep_idx + 1)
        candidates = [c for c in (next_router, next_helper) if c >= 0]
        end = min(candidates) if candidates else (ep_idx + 2500)
        body = src[ep_idx:end]
        if "GACHA_DUPLICATE_DEAD_CODE_QUARANTINED" not in body:
            return _fail(name, f"route {ep} non solleva il blocker dead-code")
        if "raise HTTPException(423" not in body:
            return _fail(name, f"route {ep} non solleva HTTP 423")
        # gems spend / insert NON ammessi nel corpo registrato.
        if re.search(r'db\.users\.update_one\([^)]*\$inc[^)]*gems', body, re.DOTALL):
            return _fail(name, f"route {ep} contiene gems spend prima del guard")
        if 'db.user_heroes.insert_one' in body:
            return _fail(name, f"route {ep} contiene user_heroes.insert_one prima del guard")
    # I helper privati `_legacy_gacha_pull_dead_code` / `_legacy_gacha_pull_10_dead_code`
    # / `_do_gacha_pull` sono ammessi solo se NON registrati come route (verifica negativa).
    illegal_router_for_helper = re.search(r'router\.add_api_route\([^)]*_legacy_gacha_pull', src)
    if illegal_router_for_helper:
        return _fail(name, "helper legacy gacha registrato come route (atteso: unreachable)")
    return _ok(name, "route /gacha/pull e /gacha/pull10 quarantinate dead-code senza side-effect; helper legacy unreachable")


def check_06_pre_battle_lobby_uses_v101_selected_server_id() -> Tuple[bool, str, str]:
    src = _read("frontend/app/pre-battle-lobby.tsx")
    name = "06_PRE_BATTLE_LOBBY_USES_V101_SELECTED_SERVER_ID"
    if "v101_selected_server_id" not in src:
        return _fail(name, "chiave v101_selected_server_id non usata in pre-battle-lobby.tsx")
    if not re.search(r"AsyncStorage\.getItem\(['\"]v101_selected_server_id['\"]\)", src):
        return _fail(name, "AsyncStorage.getItem('v101_selected_server_id') non trovato")
    return _ok(name, "v101_selected_server_id letto via AsyncStorage")


def check_07_pre_battle_lobby_uses_auth_token_compat() -> Tuple[bool, str, str]:
    src = _read("frontend/app/pre-battle-lobby.tsx")
    name = "07_PRE_BATTLE_LOBBY_USES_AUTH_TOKEN_COMPAT"
    if "authTokenCompat" not in src:
        return _fail(name, "modulo authTokenCompat non referenziato")
    if "getAuthTokenCompat" not in src:
        return _fail(name, "funzione getAuthTokenCompat non chiamata")
    return _ok(name, "authTokenCompat + getAuthTokenCompat presenti")


def check_08_pre_battle_lobby_no_expo_secure_store_import() -> Tuple[bool, str, str]:
    src = _read("frontend/app/pre-battle-lobby.tsx")
    name = "08_PRE_BATTLE_LOBBY_NO_EXPO_SECURE_STORE_IMPORT"
    # nessun import statico o dinamico
    if re.search(r'^\s*import\s.+from\s+[\'"]expo-secure-store[\'"]', src, re.MULTILINE):
        return _fail(name, "import statico da 'expo-secure-store' ancora presente")
    if re.search(r'require\([\'"]expo-secure-store[\'"]\)', src):
        return _fail(name, "require('expo-secure-store') ancora presente")
    if re.search(r"import\([\'\"]expo-secure-store[\'\"]\)", src):
        return _fail(name, "dynamic import('expo-secure-store') ancora presente")
    return _ok(name, "nessun import di expo-secure-store (statico/dinamico/require)")


def check_09_pre_battle_lobby_no_securestore_getitem_call() -> Tuple[bool, str, str]:
    src = _read("frontend/app/pre-battle-lobby.tsx")
    name = "09_PRE_BATTLE_LOBBY_NO_SECURESTORE_GETITEMASYNC_CALL"
    if re.search(r'\bSecureStore\.getItemAsync\b', src):
        return _fail(name, "SecureStore.getItemAsync(...) ancora invocato")
    if re.search(r'\bSecureStore\.setItemAsync\b', src):
        return _fail(name, "SecureStore.setItemAsync(...) ancora invocato")
    if re.search(r'\bSecureStore\.deleteItemAsync\b', src):
        return _fail(name, "SecureStore.deleteItemAsync(...) ancora invocato")
    return _ok(name, "nessuna chiamata a SecureStore.*ItemAsync")


def check_10_home_overflow_pack_113_guard_intact() -> Tuple[bool, str, str]:
    """home.tsx contiene HomeOverflowPanel che usa _pushPreQaGuarded + isRouteAllowedInPreQa."""
    home = _read("frontend/app/(tabs)/home.tsx")
    name = "10_HOME_OVERFLOW_PACK_113_GUARD_INTACT"
    if "HomeOverflowPanel" not in home:
        return _fail(name, "HomeOverflowPanel rimosso da home.tsx")
    if "_pushPreQaGuarded" not in home:
        return _fail(name, "_pushPreQaGuarded helper non presente in home.tsx")
    if "isRouteAllowedInPreQa" not in home:
        return _fail(name, "isRouteAllowedInPreQa non utilizzato in home.tsx")
    return _ok(name, "HomeOverflowPanel + _pushPreQaGuarded + isRouteAllowedInPreQa presenti")


def check_11_preqa_nav_guard_blocks_unsafe_routes() -> Tuple[bool, str, str]:
    src = _read("frontend/src/utils/preQaNavGuard.ts")
    name = "11_PREQA_NAV_GUARD_BLOCKS_UNSAFE_ROUTES"
    required_routes = ["/pvp", "/gacha", "/events", "/vip", "/shop", "/guild"]
    for r in required_routes:
        if f"'{r}'" not in src and f'"{r}"' not in src:
            return _fail(name, f"route unsafe {r!r} non bloccata in PRE_QA_BLOCKED_PLAYER_ROUTES")
    if "isRouteAllowedInPreQa" not in src:
        return _fail(name, "isRouteAllowedInPreQa non esportato")
    if "PRE_QA_BLOCKED_PLAYER_ROUTES" not in src:
        return _fail(name, "PRE_QA_BLOCKED_PLAYER_ROUTES non definito")
    return _ok(name, "guard funzionale con route unsafe canoniche bloccate")


def check_12_legacy_battle_routes_quarantined() -> Tuple[bool, str, str]:
    """combat.py: story/pvp/events/tower legacy routes hanno blocker visibile."""
    src = _read("backend/routes/combat.py")
    name = "12_LEGACY_BATTLE_ROUTES_QUARANTINED"
    required_markers = {
        "story": ("Legacy story battle senza server_id quarantineato", "quarantine"),
        "pvp": ("PvP battle legacy account-wide quarantine", "PVP"),
        "events": ("Events battle legacy account-wide quarantine", "EVENTS"),
        "tower": ("TOWER_LEGACY_QUARANTINED", "TOWER"),
    }
    missing = []
    for label, (needle, _tag) in required_markers.items():
        if needle not in src:
            missing.append(f"{label} (marker '{needle}' non trovato)")
    if missing:
        return _fail(name, "marker mancanti: " + "; ".join(missing))
    return _ok(name, "story/pvp/events/tower marker quarantine tutti presenti")


def check_13_achievements_legacy_claim_quarantined() -> Tuple[bool, str, str]:
    src = _read("backend/routes/achievements.py")
    name = "13_ACHIEVEMENTS_LEGACY_CLAIM_QUARANTINED"
    if "ACHIEVEMENT_LEGACY_CLAIM_QUARANTINED" not in src:
        return _fail(name, "blocker ACHIEVEMENT_LEGACY_CLAIM_QUARANTINED assente")
    if "ACHIEVEMENT_LEGACY_CLAIM_ENABLED" not in src:
        return _fail(name, "kill-switch env ACHIEVEMENT_LEGACY_CLAIM_ENABLED assente")
    return _ok(name, "legacy achievement claim quarantinato")


def check_14_team_formation_server_scoped_safe() -> Tuple[bool, str, str]:
    src = _read("backend/routes/v96_team_formation.py")
    name = "14_TEAM_FORMATION_SERVER_SCOPED_SAFE"
    if "pack_88_strict_server_scope" not in src:
        return _fail(name, "marker pack_88_strict_server_scope assente")
    if "PLAYER_SERVER_PROFILE_REQUIRED" not in src and "PLAYER_TEAM_NOT_CONFIGURED_FOR_SERVER" not in src:
        return _fail(name, "blocker scope server-scoped assenti")
    if re.search(r'\.update_one\(.*team_formation', src, re.DOTALL):
        return _fail(name, "endpoint read-only contiene update_one su team_formation")
    return _ok(name, "server-scoped strict, nessun write team_formation")


def check_15_no_bypass_preqanavguard_on_unsafe_routes() -> Tuple[bool, str, str]:
    """Nessun router.push diretto verso route in PRE_QA_BLOCKED_PLAYER_ROUTES senza guard nelle pagine home/menu."""
    name = "15_NO_BYPASS_PREQANAVGUARD_ON_UNSAFE_ROUTES"
    suspect_routes = ["/pvp", "/gacha", "/shop", "/guild", "/events", "/battlepass"]
    targets = [
        "frontend/app/(tabs)/home.tsx",
        "frontend/app/(tabs)/menu.tsx",
    ]
    failures: List[str] = []
    for tgt in targets:
        p = REPO_ROOT / tgt
        if not p.exists():
            continue
        content = p.read_text(encoding="utf-8", errors="ignore")
        for r in suspect_routes:
            # cerca router.push('/route') o router.push("/route")
            for m in re.finditer(r"router\.push\(\s*['\"]" + re.escape(r) + r"(?:[^'\"]*)?['\"]", content):
                # finestra di 200 char prima per vedere se c'e' isRouteAllowedInPreQa o _pushPreQaGuarded
                window_start = max(0, m.start() - 300)
                window = content[window_start: m.end()]
                if "isRouteAllowedInPreQa" not in window and "_pushPreQaGuarded" not in window:
                    failures.append(f"{tgt}: router.push diretto a {r} senza guard")
    if failures:
        return _fail(name, "; ".join(failures[:5]) + (" ..." if len(failures) > 5 else ""))
    return _ok(name, "nessun bypass del preQaNavGuard rilevato in home/menu")


CHECKS_FUNCS = [
    check_01_gacha_pull_blocker,
    check_02_gacha_pull10_blocker,
    check_03_guard_precedes_gems_spend,
    check_04_guard_precedes_user_heroes_insert,
    check_05_heroes_gacha_duplicate_dead_code,
    check_06_pre_battle_lobby_uses_v101_selected_server_id,
    check_07_pre_battle_lobby_uses_auth_token_compat,
    check_08_pre_battle_lobby_no_expo_secure_store_import,
    check_09_pre_battle_lobby_no_securestore_getitem_call,
    check_10_home_overflow_pack_113_guard_intact,
    check_11_preqa_nav_guard_blocks_unsafe_routes,
    check_12_legacy_battle_routes_quarantined,
    check_13_achievements_legacy_claim_quarantined,
    check_14_team_formation_server_scoped_safe,
    check_15_no_bypass_preqanavguard_on_unsafe_routes,
]


def main() -> int:
    print("=" * 78)
    print("PRE_QA_STABILIZATION_114B_GACHA_COMBAT_LOBBY_GUARD_REPAIR — VALIDATOR")
    print("=" * 78)
    passed = 0
    failed = 0
    results = []
    for fn in CHECKS_FUNCS:
        try:
            ok, label, detail = fn()
        except FileNotFoundError as e:
            ok, label, detail = False, fn.__name__, f"FileNotFoundError: {e}"
        except Exception as e:  # pragma: no cover
            ok, label, detail = False, fn.__name__, f"Exception: {type(e).__name__}: {e}"
        status = "PASS" if ok else "FAIL"
        marker = "✓" if ok else "✗"
        print(f"[{marker}] {status:4s} {label}  — {detail}")
        results.append((ok, label, detail))
        if ok:
            passed += 1
        else:
            failed += 1
    print("-" * 78)
    print(f"TOTALE: {passed} PASS, {failed} FAIL su {len(CHECKS_FUNCS)} check.")
    print("Invarianti: DB writes = 0 (validator statico). GACHA_LIVE_ENABLED non modificato.")
    if failed == 0:
        print("VERDETTO: VALIDATOR_PASS — Pack 114B coerente con scope richiesto.")
        return 0
    print("VERDETTO: VALIDATOR_FAIL — drift residuo, vedi dettaglio sopra.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
