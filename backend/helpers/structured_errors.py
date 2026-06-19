"""Pack 129 — Structured Errors Contract (additivo, non-breaking).

Fornisce:
  - Costanti codice errore strutturate (CODES).
  - Funzione `build_structured_detail(...)` per costruire il payload.
  - Mapper `legacy_blocker_to_code(blocker)` per allineare le risposte
    Pack 125 esistenti (formato `{detail: {blocker, message}}`) al contratto
    Pack 129 (`{detail, code, category, route, method, next_gate, recoverable}`).

NON cambia il comportamento dei route esistenti: e' un helper opt-in che i
route possono adottare in Pack 129+ senza rompere il frontend Pack 125/126.

Shape attesa del detail Pack 129:
  {
    "detail": "Human readable Italian message",
    "code": "STRUCTURED_ERROR_CODE",
    "category": "auth|server|team|pre_qa|validation|locked|not_found",
    "route": "/api/...",
    "method": "POST",
    "next_gate": "PACK_129_OR_LATER",
    "recoverable": true|false,
  }
"""
from __future__ import annotations

from typing import Optional

# -- Codici minimi richiesti dal prompt Pack 129. --------------------------

# Auth
AUTH_REQUIRED = 'AUTH_REQUIRED'

# Server context
SERVER_CONTEXT_REQUIRED = 'SERVER_CONTEXT_REQUIRED'
SERVER_CONTEXT_INVALID = 'SERVER_CONTEXT_INVALID'
SERVER_NOT_READY = 'SERVER_NOT_READY'
SERVER_PROFILE_MISSING = 'SERVER_PROFILE_MISSING'
SERVER_SCOPE_UNAVAILABLE = 'SERVER_SCOPE_UNAVAILABLE'
SERVER_MISMATCH = 'SERVER_MISMATCH'

# Team formation
TEAM_SAVE_DISABLED_PRE_QA = 'TEAM_SAVE_DISABLED_PRE_QA'
TEAM_INVALID_PAYLOAD = 'TEAM_INVALID_PAYLOAD'
TEAM_INVALID_SIZE = 'TEAM_INVALID_SIZE'
TEAM_INVALID_SLOT = 'TEAM_INVALID_SLOT'
TEAM_DUPLICATE_HERO = 'TEAM_DUPLICATE_HERO'
TEAM_HERO_NOT_OWNED = 'TEAM_HERO_NOT_OWNED'
TEAM_HERO_NOT_AVAILABLE = 'TEAM_HERO_NOT_AVAILABLE'
TEAM_FORMATION_BLOCKED_PRE_QA = 'TEAM_FORMATION_BLOCKED_PRE_QA'

# Pre-QA generic
PRE_QA_MUTATION_BLOCKED = 'PRE_QA_MUTATION_BLOCKED'
FEATURE_LOCKED_PRE_QA = 'FEATURE_LOCKED_PRE_QA'

ALL_CODES = (
    AUTH_REQUIRED,
    SERVER_CONTEXT_REQUIRED, SERVER_CONTEXT_INVALID, SERVER_NOT_READY,
    SERVER_PROFILE_MISSING, SERVER_SCOPE_UNAVAILABLE, SERVER_MISMATCH,
    TEAM_SAVE_DISABLED_PRE_QA, TEAM_INVALID_PAYLOAD, TEAM_INVALID_SIZE,
    TEAM_INVALID_SLOT, TEAM_DUPLICATE_HERO, TEAM_HERO_NOT_OWNED,
    TEAM_HERO_NOT_AVAILABLE, TEAM_FORMATION_BLOCKED_PRE_QA,
    PRE_QA_MUTATION_BLOCKED, FEATURE_LOCKED_PRE_QA,
)

# Categorie possibili.
CATEGORY_AUTH = 'auth'
CATEGORY_SERVER = 'server'
CATEGORY_TEAM = 'team'
CATEGORY_PRE_QA = 'pre_qa'
CATEGORY_VALIDATION = 'validation'
CATEGORY_LOCKED = 'locked'
CATEGORY_NOT_FOUND = 'not_found'

