# 154C — Server Profiles Preview Contract Draft

**Verdict:** `TRACK_C_SERVER_PROFILES_PREVIEW_CONTRACT_DRAFT_READY` · design-only

## Contratto draft (NO endpoint added in this pack)

### Endpoint
`GET /api/account/server-profiles/preview`

### Auth
- Required: ✅ (dependency `get_current_user`)

### Feature flag gating
- Primary: `SERVER_PROFILES_RUNTIME_ENABLED`
- Secondary (per preview envelope): `SERVER_PROFILES_PREVIEW_ENABLED`
- Both OFF response: `503 {status:'disabled', feature_flag:'SERVER_PROFILES_RUNTIME_ENABLED', reason:'preview gated; awaiting approval'}`

### Both ON response envelope
```json
{
  "status": "preview",
  "current_legacy_server": "<users.server or null>",
  "future_profile_readiness": {
    "profile_id": null,
    "is_archived": false,
    "dual_write_enabled": false,
    "seed_completed": false
  },
  "mutation_executed": false,
  "active_server_switched": false,
  "dual_write_executed": false
}
```

### Invariants di non-mutation
- no write `users.server`
- no write `server_profiles`
- no write `active_server_profile_id` (non esiste ancora)
- no capacity check enforcement (delegato al legacy POST durante transizione)
- no maintenance check bypass

### Metodi HTTP
- Supportati: `GET`
- Esplicitamente rifiutati: `POST`, `PUT`, `PATCH`, `DELETE`

### Telemetria raccomandata
- counter `server_profiles_preview_calls_total{result}`
- counter `server_profiles_preview_503_total`

## Pack futuro per implementare
`PROJECT_SERVER_PROFILES_AUTH_AND_CONTRACT_HARDENING_PACK`
