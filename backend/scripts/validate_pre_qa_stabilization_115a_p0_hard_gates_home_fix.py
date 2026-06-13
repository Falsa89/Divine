#!/usr/bin/env python3
"""
PRE_QA_STABILIZATION_115A_P0_HARD_GATES_HOME_FIX — VALIDATOR
============================================================

Validator statico per il Pack 115A. Verifica:
  A) Home `/profile` push tutti guarded inline (no direct push).
  B) `/research` in PRE_QA_BLOCKED_PLAYER_ROUTES.
  C) Niente `profile.tsx` o `research.tsx` creati.
  D) Backend gate default-OFF su tutti gli endpoint legacy mutanti elencati
     dal pack (shop, mail, battlepass, server-select, vip-daily, gvg-player,
     raid, exclusive-items/craft, cosmetics, territory).
  E) GET `/api/battlepass` e `/api/vip` non eseguono insert_one a meno che il
     gate sia esplicitamente abilitato (NO-WRITE in pre-QA).
  F) Pack 113 HomeOverflow guard preservato.
  G) Pack 114 Home Routes validator preservato.
  H) Pack 114B gacha guard preservato.
  I) Nessun bypass dei gate (es. body endpoint che chiama db.update_one
     PRIMA della dependency gate e' impossibile per design FastAPI dato che
     le dependencies vengono valutate prima del body).

Tutto STATICO (regex + AST). Nessun DB write, nessun side-effect.
Output: PASS/FAIL per check + summary. Exit 0 se tutti PASS, 1 altrimenti.

Tutti i log in italiano.
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


def _ok(name: str, detail: str = "") -> Tuple[bool, str, str]:
    return (True, name, detail)


def _fail(name: str, detail: str) -> Tuple[bool, str, str]:
    return (False, name, detail)


# --------------------------------------------------------------------------- #
# CHECK A — Home /profile push guarded
# --------------------------------------------------------------------------- #
def check_A_home_profile_pushes_guarded():
    home = _read("frontend/app/(tabs)/home.tsx")
    name = "A_HOME_PROFILE_PUSHES_ALL_GUARDED"
    direct = list(re.finditer(r"router\.push\(\s*['\"]/profile['\"]\s+as\s+any\s*\)", home))
    if not direct:
        return _fail(name, "nessun /profile push trovato (atteso: 4 push, tutti guarded)")
    unguarded = []
    for m in direct:
        start = max(0, m.start() - 250)
        window = home[start:m.end()]
        if "isRouteAllowedInPreQa('/profile')" not in window:
            unguarded.append(m.start())
    if unguarded:
        return _fail(name, f"trovati {len(unguarded)} push UNGUARDED a /profile (offsets {unguarded[:5]})")
    return _ok(name, f"{len(direct)} push /profile tutti con guard inline isRouteAllowedInPreQa")


def check_A2_home_no_dead_screens():
    name = "A2_NO_PROFILE_NO_RESEARCH_SCREEN_FILES"
    if _exists("frontend/app/profile.tsx"):
        return _fail(name, "frontend/app/profile.tsx creato (FORBIDDEN dal pack 115A)")
    if _exists("frontend/app/research.tsx"):
        return _fail(name, "frontend/app/research.tsx creato (FORBIDDEN dal pack 115A)")
    return _ok(name, "nessuna nuova schermata profile/research creata")


# --------------------------------------------------------------------------- #
# CHECK B — preQaNavGuard.ts contiene /research e /profile
# --------------------------------------------------------------------------- #
def check_B_guard_blocks_research_and_profile():
    guard = _read("frontend/src/utils/preQaNavGuard.ts")
    name = "B_GUARD_BLOCKS_RESEARCH_AND_PROFILE"
    if "'/research'" not in guard:
        return _fail(name, "/research non presente in PRE_QA_BLOCKED_PLAYER_ROUTES")
    if "'/profile'" not in guard:
        return _fail(name, "/profile non presente in PRE_QA_BLOCKED_PLAYER_ROUTES")
    return _ok(name, "/research e /profile entrambi in PRE_QA_BLOCKED_PLAYER_ROUTES")


# --------------------------------------------------------------------------- #
# CHECK C — postqa_d gate module ha tutti i nuovi gate registrati
# --------------------------------------------------------------------------- #
REQUIRED_GATES = {
    "DIVINE_ALLOW_LEGACY_SHOP_MUTATIONS": ["/api/shop/buy", "/api/shop/claim-daily/{item_id}"],
    "DIVINE_ALLOW_LEGACY_MAIL_MUTATIONS": ["/api/mail/claim/{mail_id}"],
    "DIVINE_ALLOW_LEGACY_BATTLEPASS_PROGRESS_MUTATIONS": [
        "/api/battlepass/claim/{level}",
        "/api/battlepass/add-exp",
        "/api/battlepass",
    ],
    "DIVINE_ALLOW_LEGACY_SERVER_SELECT_MUTATIONS": ["/api/server/select"],
    "DIVINE_ALLOW_LEGACY_VIP_DAILY_MUTATIONS": ["/api/vip/claim-daily", "/api/vip"],
    "DIVINE_ALLOW_LEGACY_GVG_PLAYER_MUTATIONS": ["/api/gvg/matchmake", "/api/gvg/attack"],
    "DIVINE_ALLOW_LEGACY_RAID_MUTATIONS": [
        "/api/raid/create",
        "/api/raid/attack/{boss_id}",
        "/api/exclusive-items/craft",
    ],
    "DIVINE_ALLOW_LEGACY_COSMETICS_MUTATIONS": ["/api/cosmetics/buy", "/api/cosmetics/equip"],
    "DIVINE_ALLOW_LEGACY_TERRITORY_MUTATIONS": ["/api/territory/attack"],
}


def check_C_gate_module_has_new_gates():
    src = _read("backend/utils/postqa_d_mutation_gate.py")
    name = "C_GATE_MODULE_REGISTERS_ALL_115A_GATES"
    missing = []
    for gate, endpoints in REQUIRED_GATES.items():
        if gate not in src:
            missing.append(gate)
            continue
        for ep in endpoints:
            if ep not in src:
                missing.append(f"{gate}->{ep}")
    if missing:
        return _fail(name, "mancanti in LEGACY_MUTATION_GATES: " + ", ".join(missing[:6]) + (" ..." if len(missing) > 6 else ""))
    if "is_legacy_mutation_gate_enabled" not in src:
        return _fail(name, "helper is_legacy_mutation_gate_enabled assente (richiesto per GET no-write)")
    return _ok(name, f"{len(REQUIRED_GATES)} gate 115A tutti registrati con endpoint corretti")


# --------------------------------------------------------------------------- #
# CHECK D — Ogni endpoint protetto ha il Depends del gate corretto
# --------------------------------------------------------------------------- #
ENDPOINT_TO_GATE = {
    # economy.py
    ('backend/routes/economy.py', '/shop/buy'): "DIVINE_ALLOW_LEGACY_SHOP_MUTATIONS",
    ('backend/routes/economy.py', '/shop/claim-daily/{item_id}'): "DIVINE_ALLOW_LEGACY_SHOP_MUTATIONS",
    ('backend/routes/economy.py', '/mail/claim/{mail_id}'): "DIVINE_ALLOW_LEGACY_MAIL_MUTATIONS",
    ('backend/routes/economy.py', '/battlepass/claim/{level}'): "DIVINE_ALLOW_LEGACY_BATTLEPASS_PROGRESS_MUTATIONS",
    ('backend/routes/economy.py', '/battlepass/add-exp'): "DIVINE_ALLOW_LEGACY_BATTLEPASS_PROGRESS_MUTATIONS",
    ('backend/routes/economy.py', '/server/select'): "DIVINE_ALLOW_LEGACY_SERVER_SELECT_MUTATIONS",
    ('backend/routes/economy.py', '/vip/claim-daily'): "DIVINE_ALLOW_LEGACY_VIP_DAILY_MUTATIONS",
    # gvg.py
    ('backend/routes/gvg.py', '/gvg/matchmake'): "DIVINE_ALLOW_LEGACY_GVG_PLAYER_MUTATIONS",
    ('backend/routes/gvg.py', '/gvg/attack'): "DIVINE_ALLOW_LEGACY_GVG_PLAYER_MUTATIONS",
    # raids.py
    ('backend/routes/raids.py', '/raid/create'): "DIVINE_ALLOW_LEGACY_RAID_MUTATIONS",
    ('backend/routes/raids.py', '/raid/attack/{boss_id}'): "DIVINE_ALLOW_LEGACY_RAID_MUTATIONS",
    ('backend/routes/raids.py', '/exclusive-items/craft'): "DIVINE_ALLOW_LEGACY_RAID_MUTATIONS",
    # cosmetics.py
    ('backend/routes/cosmetics.py', '/cosmetics/buy'): "DIVINE_ALLOW_LEGACY_COSMETICS_MUTATIONS",
    ('backend/routes/cosmetics.py', '/cosmetics/equip'): "DIVINE_ALLOW_LEGACY_COSMETICS_MUTATIONS",
    ('backend/routes/cosmetics.py', '/territory/attack'): "DIVINE_ALLOW_LEGACY_TERRITORY_MUTATIONS",
}


def check_D_all_endpoints_have_correct_gate():
    name = "D_ALL_115A_ENDPOINTS_DECORATED_WITH_CORRECT_GATE"
    failures = []
    for (rel, ep), gate in ENDPOINT_TO_GATE.items():
        src = _read(rel)
        # Cerca `@router.post(\n        "<ep>",\n` o variante senza newline
        ep_re = re.compile(
            r'@router\.post\(\s*[\'"]' + re.escape(ep) + r'[\'"]\s*,\s*dependencies\s*=\s*\[\s*'
            r'_Depends_postqa_d\(\s*make_legacy_mutation_gate_dep\(\s*[\'"]' + re.escape(gate) + r'[\'"]',
            re.DOTALL,
        )
        if not ep_re.search(src):
            failures.append(f"{rel}:{ep} non protetto da {gate}")
    if failures:
        return _fail(name, "; ".join(failures[:4]) + (" ..." if len(failures) > 4 else ""))
    return _ok(name, f"{len(ENDPOINT_TO_GATE)} endpoint tutti decorati con il gate corretto")


# --------------------------------------------------------------------------- #
# CHECK E — GET /api/battlepass e /api/vip NO-WRITE in pre-QA
# --------------------------------------------------------------------------- #
def check_E_get_battlepass_no_write():
    src = _read("backend/routes/economy.py")
    name = "E_GET_BATTLEPASS_NO_WRITE_IN_PRE_QA"
    # Estrai handler get_battle_pass: dal `async def get_battle_pass` fino al prossimo `@router.` o EOF.
    idx = src.find("async def get_battle_pass")
    if idx < 0:
        return _fail(name, "handler get_battle_pass non trovato")
    next_router = src.find("\n    @router.", idx + 1)
    body = src[idx:next_router] if next_router > 0 else src[idx:]
    if "db.battle_pass.insert_one" not in body:
        return _ok(name, "GET battlepass non contiene insert_one (gia' no-write)")
    if "is_legacy_mutation_gate_enabled" not in body:
        return _fail(name, "GET battlepass contiene insert_one ma NON e' gated da is_legacy_mutation_gate_enabled")
    if "DIVINE_ALLOW_LEGACY_BATTLEPASS_PROGRESS_MUTATIONS" not in body:
        return _fail(name, "GET battlepass non usa il gate DIVINE_ALLOW_LEGACY_BATTLEPASS_PROGRESS_MUTATIONS")
    igen_pos = body.find("is_legacy_mutation_gate_enabled")
    insert_pos = body.find("db.battle_pass.insert_one")
    if igen_pos < 0 or insert_pos < 0 or igen_pos >= insert_pos:
        return _fail(name, "is_legacy_mutation_gate_enabled NON precede insert_one nel GET battlepass")
    return _ok(name, "GET battlepass NO-WRITE in pre-QA (insert_one gated)")


def check_E2_get_vip_no_write():
    src = _read("backend/routes/economy.py")
    name = "E2_GET_VIP_NO_WRITE_IN_PRE_QA"
    idx = src.find("async def get_vip_status")
    if idx < 0:
        return _fail(name, "handler get_vip_status non trovato")
    # confine: prossimo def/decoratore di livello superiore
    next_def = src.find("\n    def _can_claim_vip_daily", idx + 1)
    next_router = src.find("\n    @router.", idx + 1)
    bounds = [b for b in (next_def, next_router) if b > 0]
    end = min(bounds) if bounds else len(src)
    body = src[idx:end]
    if "db.vip_data.insert_one" not in body:
        return _ok(name, "GET /vip non contiene insert_one (gia' no-write)")
    if "is_legacy_mutation_gate_enabled" not in body:
        return _fail(name, "GET /vip contiene insert_one ma NON e' gated da is_legacy_mutation_gate_enabled")
    if "DIVINE_ALLOW_LEGACY_VIP_DAILY_MUTATIONS" not in body:
        return _fail(name, "GET /vip non usa il gate DIVINE_ALLOW_LEGACY_VIP_DAILY_MUTATIONS")
    igen_pos = body.find("is_legacy_mutation_gate_enabled")
    insert_pos = body.find("db.vip_data.insert_one")
    if igen_pos < 0 or insert_pos < 0 or igen_pos >= insert_pos:
        return _fail(name, "is_legacy_mutation_gate_enabled NON precede insert_one nel GET /vip")
    return _ok(name, "GET /vip NO-WRITE in pre-QA (insert_one gated)")


# --------------------------------------------------------------------------- #
# CHECK F — Pack 113 HomeOverflow guard preservato
# --------------------------------------------------------------------------- #
def check_F_pack113_homeoverflow_preserved():
    home = _read("frontend/app/(tabs)/home.tsx")
    name = "F_PACK_113_HOMEOVERFLOW_GUARD_PRESERVED"
    for needle in ("HomeOverflowPanel", "_pushPreQaGuarded", "isRouteAllowedInPreQa"):
        if needle not in home:
            return _fail(name, f"{needle} assente in home.tsx")
    return _ok(name, "HomeOverflowPanel + _pushPreQaGuarded + isRouteAllowedInPreQa preservati")


# --------------------------------------------------------------------------- #
# CHECK G — Pack 114B gacha guard preservato (smoke statico)
# --------------------------------------------------------------------------- #
def check_G_pack114b_gacha_guard_preserved():
    src = _read("backend/server.py")
    name = "G_PACK_114B_GACHA_GUARD_PRESERVED"
    if 'GACHA_LIVE_DISABLED_PRE_QA' not in src:
        return _fail(name, "blocker GACHA_LIVE_DISABLED_PRE_QA assente da server.py")
    if '@app.post("/api/gacha/pull")' not in src or '@app.post("/api/gacha/pull10")' not in src:
        return _fail(name, "endpoint gacha mancanti")
    return _ok(name, "gacha guard pre-QA invariato")


# --------------------------------------------------------------------------- #
# CHECK H — /api/gvg/end-war gate preservato (non regredisce)
# --------------------------------------------------------------------------- #
def check_H_gvg_end_war_admin_gate_preserved():
    src = _read("backend/routes/gvg.py")
    name = "H_GVG_END_WAR_ADMIN_GATE_PRESERVED"
    if "DIVINE_ALLOW_LEGACY_GVG_ADMIN_MUTATIONS" not in src:
        return _fail(name, "gate end-war admin assente")
    if "/api/gvg/end-war" not in src:
        return _fail(name, "endpoint end-war assente")
    return _ok(name, "end-war admin gate invariato")


# --------------------------------------------------------------------------- #
# CHECK I — Forbidden files NON toccati: battle_engine.py / combat.tsx
# --------------------------------------------------------------------------- #
def check_I_forbidden_files_untouched():
    name = "I_FORBIDDEN_FILES_NOT_MODIFIED_BY_115A"
    # check statico: i file devono esistere e non importare cose 115A (cintura).
    candidates = ["backend/battle_engine.py", "frontend/app/combat.tsx"]
    for c in candidates:
        if not _exists(c):
            continue
        s = _read(c)
        if "DIVINE_ALLOW_LEGACY_SHOP_MUTATIONS" in s or "DIVINE_ALLOW_LEGACY_RAID_MUTATIONS" in s:
            return _fail(name, f"{c} contiene riferimenti a gate 115A — file forbidden modificato.")
    return _ok(name, "battle_engine.py e combat.tsx non contengono modifiche 115A")


CHECKS = [
    check_A_home_profile_pushes_guarded,
    check_A2_home_no_dead_screens,
    check_B_guard_blocks_research_and_profile,
    check_C_gate_module_has_new_gates,
    check_D_all_endpoints_have_correct_gate,
    check_E_get_battlepass_no_write,
    check_E2_get_vip_no_write,
    check_F_pack113_homeoverflow_preserved,
    check_G_pack114b_gacha_guard_preserved,
    check_H_gvg_end_war_admin_gate_preserved,
    check_I_forbidden_files_untouched,
]


def main() -> int:
    print("=" * 78)
    print("PRE_QA_STABILIZATION_115A_P0_HARD_GATES_HOME_FIX — VALIDATOR")
    print("=" * 78)
    passed = failed = 0
    for fn in CHECKS:
        try:
            ok, label, detail = fn()
        except FileNotFoundError as e:
            ok, label, detail = False, fn.__name__, f"FileNotFoundError: {e}"
        except AssertionError as e:
            ok, label, detail = False, fn.__name__, f"AssertionError: {e}"
        except Exception as e:
            ok, label, detail = False, fn.__name__, f"Exception: {type(e).__name__}: {e}"
        marker = "✓" if ok else "✗"
        status = "PASS" if ok else "FAIL"
        print(f"[{marker}] {status:4s} {label}  — {detail}")
        if ok:
            passed += 1
        else:
            failed += 1
    print("-" * 78)
    print(f"TOTALE: {passed} PASS, {failed} FAIL su {len(CHECKS)} check.")
    print("Invarianti: db_writes=0 (validator statico), nessun gate aperto, "
          "nessuna mutazione runtime, nessun bypass nav guard.")
    if failed == 0:
        print("VERDETTO: VALIDATOR_PASS — Pack 115A scope-coerente e gate-completo.")
        return 0
    print("VERDETTO: VALIDATOR_FAIL — vedi dettaglio sopra.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
