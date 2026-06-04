# 497 — Reward Claim UI Summary — Gated Design (v80)

**SOLO DESIGN. Nessuna UI di produzione in v80.**

## Surface (futura)
`future_reward_claim_ui_summary_preview_shell` — sarà implementata come anteprima
in un pack futuro (v81 o successivo) solo dopo:
- wave2 clean confermata
- approvazione esplicita v81
- assenza di premium currency visibile

## Data source futura
- `local_canary_result_summary`
- `reward_payload_summary`
- `idempotency_status`
- `rollback_status`

## Concetti UI
reward_preview, claim_result, idempotent_replay_label, blocked_rejected_reason, rollback_state.

## Distinzioni obbligatorie
- preview/staging reward **vs** live reward
- vietato mischiare preview e live nella stessa surface senza label esplicito
- label richiesti: `PREVIEW`, `STAGING`, `CANARY_LOCAL`

## Vietato in UI summary
- esposizione UI di produzione
- bottone real-reward-claim
- trigger account_mutation o DB write
- chiamate a endpoint claim backend
- display di premium/gacha/event/arena/VIP/BP come grantable
