#!/usr/bin/env python3
"""
PRE_QA_STABILIZATION_115A_P0_HARD_GATES_HOME_FIX — SMOKE
========================================================

Smoke runtime HTTP per il Pack 115A. Verifica che TUTTI i 15 endpoint
legacy mutanti elencati nel pack restituiscano HTTP 423 + token
`LEGACY_MUTATION_LOCKED_BY_POSTQA_D` di default (gate OFF).

Inoltre verifica che:
  - GET /api/battlepass non crei doc `battle_pass` per un guest senza dati
    (status 200 con doc default in-memory, senza side-effect DB);
  - GET /api/vip non crei doc `vip_data` per un guest senza dati.

Auth bootstrap: /api/auth/guest (sandbox GUEST_QA_ONLY).

Safety: NESSUN gate env attivato. NESSUNA mutazione DB attesa.
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from typing import Any, Dict, List, Optional, Tuple

try:
    import requests  # type: ignore
except Exception:
    print("[ERRORE] modulo 'requests' non installato.")
    sys.exit(2)

BASE = os.environ.get("PACK115A_SMOKE_BACKEND_URL", "http://localhost:8001").rstrip("/")
TIMEOUT_S = 10

# Forbidden: nessun gate aperto.
_FORBIDDEN_GATES = [
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
for g in _FORBIDDEN_GATES:
    if str(os.environ.get(g, "")).strip().lower() in ("true", "1", "yes", "on"):
        print(f"[ERRORE FATALE] gate {g}=truthy in env. Smoke 115A ABORTATO per safety.")
        sys.exit(3)

# Endpoint POST attesi 423 + LEGACY_MUTATION_LOCKED_BY_POSTQA_D
POST_ENDPOINTS = [
    "/api/shop/buy",
    "/api/shop/claim-daily/x",
    "/api/mail/claim/x",
    "/api/battlepass/claim/1",
    "/api/battlepass/add-exp",
    "/api/server/select",
    "/api/vip/claim-daily",
    "/api/gvg/matchmake",
    "/api/gvg/attack",
    "/api/raid/create",
    "/api/raid/attack/x",
    "/api/exclusive-items/craft",
    "/api/cosmetics/buy",
    "/api/cosmetics/equip",
    "/api/territory/attack",
]


def _bootstrap_token() -> Optional[str]:
    suffix = uuid.uuid4().hex[:6]
    try:
        r = requests.post(f"{BASE}/api/auth/guest", json={"alias_hint": f"p115a_{suffix}"}, timeout=TIMEOUT_S)
        if r.status_code == 200:
            tok = (r.json() or {}).get("token")
            if tok:
                return str(tok)
    except Exception as e:
        print(f"[WARN] guest auth fallita: {e}")
    return None


def step_post_gates(token: str) -> List[Tuple[str, bool, str]]:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    results = []
    for ep in POST_ENDPOINTS:
        try:
            r = requests.post(f"{BASE}{ep}", headers=headers, json={}, timeout=TIMEOUT_S)
            sc = r.status_code
            try:
                body = r.json()
            except Exception:
                body = r.text
            ok = False
            reason = f"status={sc}"
            if sc == 423:
                detail = body.get("detail") if isinstance(body, dict) else None
                code = (detail or {}).get("code") if isinstance(detail, dict) else None
                if code == "LEGACY_MUTATION_LOCKED_BY_POSTQA_D":
                    ok = True
                    reason = "423 + LEGACY_MUTATION_LOCKED_BY_POSTQA_D"
                else:
                    reason = f"423 ma code inatteso: {code!r}"
            results.append((ep, ok, reason))
        except Exception as e:
            results.append((ep, False, f"errore HTTP: {e}"))
    return results


def step_get_no_write(token: str) -> List[Tuple[str, bool, str]]:
    """Verifica che GET /battlepass e /vip rispondano 200 senza creare doc.

    Non possiamo direttamente ispezionare il DB senza credenziali admin; la
    verifica statica e' coperta dal validator (insert_one gated da
    is_legacy_mutation_gate_enabled). Qui ci limitiamo a confermare che la
    risposta HTTP sia 200 e che il payload contenga i valori default
    in-memory (battle pass: level 1, exp 0; vip: vip_level 0).
    """
    headers = {"Authorization": f"Bearer {token}"}
    results = []
    try:
        r = requests.get(f"{BASE}/api/battlepass", headers=headers, timeout=TIMEOUT_S)
        if r.status_code == 200 and isinstance(r.json(), dict) and r.json().get("current_level") == 1 and r.json().get("current_exp") == 0:
            results.append(("/api/battlepass", True, "200 + doc default in-memory (level=1, exp=0)"))
        else:
            results.append(("/api/battlepass", False, f"status={r.status_code} payload={str(r.text)[:100]}"))
    except Exception as e:
        results.append(("/api/battlepass", False, f"errore: {e}"))
    try:
        r = requests.get(f"{BASE}/api/vip", headers=headers, timeout=TIMEOUT_S)
        if r.status_code == 200 and isinstance(r.json(), dict) and r.json().get("vip_level") == 0 and r.json().get("total_spend") == 0:
            results.append(("/api/vip", True, "200 + doc default in-memory (vip_level=0)"))
        else:
            results.append(("/api/vip", False, f"status={r.status_code} payload={str(r.text)[:100]}"))
    except Exception as e:
        results.append(("/api/vip", False, f"errore: {e}"))
    return results


def main() -> int:
    print("=" * 78)
    print("PRE_QA_STABILIZATION_115A_P0_HARD_GATES_HOME_FIX — SMOKE")
    print("=" * 78)
    print(f"backend_base = {BASE}")
    for g in _FORBIDDEN_GATES:
        print(f"env {g} = {os.environ.get(g, '<unset>')}")

    # health
    try:
        r = requests.get(f"{BASE}/api/health", timeout=TIMEOUT_S)
        if r.status_code != 200:
            print("[ERRORE] backend non healthy. Smoke SKIPPED.")
            return 1
    except Exception as e:
        print(f"[ERRORE] backend non raggiungibile: {e}. Smoke SKIPPED.")
        return 1
    print("[OK] backend reachable.")

    token = _bootstrap_token()
    if not token:
        print("[ERRORE] impossibile ottenere token guest. Smoke FAIL (autenticazione necessaria).")
        return 1
    print(f"[OK] guest token len={len(token)}.")

    print("-" * 78)
    print(f"SEZIONE 1 — {len(POST_ENDPOINTS)} POST endpoint legacy attesi 423 + LEGACY_MUTATION_LOCKED_BY_POSTQA_D")
    post_results = step_post_gates(token)
    for ep, ok, reason in post_results:
        marker = "✓" if ok else "✗"
        print(f"  [{marker}] {ep:35s}  {reason}")

    print("-" * 78)
    print("SEZIONE 2 — GET no-write proof (/api/battlepass e /api/vip)")
    get_results = step_get_no_write(token)
    for ep, ok, reason in get_results:
        marker = "✓" if ok else "✗"
        print(f"  [{marker}] {ep:35s}  {reason}")

    print("=" * 78)
    all_results = post_results + get_results
    passed = sum(1 for _, ok, _ in all_results if ok)
    failed = sum(1 for _, ok, _ in all_results if not ok)
    print(f"SMOKE TOTALE: {passed}/{len(all_results)} PASS ({failed} FAIL).")
    print("Invarianti runtime: nessun gate env aperto, nessun reward grant atteso, nessun gold/gems/exp mutation atteso.")
    if failed == 0:
        print("VERDETTO: SMOKE_PASS — Pack 115A hard-gates funzionano runtime.")
        return 0
    print("VERDETTO: SMOKE_FAIL — vedi dettagli.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
