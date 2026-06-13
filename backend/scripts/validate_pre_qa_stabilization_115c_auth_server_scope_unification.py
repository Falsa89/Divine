#!/usr/bin/env python3
"""
PRE_QA_STABILIZATION_115C_AUTH_SERVER_SCOPE_UNIFICATION — VALIDATOR

Coperture (statiche, regex/AST/grep):
  1. api.ts usa authTokenCompat e non legge piu' direttamente AsyncStorage.getItem('token').
  2. backendUrl.ts canonical helper esiste ed e' usato da api.ts.
  3. servers.tsx usa getCanonicalBackendUrl (helper canonico).
  4. login.tsx route post-login -> '/servers' (non '/(tabs)/menu'), CTA inclusa.
  5. useServerScope mantiene no-silent-s1 e ha refresh oltre il mount (AppState 'active' o focus).
  6. Player-facing files NO fallback pattern account-wide:
     - heroes.tsx, hero-collection.tsx, battle.tsx, story.tsx, soul-forge.tsx, select-home-hero.tsx
  7. battle.tsx non chiama piu' apiCall('/api/team') e USA /api/team/get-formation?server_id=.
  8. battle.tsx NON chiama /api/team/update-formation come save path normale.
  9. select-home-hero.tsx NON POST a /api/sanctuary/home-hero in pre-QA.
  10. Pack 113/114/114B/115A/115B markers preservati (no regression).

Tutte le verifiche STATICHE. Nessun DB write. Log in italiano.
"""
from __future__ import annotations
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

REPO = Path(__file__).resolve().parents[2]


def _read(rel: str) -> str:
    p = REPO / rel
    if not p.exists():
        raise FileNotFoundError(rel)
    return p.read_text(encoding="utf-8", errors="strict")


def _ok(n, d=""): return (True, n, d)
def _fail(n, d): return (False, n, d)


def check_1_apicall_uses_auth_token_compat():
    src = _read("frontend/utils/api.ts")
    name = "1_API_CALL_USES_AUTH_TOKEN_COMPAT"
    if "authTokenCompat" not in src or "authHeaderCompat" not in src:
        return _fail(name, "api.ts non importa authTokenCompat/authHeaderCompat")
    # Direct AsyncStorage.getItem('token') NON deve esserci.
    if re.search(r"AsyncStorage\.getItem\(\s*['\"]token['\"]\s*\)", src):
        return _fail(name, "api.ts contiene ancora AsyncStorage.getItem('token') diretto")
    # Non importare AsyncStorage da @react-native-async-storage in api.ts
    if "@react-native-async-storage/async-storage" in src:
        return _fail(name, "api.ts importa ancora AsyncStorage direttamente")
    # No token log raw
    if re.search(r"console\.(log|warn|error)\([^)]*token", src, re.IGNORECASE):
        return _fail(name, "possibile token log in api.ts")
    return _ok(name, "api.ts usa authHeaderCompat, no AsyncStorage diretto, no token logs")


def check_2_backendurl_helper_exists():
    name = "2_BACKEND_URL_CANONICAL_HELPER_EXISTS"
    src_path = "frontend/src/utils/backendUrl.ts"
    if not (REPO / src_path).exists():
        return _fail(name, f"{src_path} non esiste")
    src = _read(src_path)
    if "export function getCanonicalBackendUrl" not in src:
        return _fail(name, "export getCanonicalBackendUrl assente")
    if "EXPO_BACKEND_URL" not in src:
        return _fail(name, "EXPO_BACKEND_URL non referenziato (necessario per parita' con servers.tsx)")
    if "Platform.OS === 'web'" not in src:
        return _fail(name, "comportamento web relative URL assente")
    return _ok(name, "backendUrl.ts helper canonico operativo")


def check_3_api_uses_backendurl_helper():
    src = _read("frontend/utils/api.ts")
    name = "3_API_USES_CANONICAL_BACKEND_URL"
    if "getCanonicalBackendUrl" not in src:
        return _fail(name, "api.ts non importa getCanonicalBackendUrl")
    if "backendUrl" not in src:
        return _fail(name, "api.ts non referenzia il modulo backendUrl")
    return _ok(name, "api.ts usa getCanonicalBackendUrl")


