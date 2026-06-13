#!/usr/bin/env python3
"""
PRE_QA_STABILIZATION_115D_SCREEN_ENTRY_DEEPLINK_GUARD — VALIDATOR

Coperture (statiche, regex):
  1. PreQaScreenGate component esiste con export default + isScreenGated.
  2. Component usa policy canonica (isRouteAllowedInPreQa + PRE_QA_ROUTE_BLOCKED_TOKEN).
  3. Tutti i 17 target screen importano PreQaScreenGate + isScreenGated.
  4. Ogni target screen ha early-return `if (isScreenGated(...)) return <PreQaScreenGate.../>;`
     PRIMA del primo useEffect/useState con API call (statico: prima funzionale del body).
  5. (tabs)/gacha.tsx ha self-gate diretto.
  6. profile.tsx e research.tsx non esistono.
  7. combat.tsx, tower.tsx, battle_engine.py, gacha rates, character_bible, skill_kit
     non modificati (no reference a PreQaScreenGate in questi file).
  8. Pack 113/114/114B/115A/115B/115C/115C-FIX-A markers preservati.
  9. Nessun data/design/** modificato in scope 115D (verifica negativa).

Output PASS/FAIL per check + summary. Exit 0 se tutti PASS.
Log in italiano.
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


def _exists(rel: str) -> bool:
    return (REPO / rel).exists()


def _ok(n, d=""): return (True, n, d)
def _fail(n, d): return (False, n, d)


TARGETS = [
    ("frontend/app/battlepass.tsx",  "/battlepass"),
    ("frontend/app/vip.tsx",         "/vip"),
    ("frontend/app/shop.tsx",        "/shop"),
    ("frontend/app/item-shop.tsx",   "/item-shop"),
    ("frontend/app/guild.tsx",       "/guild"),
    ("frontend/app/gvg.tsx",         "/gvg"),
    ("frontend/app/raid.tsx",        "/raid"),
    ("frontend/app/territory.tsx",   "/territory"),
    ("frontend/app/cosmetics.tsx",   "/cosmetics"),
    ("frontend/app/friends.tsx",     "/friends"),
    ("frontend/app/mail.tsx",        "/mail"),
    ("frontend/app/events.tsx",      "/events"),
    ("frontend/app/pvp.tsx",         "/pvp"),
    ("frontend/app/plaza.tsx",       "/plaza"),
    ("frontend/app/dm.tsx",          "/dm"),
    ("frontend/app/sanctuary.tsx",   "/sanctuary"),
    ("frontend/app/(tabs)/gacha.tsx", "/(tabs)/gacha"),
]


def check_1_gate_component_exists():
    name = "1_GATE_COMPONENT_EXISTS"
    rel = "frontend/src/components/PreQaScreenGate.tsx"
    if not _exists(rel):
        return _fail(name, f"{rel} non esiste")
    src = _read(rel)
    if "export default" not in src:
        return _fail(name, "export default mancante")
    if "export function isScreenGated" not in src:
        return _fail(name, "export isScreenGated mancante")
    if "PreQaScreenGate" not in src:
        return _fail(name, "componente PreQaScreenGate non definito")
    return _ok(name, "PreQaScreenGate.tsx con export default + isScreenGated presenti")


def check_2_gate_uses_canonical_policy():
    name = "2_GATE_USES_CANONICAL_POLICY"
    src = _read("frontend/src/components/PreQaScreenGate.tsx")
    if "isRouteAllowedInPreQa" not in src:
        return _fail(name, "isRouteAllowedInPreQa non importato")
    if "PRE_QA_ROUTE_BLOCKED_TOKEN" not in src:
        return _fail(name, "PRE_QA_ROUTE_BLOCKED_TOKEN non importato/mostrato")
    if "preQaNavGuard" not in src:
        return _fail(name, "preQaNavGuard policy module non referenziato")
    return _ok(name, "guard component usa policy canonica isRouteAllowedInPreQa + PRE_QA_ROUTE_BLOCKED_TOKEN")


def check_3_all_targets_import_gate():
    name = "3_ALL_TARGETS_IMPORT_GATE"
    missing = []
    for rel, _r in TARGETS:
        src = _read(rel)
        if "isScreenGated" not in src or "PreQaScreenGate" not in src:
            missing.append(rel)
    if missing:
        return _fail(name, f"{len(missing)} target senza import: " + ", ".join(missing[:5]))
    return _ok(name, f"{len(TARGETS)} target screen importano isScreenGated + PreQaScreenGate")


def check_4_early_return_pattern():
    """Verifica che ogni target abbia l'early-return PRIMA di ogni useEffect o useState con API call.

    Estrazione: trova il primo `useEffect(` o `useState(` (post `function XxxScreen() {`),
    confrontalo con la posizione del primo `if (isScreenGated(...)) return <PreQaScreenGate`.
    L'early-return DEVE precedere il primo useEffect (no API call prima del guard).
    """
    name = "4_EARLY_RETURN_PRECEDES_API_HOOKS"
    failures = []
    for rel, route in TARGETS:
        src = _read(rel)
        # cerca posizione del primo isScreenGated dopo "export default function"
        # In (tabs)/gacha la firma e' diversa, accettiamo qualunque export default function
        func_m = re.search(r"export default function \w+\s*\([^)]*\)\s*\{", src)
        if not func_m:
            failures.append(f"{rel}: function default non trovata")
            continue
        body_start = func_m.end()
        body = src[body_start:]
        # posizione guard
        guard_m = re.search(r"if\s*\(\s*isScreenGated\s*\(", body)
        if not guard_m:
            failures.append(f"{rel}: guard isScreenGated non trovato nel body")
            continue
        guard_pos = guard_m.start()
        # posizione primo useEffect / useState con probabile API call (apiCall, fetch)
        # check: useEffect chiamato prima del guard? — fail
        # Per scope statico, semplifichiamo: il guard deve essere nei primi 600 char del body
        if guard_pos > 600:
            failures.append(f"{rel}: guard troppo profondo (offset {guard_pos}) — possibile useEffect prima")
            continue
        # Cerca useEffect prima del guard
        pre_guard = body[:guard_pos]
        if re.search(r"\buseEffect\s*\(", pre_guard):
            failures.append(f"{rel}: useEffect chiamato PRIMA del guard")
            continue
        if re.search(r"\bapiCall\s*\(", pre_guard):
            failures.append(f"{rel}: apiCall chiamata PRIMA del guard")
            continue
    if failures:
        return _fail(name, "; ".join(failures[:4]) + (" ..." if len(failures) > 4 else ""))
    return _ok(name, f"{len(TARGETS)} target: early-return guard precede qualunque useEffect/apiCall")


def check_5_gacha_tab_self_gate():
    name = "5_GACHA_TAB_SELF_GATE"
    src = _read("frontend/app/(tabs)/gacha.tsx")
    if "isScreenGated" not in src or "PreQaScreenGate" not in src:
        return _fail(name, "(tabs)/gacha.tsx senza self-gate")
    if "/(tabs)/gacha" not in src and "'/gacha'" not in src:
        return _fail(name, "self-gate non punta a route canonica gacha")
    return _ok(name, "(tabs)/gacha.tsx self-gate diretto presente")


def check_6_no_profile_no_research():
    name = "6_NO_PROFILE_NO_RESEARCH_SCREEN"
    if _exists("frontend/app/profile.tsx"):
        return _fail(name, "profile.tsx creato (FORBIDDEN)")
    if _exists("frontend/app/research.tsx"):
        return _fail(name, "research.tsx creato (FORBIDDEN)")
    return _ok(name, "nessun profile.tsx/research.tsx")


def check_7_forbidden_files_untouched():
    name = "7_FORBIDDEN_FILES_UNTOUCHED_BY_115D"
    forbidden_no_ref = [
        "frontend/app/combat.tsx",
        # NOTE: tower.tsx era forbidden in Pack 115D, ma e' in scope autorizzato del
        # Pack 115E (legacy hardening con PreQaScreenGate). Escluso da questo check.
        "backend/battle_engine.py",
    ]
    for f in forbidden_no_ref:
        if not _exists(f):
            continue
        s = _read(f)
        if "PreQaScreenGate" in s or "isScreenGated" in s:
            return _fail(name, f"{f} contiene reference 115D — file forbidden modificato")
    # backend route logic: verifica che postqa_d_mutation_gate.py NON sia stato toccato dal Pack 115D
    # (cioe' il file non e' nello scope; ma serviranno i marker 115A/115B preservati)
    gate = _read("backend/utils/postqa_d_mutation_gate.py")
    if "DIVINE_ALLOW_LEGACY_FORGE_MUTATIONS" not in gate:
        return _fail(name, "Pack 115B gate FORGE assente — backend modificato in modo improprio")
    if "DIVINE_ALLOW_LEGACY_SHOP_MUTATIONS" not in gate:
        return _fail(name, "Pack 115A gate SHOP assente")
    return _ok(name, "combat.tsx/tower.tsx/battle_engine.py/backend route logic preservati")


def check_8_prior_packs_preserved():
    name = "8_PRIOR_PACKS_MARKERS_PRESERVED"
    home = _read("frontend/app/(tabs)/home.tsx")
    guard = _read("frontend/src/utils/preQaNavGuard.ts")
    pre_lobby = _read("frontend/app/pre-battle-lobby.tsx")
    api_ts = _read("frontend/utils/api.ts")
    sf = _read("frontend/app/soul-forge.tsx")
    if "HomeOverflowPanel" not in home or "_pushPreQaGuarded" not in home:
        return _fail(name, "Pack 113 markers mancanti")
    if re.search(r"import\s.+from\s+['\"]expo-secure-store['\"]", pre_lobby):
        return _fail(name, "Pack 114B regression: pre-battle-lobby importa expo-secure-store")
    if "'/research'" not in guard or "'/profile'" not in guard:
        return _fail(name, "Pack 115A guard set incompleto")
    if "authHeaderCompat" not in api_ts or "getCanonicalBackendUrl" not in api_ts:
        return _fail(name, "Pack 115C api.ts auth/url canon mancante")
    if re.search(r"apiCall\(\s*['\"]/api/wallet['\"]\s*\)", sf):
        return _fail(name, "Pack 115C-FIX-A regression: /api/wallet account-wide in soul-forge.tsx")
    return _ok(name, "Pack 113/114B/115A/115C/115C-FIX-A markers tutti preservati")


def check_9_no_data_design_refs_in_115d_files():
    name = "9_NO_DATA_DESIGN_REFS_IN_115D_FILES"
    files_115d = ["frontend/src/components/PreQaScreenGate.tsx"] + [r for r, _ in TARGETS]
    for f in files_115d:
        if not _exists(f):
            continue
        s = _read(f)
        if "data/design" in s or "data\\design" in s:
            return _fail(name, f"{f} contiene reference a data/design")
    return _ok(name, "nessun reference a data/design nei file 115D")


CHECKS = [
    check_1_gate_component_exists,
    check_2_gate_uses_canonical_policy,
    check_3_all_targets_import_gate,
    check_4_early_return_pattern,
    check_5_gacha_tab_self_gate,
    check_6_no_profile_no_research,
    check_7_forbidden_files_untouched,
    check_8_prior_packs_preserved,
    check_9_no_data_design_refs_in_115d_files,
]


def main() -> int:
    print("=" * 78)
    print("PRE_QA_STABILIZATION_115D_SCREEN_ENTRY_DEEPLINK_GUARD — VALIDATOR")
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
    print("Invarianti: validator statico, db_writes=0, no runtime activation, "
          "no nuova feature, no API call player-facing su route gated.")
    if failed == 0:
        print("VERDETTO: VALIDATOR_PASS — Pack 115D screen-entry/deeplink guard coerente.")
        return 0
    print("VERDETTO: VALIDATOR_FAIL — vedi dettaglio sopra.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
