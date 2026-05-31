# 242 — PROJECT_GEAR_FORGE_FUSION_COMMIT_SAFETY_HARDENING (v38 Track A)

**Phase**: PHASE_8A
**Mode**: BUILD_SYSTEM_ECONOMY_SAFETY_HARDENING_PREVIEW_ONLY_NO_LIVE_COMMIT
**Feature flag**: `GEAR_FORGE_FUSION_SAFETY_PREVIEW_ENABLED` (default OFF)
**Namespace**: `/api/gear-forge-fusion-safety-preview`
**Operation family**: `gear_forge_fusion_commit`

## Scopo

Definire un livello preview-only/gated di safety per il FUTURO commit di Gear
Forge/Fusion (upgrade, fusion, reforge preview). Nessun commit live. Nessuna
mutazione gear. Nessun consumo materiali/oro/gemme. Nessun uso premium
`users.gems`. Nessun trigger BP Delta. Zero scritture DB.

## Endpoints

- `GET /api/gear-forge-fusion-safety-preview/config`
- `POST /api/gear-forge-fusion-safety-preview/validate-request`
- `POST /api/gear-forge-fusion-safety-preview/guard-plan-preview`
- `POST /api/gear-forge-fusion-safety-preview/idempotency-preview`

## Allowed operation types

`gear_upgrade`, `gear_fusion`, `gear_reforge_preview`.

## Required request fields

14 campi obbligatori (vedi `gear_forge_fusion_commit_request_schema_v1.json`):
`request_id`, `idempotency_key`, `operation_type`, `user_id`, `server_id`,
`base_gear_instance_id`, `fodder_gear_instance_ids`, `target_level`,
`target_rarity`, `expected_base_gear_version`, `expected_inventory_version`,
`expected_materials_version`, `client_trace_id`, `created_at`.

## Guard checks (27)

Vedi `gear_forge_fusion_guard_policy_v1.json` per la lista completa. Tutti
runnati solo in modalità `would_run / preview_only`.

## Safety invariants

- `commit_enabled = false`
- `live_mutation_enabled = false`
- `gear_mutation_enabled = false`
- `materials_consumed = false`
- `currency_consumed = false`
- `premium_gems_currency_used = false`
- `bp_delta_triggered = false`
- `db_writes = 0`
- `calls_forge_legacy = false`

## File non modificati

- `backend/routes/forge.py`
- `backend/routes/equipment.py` (se presente)
- `backend/battle_engine.py`
- inventory/item routes
- frontend gameplay routes

## Caveat suite runner pubblico

`SUITE_RUNNER_PUBLIC_BLOB_STALE_KNOWN_PLATFORM_LIMITATION` accettato.
