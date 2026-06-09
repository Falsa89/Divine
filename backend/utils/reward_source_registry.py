"""Pack 96 — Reward Source Registry (allowlist).

Centralizza la definizione delle source di reward claim attive in Pack 96.

Regole:
  - Ogni source DEVE essere allowlisted qui per essere accettata dall'endpoint
    `POST /api/rewards/claim`. Qualunque source non registrata viene rifiutata
    con il blocker `REWARD_SOURCE_NOT_ALLOWLISTED`.
  - Source `server_scoped=True` richiedono server_id + PSP.
  - `reward_types` definisce quali chiavi sono ammesse nel payload (whitelist).
  - `grant_fn` e' applicata SOLO se il source e' `live=True` e l'eseguito non e'
    un replay del ledger.
  - Premium / hard currency (`gems`) e' BANNATA in Pack 96 per qualunque source.
"""
from typing import Any, Dict, List, Optional

# Pack 96 forbidden reward types (premium / hard / cross-system)
FORBIDDEN_REWARD_TYPES = {
    "gems",                # premium currency
    "premium_pull",        # gacha
    "standard_pull",       # gacha
    "stamina",             # not server-scoped soft currency
    "experience",          # account-wide hero exp
}

# Allowlist of soft currencies (PSP.soft_currencies) for Pack 96 controlled sources
ALLOWED_SOFT_CURRENCIES = {
    "gold", "honor", "guild_points", "mission_coins",
    "dimension_frags", "prana", "soul_seals", "star_dust",
}


def _grant_soft_currency_to_psp(db, user_id: str, server_id: str,
                                payload: Dict[str, Any]) -> Dict[str, Any]:
    """Grant function: scrive SOLO `player_server_profiles.soft_currencies.*`.

    Ritorna l'oggetto granted per audit nel ledger.
    """
    inc: Dict[str, int] = {}
    for k, v in (payload or {}).items():
        if k in FORBIDDEN_REWARD_TYPES:
            raise _PremiumGrantBlocked(k)
        if k not in ALLOWED_SOFT_CURRENCIES:
            raise _RewardTypeNotAllowed(k)
        try:
            amount = int(v)
        except Exception:
            raise _RewardTypeNotAllowed(f"{k}:invalid_amount")
        if amount <= 0 or amount > 10000:
            # Pack 96: cap soft currency grant per call to a sane test bound.
            raise _RewardTypeNotAllowed(f"{k}:amount_out_of_bounds")
        inc[f"soft_currencies.{k}"] = amount
    return inc


def _grant_noop(_db, _user_id: str, _server_id: str, _payload: Dict[str, Any]):
    """No-op grant: usato per source `story_progress_marker_claim`."""
    return {}


class _PremiumGrantBlocked(Exception):
    def __init__(self, reward_key: str):
        super().__init__(f"PREMIUM_GRANT_BLOCKED:{reward_key}")
        self.reward_key = reward_key


class _RewardTypeNotAllowed(Exception):
    def __init__(self, reward_key: str):
        super().__init__(f"REWARD_TYPE_NOT_ALLOWED:{reward_key}")
        self.reward_key = reward_key


REWARD_SOURCE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "qa_controlled_soft_currency_claim": {
        "server_scoped": True,
        "reward_types": list(ALLOWED_SOFT_CURRENCIES),
        "live": True,
        "grant_fn_name": "grant_soft_currency_to_psp",
        "idempotency": "mandatory",
        "pack_origin": "pack_96",
        "description": "Test/QA controlled soft currency claim. Server-scoped, non-premium. Payload e' un dict di soft currency increments capped a 10000 per chiave.",
    },
    "story_progress_marker_claim": {
        "server_scoped": True,
        "reward_types": [],
        "live": True,
        "grant_fn_name": "grant_noop",
        "idempotency": "mandatory",
        "pack_origin": "pack_96",
        "description": "Marker-only claim per story progress milestones. NESSUN reward grant, scrive solo ledger row + opzionalmente PSP.story_progress (futuro pack).",
    },
}


_GRANT_FN_MAP = {
    "grant_soft_currency_to_psp": _grant_soft_currency_to_psp,
    "grant_noop": _grant_noop,
}


def lookup_source(source_id: str) -> Optional[Dict[str, Any]]:
    return REWARD_SOURCE_REGISTRY.get(source_id)


def is_source_live(source_id: str) -> bool:
    src = REWARD_SOURCE_REGISTRY.get(source_id)
    return bool(src and src.get("live"))


def get_grant_fn(source_id: str):
    src = REWARD_SOURCE_REGISTRY.get(source_id) or {}
    return _GRANT_FN_MAP.get(src.get("grant_fn_name") or "")


def list_allowlisted_sources() -> List[str]:
    return [k for k, v in REWARD_SOURCE_REGISTRY.items() if v.get("live")]


__all__ = [
    "REWARD_SOURCE_REGISTRY", "FORBIDDEN_REWARD_TYPES", "ALLOWED_SOFT_CURRENCIES",
    "lookup_source", "is_source_live", "get_grant_fn", "list_allowlisted_sources",
    "_PremiumGrantBlocked", "_RewardTypeNotAllowed",
]
