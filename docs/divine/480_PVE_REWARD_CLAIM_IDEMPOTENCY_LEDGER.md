# 480 — PvE Reward Claim Idempotency, Ledger & Replay Matrix

## Idempotency policy
- `same_key_same_hash` → restituisce risultato esistente (`idempotent_replay=true`)
- `same_key_different_hash` → reject `idempotency_conflict`
- `missing_key` / `expired_key` → reject
- `claim_over_user_cap` / `claim_over_total_cap` → reject
- `non_allowlisted_user` → reject
- TTL chiave: 86400s; formato: `idem:<server_id>:<user_id_hash>:<claim_id>`

## Ledger
- Collection isolata: `pve_reward_claim_canary_ledger_v1`
- Campi: `tx_id`, `user_id_hash`, `server_id`, `claim_id`, `route_id`, `reward_hash`,
  `reward_payload_summary`, `rollback_token`, `created_at`, `canary=true`
- **No PII** (nessun email/plain user_id) — **No premium fields**

## Replay matrix
10 scenari documentati (S1–S10): same_key_same_hash, same_key_different_hash,
missing_key, expired_key, over_user_cap, over_total_cap, non_allowlisted_user,
premium_reward_in_payload, hash_mismatch, happy_path_first_claim.

## DB writes
`db_writes_dryrun = 0`.
