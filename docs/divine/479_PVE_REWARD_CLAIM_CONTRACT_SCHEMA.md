# 479 — PvE Reward Claim Contract / Request / Response Schema

## Contratto
- `claim_source = pve`
- Sorgenti supportate: `story_alpha_slice_preview`, `training_combat_onboarding_preview`,
  `boss_tower_alpha_loop_preview`, `material_raid_pve_preview`
- Sorgenti escluse: `event_arena_alpha_preview`, arena ranking, guild war, gacha, shop, VIP, BP
- Sorgente canary preferita: `story_alpha_slice_preview` (fallback `material_raid_pve_preview`)

## Reward
- **Allowed**: `gold`, `account_exp`, `hero_exp`, `basic_material`
- **Forbidden**: `premium_currency`, `gacha_currency`, `event_currency`, `arena_points`,
  `vip_points`, `battle_pass_xp`

## Cap canary
- Allowlist 1–5 utenti
- Max 1 claim/utente
- Max 20 claim totali

## Request fields (obbligatori)
`user_id`, `server_id`, `route_id`, `run_id`, `claim_id`, `idempotency_key`, `reward_hash`, `reward_payload`

## Response fields (obbligatori)
`applied`, `idempotent_replay`, `rejected_reason`, `ledger_tx_id`, `rollback_token`, `observation_ref`, `db_writes`

## Stato corrente
Design-only. Nessuna route esposta. `db_writes_default=0`.
