# 207E — FUSION SAFETY AND ECONOMY POLICY

**Track**: E | **Verdict**: `TRACK_E_FUSION_SAFETY_AND_ECONOMY_POLICY_READY`

## Fusion commit abilitato

**NO**.

## Blocker

1. Legacy `/forge/fuse` manca check `fodder.equipped_to`.
2. Manca check `fodder.locked` / `favorite`.
3. Manca check `base.in_active_team`.
4. Manca atomicità transactional sui delete cascata.
5. Manca pre-check negative balance gold pre-mutation.
6. Manca envelope di outcome deterministico esplicito.

## Required guards per future commit

- auth_required, ownership_user_id_match
- base_belongs_to_user, fodder_belongs_to_user
- fodder_not_equipped, fodder_not_locked_or_favorite, fodder_not_protected_or_seasonal
- base_not_in_active_team
- deterministic_result_envelope
- no_paid_currency, no_negative_balance
- no_broad_db_migration, atomic_transaction

## Economia toccata in questo pack

**Nessuna**. Zero paid currency, zero gold spent, zero materiali spesi, zero shop/BP/VIP/IAP unlock.

## Pack futuro proposto

`PROJECT_GEAR_FORGE_FUSION_COMMIT_SAFETY_HARDENING_PACK`.
