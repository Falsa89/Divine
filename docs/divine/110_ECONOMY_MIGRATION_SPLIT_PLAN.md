# v110 PSP PREP — Economy Migration Split Plan

**Pack**: `MEGA_RELEASE_ACCELERATION_70_v110_PSP_APPLY_AND_LEGACY_CLEANUP_PREP_GATED_NOT_APPLIED`
**Track**: H
**Public sync tag**: `PUBLIC_SYNC_TAG_v110_PSP_APPLY_AND_LEGACY_CLEANUP_PREP_GATED_NOT_APPLIED`

## Regole di split

| Categoria | Esempi | Scope post-v110 |
|---|---|---|
| Soft currencies | `coins`, `stamina`, `arena_tickets`, `guild_coins`, `tower_coins`, `event_currency` | **server_scoped** (via PSP) |
| Hard currencies | `gold`, `summon_tickets_general` | **account_global** |
| Premium currencies | `diamonds`, `premium_summon_tickets`, `vip_tokens` | **account_global** |

Motivazione: le premium currencies sono legate a IAP/spese reali e rispettano gli store terms (Apple/Google) → restano account-global salvo decisione esplicita di business.

## Override richiede decisione esplicita

- Qualunque tentativo di server-scope su hard/premium → richiede approvazione esplicita.
- Qualunque duplicazione di balance soft tra server → vietata.
- Qualunque grant non documentato → vietato.

## Audit rules

- `per_user_total_premium_before_after_must_match`: true
- `per_user_total_hard_before_after_must_match`: true
- `per_user_total_soft_before_after_must_match_per_server_aggregated`: true
- `duplication_forbidden`: true
- `premium_grant_forbidden`: true
- `audit_log_collection`: `migration_logs.v110_economy_split`

## Rollback strategy

- Ripristino da backup `mongodump`.
- Confronto balance snapshot pre/post.
- Abort su qualunque mismatch.

## Stato v110

- `applied_in_this_pack`: **false**
- `db_writes`: **0**
- `premium_grant`: **false**
- `currency_duplication`: **false**

## Riferimento JSON

`/app/data/design/v110_psp_migration/v110_economy_migration_split_plan_v1.json`
