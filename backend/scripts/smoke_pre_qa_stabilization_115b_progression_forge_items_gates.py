#!/usr/bin/env python3
"""
PRE_QA_STABILIZATION_115B — SMOKE runtime hard-gate cintura progression/forge/items.

Verifica che TUTTI i 24 endpoint POST gateati dal Pack 115B + `/api/equipment/unequip`
legacy path restituiscano 423 di default. wallet/spend resta in scope come strict-safe:
viene chiamato senza server_id atteso 400 (SERVER_ID_REQUIRED), non gate 423.

Auth: /api/auth/guest sandbox local-safe.
NESSUN gate env attivato. NESSUNA mutazione attesa.
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from typing import List, Optional, Tuple

try:
    import requests
except Exception:
    print("[ERRORE] modulo 'requests' non installato.")
    sys.exit(2)

BASE = os.environ.get("PACK115B_SMOKE_BACKEND_URL", "http://localhost:8001").rstrip("/")
TIMEOUT_S = 10

# Forbidden: nessun gate env attivo
_GATES = [
    "DIVINE_ALLOW_LEGACY_FORGE_MUTATIONS",
    "DIVINE_ALLOW_LEGACY_RUNE_MUTATIONS",
    "DIVINE_ALLOW_LEGACY_REINCARNATION_MUTATIONS",
    "DIVINE_ALLOW_LEGACY_FRAGMENT_MUTATIONS",
    "DIVINE_ALLOW_LEGACY_MATERIAL_MUTATIONS",
    "DIVINE_ALLOW_LEGACY_ITEM_SHOP_MUTATIONS",
    "DIVINE_ALLOW_LEGACY_INVENTORY_PROGRESS_MUTATIONS",
    "DIVINE_ALLOW_LEGACY_SKILL_UPGRADE_MUTATIONS",
    "DIVINE_ALLOW_LEGACY_UNIQUE_ITEM_MUTATIONS",
    "DIVINE_ALLOW_LEGACY_SOUL_FORGE_RETIRE_MUTATIONS",
    "DIVINE_ALLOW_LEGACY_SPECIAL_SHOP_MUTATIONS",
    "DIVINE_ALLOW_LEGACY_CURRENCY_EARN_MUTATIONS",
    "DIVINE_ALLOW_LEGACY_LEVEL_SHARING_MUTATIONS",
]
for g in _GATES:
    if str(os.environ.get(g, "")).strip().lower() in ("true", "1", "yes", "on"):
        print(f"[ERRORE FATALE] gate {g} TRUTHY in env. Smoke 115B ABORTATO.")
        sys.exit(3)

POST_ENDPOINTS = [
    "/api/forge/upgrade",
    "/api/forge/fuse",
    "/api/runes/craft",
    "/api/runes/craft-premium",
    "/api/runes/fuse",
    "/api/runes/equip",
    "/api/hero/reincarnate",
    "/api/fragments/combine",
    "/api/fragments/add",
    "/api/materials/buy",
    "/api/item-shop/buy",
    "/api/inventory/use-exp",
    "/api/hero/skill-upgrade",
    "/api/unique-items/craft",
    "/api/unique-items/equip",
    "/api/soul-forge/retire",
    "/api/shops/buy",
    "/api/currency/earn-pvp",
    "/api/currency/earn-guild",
    "/api/currency/earn-mission",
    "/api/currency/earn-dimension",
    "/api/level-sharing/unlock",
    "/api/level-sharing/assign",
    "/api/level-sharing/remove/1",
]


def _guest_token() -> Optional[str]:
    try:
        r = requests.post(f"{BASE}/api/auth/guest", json={"alias_hint": f"p115b_{uuid.uuid4().hex[:6]}"}, timeout=TIMEOUT_S)
        if r.status_code == 200:
            return (r.json() or {}).get("token")
    except Exception:
        return None
    return None


def step_gate_probe(token: str) -> List[Tuple[str, bool, str]]:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    out = []
    for ep in POST_ENDPOINTS:
        try:
            r = requests.post(f"{BASE}{ep}", headers=headers, json={}, timeout=TIMEOUT_S)
            sc = r.status_code
            try: body = r.json()
            except Exception: body = r.text
            ok = False; reason = f"status={sc}"
            if sc == 423:
                detail = body.get("detail") if isinstance(body, dict) else None
                code = (detail or {}).get("code") if isinstance(detail, dict) else None
                if code == "LEGACY_MUTATION_LOCKED_BY_POSTQA_D":
                    ok = True; reason = "423 + LEGACY_MUTATION_LOCKED_BY_POSTQA_D"
                else:
                    reason = f"423 ma code inatteso: {code!r}"
            out.append((ep, ok, reason))
        except Exception as e:
            out.append((ep, False, f"errore: {e}"))
    return out


def step_unequip_legacy_fail_closed(token: str) -> Tuple[bool, str]:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        r = requests.post(f"{BASE}/api/equipment/unequip/nonexistent_eq_id", headers=headers, json={}, timeout=TIMEOUT_S)
        if r.status_code != 423:
            return False, f"status={r.status_code} (atteso 423)"
        body = r.json()
        detail = body.get("detail") if isinstance(body, dict) else None
        code = (detail or {}).get("code") if isinstance(detail, dict) else None
        if code == "LEGACY_UNEQUIP_NO_SERVER_ID_FAIL_CLOSED":
            return True, "423 + LEGACY_UNEQUIP_NO_SERVER_ID_FAIL_CLOSED"
        return False, f"423 ma code inatteso: {code!r}"
    except Exception as e:
        return False, f"errore: {e}"


def step_wallet_spend_strict_400(token: str) -> Tuple[bool, str]:
    """wallet/spend senza server_id deve restituire 400 SERVER_ID_REQUIRED (strict-safe).

    Se ritornasse 423 da gate, vorrebbe dire che e' stato accidentalmente gated
    (regression). Se ritorna 400 SERVER_ID_REQUIRED, e' la prova che il path strict
    funziona ed e' preservato.
    """
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        r = requests.post(f"{BASE}/api/wallet/spend", headers=headers,
                          json={"currency": "honor", "amount": 1, "idempotency_token": "x"}, timeout=TIMEOUT_S)
        # 400 + SERVER_ID_REQUIRED atteso (strict path attivo).
        if r.status_code == 400:
            body = r.json() if r.headers.get("content-type","").startswith("application/json") else r.text
            if isinstance(body, dict) and "SERVER_ID_REQUIRED" in str(body.get("detail", "")):
                return True, "400 SERVER_ID_REQUIRED (strict path preservato)"
            return True, f"400 (strict path), detail={body}"
        if r.status_code == 423:
            return False, "423 — wallet/spend non deve essere gated (strict-safe by design)"
        return False, f"status inatteso: {r.status_code}"
    except Exception as e:
        return False, f"errore: {e}"


def main() -> int:
    print("=" * 78)
    print("PRE_QA_STABILIZATION_115B — SMOKE PROGRESSION/FORGE/ITEMS HARD-GATES")
    print("=" * 78)
    print(f"backend_base = {BASE}")

    try:
        r = requests.get(f"{BASE}/api/health", timeout=TIMEOUT_S)
        if r.status_code != 200:
            print("[SKIPPED_BACKEND_DOWN] /api/health non 200")
            return 1
    except Exception as e:
        print(f"[SKIPPED_BACKEND_DOWN] {e}")
        return 1
    print("[OK] backend reachable.")

    token = _guest_token()
    if not token:
        print("[ERRORE] guest token bootstrap fallito. Smoke FAIL.")
        return 1
    print(f"[OK] guest token len={len(token)}")

    print("-" * 78)
    print(f"SEZIONE 1 — {len(POST_ENDPOINTS)} POST endpoint gated attesi 423 + LEGACY_MUTATION_LOCKED_BY_POSTQA_D")
    gate_results = step_gate_probe(token)
    for ep, ok, reason in gate_results:
        marker = "✓" if ok else "✗"
        print(f"  [{marker}] {ep:42s}  {reason}")

    print("-" * 78)
    print("SEZIONE 2 — /api/equipment/unequip/{id} legacy fail-closed")
    ok_unequip, reason_unequip = step_unequip_legacy_fail_closed(token)
    print(f"  [{'✓' if ok_unequip else '✗'}] /api/equipment/unequip/<id>  {reason_unequip}")

    print("-" * 78)
    print("SEZIONE 3 — /api/wallet/spend strict-safe classification (NOT gated)")
    ok_wallet, reason_wallet = step_wallet_spend_strict_400(token)
    print(f"  [{'✓' if ok_wallet else '✗'}] /api/wallet/spend  {reason_wallet}")

    print("=" * 78)
    all_r = gate_results + [("/api/equipment/unequip/legacy", ok_unequip, reason_unequip),
                            ("/api/wallet/spend", ok_wallet, reason_wallet)]
    passed = sum(1 for _, ok, _ in all_r if ok)
    failed = sum(1 for _, ok, _ in all_r if not ok)
    total = len(all_r)
    print(f"SMOKE TOTALE: {passed}/{total} PASS ({failed} FAIL).")
    print("Invarianti runtime: nessun gate env aperto, nessuna mutazione attesa, wallet/spend strict-safe preservato.")
    if failed == 0:
        print("VERDETTO: SMOKE_PASS — Pack 115B hard-gates progression/forge/items operativi.")
        return 0
    print("VERDETTO: SMOKE_FAIL — vedi dettagli.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
