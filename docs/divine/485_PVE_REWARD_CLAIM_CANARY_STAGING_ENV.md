# 485 — PvE Reward Claim Canary Staging Environment (v79)

## Tipologia
- `staging_env_type = local_file_based`
- `staging_root = /app/data/canary_staging`
- **No DB live, no MongoDB, no Redis, no pymongo/motor**
- **No backend route exposure, no `.env` mutation**

## Vincoli operativi
- `live_db_allowed = false`
- `real_user_accounts_allowed = false`
- `premium_currency_allowed = false`
- `local_ledger_only = true`
- `max_claims_per_user = 1`, `max_total_claims = 20`
- `allowlist_required = true` (alias-only, no PII)
- `rollback_required = true`, `observation_required = true`, `kill_switch_required = true`

## Forbidden in staging
Live DB writes, MONGO_URL/pymongo/motor/Redis, backend route registration,
`server.py`/`battle_engine.py`/`story.tsx`/`combat.tsx` change, real user account
mutation, live reward grant, premium/gacha/event/arena/VIP/BP currency, asset
import, Character Bible/final_numbers/hero roster change, broad rollout,
`.env` mutation, validator weakening, fake PASS.
