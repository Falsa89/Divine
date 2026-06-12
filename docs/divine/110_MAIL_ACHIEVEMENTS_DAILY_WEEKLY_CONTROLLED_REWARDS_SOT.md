# 110 — Pack 106 SOT (Source Of Truth)
## MAIL / ACHIEVEMENTS / DAILY-WEEKLY — CONTROLLED REWARDS

> Documento canonico Pack 106: 3 nuove claim source controllate ledger-backed.

## Strict keys

| Risorsa | Chiave server-scoped |
|---|---|
| mail claim | `user_id + server_id + mail_id` (claim_key = `mail_<sid>_<mail_id>`) |
| achievement claim | `user_id + server_id + achievement_id` (claim_key = `achievement_<sid>_<achievement_id>`) |
| daily reward | `user_id + server_id + task_id + UTC_day` (claim_key = `dwr_<sid>_<task_id>_<YYYY-MM-DD>`) |
| weekly reward | `user_id + server_id + task_id + UTC_ISO_week` (claim_key = `dwr_<sid>_<task_id>_<YYYY-W##>`) |

## Endpoints Pack 106

* `GET  /api/controlled-rewards/health`
* `GET  /api/controlled-rewards/catalog`
* `POST /api/controlled-rewards/mail/claim?server_id=<sid>`
* `POST /api/controlled-rewards/achievement/claim?server_id=<sid>`
* `POST /api/controlled-rewards/daily-weekly/claim?server_id=<sid>`

## Reward source registry additions (Pack 106)

* `mail_claim_controlled`
* `achievement_claim_controlled` — `completion_proof_required: true`
* `daily_weekly_reward_claim` — `period_keying: UTC_day_or_iso_week`

Tutte ledger-gated, idempotency mandatory, per-source kill switch default OFF.

## Kill switches (default OFF)

| Env | Scope |
|---|---|
| `REWARD_CLAIM_LEDGER_LIVE_ENABLED` | global ledger live |
| `MAIL_CLAIM_CONTROLLED_ENABLED` | mail claim controlled |
| `ACHIEVEMENT_CLAIM_CONTROLLED_ENABLED` | achievement claim controlled |
| `DAILY_WEEKLY_REWARD_CLAIM_ENABLED` | daily/weekly reward claim |

Ogni endpoint mutating Pack 106 gata su **AND** del kill switch globale e di quello per-source.

## Frontend guards (default OFF)

| Env | Scope |
|---|---|
| `EXPO_PUBLIC_REWARD_CENTER_UI_ENABLED` | UI reward center master flag |
| `EXPO_PUBLIC_MAIL_CLAIM_UI_ENABLED` | UI mail claim |
| `EXPO_PUBLIC_ACHIEVEMENT_CLAIM_UI_ENABLED` | UI achievement claim |
| `EXPO_PUBLIC_DAILY_WEEKLY_UI_ENABLED` | UI daily/weekly tasks |

## Server-Side Catalog

File: `backend/data/controlled_reward_catalog_v1.py`

* `MAIL_REWARD_CATALOG_V1`: 2 mail templates (`welcome_pack_mail`, `server_event_announce_mail`).
* `ACHIEVEMENT_REWARD_CATALOG_V1`: 2 achievement (`first_login_achievement`, `first_battle_achievement`).
* `DAILY_WEEKLY_REWARD_CATALOG_V1`: 3 task (2 daily + 1 weekly).
* `ALLOWED_PACK_106_REWARDS`: 7 reward keys (2 soft + 5 materials).
* `FORBIDDEN_PACK_106_REWARDS`: gems, premium_pull, standard_pull, stamina, experience, gold.

Validazione bloccante al load time. Client payload IGNORATO.

## Achievement Completion Proof

Marker test-only su `users.<id>`:
```
pack_106_achievement_completion_<achievement_id>: True
```
Se non presente, `/api/controlled-rewards/achievement/claim` ritorna **409 ACHIEVEMENT_COMPLETION_REQUIRED**.

## Forbidden in Pack 106 strict paths

* silent `server_id="s1"`
* account-wide reward writes
* `users.gold/users.gems/users.experience` mutation
* gems / premium / pull tickets / hero grant / equipment grant
* client-supplied reward payload
* non-idempotent repeat claim
* cross-server mail/achievement/daily/weekly claim
* IAP / gacha / payment
* battlepass / event / AFK / PvP / guild rewards live
* `reward_live_general=true`
* `release_readiness_claimed=true`

## Safety summary

- reward_live_general=false
- release_readiness_claimed=false
- premium_grants=false
- no_iap_gacha_payment=true
- no_account_wide_writes=true
- no_cross_server=true
- no_battlepass_event_afk_pvp_guild_live=true
- no users.gold/users.gems/users.experience mutation
- Pack 91-105 preservati
