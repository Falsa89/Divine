# 247 — PROJECT_ARTIFACT_UPGRADE_COMMIT_SAFETY_HARDENING (v39 Track A)

**Phase**: PHASE_9A
**Mode**: ENDGAME_ECONOMY_SAFETY_HARDENING_PREVIEW_ONLY_NO_LIVE_COMMIT
**Feature flag**: `ARTIFACT_UPGRADE_SAFETY_PREVIEW_ENABLED` (default OFF)
**Namespace**: `/api/artifact-upgrade-safety-preview`
**Operation family**: `artifact_upgrade_commit`

## Distinzione canonica

- **Artifact** = collezione globale roster/account.
- Artifact NON è equip / NON è Gear.
- Artifact NON è Gemme.
- Artifact NON è Rune (scroll/talismani sull'eroe).
- Artifact NON è Divine Weapon.
- I bonus globali Artifact non si attivano senza Bible/validator dedicati.

## Scopo

Layer preview-only/gated per il futuro commit di Artifact upgrade / duplicate
fusion / limit break. Nessun commit live. Nessuna mutazione artifact. Nessuna
attivazione bonus globali. Nessun consumo materiali/oro/gemme. Nessun uso
premium `users.gems`. Nessun trigger BP Delta. Zero scritture DB.

## Endpoints

- `GET /api/artifact-upgrade-safety-preview/config`
- `POST /api/artifact-upgrade-safety-preview/validate-request`
- `POST /api/artifact-upgrade-safety-preview/guard-plan-preview`
- `POST /api/artifact-upgrade-safety-preview/idempotency-preview`

## Allowed operation types

`artifact_upgrade`, `artifact_duplicate_fusion`, `artifact_limit_break_preview`.

## Required request fields (14)

Vedi `artifact_upgrade_commit_request_schema_v1.json`.

## Guard checks (27)

Vedi `artifact_upgrade_guard_policy_v1.json`. Tra cui Artifact Bible
required, anti-power-creep validator required, global bonus activation
disabled.

## Safety invariants

- `commit_enabled = false`
- `live_mutation_enabled = false`
- `artifact_mutation_enabled = false`
- `artifact_bonus_activation_enabled = false`
- `materials_consumed = false`
- `currency_consumed = false`
- `premium_gems_currency_used = false`
- `bp_delta_triggered = false`
- `db_writes = 0`
- `calls_artifacts_legacy = false`

## File non modificati

- `backend/routes/artifacts.py` (MD5 locked)
- gacha/pull/banner routes
- inventory routes
- `backend/battle_engine.py`
- frontend gameplay routes
