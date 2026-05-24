# 129A — Server Profiles Preview Contract Freeze (Track A)

**Verdict:** `TRACK_A_SERVER_PROFILES_PREVIEW_CONTRACT_FROZEN_INERT`

## Scope
Freeze contrattuale del comportamento read-only di `/api/server-profiles/select`
già hardened in Pack F. Nessun cambio runtime; default 503 con entrambi i
flag spenti.

## Cose congelate
- Risposta 503 (GET + POST) con payload `{status: disabled, feature_flag: SERVER_PROFILES_RUNTIME_ENABLED, ...}` quando flag OFF.
- Envelope con flag ON: `PROJECT_C_TRACK_A_BEHAVIOR_LAYER_READ_ONLY` con
  `mutation_executed=False`, `active_server_switched=False`,
  `dual_write_executed=False`.
- Doppio gate `SERVER_PROFILES_RUNTIME_ENABLED ∧ SERVER_PROFILES_PREVIEW_ENABLED`.
- Default handlers non chiamano `_preview_dry_run_envelope`.
- 0 DB write keyword nei handler.
- `server_profiles` collection: 0 docs.

## Vincoli rispettati
- NO live enable, NO active switch, NO DB writes, NO second server, NO frontend.
