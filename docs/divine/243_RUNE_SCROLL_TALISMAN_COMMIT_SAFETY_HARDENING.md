# 243 — PROJECT_RUNE_SCROLL_TALISMAN_COMMIT_SAFETY_HARDENING (v38 Track B)

**Phase**: PHASE_8B
**Mode**: BUILD_SYSTEM_ECONOMY_SAFETY_HARDENING_PREVIEW_ONLY_NO_LIVE_COMMIT
**Feature flag**: `RUNE_SCROLL_TALISMAN_SAFETY_PREVIEW_ENABLED` (default OFF)
**Namespace**: `/api/rune-scroll-talisman-safety-preview`
**Operation family**: `rune_scroll_talisman_commit`

## Distinzione canonica

- **Rune** = scroll/talismani/pergamene/sigilli equipaggiati sull'eroe.
- Rune NON è Gemme (le Gemme appartengono ai socket del gear).
- Rune NON è Artifact (collezione globale).
- Rune NON è Divine Weapon (sistema 6★ legato al personaggio).

## Scopo

Definire un livello preview-only/gated di safety per il FUTURO commit di
Rune/Scroll/Talisman (equip, replace, unsocket, fuse, upgrade). Nessun commit
live. Nessuna mutazione hero rune slots. Nessuna mutazione rune inventory.
Nessun consumo materiali/oro/gemme. Nessun uso premium `users.gems`. Nessun
trigger BP Delta. Zero scritture DB.

## Endpoints

- `GET /api/rune-scroll-talisman-safety-preview/config`
- `POST /api/rune-scroll-talisman-safety-preview/validate-request`
- `POST /api/rune-scroll-talisman-safety-preview/guard-plan-preview`
- `POST /api/rune-scroll-talisman-safety-preview/idempotency-preview`

## Allowed operation types

`rune_equip`, `rune_replace`, `rune_unsocket`, `rune_fuse`, `rune_upgrade`.

## Required request fields

14 campi obbligatori (vedi `rune_scroll_talisman_commit_request_schema_v1.json`).

## Guard checks (32)

Vedi `rune_scroll_talisman_guard_policy_v1.json` per la lista completa.
Includono ownership hero/rune, slot validity, fodder safety, defense policy
future, idempotency.

## Safety invariants

- `commit_enabled = false`
- `live_mutation_enabled = false`
- `hero_rune_slot_mutation_enabled = false`
- `rune_inventory_mutation_enabled = false`
- `materials_consumed = false`
- `currency_consumed = false`
- `premium_gems_currency_used = false`
- `bp_delta_triggered = false`
- `db_writes = 0`
- `calls_forge_legacy = false`

## File non modificati

- `backend/routes/forge.py`
- live rune routes (se presenti)
- hero routes
- inventory routes
- `backend/battle_engine.py`
- frontend gameplay routes

## Caveat suite runner pubblico

`SUITE_RUNNER_PUBLIC_BLOB_STALE_KNOWN_PLATFORM_LIMITATION` accettato.
