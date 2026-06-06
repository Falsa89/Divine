"""v108_AUTHORITATIVE_LIVE_PRECONDITIONS - Idempotency ledger adapter (DRY-RUN ONLY).

PUBLIC_SYNC_TAG_v108_AUTHORITATIVE_LIVE_PRECONDITIONS_AND_IDEMPOTENCY_LEDGER

Adapter SAFE. NESSUNA scrittura DB, NESSUNA creazione di collection, NESSUN
indice. Espone:
- LEDGER_SCHEMA (campi del documento futuro);
- compute_request_hash / compute_result_hash (sha256 deterministico);
- prepare_ledger_entry_dry_run (ritorna il documento candidato, NON lo scrive);
- check_live_preconditions(precond) (raise HTTP 423 esplicito se precond NOT met).

Il pack 68 non abilita reward/progress live e questi adapter NON devono mai
scrivere su DB finche' un futuro pack autorizzato non rimuovera' il dry-run.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Optional

from fastapi import HTTPException

PUBLIC_SYNC_TAG = (
    "PUBLIC_SYNC_TAG_v108_AUTHORITATIVE_LIVE_PRECONDITIONS_AND_IDEMPOTENCY_LEDGER"
)

LEDGER_COLLECTION_FUTURE_NAME = "battle_resolution_ledger"

LEDGER_SCHEMA: Dict[str, str] = {
    "idempotency_key": "string (required, unique per account_id+server_id)",
    "account_id": "string (required)",
    "server_id": "string (required)",
    "battle_instance_id": "string (required)",
    "battle_result_id": "string (uuid)",
    "mode": "enum",
    "encounter_id": "string (nullable)",
    "reward_policy": "enum {none, preview, live}",
    "progress_policy": "enum {none, preview, live}",
    "request_hash": "sha256",
    "result_hash": "sha256",
    "status": "enum {pending, applied, rolled_back, conflict_duplicate}",
    "created_at": "datetime utc",
    "expires_at": "datetime utc (request_hash idempotency window)",
    "replay_count": "int >=0",
    "safety": "object (dry_run, live, db_writes_performed=0 in dry-run)",
}

LIVE_PRECONDITION_CODES = {
    "AUTHORITATIVE_LIVE_REWARD_PRECONDITIONS_NOT_MET",
    "AUTHORITATIVE_LIVE_PROGRESS_PRECONDITIONS_NOT_MET",
    "AUTHORITATIVE_LIVE_IDEMPOTENCY_REQUIRED",
    "AUTHORITATIVE_LIVE_SERVER_FILTER_REQUIRED",
    "AUTHORITATIVE_LIVE_ROLLBACK_REQUIRED",
}


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def compute_request_hash(payload: Dict[str, Any]) -> str:
    """Hash deterministico del request payload (ordered keys)."""
    return _sha256(json.dumps(payload, sort_keys=True, default=str))


def compute_result_hash(envelope: Dict[str, Any]) -> str:
    """Hash deterministico del risultato (winner + turn_log + safety)."""
    snippet = {
        "winner": envelope.get("winner"),
        "turn_count": len(envelope.get("turn_log", []) or []),
        "authoritative_live": envelope.get("authoritative_live"),
        "authoritative_staging": envelope.get("authoritative_staging"),
        "reward_policy": envelope.get("reward_policy"),
        "progress_policy": envelope.get("progress_policy"),
    }
    return _sha256(json.dumps(snippet, sort_keys=True, default=str))


def prepare_ledger_entry_dry_run(
    *,
    idempotency_key: str,
    account_id: str,
    server_id: str,
    battle_instance_id: str,
    mode: str,
    encounter_id: Optional[str],
    request_payload: Dict[str, Any],
    result_envelope: Dict[str, Any],
    reward_policy: str = "preview",
    progress_policy: str = "preview",
) -> Dict[str, Any]:
    """Ritorna l'oggetto candidato per il ledger SENZA scriverlo.

    Garanzie:
    - nessun import di driver DB / db a livello modulo;
    - nessuna chiamata a una collezione;
    - safety.dry_run=True, safety.live=False, db_writes_performed=0.
    """
    return {
        "collection_target_name_future": LEDGER_COLLECTION_FUTURE_NAME,
        "sync_tag": PUBLIC_SYNC_TAG,
        "idempotency_key": idempotency_key,
        "account_id": account_id,
        "server_id": server_id,
        "battle_instance_id": battle_instance_id,
        "battle_result_id": result_envelope.get("battle_instance_id"),
        "mode": mode,
        "encounter_id": encounter_id,
        "reward_policy": reward_policy,
        "progress_policy": progress_policy,
        "request_hash": compute_request_hash(request_payload),
        "result_hash": compute_result_hash(result_envelope),
        "status": "dry_run_pending",
        "replay_count": 0,
        "safety": {
            "dry_run": True,
            "live": False,
            "db_writes_performed": 0,
            "collection_created": False,
            "index_created": False,
        },
    }


def check_live_preconditions(precond: Dict[str, bool]) -> None:
    """Solleva HTTP 423 con codice esplicito se anche UNA precondizione manca.

    Il chiamante (futuro pack live) DEVE invocare questa funzione PRIMA di
    qualsiasi scrittura su `battle_resolution_ledger` o qualsiasi reward/progress.

    precond expected keys:
      - reward_preconditions_pass: bool
      - progress_preconditions_pass: bool
      - idempotency_present: bool
      - server_filter_applied: bool
      - rollback_plan_ready: bool
    """
    if not precond.get("reward_preconditions_pass", False):
        raise HTTPException(
            status_code=423,
            detail={"code": "AUTHORITATIVE_LIVE_REWARD_PRECONDITIONS_NOT_MET", "sync_tag": PUBLIC_SYNC_TAG},
        )
    if not precond.get("progress_preconditions_pass", False):
        raise HTTPException(
            status_code=423,
            detail={"code": "AUTHORITATIVE_LIVE_PROGRESS_PRECONDITIONS_NOT_MET", "sync_tag": PUBLIC_SYNC_TAG},
        )
    if not precond.get("idempotency_present", False):
        raise HTTPException(
            status_code=423,
            detail={"code": "AUTHORITATIVE_LIVE_IDEMPOTENCY_REQUIRED", "sync_tag": PUBLIC_SYNC_TAG},
        )
    if not precond.get("server_filter_applied", False):
        raise HTTPException(
            status_code=423,
            detail={"code": "AUTHORITATIVE_LIVE_SERVER_FILTER_REQUIRED", "sync_tag": PUBLIC_SYNC_TAG},
        )
    if not precond.get("rollback_plan_ready", False):
        raise HTTPException(
            status_code=423,
            detail={"code": "AUTHORITATIVE_LIVE_ROLLBACK_REQUIRED", "sync_tag": PUBLIC_SYNC_TAG},
        )


__all__ = [
    "PUBLIC_SYNC_TAG",
    "LEDGER_COLLECTION_FUTURE_NAME",
    "LEDGER_SCHEMA",
    "LIVE_PRECONDITION_CODES",
    "compute_request_hash",
    "compute_result_hash",
    "prepare_ledger_entry_dry_run",
    "check_live_preconditions",
]
