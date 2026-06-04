# 482 — Rollback / Observation / Kill Switch

## Rollback
- `rollback_token_required = true`
- Scope: **solo** righe canary (`canary=true`) entro la finestra
- Vietato rollback su balance live o broad rollback

## Observation
- Finestra: 60 minuti
- Metriche: `claim_attempts_total`, `claim_success_total`, `claim_reject_total`,
  `idempotent_replay_total`, `duplicate_conflict_total`, `non_allowlisted_reject_total`,
  `over_cap_reject_total`, `premium_reward_reject_total`, `db_write_total`,
  `rollback_required_total`, `error_total`
- Sink: `local_canary_log_only` (no PII)

## Kill switch
- Azione: `disable_canary_immediately`
- P0: `premium_reward_granted`, `db_write_outside_allowlist`,
  `account_persistence_outside_canary`, `duplicate_grant_conflict`
- P1: `observation_window_breach`, `unexpected_error_rate_spike`
- On trigger: disable + alert + rollback canary tx + freeze allowlist
