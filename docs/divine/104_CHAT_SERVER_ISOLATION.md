# v104 — Chat Server Isolation

**Pack**: `MEGA_RELEASE_ACCELERATION_53_v104_SERVER_SCOPED_RUNTIME_DATA_AND_CHAT_ISOLATION_FIX`

## Stato corrente

- Surface chat frontend: **NON presente** (nessun file `chat*` in `frontend/app`).
- Endpoint chat backend: **NON presenti** come superfici dedicate.
- Isolamento chat per `server_id`: **NON implementato**.
- Osservazione QA manuale post-v103: messaggi/contesto chat identici su S1 e S2.

## Stato dichiarato

`DECLARED_PENDING`

## Contract obbligatorio quando la chat verrà implementata

- **Formato chiave canale**: `{server_id}:{channel_name}`
- **Canale globale esplicito**: `global:global` (unico canale cross-server consentito)
- **Bot messages**: `server_bound` (mai cross-server)
- **Live announcement**: `server_bound` oppure `global` esplicito
- **Cache locale**: `chat_cache_{server_id}_{channel_name}`
- **Send payload**: deve includere `server_id` lato client

## Acceptance fixture (per QA quando la chat sarà live)

1. Invia messaggio M1 su S1 → appare su S1.
2. Cambia a S2 → M1 NON deve apparire (a meno che canale sia `global`).
3. Invia messaggio M2 su S2 → appare su S2.
4. Cambia a S1 → M2 NON deve apparire (a meno che canale sia `global`).

## Obbligo UI finché la chat non è implementata

Banner persistente su `/servers` con token `SERVER_DATA_ISOLATION_BACKEND_PENDING`.

## Safety

- `fake_per_server_chat_data = false`
- `fake_PASS = false`
- `validator_weakening = false`
