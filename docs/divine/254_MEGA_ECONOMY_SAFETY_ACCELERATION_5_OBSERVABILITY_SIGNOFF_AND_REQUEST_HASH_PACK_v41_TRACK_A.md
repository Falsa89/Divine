# 254 — MEGA_ECONOMY_SAFETY_ACCELERATION_5 v41 · Track A

## Shared Request Hash & Idempotency Contract

**Pack**: `MEGA_ECONOMY_SAFETY_ACCELERATION_5_OBSERVABILITY_SIGNOFF_AND_REQUEST_HASH_PACK_v41`  
**Track**: A  
**Modalità**: DESIGN_CONTRACT_AUDIT_ONLY  
**Runtime activation**: `false`  
**DB writes**: `0`

### Scopo

Introdurre un contratto **condiviso** di request-hash e idempotency per tutte
le 8 famiglie operation economy già coperte da safety preview (v37–v40):

- `gem_socket_commit`
- `material_raid_claim`
- `gear_forge_fusion_commit`
- `rune_scroll_talisman_commit`
- `artifact_upgrade_commit`
- `divine_weapon_upgrade_commit`
- `battle_pass_reward_claim`
- `mail_reward_claim`

Il contratto **estende** `economy_idempotency_and_atomic_commit_contract_v1`
(v37) aggiungendo regole canoniche di hashing della request, raccordo
client/server idempotency, conflict detection cross-family.

### File creati

- `data/design/economy_safety/shared_request_hash_idempotency_contract_v1.json`
- `data/design/economy_safety/shared_request_hash_idempotency_contract_proof_marker_v1.json`
- `backend/scripts/validate_shared_request_hash_idempotency_contract_v1.py`

### Invarianti di sicurezza

- `no_pii_in_request_hash = true`
- `no_pii_in_idempotency_key = true`
- `no_live_commit_in_this_pack = true`
- `no_live_claim_in_this_pack = true`
- `no_db_writes_in_this_pack = true`
- `no_reward_grant_in_this_pack = true`
- `no_premium_currency_use_in_this_pack = true`
- `no_bp_delta_runtime_in_this_pack = true`

### Algoritmo canonico

```
server_request_hash = sha256(
  operation_family | operation | user_id |
  canonicalize(critical_payload_subset)
) -> hex lowercase, troncato a 32 char
```

Dove `canonicalize` rimuove i campi volatili (clock, telemetry, UA) e tutti
i campi PII (email, ip, device_id, push_token, phone).

### Cross-family critical payload subsets

Definiti per ciascuna delle 8 famiglie, per evitare collisioni cross-user e
cross-family. Il subset critico è il minimo set di campi che identifica
in modo univoco la transazione.

### Conflict rules

| same_key | same_hash | esito |
|----------|-----------|-------|
| ✓ | ✓ | `return_cached_result` |
| ✓ | ✗ | `reject_with_conflict` |
| ✗ | ✓ | `allowed_if_distinct_user_id_or_operation_family` |
| any | any | `cross_user_collision = forbidden` |

Replay window: `86400s` default, `604800s` max.

### Non in questo pack

- Implementazione runtime del contratto (NO codice di hashing attivo)
- Modifiche alle route v37–v40 (intatte)
- Modifiche a `server.py` (intatto)
- Modifiche a `battle_engine.py`, `backend/.env`, `routes/artifacts.py`,
  `frontend/app/battlepass.tsx`, `frontend/app/vip.tsx` (MD5-locked)