def check_4_servers_uses_backendurl_helper():
    src = _read("frontend/app/servers.tsx")
    name = "4_SERVERS_USES_CANONICAL_BACKEND_URL"
    if "getCanonicalBackendUrl" not in src:
        return _fail(name, "servers.tsx non importa getCanonicalBackendUrl")
    # logica divergente (process.env.EXPO_BACKEND_URL fallback inline) deve essere assente
    if re.search(r"const\s+BACKEND_URL\s*=\s*\(?\s*process\.env\.EXPO_BACKEND_URL", src):
        return _fail(name, "servers.tsx mantiene ancora logica BACKEND_URL inline divergente")
    return _ok(name, "servers.tsx usa helper canonico")


def check_5_login_routes_to_servers():
    src = _read("frontend/app/login.tsx")
    name = "5_LOGIN_ROUTES_TO_SERVERS_NOT_TABS_MENU"
    # Conta direct push a '/(tabs)/menu' (non devono esistere piu')
    bad = list(re.finditer(r"router\.replace\(\s*['\"]\/\(tabs\)\/menu['\"]", src))
    if bad:
        return _fail(name, f"trovati {len(bad)} router.replace('/(tabs)/menu') ancora presenti")
    # Conferma route a /servers
    good_count = len(re.findall(r"router\.replace\(\s*['\"]\/servers['\"]", src))
    if good_count < 4:
        return _fail(name, f"router.replace('/servers') trovati solo {good_count} (atteso >=4: 3 login + 1 CTA)")
    return _ok(name, f"{good_count} route a /servers; nessun route a /(tabs)/menu")


def check_6_useserverscope_refresh_and_no_silent_s1():
    src = _read("frontend/src/hooks/useServerScope.ts")
    name = "6_USE_SERVER_SCOPE_NO_SILENT_S1_AND_REFRESHES"
    if "s1" in src.lower().replace("storage", "").replace("AsyncStorage", "").replace("storageId", ""):
        # check piu' preciso: deve esserci il flag esplicito
        pass
    if "no_silent_s1_fallback" not in src:
        return _fail(name, "no_silent_s1_fallback flag assente")
    if "AppState" not in src:
        return _fail(name, "AppState refresh assente (refresh oltre il mount non implementato)")
    if "addEventListener" not in src:
        return _fail(name, "AppState.addEventListener non chiamato (no refresh on active)")
    if "v101_selected_server_id" not in src:
        return _fail(name, "key canonica v101_selected_server_id assente")
    if "v102_selected_server_name" not in src:
        return _fail(name, "key v102_selected_server_name assente")
    return _ok(name, "no silent s1 + refresh on AppState active + key canoniche")


def check_7_no_account_wide_fallbacks():
    name = "7_NO_ACCOUNT_WIDE_FALLBACKS_PLAYER_FACING"
    files_to_check = [
        ("frontend/app/(tabs)/heroes.tsx", ["/api/user/heroes"]),
        ("frontend/app/(tabs)/battle.tsx", ["/api/user/heroes", "apiCall('/api/team')"]),
        ("frontend/app/hero-collection.tsx", ["/api/user/heroes"]),
        ("frontend/app/story.tsx", ["/api/story/chapters"]),
        ("frontend/app/soul-forge.tsx", ["/api/user/heroes", "/api/wallet", "/api/team"]),
        ("frontend/app/select-home-hero.tsx", ["/api/user/heroes", "/api/sanctuary/home-hero"]),
    ]
    # Pattern fallback "ternary or string literal as fallback"
    fallback_patterns = [
        r"\?\s*`/api/user/heroes\?server_id=[^`]+`\s*:\s*['\"]/api/user/heroes['\"]",
        r"\?\s*`/api/story/chapters\?server_id=[^`]+`\s*:\s*['\"]/api/story/chapters['\"]",
        r"\?\s*`/api/wallet\?server_id=[^`]+`\s*:\s*['\"]/api/wallet['\"]",
    ]
    failures = []
    for rel, endpoints in files_to_check:
        src = _read(rel)
        for pat in fallback_patterns:
            m = re.search(pat, src)
            if m:
                failures.append(f"{rel}: fallback pattern presente '{m.group(0)[:60]}...'")
    if failures:
        return _fail(name, "; ".join(failures[:4]))
    return _ok(name, "nessun fallback ternary account-wide nelle 6 schermate player-facing")


