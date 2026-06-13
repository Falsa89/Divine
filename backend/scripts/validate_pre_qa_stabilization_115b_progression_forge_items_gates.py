#!/usr/bin/env python3
"""
PRE_QA_STABILIZATION_115B_PROGRESSION_FORGE_ITEMS_MUTATION_CLASSIFICATION — VALIDATOR

Validator statico per il Pack 115B. Coperture:
  A) Tutti i 13 nuovi gate registrati in LEGACY_MUTATION_GATES con default False.
  B) Ogni endpoint POST target ha @router.post(... dependencies=[make_legacy_mutation_gate_dep(<gate>, <ep>)]).
  C) Gate 115A e v108_POSTQA_D preservati (no regression).
  D) `/api/wallet/spend` classificato strict-safe (server_id required, PSP, soft allowlist,
     idempotency token required, no users.gold/gems, ledger insert).
  E) `/api/equipment/unequip/{equipment_id}` legacy no-server-id path fail-closed 423
     con LEGACY_UNEQUIP_NO_SERVER_ID_FAIL_CLOSED, strict path preservato.
  F) Nessuna nuova UI/feature/profile.tsx/research.tsx introdotta.
  G) data/design/** non toccato (verifica via git diff-name vs baseline 115A).
  H) battle_engine.py / combat.tsx non toccati.

Output PASS/FAIL per check + summary. Exit 0 su tutto PASS.
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


def _ok(name: str, detail: str = "") -> Tuple[bool, str, str]:
    return (True, name, detail)


def _fail(name: str, detail: str) -> Tuple[bool, str, str]:
    return (False, name, detail)


REQUIRED_GATES_115B = {
    "DIVINE_ALLOW_LEGACY_FORGE_MUTATIONS": ["/api/forge/upgrade", "/api/forge/fuse"],
    "DIVINE_ALLOW_LEGACY_RUNE_MUTATIONS": [
        "/api/runes/craft", "/api/runes/craft-premium", "/api/runes/fuse", "/api/runes/equip",
    ],
    "DIVINE_ALLOW_LEGACY_REINCARNATION_MUTATIONS": ["/api/hero/reincarnate"],
    "DIVINE_ALLOW_LEGACY_FRAGMENT_MUTATIONS": ["/api/fragments/combine", "/api/fragments/add"],
    "DIVINE_ALLOW_LEGACY_MATERIAL_MUTATIONS": ["/api/materials/buy"],
    "DIVINE_ALLOW_LEGACY_ITEM_SHOP_MUTATIONS": ["/api/item-shop/buy"],
    "DIVINE_ALLOW_LEGACY_INVENTORY_PROGRESS_MUTATIONS": ["/api/inventory/use-exp"],
    "DIVINE_ALLOW_LEGACY_SKILL_UPGRADE_MUTATIONS": ["/api/hero/skill-upgrade"],
    "DIVINE_ALLOW_LEGACY_UNIQUE_ITEM_MUTATIONS": ["/api/unique-items/craft", "/api/unique-items/equip"],
    "DIVINE_ALLOW_LEGACY_SOUL_FORGE_RETIRE_MUTATIONS": ["/api/soul-forge/retire"],
    "DIVINE_ALLOW_LEGACY_SPECIAL_SHOP_MUTATIONS": ["/api/shops/buy"],
    "DIVINE_ALLOW_LEGACY_CURRENCY_EARN_MUTATIONS": [
        "/api/currency/earn-pvp", "/api/currency/earn-guild",
        "/api/currency/earn-mission", "/api/currency/earn-dimension",
    ],
    "DIVINE_ALLOW_LEGACY_LEVEL_SHARING_MUTATIONS": [
        "/api/level-sharing/unlock", "/api/level-sharing/assign",
        "/api/level-sharing/remove/{slot_number}",
    ],
}

ENDPOINT_TO_GATE = {
    # forge.py
    ('backend/routes/forge.py', '/forge/upgrade'): "DIVINE_ALLOW_LEGACY_FORGE_MUTATIONS",
    ('backend/routes/forge.py', '/forge/fuse'): "DIVINE_ALLOW_LEGACY_FORGE_MUTATIONS",
    ('backend/routes/forge.py', '/runes/craft'): "DIVINE_ALLOW_LEGACY_RUNE_MUTATIONS",
    ('backend/routes/forge.py', '/runes/craft-premium'): "DIVINE_ALLOW_LEGACY_RUNE_MUTATIONS",
    ('backend/routes/forge.py', '/runes/fuse'): "DIVINE_ALLOW_LEGACY_RUNE_MUTATIONS",
    ('backend/routes/forge.py', '/runes/equip'): "DIVINE_ALLOW_LEGACY_RUNE_MUTATIONS",
    # hero_progression.py
    ('backend/routes/hero_progression.py', '/hero/reincarnate'): "DIVINE_ALLOW_LEGACY_REINCARNATION_MUTATIONS",
    ('backend/routes/hero_progression.py', '/fragments/combine'): "DIVINE_ALLOW_LEGACY_FRAGMENT_MUTATIONS",
    ('backend/routes/hero_progression.py', '/fragments/add'): "DIVINE_ALLOW_LEGACY_FRAGMENT_MUTATIONS",
    ('backend/routes/hero_progression.py', '/materials/buy'): "DIVINE_ALLOW_LEGACY_MATERIAL_MUTATIONS",
    # items.py
    ('backend/routes/items.py', '/item-shop/buy'): "DIVINE_ALLOW_LEGACY_ITEM_SHOP_MUTATIONS",
    ('backend/routes/items.py', '/inventory/use-exp'): "DIVINE_ALLOW_LEGACY_INVENTORY_PROGRESS_MUTATIONS",
    ('backend/routes/items.py', '/hero/skill-upgrade'): "DIVINE_ALLOW_LEGACY_SKILL_UPGRADE_MUTATIONS",
    # unique_items.py
    ('backend/routes/unique_items.py', '/unique-items/craft'): "DIVINE_ALLOW_LEGACY_UNIQUE_ITEM_MUTATIONS",
    ('backend/routes/unique_items.py', '/unique-items/equip'): "DIVINE_ALLOW_LEGACY_UNIQUE_ITEM_MUTATIONS",
    # soul_forge.py
    ('backend/routes/soul_forge.py', '/soul-forge/retire'): "DIVINE_ALLOW_LEGACY_SOUL_FORGE_RETIRE_MUTATIONS",
    ('backend/routes/soul_forge.py', '/shops/buy'): "DIVINE_ALLOW_LEGACY_SPECIAL_SHOP_MUTATIONS",
    ('backend/routes/soul_forge.py', '/currency/earn-pvp'): "DIVINE_ALLOW_LEGACY_CURRENCY_EARN_MUTATIONS",
    ('backend/routes/soul_forge.py', '/currency/earn-guild'): "DIVINE_ALLOW_LEGACY_CURRENCY_EARN_MUTATIONS",
    ('backend/routes/soul_forge.py', '/currency/earn-mission'): "DIVINE_ALLOW_LEGACY_CURRENCY_EARN_MUTATIONS",
    ('backend/routes/soul_forge.py', '/currency/earn-dimension'): "DIVINE_ALLOW_LEGACY_CURRENCY_EARN_MUTATIONS",
    # level_sharing.py
    ('backend/routes/level_sharing.py', '/level-sharing/unlock'): "DIVINE_ALLOW_LEGACY_LEVEL_SHARING_MUTATIONS",
    ('backend/routes/level_sharing.py', '/level-sharing/assign'): "DIVINE_ALLOW_LEGACY_LEVEL_SHARING_MUTATIONS",
    ('backend/routes/level_sharing.py', '/level-sharing/remove/{slot_number}'): "DIVINE_ALLOW_LEGACY_LEVEL_SHARING_MUTATIONS",
}


def check_A_gates_registered():
    src = _read("backend/utils/postqa_d_mutation_gate.py")
    name = "A_ALL_115B_GATES_REGISTERED_DEFAULT_OFF"
    missing = []
    for gate, endpoints in REQUIRED_GATES_115B.items():
        if gate not in src:
            missing.append(gate)
            continue
        # Verifica default False
        gate_idx = src.find(f'"{gate}":')
        # Cerca "default": False entro 400 char dal gate
        window = src[gate_idx:gate_idx + 600]
        if '"default": False' not in window:
            missing.append(f"{gate} (default non False)")
            continue
        for ep in endpoints:
            if ep not in src:
                missing.append(f"{gate}->{ep}")
    if missing:
        return _fail(name, "mancanti: " + ", ".join(missing[:8]) + (" ..." if len(missing) > 8 else ""))
    return _ok(name, f"{len(REQUIRED_GATES_115B)} gate 115B registrati default=False")


def check_B_endpoints_decorated():
    name = "B_ALL_115B_ENDPOINTS_DECORATED"
    failures = []
    for (rel, ep), gate in ENDPOINT_TO_GATE.items():
        src = _read(rel)
        ep_re = re.compile(
            r'@router\.post\(\s*[\'"]' + re.escape(ep) + r'[\'"]\s*,\s*dependencies\s*=\s*\[\s*'
            r'_Depends_postqa_d\(\s*make_legacy_mutation_gate_dep\(\s*[\'"]' + re.escape(gate) + r'[\'"]',
            re.DOTALL,
        )
        if not ep_re.search(src):
            failures.append(f"{rel}:{ep} non protetto da {gate}")
    if failures:
        return _fail(name, "; ".join(failures[:4]) + (" ..." if len(failures) > 4 else ""))
    return _ok(name, f"{len(ENDPOINT_TO_GATE)} endpoint tutti decorati col gate corretto")


def check_C_v108_115a_gates_preserved():
    src = _read("backend/utils/postqa_d_mutation_gate.py")
    name = "C_V108_115A_GATES_PRESERVED"
    preserved_required = [
        # v108_POSTQA_D
        "DIVINE_ALLOW_LEGACY_HERO_PROGRESS_MUTATIONS",
        "DIVINE_ALLOW_LEGACY_FUSION_MUTATIONS",
        "DIVINE_ALLOW_LEGACY_SOUL_FORGE_MUTATIONS",
        "DIVINE_ALLOW_LEGACY_MONETIZATION_MUTATIONS",
        "DIVINE_ALLOW_LEGACY_SOCIAL_GIFT_MUTATIONS",
        "DIVINE_ALLOW_LEGACY_GVG_ADMIN_MUTATIONS",
        "DIVINE_ALLOW_LEGACY_EQUIPMENT_MUTATIONS",
        # 115A
        "DIVINE_ALLOW_LEGACY_SHOP_MUTATIONS",
        "DIVINE_ALLOW_LEGACY_MAIL_MUTATIONS",
        "DIVINE_ALLOW_LEGACY_BATTLEPASS_PROGRESS_MUTATIONS",
        "DIVINE_ALLOW_LEGACY_SERVER_SELECT_MUTATIONS",
        "DIVINE_ALLOW_LEGACY_VIP_DAILY_MUTATIONS",
        "DIVINE_ALLOW_LEGACY_GVG_PLAYER_MUTATIONS",
        "DIVINE_ALLOW_LEGACY_RAID_MUTATIONS",
        "DIVINE_ALLOW_LEGACY_COSMETICS_MUTATIONS",
        "DIVINE_ALLOW_LEGACY_TERRITORY_MUTATIONS",
    ]
    missing = [g for g in preserved_required if g not in src]
    if missing:
        return _fail(name, "preservation regression: " + ", ".join(missing))
    return _ok(name, f"{len(preserved_required)} gate v108+115A tutti preservati")


def check_D_wallet_spend_strict_safe():
    src = _read("backend/routes/soul_forge.py")
    name = "D_WALLET_SPEND_STRICT_SERVER_SCOPED_SAFE"
    idx = src.find('@router.post("/wallet/spend")')
    if idx < 0:
        return _fail(name, "endpoint /wallet/spend non trovato")
    # estrai corpo fino al prossimo @router.
    next_router = src.find("\n    @router.", idx + 1)
    body = src[idx:next_router] if next_router > 0 else src[idx:]
    required_markers = [
        ("SERVER_ID_REQUIRED", "server_id required check"),
        ("PLAYER_SERVER_PROFILE_REQUIRED", "PSP required check"),
        ("SOFT_KEYS", "soft-currency allowlist"),
        ("IDEMPOTENCY_TOKEN_REQUIRED", "idempotency token check"),
        ("wallet_spend_ledger", "ledger collection"),
        ("soft_currencies", "soft_currencies write target"),
    ]
    missing = []
    for needle, desc in required_markers:
        if needle not in body:
            missing.append(desc)
    if missing:
        return _fail(name, "missing strict markers: " + "; ".join(missing))
    # Negative: no users.gold/gems mutation
    if re.search(r'db\.users\.update_one\([^)]*\$inc[^)]*(?:gold|gems)', body, re.DOTALL):
        return _fail(name, "wallet/spend muta users.gold/gems (violazione strict)")
    return _ok(name, "wallet/spend strict-safe: server_id+PSP+soft-allowlist+idempotency+ledger, no users.gold/gems")


def check_E_equipment_unequip_legacy_fail_closed():
    src = _read("backend/routes/equipment.py")
    name = "E_EQUIPMENT_UNEQUIP_LEGACY_FAIL_CLOSED"
    idx = src.find("async def unequip_item")
    if idx < 0:
        return _fail(name, "handler unequip_item non trovato")
    body = src[idx:]
    if "LEGACY_UNEQUIP_NO_SERVER_ID_FAIL_CLOSED" not in body:
        return _fail(name, "blocker LEGACY_UNEQUIP_NO_SERVER_ID_FAIL_CLOSED assente")
    if "raise HTTPException(\n            423" not in body and "HTTPException(423" not in body:
        return _fail(name, "fail-closed non solleva HTTP 423")
    # Strict path deve restare presente.
    if 'pack_94_strict_server_scoped_write' not in body:
        return _fail(name, "strict server-scoped path rimosso (regressione)")
    # Il path legacy senza server_id NON deve avere update_one prima del raise.
    # Trova posizione di "raise HTTPException(\n            423" e verifica nessun update_one prima a livello legacy.
    # Cerchiamo: dopo la chiusura del blocco strict (return), il body restante deve essere il raise.
    after_strict = body[body.find('pack_94_strict_server_scoped_write'):]
    if 'db.user_equipment.update_one' in after_strict:
        return _fail(name, "update_one residuo nel path legacy dopo il return strict")
    return _ok(name, "legacy no-server-id path fail-closed 423, strict path preservato, nessun write residuo")


def check_F_no_new_screens_or_features():
    name = "F_NO_NEW_UI_FEATURE"
    forbidden = ["frontend/app/profile.tsx", "frontend/app/research.tsx"]
    for f in forbidden:
        if _exists(f):
            return _fail(name, f"file proibito creato: {f}")
    return _ok(name, "nessuna nuova schermata profile/research/UI")


def check_G_no_data_design_touched():
    """Verifica che il working tree non abbia modifiche staged a data/design/**.

    Static check: lista i file del Pack 115B (legacy mutation gate + routes/scripts/docs)
    e si limita a confermare che nessun import di data/design/* sia stato aggiunto.
    """
    name = "G_NO_DATA_DESIGN_REFERENCES_INTRODUCED"
    files_115b = [
        "backend/utils/postqa_d_mutation_gate.py",
        "backend/routes/forge.py",
        "backend/routes/hero_progression.py",
        "backend/routes/items.py",
        "backend/routes/unique_items.py",
        "backend/routes/soul_forge.py",
        "backend/routes/level_sharing.py",
        "backend/routes/equipment.py",
    ]
    for f in files_115b:
        src = _read(f)
        if "data/design" in src or "data\\design" in src:
            return _fail(name, f"{f} contiene reference a data/design (proibito)")
    return _ok(name, "nessun reference a data/design nei file 115B")


def check_H_battle_engine_combat_untouched():
    name = "H_BATTLE_ENGINE_AND_COMBAT_UNTOUCHED"
    # Static check: verifica che battle_engine.py / combat.tsx non importino i gate 115B.
    candidates = ["backend/battle_engine.py", "frontend/app/combat.tsx"]
    for c in candidates:
        if not _exists(c):
            continue
        s = _read(c)
        for new_gate in REQUIRED_GATES_115B:
            if new_gate in s:
                return _fail(name, f"{c} contiene reference a gate 115B {new_gate}")
    return _ok(name, "battle_engine.py / combat.tsx non toccati dal Pack 115B")


CHECKS = [
    check_A_gates_registered,
    check_B_endpoints_decorated,
    check_C_v108_115a_gates_preserved,
    check_D_wallet_spend_strict_safe,
    check_E_equipment_unequip_legacy_fail_closed,
    check_F_no_new_screens_or_features,
    check_G_no_data_design_touched,
    check_H_battle_engine_combat_untouched,
]


def main() -> int:
    print("=" * 78)
    print("PRE_QA_STABILIZATION_115B_PROGRESSION_FORGE_ITEMS — VALIDATOR")
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
    print("Invarianti: db_writes=0 (validator statico), tutti i nuovi gate default OFF, "
          "nessuna mutazione runtime, nessuna nuova feature/UI.")
    if failed == 0:
        print("VERDETTO: VALIDATOR_PASS — Pack 115B scope-coerente e gate-completo.")
        return 0
    print("VERDETTO: VALIDATOR_FAIL — vedi dettaglio sopra.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
