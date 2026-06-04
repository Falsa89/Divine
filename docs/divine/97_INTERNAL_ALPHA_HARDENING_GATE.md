# 97 — Internal Alpha Hardening Gate

## Pack

`MEGA_RELEASE_ACCELERATION_46_v97`

## Stato per area

| Area | Stato |
|------|-------|
| **account_auth** | INTERNAL_ALPHA_READY (refresh rotation, soft delete, privacy-status, logout-all) |
| **engine** | READY (21/21 regression PASS) |
| **playability** | READY (formation account bridge v96) |
| **live_guild** | READY_GATED |
| **bots_server_actors** | DESIGN_READY (runtime persistence DEFERRED a v98) |
| **chat** | DESIGN_READY (Borea fixture PASS, manual ultimate forbidden) |
| **optional_fail_cleanup** | CLOSED_ALPHA_BLOCKER_HONEST (target<=30 NOT reached, current=133) |
| **mobile_qa** | INTERNAL_ALPHA_CONDITIONAL (manual QA required) |
| **load_locust** | INTERNAL_ALPHA_READY (low-impact smoke PASSED) |
| **compliance_privacy** | INTERNAL_ALPHA_DESIGN_READY (live URLs required for closed alpha) |

## Overall verdict

- **READY_FOR_INTERNAL_ALPHA_HARDENED**: true
- **CONDITIONAL_FOR_CLOSED_ALPHA**: true
- **BLOCKED_FOR_COMMERCIAL_RELEASE**: true

## Blockers per closed alpha

1. `provider_token_verification`: real Google/Apple credentials required.
2. `optional_fail_cleanup`: target ≤ 30 NOT reached (current 133).
3. `mobile_qa`: physical device run Android/iOS.
4. `load_locust`: full dedicated infra run.
5. `compliance`: live privacy/terms URLs pubblici.
6. `bot_runtime_persistence`: deferred to v98 (controlled rollout).
7. `hard_delete_runtime`: commercial review.

## Safety flags

Tutti `false`: reward_live, iap_active, production_push, production_broadcast, real_pii_in_bot_chat, fake_users_presented_as_real, day_one_high_level_bots, bot_event_access_bypass, bot_ranking_domination, bot_premium_reward_theft, random_opponents, bot_economy_exploit, raw_oauth_logs, provider_secrets_in_repo, validator_weakening, fake_PASS.
