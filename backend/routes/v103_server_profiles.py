"""v103 — Safe read-only /api/server-profiles/list endpoint.

Restituisce un elenco QA/fallback dichiarato per popolare la schermata di
selezione server senza fingere dati di produzione. La server data isolation
reale (account/inventory/team per server_id) e' PENDING e dichiarata
esplicitamente nei flag di risposta.

Safety:
- read-only (nessuna mutazione DB)
- nessun PII raw nel payload
- nessun OAuth token log
- nessun secret in repo
- is_qa_fallback=true dichiarato apertamente
- backend_data_isolation_implemented=false dichiarato apertamente
"""
from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter()


@router.get('/api/server-profiles/list')
async def list_server_profiles():
    """Returns a QA/fallback list of selectable server profiles.

    Names are explicitly tagged as [QA] to avoid being mistaken for
    production servers. has_character is omitted/false because per-server
    data isolation is not yet implemented (backend_data_isolation_implemented=false).
    """
    servers = [
        {
            'server_id': 'qa-eu-01',
            'server_name': '[QA] Aurora · EU-01',
            'region': 'EU',
            'status': 'online',
            'recommended': True,
            'is_last_played': False,
            'has_character': False,
            'character_name': None,
            'character_level': None,
            'power': None,
            'can_enter': True,
            'is_new': True,
            'reason_if_locked': None,
        },
        {
            'server_id': 'qa-eu-02',
            'server_name': '[QA] Crepuscolo · EU-02',
            'region': 'EU',
            'status': 'online',
            'recommended': False,
            'is_last_played': False,
            'has_character': False,
            'character_name': None,
            'character_level': None,
            'power': None,
            'can_enter': True,
            'reason_if_locked': None,
        },
        {
            'server_id': 'qa-na-01',
            'server_name': '[QA] Eclissi · NA-01',
            'region': 'NA',
            'status': 'busy',
            'has_character': False,
            'can_enter': True,
            'reason_if_locked': None,
        },
        {
            'server_id': 'qa-asia-01',
            'server_name': '[QA] Alba · ASIA-01',
            'region': 'ASIA',
            'status': 'online',
            'has_character': False,
            'can_enter': True,
            'reason_if_locked': None,
        },
        {
            'server_id': 'qa-eu-99',
            'server_name': '[QA] Nebbia · EU-99 (Manutenzione)',
            'region': 'EU',
            'status': 'maintenance',
            'has_character': False,
            'can_enter': False,
            'reason_if_locked': 'In manutenzione programmata',
        },
    ]
    return {
        'is_qa_fallback': True,
        'is_production_data': False,
        'backend_data_isolation_implemented': False,
        'backend_data_isolation_note': (
            'Server-scoped account/inventory/team isolation richiede schema DB '
            'multi-shard. Implementazione DEFERRED a v104+. Per ora ogni '
            'selezione server condivide la stessa collezione users (account_id) '
            'ma la UI dichiara apertamente la natura QA dei profili server.'
        ),
        'generated_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'pack': 'MEGA_RELEASE_ACCELERATION_52_v103',
        'servers': servers,
        'safety': {
            'read_only': True,
            'no_db_writes': True,
            'no_raw_token_logs': True,
            'no_provider_secrets': True,
            'fake_production_data': False,
            'declared_qa_fallback': True,
        },
    }
