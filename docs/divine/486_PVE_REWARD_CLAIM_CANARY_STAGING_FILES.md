# 486 — PvE Reward Claim Canary Staging Files (v79)

## Manifest
- `/app/data/canary_staging/README.md`
- `/app/data/canary_staging/allowlist_v1.json` (alias: `canary_user_001..003`)
- `/app/data/canary_staging/reward_fixtures_v1.json` (gold<=500, account_exp<=50, hero_exp<=100, basic_material<=3)
- `/app/data/canary_staging/local_ledger_v1.json` (`canary=true`, `isolated_from_live=true`)
- `/app/data/canary_staging/rollback_tokens_v1.json`
- `/app/data/canary_staging/observation_log_v1.json`

## Proprietà
- **file-based only** (no DB)
- **no PII** (alias-only)
- reward fixtures **non-premium**, vietate chiavi `premium_currency`,
  `gacha_currency`, `event_currency`, `arena_points`, `vip_points`, `battle_pass_xp`
- ledger inizialmente vuoto; popolato solo se Track D apply locale riesce
