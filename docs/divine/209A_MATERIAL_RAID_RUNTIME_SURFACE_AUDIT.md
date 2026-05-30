# 209A — MATERIAL RAID SURFACE AUDIT

**Track**: A | **Verdict**: `TRACK_A_MATERIAL_RAID_SURFACE_AUDIT_READY`

## Legacy routes auditati

| Path | Handler | Ruolo | DB writes |
|---|---|---|---|
| `GET /raids` | `get_raids` | Boss raids list | NO |
| `POST /raid/create` | `create_raid` | Crea boss raid | **SÌ** |
| `POST /raid/attack/{boss_id}` | `attack_raid_boss` | Attacca boss → grant gold/gems/exp | **SÌ** |
| `GET /inventory` | `get_inventory` | EXP_ITEMS + SKILL_MATERIALS | NO |
| `POST /item-shop/buy` | `buy_item` | Buy EXP_ITEMS | **SÌ** |

## Material_id canonici Bible 202 presenti in DB

**ZERO**. Non esistono ancora come item_id.

## Safety guards MANCANTI

- canonical_material_id_registry ❌
- idempotent_grant_with_request_id ❌
- atomic_transaction ❌
- rate_limit_or_attempt_counter ❌
- deterministic_drop_resolver ❌
- audit_log ❌
- replay_protection ❌

## Decisione

**`PREVIEW_ONLY_NEW_NAMESPACE`** — legacy intoccato, nuovo `/api/material-raid/*` preview-only.
