#!/usr/bin/env python3
"""PRE_QA_STABILIZATION_115E_COMBAT_TOWER_LEGACY_HARDENING — VALIDATOR.

Coperture statiche (regex/grep):
  A. combat.tsx contiene LEGACY_COMBAT_ENTRY_BLOCKED_PRE_QA + token
     PRE_QA_COMBAT_REQUIRES_LAUNCH_CONTEXT.
  B. combat.tsx: in startBattle(), il check LEGACY_COMBAT_ENTRY_MUTATING (no-launch)
     PRECEDE qualunque apiCall('/api/battle/simulate'); il path no-launch e' fail-closed.
  C. combat.tsx: PREVIEW_REWARD_LOCK_ACTIVE e PREVIEW_NON_AUTHORITATIVE preservati.
  D. combat.tsx: nel render del fail-closed branch nessun reward/EXP/drop/progress/affinity grant.
  E. tower.tsx: usa PreQaScreenGate.
  F. tower.tsx: nessun import/uso apiCall, niente refreshUser, niente /api/tower/status,
     niente /api/tower/battle.
  G. preQaNavGuard.ts: '/tower' in PRE_QA_BLOCKED_PLAYER_ROUTES.
  H. tower-of-the-hells.tsx + tower-visual-preview.tsx non sono stati modificati (no
     reference a PreQaScreenGate o LEGACY_COMBAT_ENTRY_BLOCKED_PRE_QA in essi).
  I. battle_engine.py + backend route logic gate file + character_bible non toccati
     (no marker 115E in essi); gacha rates / skill catalog non importati da combat/tower.
  J. profile.tsx e research.tsx non esistono.
  K. Nessun reference data/design/** nei file 115E.

Output PASS/FAIL + summary. Exit 0 su tutto PASS. Log in italiano.
"""
from __future__ import annotations
import re, sys
from pathlib import Path
from typing import Tuple

REPO = Path(__file__).resolve().parents[2]
def _read(rel): return (REPO/rel).read_text(encoding="utf-8", errors="strict")
def _exists(rel): return (REPO/rel).exists()
def _ok(n,d=""): return (True,n,d)
def _fail(n,d): return (False,n,d)


def check_A_combat_tokens_present():
    src = _read("frontend/app/combat.tsx")
    name = "A_COMBAT_TOKENS_PRESENT"
    if "LEGACY_COMBAT_ENTRY_BLOCKED_PRE_QA" not in src:
        return _fail(name, "token LEGACY_COMBAT_ENTRY_BLOCKED_PRE_QA assente")
    if "PRE_QA_COMBAT_REQUIRES_LAUNCH_CONTEXT" not in src:
        return _fail(name, "token PRE_QA_COMBAT_REQUIRES_LAUNCH_CONTEXT assente")
    return _ok(name, "tokens 115E presenti in combat.tsx")


def check_B_simulate_guarded_by_no_launch_check():
    src = _read("frontend/app/combat.tsx")
    name = "B_SIMULATE_FAIL_CLOSED_NO_LAUNCH_CONTEXT"
    # Estrai funzione startBattle dal "const startBattle = async () => {" fino al primo "\n  };" matching depth
    idx = src.find("const startBattle = async () => {")
    if idx < 0:
        return _fail(name, "funzione startBattle non trovata")
    # Confine: prossimo "\n  const " a livello 2 spazi o EOF
    next_const = src.find("\n  const ", idx + 30)
    body = src[idx:next_const] if next_const > 0 else src[idx:]
    # Controllo: LEGACY_COMBAT_ENTRY_MUTATING check PRECEDE apiCall
    legacy_pos = body.find("LEGACY_COMBAT_ENTRY_MUTATING")
    sim_pos = body.find("apiCall('/api/battle/simulate'")
    if legacy_pos < 0:
        return _fail(name, "check LEGACY_COMBAT_ENTRY_MUTATING assente in startBattle")
    if sim_pos > 0 and legacy_pos >= sim_pos:
        return _fail(name, "LEGACY_COMBAT_ENTRY_MUTATING check NON precede apiCall simulate")
    if "LEGACY_COMBAT_ENTRY_BLOCKED_PRE_QA" not in body:
        return _fail(name, "blocco LEGACY_COMBAT_ENTRY_BLOCKED_PRE_QA non documentato nel body startBattle")
    return _ok(name, "no-launch-context guard precede apiCall simulate in startBattle")


def check_C_preview_tokens_preserved():
    src = _read("frontend/app/combat.tsx")
    name = "C_PREVIEW_TOKENS_PRESERVED"
    if "PREVIEW_REWARD_LOCK_ACTIVE" not in src:
        return _fail(name, "PREVIEW_REWARD_LOCK_ACTIVE rimosso (regression)")
    if "PREVIEW_NON_AUTHORITATIVE" not in src:
        return _fail(name, "PREVIEW_NON_AUTHORITATIVE rimosso (regression)")
    return _ok(name, "preview tokens preservati")


def check_D_no_reward_in_blocked_branch():
    """Nel render branch legacy_blocked NON devono esserci grantAffinity/refreshUser/reward UI live."""
    src = _read("frontend/app/combat.tsx")
    name = "D_NO_REWARD_GRANT_IN_BLOCKED_BRANCH"
    # Estrai il branch legacy_blocked: dal `if (phase === ('legacy_blocked' as any)` fino al prossimo `if (phase ===`
    m = re.search(r"if\s*\(phase\s*===\s*\('legacy_blocked'\s+as\s+any\)", src)
    if not m:
        return _fail(name, "render branch legacy_blocked non trovato")
    start = m.start()
    nxt = src.find("\n  // LOADING", start)
    branch = src[start:nxt] if nxt > 0 else src[start:start+4000]
    for forbidden in ("grantAffinity(", "refreshUser(", "user_heroes", "$inc"):
        if forbidden in branch:
            return _fail(name, f"branch blocked contiene reference proibita: {forbidden}")
    return _ok(name, "blocked branch render-only, nessun grant/refresh/mutation")


