"""Pack 129 — Server Ready Guard helper (read-only, non-mutativo).

Valuta se una richiesta autenticata ha un server context valido e PSP
(`player_server_profiles`) corrispondente. Usato dai route che richiedono
scope server-strict.

Questa funzione è read-only: NON crea PSP, NON tocca user_heroes, NON
muta inventory/reward/progress. Restituisce uno stato esplicito che il caller
usa per decidere se proseguire o sollevare HTTPException con structured error.

Stati possibili (vedi pack 129 prompt §6.3):
  SERVER_READY            — PSP esiste per (user_id, server_id).
  SERVER_CONTEXT_MISSING  — server_id non fornito o vuoto.
  SERVER_CONTEXT_INVALID  — server_id formato non valido.
  SERVER_PROFILE_MISSING  — PSP non trovato per la coppia (user, server).
  SERVER_SCOPE_UNAVAILABLE— DB lookup fallito / scope determination non sicura.
  SERVER_MISMATCH         — server_id body ≠ server_id auth context.

Questa helper NON modifica i route esistenti (Pack 125 v96_team_formation.py).
E' una libreria opt-in per Pack 129+ che NUOVI route possono usare.
"""
from __future__ import annotations

from typing import Any, Optional, Tuple

from .structured_errors import (
    SERVER_CONTEXT_INVALID,
    SERVER_CONTEXT_REQUIRED,
    SERVER_MISMATCH,
    SERVER_PROFILE_MISSING,
    SERVER_SCOPE_UNAVAILABLE,
)

STATE_READY = 'SERVER_READY'
STATE_CONTEXT_MISSING = 'SERVER_CONTEXT_MISSING'
STATE_CONTEXT_INVALID = 'SERVER_CONTEXT_INVALID'
STATE_PROFILE_MISSING = 'SERVER_PROFILE_MISSING'
STATE_SCOPE_UNAVAILABLE = 'SERVER_SCOPE_UNAVAILABLE'
STATE_MISMATCH = 'SERVER_MISMATCH'

# Mapping state -> structured error code Pack 129.
STATE_TO_CODE = {
    STATE_CONTEXT_MISSING: SERVER_CONTEXT_REQUIRED,
    STATE_CONTEXT_INVALID: SERVER_CONTEXT_INVALID,
    STATE_PROFILE_MISSING: SERVER_PROFILE_MISSING,
    STATE_SCOPE_UNAVAILABLE: SERVER_SCOPE_UNAVAILABLE,
    STATE_MISMATCH: SERVER_MISMATCH,
}


def _normalize_server_id(server_id: Any) -> Optional[str]:
    """Valida e normalizza server_id. None/'' -> None. Non-string -> None."""
    if server_id is None:
        return None
    if not isinstance(server_id, str):
        return None
    s = server_id.strip()
    if not s:
        return None
    # server_id format check: alphanumeric + _- only, max 64 char.
    if len(s) > 64:
        return None
    for ch in s:
        if not (ch.isalnum() or ch in '_-'):
            return None
    return s


async def check_server_ready(
    db,
    user_id: Optional[str],
    server_id: Any,
    *,
    auth_context_server_id: Optional[str] = None,
) -> Tuple[str, dict]:
    """Classifica lo stato server-ready per (user_id, server_id).

    Args:
        db: motor.AsyncIOMotorDatabase.
        user_id: l'id utente autenticato (UUID).
        server_id: candidato da request body / context.
        auth_context_server_id: se passato, deve matchare server_id; altrimenti
            ritorna SERVER_MISMATCH.

    Returns:
        (state, info_dict). state e' uno dei STATE_* sopra; info contiene
        chiavi diagnostiche (server_id, user_id, profile_exists, ...).
    """
    info: dict = {
        'user_id': user_id,
        'server_id_raw': server_id,
        'auth_context_server_id': auth_context_server_id,
        'profile_exists': False,
    }
    if not user_id:
        # Auth gate dovrebbe averlo già bloccato a monte, ma defense-in-depth.
        info['reason'] = 'user_id is empty'
        return STATE_SCOPE_UNAVAILABLE, info
    if server_id is None or (isinstance(server_id, str) and not server_id.strip()):
        info['reason'] = 'server_id missing'
        return STATE_CONTEXT_MISSING, info
    normalized = _normalize_server_id(server_id)
    if normalized is None:
        info['reason'] = 'server_id invalid format'
        return STATE_CONTEXT_INVALID, info
    info['server_id'] = normalized
    if auth_context_server_id is not None and normalized != auth_context_server_id:
        info['reason'] = 'server_id body != auth context'
        return STATE_MISMATCH, info
    try:
        psp = await db.player_server_profiles.find_one(
            {'user_id': user_id, 'server_id': normalized},
            projection={'_id': 0, 'user_id': 1, 'server_id': 1},
        )
    except Exception as e:
        info['reason'] = f'DB lookup failed: {e!r}'
        return STATE_SCOPE_UNAVAILABLE, info
    if not psp:
        info['reason'] = 'PSP not found for (user_id, server_id)'
        return STATE_PROFILE_MISSING, info
    info['profile_exists'] = True
    return STATE_READY, info


def state_to_structured_code(state: str) -> str:
    """Converte uno stato server-ready in un codice errore strutturato Pack 129.
    Se lo stato è STATE_READY ritorna stringa vuota (non e' un errore).
    """
    if state == STATE_READY:
        return ''
    return STATE_TO_CODE.get(state, SERVER_SCOPE_UNAVAILABLE)
