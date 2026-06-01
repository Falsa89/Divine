# 252 — PROJECT_MAIL_REWARD_CLAIM_SAFETY_HARDENING (v40 Track B)

**Phase**: PHASE_10B
**Mode**: REWARD_CLAIM_ECONOMY_SAFETY_HARDENING_PREVIEW_ONLY_NO_LIVE_CLAIM
**Feature flag**: `MAIL_CLAIM_SAFETY_PREVIEW_ENABLED` (default OFF)
**Namespace**: `/api/mail-claim-safety-preview`
**Operation family**: `mail_reward_claim`

## Scopo

Layer preview-only/gated per il futuro claim Mail (single, bulk preview,
attachment, compensation preview, event preview). Nessun claim live. Nessun
reward grant. Nessuna mutazione mail state (no delete, no read/unread flip,
no claim state). Nessuna mutazione inventory/currency/materials. Nessun
premium `users.gems`. Nessun trigger BP Delta. Zero scritture DB. Nessun
admin/mail sender live tooling.

## Endpoints

- `GET /api/mail-claim-safety-preview/config`
- `POST /api/mail-claim-safety-preview/validate-request`
- `POST /api/mail-claim-safety-preview/guard-plan-preview`
- `POST /api/mail-claim-safety-preview/idempotency-preview`

## Allowed operation types (5)

`mail_single_reward_claim`, `mail_bulk_reward_claim_preview`,
`mail_attachment_claim`, `mail_compensation_claim_preview`,
`mail_event_reward_claim_preview`.

## Required request fields (12)

`request_id`, `idempotency_key`, `operation_type`, `user_id`, `server_id`,
`mail_message_id`, `mail_reward_slot_ids`, `expected_mail_version`,
`expected_inventory_version`, `expected_user_wallet_version`,
`client_trace_id`, `created_at`.

## Guard checks (24)

Incluse: `mail_belongs_to_user`,
`mail_belongs_to_server_or_account_scope_valid`, `mail_not_deleted`,
`mail_not_expired`, `mail_not_already_claimed`, `bulk_claim_cap_valid`,
`sender_system_trust_policy_valid`,
`compensation_policy_requires_admin_marker_future`,
`no_premium_currency_consumption`, `bp_delta_not_triggered_in_preview`.

## Safety invariants

- `claim_enabled = false`
- `live_mutation_enabled = false`
- `reward_grant_enabled = false`
- `inventory_mutation_enabled = false`
- `currency_mutation_enabled = false`
- `premium_currency_used = false`
- `mail_state_mutation_enabled = false`
- `mail_delete_enabled = false`
- `mail_read_state_mutation_enabled = false`
- `bp_delta_triggered = false`
- `db_writes = 0`
