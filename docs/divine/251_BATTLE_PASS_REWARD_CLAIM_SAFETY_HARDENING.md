# 251 — PROJECT_BATTLE_PASS_REWARD_CLAIM_SAFETY_HARDENING (v40 Track A)

**Phase**: PHASE_10A
**Mode**: REWARD_CLAIM_ECONOMY_SAFETY_HARDENING_PREVIEW_ONLY_NO_LIVE_CLAIM
**Feature flag**: `BATTLE_PASS_CLAIM_SAFETY_PREVIEW_ENABLED` (default OFF)
**Namespace**: `/api/battle-pass-claim-safety-preview`
**Operation family**: `battle_pass_reward_claim`

## Scopo

Layer preview-only/gated per il futuro claim Battle Pass (free + premium
preview + milestone + season preview). Nessun claim live. Nessun reward
grant. Nessuna mutazione inventory/currency/materials. Nessun premium
Battle Pass unlock/purchase. Nessuna mutazione VIP/shop/IAP. Nessun trigger
BP Delta. Zero scritture DB. `frontend/app/battlepass.tsx` MD5 locked,
intoccato. `frontend/app/vip.tsx` MD5 locked, intoccato.

## Endpoints

- `GET /api/battle-pass-claim-safety-preview/config`
- `POST /api/battle-pass-claim-safety-preview/validate-request`
- `POST /api/battle-pass-claim-safety-preview/guard-plan-preview`
- `POST /api/battle-pass-claim-safety-preview/idempotency-preview`

## Allowed operation types (4)

`battle_pass_free_reward_claim`,
`battle_pass_premium_reward_claim_preview`,
`battle_pass_milestone_reward_claim`,
`battle_pass_season_reward_claim_preview`.

## Required request fields (14)

`request_id`, `idempotency_key`, `operation_type`, `user_id`, `server_id`,
`season_id`, `battle_pass_track`, `reward_tier_id`, `reward_slot_id`,
`expected_user_bp_version`, `expected_battle_pass_state_version`,
`expected_inventory_version`, `client_trace_id`, `created_at`.

## Guard checks (26)

Incluse: `no_premium_currency_consumption`, `no_shop_purchase`,
`no_vip_unlock`, `no_battle_pass_purchase`,
`premium_track_claim_requires_entitlement_but_preview_never_grants`,
`bp_delta_not_triggered_in_preview`.

## Safety invariants

- `claim_enabled = false`
- `live_mutation_enabled = false`
- `reward_grant_enabled = false`
- `inventory_mutation_enabled = false`
- `currency_mutation_enabled = false`
- `premium_currency_used = false`
- `battle_pass_purchase_enabled = false`
- `premium_track_unlock_enabled = false`
- `vip_mutation_enabled = false`
- `shop_mutation_enabled = false`
- `bp_delta_triggered = false`
- `db_writes = 0`
