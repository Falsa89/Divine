# 123 — Tower Execute / Floor Claim Ledger / Daily Quest 2 Hook SOT (Pack 103)

Documento SOT del Pack 103 SUPERPACK.

## Stato
- `tower_floor_completion_claim` source: live, gated, ledger-backed.
- `POST /api/tower/strict/battle/execute`: NEW gated path. Triple kill switch AND (`REWARD_CLAIM_LEDGER_LIVE_ENABLED`+`TOWER_STRICT_EXECUTE_ENABLED`+`TOWER_FLOOR_CLAIM_ENABLED` tutti default OFF).
- Daily quest event mapping: `tower_floor_clear_success` -> `daily_quest_2` (source route `tower_strict_battle_execute`).
- Tower legacy: rimane quarantinato (Pack 101 preserved).

## Reward bands (server-side fixed)
- floors 1-9: `{mission_coins: 5, honor: 3}`.
- floors 10-49: `{mission_coins: 12, honor: 6}`.
- floor 50: `{mission_coins: 50, honor: 25}` (major boss mid).
- floors 51-99: `{mission_coins: 18, honor: 9}`.
- floor 100: `{mission_coins: 100, honor: 50}` (strongest launch).

Solo `mission_coins` e `honor` (PSP soft). NO gems, NO premium, NO pull, NO hero/equipment.

## Test marker
`pack_103_test_artifact=true` obbligatorio sull'utente per usare l'execute endpoint (test-only finché non c'è runtime battle reale).

## Idempotency
- `claim_key = tower_floor_<server_id>_<floor>`.
- `server_idem_token = sha1(claim_key|client_token)`.
- Replay (qualsiasi token) -> idempotent_replay=true, no double grant, no double advance.
- PSP.tower_progress.floor avanza solo al primo grant del floor.

## S1/S2 isolation
Claim su S1 NON tocca PSP/tracker di S2. Verificato dallo smoke.

## Vincoli
- NO reward live general.
- NO premium/hard grants.
- NO `users.gold/users.gems/users.experience` mutation.
- NO `/api/battle/simulate` call.
- NO battle_engine rewrite.
- NO release readiness claim.