def check_8_battle_uses_get_formation_strict():
    src = _read("frontend/app/(tabs)/battle.tsx")
    name = "8_BATTLE_USES_GET_FORMATION_SERVER_SCOPED"
    if "apiCall('/api/team')" in src or 'apiCall("/api/team")' in src:
        return _fail(name, "battle.tsx contiene ancora apiCall('/api/team') account-wide")
    if "/api/team/get-formation?server_id=" not in src:
        return _fail(name, "battle.tsx non chiama /api/team/get-formation?server_id=")
    return _ok(name, "battle.tsx usa /api/team/get-formation server-scoped, niente /api/team account-wide")


def check_9_battle_no_update_formation_save():
    src = _read("frontend/app/(tabs)/battle.tsx")
    name = "9_BATTLE_NO_UPDATE_FORMATION_AS_NORMAL_SAVE"
    # Cerca chiamate POST a /api/team/update-formation come operazione attiva
    # (non semplici commenti/stringhe).
    if re.search(r"apiCall\(\s*['\"]/api/team/update-formation['\"]", src):
        return _fail(name, "battle.tsx contiene ancora apiCall('/api/team/update-formation')")
    if not re.search(r"TEAM_FORMATION_SAVE_DEFERRED_PRE_QA|in preparazione|deferred", src, re.IGNORECASE):
        return _fail(name, "battle.tsx save non mostra messaggio deferred")
    return _ok(name, "battle.tsx save deferred; nessuna chiamata update-formation")


def check_10_select_home_hero_no_post_sanctuary():
    src = _read("frontend/app/select-home-hero.tsx")
    name = "10_SELECT_HOME_HERO_NO_POST_SANCTUARY_PLAYER_FACING"
    if re.search(r"apiCall\(\s*['\"]/api/sanctuary/home-hero['\"][^)]*method:\s*['\"]POST['\"]", src, re.DOTALL):
        return _fail(name, "select-home-hero.tsx contiene ancora POST a /api/sanctuary/home-hero")
    # Verifica messaggio deferred presente
    if "SANCTUARY_HOME_HERO_DEFERRED_PRE_QA" not in src and "in preparazione" not in src:
        return _fail(name, "select-home-hero.tsx senza messaggio deferred chiaro")
    return _ok(name, "select-home-hero.tsx POST sanctuary disattivato; messaggio deferred presente")


def check_11_prior_packs_preserved():
    name = "11_PRIOR_PACKS_MARKERS_PRESERVED"
    home = _read("frontend/app/(tabs)/home.tsx")
    guard = _read("frontend/src/utils/preQaNavGuard.ts")
    gate = _read("backend/utils/postqa_d_mutation_gate.py")
    pre_lobby = _read("frontend/app/pre-battle-lobby.tsx")
    # Pack 113
    if "HomeOverflowPanel" not in home or "_pushPreQaGuarded" not in home:
        return _fail(name, "Pack 113 markers (HomeOverflowPanel/_pushPreQaGuarded) mancanti in home.tsx")
    # Pack 114B — pre-battle-lobby no expo-secure-store import
    if re.search(r"import\s.+from\s+['\"]expo-secure-store['\"]", pre_lobby):
        return _fail(name, "Pack 114B regression: pre-battle-lobby.tsx importa expo-secure-store")
    # Pack 115A
    if "'/research'" not in guard or "'/profile'" not in guard:
        return _fail(name, "Pack 115A guard set mancante (/research o /profile)")
    if "DIVINE_ALLOW_LEGACY_SHOP_MUTATIONS" not in gate:
        return _fail(name, "Pack 115A gate SHOP mancante")
    # Pack 115B
    if "DIVINE_ALLOW_LEGACY_FORGE_MUTATIONS" not in gate:
        return _fail(name, "Pack 115B gate FORGE mancante")
    return _ok(name, "Pack 113/114B/115A/115B markers tutti preservati")


