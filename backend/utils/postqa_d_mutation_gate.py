"""
v108_POSTQA_D - Legacy Mutation Gate (default-OFF)
==================================================

Modulo introdotto dal pack
MEGA_RELEASE_ACCELERATION_65_v108_POSTQA_D_AUTHORITATIVE_PRE_GATES_AND_MUTATION_LOCKS.

Scopo:
- bloccare per default i 9 endpoint legacy mutanti high-risk prima
  dell'attivazione authoritative;
- restituire un errore esplicito (LEGACY_MUTATION_LOCKED_BY_POSTQA_D)
  invece di scrivere su DB / concedere reward / mutare progress.

Regole inderogabili (rispettano i guardrail v108_POSTQA_D):
- nessun flag attivato di default;
- nessuna cancellazione silenziosa dell'endpoint;
- nessuna scrittura DB quando il gate blocca;
- nessuna concessione di reward/progress;
- nessuna attivazione authoritative / reward live / server scoped runtime;
- nessun claim filter_applied=true.

Per abilitare un gate (solo QA / dev), settare la env var corrispondente
ad una stringa truthy (true, 1, yes, on). Il default e' sempre OFF.
"""
from __future__ import annotations

import os
from typing import Final

from fastapi import HTTPException

# Sentinel del pack D - leggibile dai validator senza eseguire codice.
PUBLIC_SYNC_TAG: Final[str] = (
    "PUBLIC_SYNC_TAG_v108_POSTQA_D_AUTHORITATIVE_PRE_GATES_AND_MUTATION_LOCKS"
)
LOCK_CODE: Final[str] = "LEGACY_MUTATION_LOCKED_BY_POSTQA_D"

# Mapping gate -> endpoint coperti (documentativo, letto anche dai validator).
LEGACY_MUTATION_GATES: Final[dict] = {
    "DIVINE_ALLOW_LEGACY_HERO_PROGRESS_MUTATIONS": {
        "endpoints": ["/api/hero/gain-exp", "/api/hero/levelup"],
        "default": False,
        "category": "hero_progress",
    },
    "DIVINE_ALLOW_LEGACY_FUSION_MUTATIONS": {
        "endpoints": ["/api/fusion/star-up"],
        "default": False,
        "category": "fusion",
    },
    "DIVINE_ALLOW_LEGACY_SOUL_FORGE_MUTATIONS": {
        "endpoints": ["/api/soul/forge"],
        "default": False,
        "category": "soul_forge",
    },
    "DIVINE_ALLOW_LEGACY_MONETIZATION_MUTATIONS": {
        "endpoints": ["/api/vip/add-spend", "/api/battlepass/buy-premium"],
        "default": False,
        "category": "monetization",
    },
    "DIVINE_ALLOW_LEGACY_SOCIAL_GIFT_MUTATIONS": {
        "endpoints": ["/api/friends/gift"],
        "default": False,
        "category": "social_gift",
    },
    "DIVINE_ALLOW_LEGACY_GVG_ADMIN_MUTATIONS": {
        "endpoints": ["/api/gvg/end-war"],
        "default": False,
        "category": "gvg_admin",
    },
    "DIVINE_ALLOW_LEGACY_EQUIPMENT_MUTATIONS": {
        "endpoints": ["/api/equipment/equip"],
        "default": False,
        "category": "equipment",
    },
}

_TRUTHY: Final[set] = {"true", "1", "yes", "on"}


def _is_enabled(gate_name: str) -> bool:
    """Ritorna True solo se la env var e' settata esplicitamente a truthy.

    Default OFF su tutto. Non viene mai dedotto da contesto.
    """
    raw = os.getenv(gate_name)
    if raw is None:
        return False
    return raw.strip().lower() in _TRUTHY


def make_legacy_mutation_gate_dep(gate_name: str, endpoint: str):
    """Factory che restituisce una dipendenza FastAPI per il gate legacy.

    Usata via `Depends(make_legacy_mutation_gate_dep(...))` nella firma del route,
    cosi' da NON modificare il body della funzione gia' coperto da MD5/marker validator
    legacy. Quando il gate e' chiuso (default), solleva HTTP 423.
    """

    def _dep() -> None:
        check_legacy_mutation_gate(gate_name, endpoint)

    _dep.__name__ = f"gate_{gate_name.lower()}"
    return _dep


def check_legacy_mutation_gate(gate_name: str, endpoint: str) -> None:
    """Solleva HTTP 423 se il gate non e' abilitato.

    PARAMS:
      gate_name : nome esatto della env var che governa il gate (chiave di
                  LEGACY_MUTATION_GATES).
      endpoint  : path dell'endpoint protetto (per debug nel payload errore).

    Quando bloccato:
      - status_code 423 LOCKED, code LEGACY_MUTATION_LOCKED_BY_POSTQA_D;
      - nessuna scrittura DB lato chiamante (l'endpoint chiama questa
        funzione PRIMA di toccare il DB);
      - nessun reward / progress / economy mutation;
      - nessun authoritative live activation.
    """
    if gate_name not in LEGACY_MUTATION_GATES:
        # Difesa: non permettiamo gate name sconosciuti, altrimenti
        # potremmo silenziare per errore un endpoint.
        raise HTTPException(
            status_code=500,
            detail={
                "code": "POSTQA_D_GATE_NAME_UNKNOWN",
                "gate": gate_name,
                "endpoint": endpoint,
                "sync_tag": PUBLIC_SYNC_TAG,
            },
        )
    if _is_enabled(gate_name):
        return  # gate aperto (QA / dev) - lascia procedere
    raise HTTPException(
        status_code=423,
        detail={
            "code": LOCK_CODE,
            "gate": gate_name,
            "endpoint": endpoint,
            "reason": (
                "Legacy mutation endpoint bloccato di default dal pack "
                "v108_POSTQA_D. Nessuna scrittura DB, nessun reward, "
                "nessun progress live. Authoritative path non ancora attivo."
            ),
            "sync_tag": PUBLIC_SYNC_TAG,
        },
    )


__all__ = [
    "PUBLIC_SYNC_TAG",
    "LOCK_CODE",
    "LEGACY_MUTATION_GATES",
    "check_legacy_mutation_gate",
    "make_legacy_mutation_gate_dep",
]