# Mapping code -> category default. Non esaustivo, ma copre i codici Pack 129.
_CODE_TO_CATEGORY = {
    AUTH_REQUIRED: CATEGORY_AUTH,
    SERVER_CONTEXT_REQUIRED: CATEGORY_SERVER,
    SERVER_CONTEXT_INVALID: CATEGORY_SERVER,
    SERVER_NOT_READY: CATEGORY_SERVER,
    SERVER_PROFILE_MISSING: CATEGORY_SERVER,
    SERVER_SCOPE_UNAVAILABLE: CATEGORY_SERVER,
    SERVER_MISMATCH: CATEGORY_SERVER,
    TEAM_SAVE_DISABLED_PRE_QA: CATEGORY_TEAM,
    TEAM_INVALID_PAYLOAD: CATEGORY_VALIDATION,
    TEAM_INVALID_SIZE: CATEGORY_VALIDATION,
    TEAM_INVALID_SLOT: CATEGORY_VALIDATION,
    TEAM_DUPLICATE_HERO: CATEGORY_VALIDATION,
    TEAM_HERO_NOT_OWNED: CATEGORY_TEAM,
    TEAM_HERO_NOT_AVAILABLE: CATEGORY_TEAM,
    TEAM_FORMATION_BLOCKED_PRE_QA: CATEGORY_PRE_QA,
    PRE_QA_MUTATION_BLOCKED: CATEGORY_PRE_QA,
    FEATURE_LOCKED_PRE_QA: CATEGORY_LOCKED,
}

# Mapping legacy Pack 125 blocker -> Pack 129 code (alias documentati).
LEGACY_BLOCKER_TO_CODE = {
    'AUTHENTICATION_REQUIRED': AUTH_REQUIRED,
    'AUTHENTICATION_INVALID': AUTH_REQUIRED,
    'QA_TEAM_SAVE_DISABLED': TEAM_SAVE_DISABLED_PRE_QA,
    'QA_TEAM_SAVE_ALLOWLIST_EMPTY': FEATURE_LOCKED_PRE_QA,
    'QA_TEAM_SAVE_ACCOUNT_NOT_ALLOWED': FEATURE_LOCKED_PRE_QA,
    'PLAYER_SERVER_PROFILE_REQUIRED': SERVER_PROFILE_MISSING,
    'TEAM_TOO_LARGE': TEAM_INVALID_SIZE,
    'DUPLICATE_POSITIONS': TEAM_INVALID_SLOT,
    'DUPLICATE_HEROES': TEAM_DUPLICATE_HERO,
    'OWNERSHIP_VALIDATION_FAILED': TEAM_HERO_NOT_OWNED,
}


def legacy_blocker_to_code(blocker: Optional[str]) -> Optional[str]:
    """Mappa un legacy `blocker` (Pack 125) al codice strutturato Pack 129.
    Restituisce None se il blocker non e' mappato (caller fa fallback).
    """
    if not blocker:
        return None
    return LEGACY_BLOCKER_TO_CODE.get(blocker)


def build_structured_detail(
    *,
    detail: str,
    code: str,
    route: str = '',
    method: str = '',
    category: Optional[str] = None,
    next_gate: str = 'PACK_129_OR_LATER',
    recoverable: bool = True,
    extra: Optional[dict] = None,
) -> dict:
    """Costruisce un payload structured-error Pack 129.

    Esempio:
        raise HTTPException(
            status_code=403,
            detail=build_structured_detail(
                detail='Team save disabilitato in pre-QA',
                code=TEAM_SAVE_DISABLED_PRE_QA,
                route='/api/team/save-formation',
                method='POST',
                recoverable=False,
            ),
        )
    """
    if code not in ALL_CODES:
        # Non lanciare: tolleriamo codici custom ma li segnaliamo come unknown.
        cat = category or 'validation'
    else:
        cat = category or _CODE_TO_CATEGORY.get(code, 'validation')
    payload = {
        'detail': detail,
        'code': code,
        'category': cat,
        'route': route,
        'method': method,
        'next_gate': next_gate,
        'recoverable': recoverable,
    }
    if extra:
        payload['extra'] = extra
    return payload