def check_12_soul_forge_no_account_wide_wallet_call():
    """Pack 115C-FIX-A — soul-forge.tsx NON deve mai chiamare /api/wallet senza server_id."""
    src = _read("frontend/app/soul-forge.tsx")
    name = "12_SOUL_FORGE_NO_ACCOUNT_WIDE_WALLET_CALL"
    # Cerca qualsiasi apiCall('/api/wallet') o apiCall("/api/wallet") senza
    # query string. Pattern stringente: apiCall + (whitespace) + ('/api/wallet').
    # NON deve esserci `?server_id=` o backtick template literal in qualunque
    # chiamata wallet.
    for m in re.finditer(r"apiCall\(\s*['\"]/api/wallet['\"]\s*\)", src):
        return _fail(name, f"trovata chiamata raw apiCall('/api/wallet') senza server_id (offset {m.start()})")
    # Pattern stringa template senza server_id: `/api/wallet`  (no query)
    for m in re.finditer(r"apiCall\(\s*`/api/wallet`\s*\)", src):
        return _fail(name, f"trovata chiamata template raw apiCall(`/api/wallet`) (offset {m.start()})")
    # Pattern ternary: `/api/wallet?...` : '/api/wallet' — vietato il path account-wide come fallback
    if re.search(r"['\"]/api/wallet['\"](?!\?)", src):
        # Permette comunque la stringa solo se costituisce parte di una URL completa server-scoped.
        # Verifica: ogni occorrenza di '/api/wallet' (no query) deve essere preceduta da
        # un check `selected_server_id ?` (template) o ignorata come commento.
        for m in re.finditer(r"['\"]/api/wallet['\"]", src):
            # Skip se preceduta da backtick (template literal con query subito dopo)
            ctx = src[max(0, m.start() - 60):m.end() + 30]
            # Se il match e' seguito da `?server_id` o e' parte di un template `${...}/api/wallet?server_id`, ok
            following = src[m.end():m.end() + 30]
            if "?server_id=" in following:
                continue
            # Se il pattern e' "/api/wallet?" all'interno di un template, ok
            if "?server_id=" in ctx and "`" in ctx:
                continue
            # Altrimenti, e' un fallback account-wide
            # tollera solo se la riga e' un commento (// or /*)
            line_start = src.rfind('\n', 0, m.start()) + 1
            line = src[line_start:m.end()]
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('*') or stripped.startswith('/*'):
                continue
            # Se la riga contiene 'Promise.reject' o 'NO_SERVER_SELECTED' significa
            # che e' lo skip esplicito fail-closed, ok
            if 'NO_SERVER_SELECTED' in line or 'Promise.reject' in line:
                continue
            return _fail(name, f"trovata stringa raw '/api/wallet' non server-scoped (riga: {line.strip()[:80]})")
    return _ok(name, "soul-forge.tsx: nessuna chiamata wallet account-wide (initial load + post-success refresh entrambi server-scoped)")


CHECKS = [
    check_1_apicall_uses_auth_token_compat,
    check_2_backendurl_helper_exists,
    check_3_api_uses_backendurl_helper,
    check_4_servers_uses_backendurl_helper,
    check_5_login_routes_to_servers,
    check_6_useserverscope_refresh_and_no_silent_s1,
    check_7_no_account_wide_fallbacks,
    check_8_battle_uses_get_formation_strict,
    check_9_battle_no_update_formation_save,
    check_10_select_home_hero_no_post_sanctuary,
    check_11_prior_packs_preserved,
    check_12_soul_forge_no_account_wide_wallet_call,
]


def main() -> int:
    print("=" * 78)
    print("PRE_QA_STABILIZATION_115C_AUTH_SERVER_SCOPE_UNIFICATION — VALIDATOR")
    print("=" * 78)
    passed = failed = 0
    for fn in CHECKS:
        try:
            ok, label, detail = fn()
        except FileNotFoundError as e:
            ok, label, detail = False, fn.__name__, f"FileNotFoundError: {e}"
        except Exception as e:
            ok, label, detail = False, fn.__name__, f"Exception: {type(e).__name__}: {e}"
        marker = "✓" if ok else "✗"
        status = "PASS" if ok else "FAIL"
        print(f"[{marker}] {status:4s} {label}  — {detail}")
        if ok: passed += 1
        else:  failed += 1
    print("-" * 78)
    print(f"TOTALE: {passed} PASS, {failed} FAIL su {len(CHECKS)} check.")
    print("Invarianti: validator statico, db_writes=0, no token logs, "
          "no nuova UI/feature/server-scoped team-save introdotto.")
    if failed == 0:
        print("VERDETTO: VALIDATOR_PASS — Pack 115C auth/server-scope coerente.")
        return 0
    print("VERDETTO: VALIDATOR_FAIL — vedi dettaglio sopra.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
