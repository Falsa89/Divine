# 510 — PvE Reward Claim Live-DB Readiness DESIGN Gate (v82)

## Importante
- **`design_only = true`**, **`live_db_apply_allowed = false`**
- `live_db_readiness_design_ready = true` significa SOLO che il design del gate è completo.
- **NESSUN live DB apply attivato in v82.**
- Un futuro pack dedicato sarà necessario per qualsiasi attivazione.

## Boundary principles
- local_file_based_canary_only fino al pack dedicato
- isolated canary ledger separato dalle collection live
- explicit env apply flag necessario per qualsiasi futuro DB apply
- audit log richiesto prima di DB apply
- manual approval + checksum richiesti

## Required for future live-DB pack
db_transaction_policy, real_account_allowlist, auth_guard, endpoint_contract,
rollback_script, observation_sink, hard_kill_switch, manual_approval_and_checksum.

## Wave-4 rollback drill
- Policy: `sample_two_canary_tx`
- 2 tx rolled-back (file-only)
- `db_rollback = false`, `db_writes = 0`
