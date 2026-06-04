# 493 — PvE Reward Claim Canary Wave-2 Files (v80)

## File creati sotto `/app/data/canary_staging/`
- `wave2_allowlist_v1.json` (alias: `canary_user_001..003`, no PII)
- `wave2_reward_fixtures_v1.json` (non-premium only, caps 500/50/100/3)
- `wave2_plan_v1.json` (3 utenti, 3 route preview)

## File creati dinamicamente dal runner
- `wave2_local_ledger_v1.json` (`wave=2`, `canary=true`, `isolated_from_live=true`)
- `wave2_rollback_tokens_v1.json`
- `wave2_observation_log_v1.json`

## Garanzie
- file-based only (no DB)
- no PII (solo alias)
- reward fixtures non-premium
- separati dai file v79 (compat preservata)
