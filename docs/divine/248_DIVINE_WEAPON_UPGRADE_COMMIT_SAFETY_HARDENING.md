# 248 — PROJECT_DIVINE_WEAPON_UPGRADE_COMMIT_SAFETY_HARDENING (v39 Track B)

**Phase**: PHASE_9B
**Mode**: ENDGAME_ECONOMY_SAFETY_HARDENING_PREVIEW_ONLY_NO_LIVE_COMMIT
**Feature flag**: `DIVINE_WEAPON_UPGRADE_SAFETY_PREVIEW_ENABLED` (default OFF)
**Namespace**: `/api/divine-weapon-upgrade-safety-preview`
**Operation family**: `divine_weapon_upgrade_commit`

## Distinzione canonica

- **Divine Weapon** = arma/relica personale character-bound per eroi nativi 6★.
- Divine Weapon NON sostituisce il gear classico (i 6★ hanno comunque gear slots).
- Divine Weapon NON è Artifact.
- Divine Weapon NON è Rune.
- Divine Weapon NON è Gemme.
- Richiede identità mitologica autentica prima di qualsiasi attivazione live.
- Richiede Character Bible prima di qualsiasi attivazione live.
- Può richiedere materiali dedicati e hero copies controllate ai livelli alti,
  ma questo pack non consuma nulla.

## Scopo

Layer preview-only/gated per il futuro commit di Divine Weapon unlock /
upgrade / awakening. Nessun commit live. Nessuna mutazione divine weapon.
Nessun consumo di hero copies. Nessun consumo materiali/oro/gemme. Nessun uso
premium `users.gems`. Nessun trigger BP Delta. Zero scritture DB. Character
Bible e hero final_numbers immutati.

## Endpoints

- `GET /api/divine-weapon-upgrade-safety-preview/config`
- `POST /api/divine-weapon-upgrade-safety-preview/validate-request`
- `POST /api/divine-weapon-upgrade-safety-preview/guard-plan-preview`
- `POST /api/divine-weapon-upgrade-safety-preview/idempotency-preview`

## Allowed operation types

`divine_weapon_unlock_preview`, `divine_weapon_upgrade`,
`divine_weapon_awaken_preview`.

## Required request fields (16)

Vedi `divine_weapon_upgrade_commit_request_schema_v1.json`.

## Guard checks (28)

Vedi `divine_weapon_guard_policy_v1.json`. Tra cui hero_is_native_6_star,
divine_weapon_bound_to_exact_hero, authentic_mythological_identity_required,
character_bible_required, anti_power_creep_validator.

## Safety invariants

- `commit_enabled = false`
- `live_mutation_enabled = false`
- `divine_weapon_mutation_enabled = false`
- `hero_copy_consumption_enabled = false`
- `materials_consumed = false`
- `currency_consumed = false`
- `premium_gems_currency_used = false`
- `bp_delta_triggered = false`
- `db_writes = 0`
- `character_bible_changed = false`
- `hero_final_numbers_changed = false`

## File non modificati

- `backend/routes/artifacts.py` (MD5 locked)
- hero routes / gear-equipment routes
- `backend/battle_engine.py`
- Character Bible
- hero final_numbers
- frontend gameplay routes
