"""Pack 128 — Pre-QA Backend Mutation Allowlist Middleware (RUNTIME).

Obiettivo:
  Bloccare a runtime ogni richiesta mutativa (POST/PUT/PATCH/DELETE) verso un
  endpoint backend NON presente nella mutation allowlist Pack 128, durante la
  fase pre-QA. Risposta strutturata `PRE_QA_MUTATION_BLOCKED` con HTTP 423.

Proprietà (onestà):
  - Default fail-OPEN (DORMANT) se env `PRE_QA_MUTATION_GUARD_ENABLED` != 'true'.
    Questo è necessario perché:
      a) Pack 128 non puo' modificare `backend/.env` (vincolo utente).
      b) Default OFF garantisce zero regressioni su QA flow esistente.
      c) Quando env diventa 'true' in supervisor QA, l'enforcement è REALE.
  - Quando attivo, applica deny-by-default: solo route nella allowlist passano.
  - Allowlist letta da `data/design/system_safety/pack_128_backend_mutation_allowlist.json`
    (fallback statico in caso file mancante per evitare crash di boot).
  - Method matching case-insensitive su (METHOD, PATH).
  - Path matching exact OR prefix-match con suffisso parametrico (`{param}`).
  - OPTIONS (CORS preflight) sempre passante (non mutativa).
  - GET/HEAD passante (Pack 128 Track C tratta mutating-GET separatamente).

NON modifica:
  - battle_engine.py / battle_core.py / formule combattimento
  - Character Bible / final_numbers
  - logica auth / reward / economy / gacha
  - DB schema o migrazioni

Vedi anche:
  - `data/design/system_safety/pack_128_backend_mutation_middleware_marker.json`
  - `backend/scripts/validate_pack_128_backend_mutation_middleware_runtime.py`
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Iterable, Set, Tuple

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ALLOWLIST_FILE = _REPO_ROOT / 'data' / 'design' / 'system_safety' / 'pack_128_backend_mutation_allowlist.json'

# Fallback statico in caso di file mancante (resilienza boot). Mantenuto piccolo
# e conservativo: solo route assolutamente necessarie per bootstrap QA.
_STATIC_FALLBACK_ALLOWLIST: Tuple[Tuple[str, str], ...] = (
    ('POST', '/api/register'),
    ('POST', '/api/login'),
    ('POST', '/api/auth/refresh'),
    ('POST', '/api/psp/ensure'),
    ('POST', '/api/psp/starter/claim'),
    ('POST', '/api/team/save-formation'),
    ('POST', '/api/battle/launch'),
    ('POST', '/api/logout'),
    ('POST', '/api/logout-all'),
)

_MUTATING_METHODS: Set[str] = {'POST', 'PUT', 'PATCH', 'DELETE'}

# Variabile env che attiva l'enforcement runtime. Default OFF per non rompere
# il QA flow esistente (l'attivazione e' un'azione esplicita di supervisor QA).
ENV_FLAG = 'PRE_QA_MUTATION_GUARD_ENABLED'


def _truthy(val: str | None) -> bool:
    return (val or '').strip().lower() in ('true', '1', 'yes', 'on')


def load_allowlist() -> Set[Tuple[str, str]]:
    """Carica l'allowlist da file JSON. Fallback statico se file assente/corrotto."""
    try:
        if _ALLOWLIST_FILE.exists():
            data = json.loads(_ALLOWLIST_FILE.read_text(encoding='utf-8'))
            entries = data.get('allowlist', [])
            parsed: Set[Tuple[str, str]] = set()
            for e in entries:
                # Supporta entrambi formati: "POST /api/xxx" o {method, path}
                if isinstance(e, str):
                    parts = e.strip().split(None, 1)
                    if len(parts) == 2:
                        parsed.add((parts[0].upper(), parts[1]))
                elif isinstance(e, dict):
                    m = str(e.get('method', '')).upper()
                    p = str(e.get('path', ''))
                    if m and p:
                        parsed.add((m, p))
            if parsed:
                return parsed
    except Exception:
        # Non far crashare il boot: usa fallback statico onesto.
        pass
    return set(_STATIC_FALLBACK_ALLOWLIST)


def _path_matches(allowlist_path: str, request_path: str) -> bool:
    """Confronto path: exact OR pattern con `{param}` segmenti."""
    if allowlist_path == request_path:
        return True
    if '{' not in allowlist_path:
        return False
    # Converte `/api/foo/{id}/bar` -> regex `/api/foo/[^/]+/bar`
    pattern = re.sub(r'\{[^/}]+\}', r'[^/]+', allowlist_path)
    return bool(re.fullmatch(pattern, request_path))


def is_allowed(method: str, path: str, allowlist: Iterable[Tuple[str, str]] | None = None) -> bool:
    """Funzione pura: True se (method, path) è nell'allowlist Pack 128."""
    m = method.upper()
    allow = allowlist if allowlist is not None else load_allowlist()
    for a_method, a_path in allow:
        if a_method == m and _path_matches(a_path, path):
            return True
    return False


class PreQaMutationGuardMiddleware(BaseHTTPMiddleware):
    """Middleware fail-closed (env-gated) per mutazioni non allowlisted in pre-QA.

    Comportamento:
      - env `PRE_QA_MUTATION_GUARD_ENABLED` != 'true' → middleware è DORMANT,
        request passa inalterata (no behavioural change runtime).
      - env == 'true' → enforce allowlist: METODI mutativi non-allowlisted →
        HTTP 423 (Locked) con payload strutturato `PRE_QA_MUTATION_BLOCKED`.
      - OPTIONS/GET/HEAD sempre pass.
    """

    def __init__(self, app, allowlist: Iterable[Tuple[str, str]] | None = None):
        super().__init__(app)
        self._explicit_allowlist = set(allowlist) if allowlist is not None else None

    @property
    def enabled(self) -> bool:
        return _truthy(os.environ.get(ENV_FLAG))

    def _allowlist(self) -> Set[Tuple[str, str]]:
        if self._explicit_allowlist is not None:
            return self._explicit_allowlist
        return load_allowlist()

    async def dispatch(self, request: Request, call_next):
        # 1) Se middleware non attivo via env → pass (default safe, no regressioni).
        if not self.enabled:
            return await call_next(request)

        method = request.method.upper()

        # 2) Metodi non mutativi → pass (Track C gestisce separatamente i GET).
        if method not in _MUTATING_METHODS:
            return await call_next(request)

        path = request.url.path

        # 3) Solo /api/* è soggetto a allowlist (frontend assets/static pass).
        if not path.startswith('/api/'):
            return await call_next(request)

        # 4) Check allowlist.
        if is_allowed(method, path, self._allowlist()):
            return await call_next(request)

        # 5) Block fail-closed con risposta strutturata.
        return JSONResponse(
            status_code=423,
            content={
                'detail': 'Mutation blocked in pre-QA',
                'code': 'PRE_QA_MUTATION_BLOCKED',
                'route': path,
                'method': method,
                'pack': 'PACK_128_ROUTE_DEEPLINK_LOCKDOWN_AND_BACKEND_MUTATION_MIDDLEWARE',
                'next_gate': 'Pack 128+ authorization required to enable this route',
            },
        )
