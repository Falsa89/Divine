# 95 — Read-Only Catalog Endpoints Runtime

## Pack

`MEGA_RELEASE_ACCELERATION_44_v95`

## Endpoints implementati (runtime, read-only, no DB writes)

- `GET /api/encounter-source/catalog` — ritorna i 7 encounter catalog (story/tower/arena/training/raid/event/guild_live);
- `GET /api/encounter-source/get?mode=X&source_id=Y` — ritorna una singola fonte encounter o l'intero catalog per la modalità;
- `GET /api/live-mode/catalog` — ritorna il catalog delle modalità live/guild/special;
- `GET /api/avatar-placeholder/catalog` — ritorna il registry placeholder avatar.

Ogni risposta contiene `v95_readonly=true` e `db_writes=0`.

## Source

- Router: `backend/routes/v95_readonly_catalog.py`
- Registrato in: `backend/server.py` (`app.include_router(v95_readonly_catalog_router)`).

## MD5

- **Old MD5** `backend/server.py`: `055df030553f4791e8cac14254f1b148`
- **New MD5** `backend/server.py`: `df22b6599cbc5621e9f0edeb0dcf832a`

MD5 break autorizzato esplicitamente dal pack v95 (`specs/v95_scope_guardrails.json` → `allowed_md5_unlocks.backend/server.py`).

## Smoke test

Tutti gli endpoint ritornano HTTP 200 + `v95_readonly=true` + `db_writes=0`. Verificato via `backend/scripts/validate_v95_readonly_catalog_endpoints_runtime.py`.

## Safety

- Nessun DB write
- Nessun reward grant
- Nessun ranking update
- Nessun PII
- Safe 404 per modalità/source_id sconosciuti, safe 400 per mode invalido
- Schema response stabile