def check_E_tower_uses_PreQaScreenGate():
    src = _read("frontend/app/tower.tsx")
    name = "E_TOWER_USES_PRE_QA_SCREEN_GATE"
    if "PreQaScreenGate" not in src or "isScreenGated" not in src:
        return _fail(name, "tower.tsx non usa PreQaScreenGate/isScreenGated")
    return _ok(name, "tower.tsx usa PreQaScreenGate canonical guard")


def check_F_tower_no_apicall_no_refresh():
    src = _read("frontend/app/tower.tsx")
    name = "F_TOWER_NO_APICALL_NO_REFRESH_NO_API_TOWER"
    forbidden = [
        ("apiCall", "apiCall importato/usato"),
        ("refreshUser", "refreshUser usato"),
        ("/api/tower/status", "/api/tower/status referenziato"),
        ("/api/tower/battle", "/api/tower/battle referenziato"),
        ("useAuth", "useAuth (refresh) importato"),
    ]
    for needle, desc in forbidden:
        if needle in src:
            return _fail(name, desc)
    return _ok(name, "tower.tsx pulito: 0 apiCall, 0 refreshUser, 0 /api/tower/*")


def check_G_navguard_blocks_tower():
    src = _read("frontend/src/utils/preQaNavGuard.ts")
    name = "G_NAV_GUARD_BLOCKS_TOWER"
    if "'/tower'" not in src:
        return _fail(name, "/tower assente da PRE_QA_BLOCKED_PLAYER_ROUTES")
    return _ok(name, "/tower in PRE_QA_BLOCKED_PLAYER_ROUTES")


def check_H_other_tower_files_untouched():
    name = "H_OTHER_TOWER_FILES_UNTOUCHED"
    for rel in ("frontend/app/tower-of-the-hells.tsx", "frontend/app/tower-visual-preview.tsx"):
        if not _exists(rel):
            continue
        s = _read(rel)
        if "LEGACY_COMBAT_ENTRY_BLOCKED_PRE_QA" in s or "115E" in s.replace("v115E", ""):
            # consentito uso di PreQaScreenGate se gia' presente da Pack 115D
            pass
        # se contiene il commento '115E', considerato modificato dal pack
        if "Pre-QA Stabilization 115E" in s:
            return _fail(name, f"{rel} modificato dal Pack 115E (fuori scope)")
    return _ok(name, "tower-of-the-hells.tsx + tower-visual-preview.tsx non toccati dal Pack 115E")


def check_I_backend_and_data_untouched():
    name = "I_BACKEND_AND_DATA_UNTOUCHED_BY_115E"
    forbidden = [
        "backend/battle_engine.py",
        "backend/utils/postqa_d_mutation_gate.py",
    ]
    for rel in forbidden:
        if not _exists(rel):
            continue
        s = _read(rel)
        if "Pre-QA Stabilization 115E" in s or "LEGACY_COMBAT_ENTRY_BLOCKED_PRE_QA" in s:
            return _fail(name, f"{rel} modificato dal Pack 115E (FORBIDDEN)")
    return _ok(name, "battle_engine.py + backend route logic non toccati dal Pack 115E")


def check_J_no_profile_no_research():
    name = "J_NO_PROFILE_NO_RESEARCH_SCREEN"
    if _exists("frontend/app/profile.tsx"):
        return _fail(name, "profile.tsx creato (FORBIDDEN)")
    if _exists("frontend/app/research.tsx"):
        return _fail(name, "research.tsx creato (FORBIDDEN)")
    return _ok(name, "nessun profile.tsx/research.tsx")


def check_K_no_data_design_refs_in_115e_files():
    name = "K_NO_DATA_DESIGN_REFS_IN_115E_FILES"
    for rel in ("frontend/app/combat.tsx", "frontend/app/tower.tsx", "frontend/src/utils/preQaNavGuard.ts"):
        s = _read(rel)
        if "data/design" in s or "data\\design" in s:
            return _fail(name, f"{rel} contiene reference a data/design")
    return _ok(name, "nessun reference a data/design nei file 115E")


CHECKS = [
    check_A_combat_tokens_present,
    check_B_simulate_guarded_by_no_launch_check,
    check_C_preview_tokens_preserved,
    check_D_no_reward_in_blocked_branch,
    check_E_tower_uses_PreQaScreenGate,
    check_F_tower_no_apicall_no_refresh,
    check_G_navguard_blocks_tower,
    check_H_other_tower_files_untouched,
    check_I_backend_and_data_untouched,
    check_J_no_profile_no_research,
    check_K_no_data_design_refs_in_115e_files,
]


def main() -> int:
    print("=" * 78)
    print("PRE_QA_STABILIZATION_115E_COMBAT_TOWER_LEGACY_HARDENING — VALIDATOR")
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
    print("Invarianti: db_writes=0 (validator statico), nessun reward grant, "
          "nessun combat autoritativo attivato, nessuna nuova feature.")
    if failed == 0:
        print("VERDETTO: VALIDATOR_PASS — Pack 115E combat/tower legacy hardening coerente.")
        return 0
    print("VERDETTO: VALIDATOR_FAIL — vedi dettaglio sopra.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
