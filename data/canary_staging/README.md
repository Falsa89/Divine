# PvE Reward Claim Canary — Local Staging (v79)

**STAGING LOCALE — NON PRODUZIONE.**

Questa directory contiene esclusivamente file di staging locale per il canary
del PvE Reward Claim. Nessuna scrittura su DB reale, nessun reward live,
nessuna mutazione account, nessun endpoint backend esposto.

## Contenuto
- `allowlist_v1.json`     — alias canary (no PII)
- `reward_fixtures_v1.json` — reward non-premium con cap
- `local_ledger_v1.json`  — ledger isolato locale (canary=true)
- `rollback_tokens_v1.json` — token rollback emessi
- `observation_log_v1.json` — log osservazione locale (no PII)

## Regole
- `live_db_allowed = false`
- `real_user_accounts_allowed = false`
- `premium_currency_allowed = false`
- `backend_route_exposure_allowed = false`
- `local_ledger_only = true`
- `max_claims_per_user = 1`, `max_total_claims = 20`
- caps: gold<=500, account_exp<=50, hero_exp<=100, basic_material<=3
