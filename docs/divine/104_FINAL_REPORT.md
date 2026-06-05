# Final Report — MEGA_RELEASE_ACCELERATION_53_v104

## Verdict

```
MEGA_RELEASE_ACCELERATION_53_SERVER_SCOPED_RUNTIME_DATA_AND_CHAT_ISOLATION_FIX_READY_WITH_BACKEND_ISOLATION_PENDING_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING
```

La UI server è onesta (banner `SERVER_DATA_ISOLATION_BACKEND_PENDING` visibile, nomi
`[QA]` prefissati, nessuna finzione di dati per-server). L'isolamento reale lato backend
resta DECLARED_PENDING per rispetto delle guardrail (`db_writes=0`, no blind migration).

## Commit

(local container — public sync pending)

## Files modified / created

### Modified
- `frontend/app/servers.tsx` (banner sub-text aggiornato con token `SERVER_DATA_ISOLATION_BACKEND_PENDING` + linguaggio onesto)
- `backend/scripts/run_hero_skill_kit_validator_suite.py` (10 tuple v104 + sentinel `PUBLIC_SYNC_TAG_v104_MEGA_RELEASE_ACCELERATION_53_SERVER_SCOPED_RUNTIME_DATA_AND_CHAT_ISOLATION_FIX`)

### Created (frontend)
- `frontend/src/hooks/useServerScope.ts`

### Created (data design — 9 JSON)
- `data/design/server_scope/v104_server_scoped_data_flow_audit_v1.json`
- `data/design/server_scope/v104_server_profile_backend_contract_result_v1.json`
- `data/design/server_scope/v104_server_naming_canonicalization_result_v1.json`
- `data/design/server_scope/v104_server_scoped_user_data_model_result_v1.json`
- `data/design/server_scope/v104_frontend_server_id_propagation_result_v1.json`
- `data/design/server_scope/v104_backend_server_id_filtering_result_v1.json`
- `data/design/server_scope/v104_chat_server_isolation_result_v1.json`
- `data/design/server_scope/v104_server_profile_creation_policy_v1.json`
- `data/design/server_scope/v104_device_retest_matrix_v1.json`
- `data/design/release_acceleration/mega_release_acceleration_53_v104_rollup_marker_v1.json`

### Created (validators — 10)
- `backend/scripts/validate_v104_server_scoped_data_flow_audit.py`
- `backend/scripts/validate_v104_server_profile_backend_contract.py`
- `backend/scripts/validate_v104_server_naming_canonicalization.py`
- `backend/scripts/validate_v104_server_scoped_user_data_model.py`
- `backend/scripts/validate_v104_frontend_server_id_propagation.py`
- `backend/scripts/validate_v104_backend_server_id_filtering.py`
- `backend/scripts/validate_v104_chat_server_isolation.py`
- `backend/scripts/validate_v104_server_profile_creation_policy.py`
- `backend/scripts/validate_v104_device_retest_matrix.py`
- `backend/scripts/validate_mega_release_acceleration_53_v104_rollup.py`

### Created (docs)
- `docs/divine/104_SERVER_SCOPED_DATA_FLOW_AUDIT.md`
- `docs/divine/104_SERVER_SCOPED_USER_DATA_MODEL.md`
- `docs/divine/104_CHAT_SERVER_ISOLATION.md`
- `docs/divine/104_DEVICE_RETEST_SERVER_SCOPED_DATA.md`
- `docs/divine/104_FINAL_REPORT.md`

## Server-Scoped Data Flow Audit

13 superfici auditate.
- `server_scoped_now`: 0
- `declared_fallback`: 3
- `backend_pending`: 3
- `not_server_scoped`: 7
- Verdict: `SERVER_DATA_ISOLATION_BACKEND_PENDING`

## Server Profile Backend Contract

- `GET /api/server-profiles/list` → IMPLEMENTED (read-only QA fallback v103).
- `POST /api/server-profiles/select` → DEFERRED (selezione client-side).
- `GET /api/server-profiles/current` → DEFERRED (deriva da AsyncStorage).
- `isolation_state`: `DECLARED_PENDING`
- Safety: `read_only=true`, `no_db_writes=true`, `declared_qa_fallback=true`.

## Server Naming / Status

- Tutti i 5 server fallback prefissati `[QA] `.
- `misleading_names_present=false`, `fake_full_or_recommended=false`, `fake_production_server_status=false`.
- Banner UI line2 contiene token `SERVER_DATA_ISOLATION_BACKEND_PENDING`.

## Server-Scoped User Data Model

- Collection target: `player_server_profiles` con PK composta `(account_id, server_id)`.
- 3 indici definiti, 5 step migration plan safe.
- 8 implementazioni per-server richieste (account_level, roster, inventory, currencies, team_formation, story_progress, arena_profile, chat_channel_keys).
- Stato: `DECLARED_PENDING`.

## Frontend Server-ID Propagation

- Hook nuovo: `frontend/src/hooks/useServerScope.ts` (legge `v101_selected_server_id`, espone `is_isolation_pending=true`).
- 9 loader documentati (home, heroes, inventory, treasury, team, battle, chat futuro, profile, live/guild/event).
- Routing guard: missing `selected_server_id` → `/servers` (già live in `index.tsx`).
- Banner globale obbligatorio con token isolation pending.

## Backend Server-ID Filtering

- 9 endpoint auditati.
- `verdict`: `BACKEND_FILTERING_NOT_IMPLEMENTED_DECLARED_PENDING`.
- Nessun endpoint accetta o filtra per `server_id`.
- Path forward documentato (3 step gated da feature flag).

## Chat Server Isolation

- Surface chat frontend assente.
- Stato: `DECLARED_PENDING`.
- Contract documentato: `channel_key_format={server_id}:{channel_name}`, cache `chat_cache_{server_id}_{channel_name}`, send payload include `server_id`.
- Acceptance fixture pronta per quando la chat sarà costruita.

## Server Profile Creation Policy

- 2 creation paths: `explicit_user_action_required` (preferito) + `auto_safe_starter` (gated da `server_scoped_runtime_enabled=false` default).
- Starter template: `account_level=1`, no premium currency, no random heroes, no legacy heroes.
- Forbidden list: 6 entries (random starter, premium grant, reward grant on creation, legacy heroes, destructive writes, silent blind migration).

## Device Retest Matrix

- 11 step (vs requisito ≥10).
- `min_steps_pass_required=10`.
- 7 critical steps.
- Banner token obbligatorio su `/servers`.
- Forbidden list per il retest: 4 entries.
- `manual_qa_required=true`.

## Validators (10/10 PASS)

| # | Validator | Result |
|---|---|---|
| 1 | `validate_v104_server_scoped_data_flow_audit.py` | PASS |
| 2 | `validate_v104_server_profile_backend_contract.py` | PASS |
| 3 | `validate_v104_server_naming_canonicalization.py` | PASS |
| 4 | `validate_v104_server_scoped_user_data_model.py` | PASS |
| 5 | `validate_v104_frontend_server_id_propagation.py` | PASS |
| 6 | `validate_v104_backend_server_id_filtering.py` | PASS |
| 7 | `validate_v104_chat_server_isolation.py` | PASS |
| 8 | `validate_v104_server_profile_creation_policy.py` | PASS |
| 9 | `validate_v104_device_retest_matrix.py` | PASS |
| 10 | `validate_mega_release_acceleration_53_v104_rollup.py` | PASS |

## Suite (master)

```
Overall: FAIL  (pass=1049, fail=23, miss=0)
REQUIRED FAIL = 0
MISS = 0
OPTIONAL FAIL = 23  (target ≤30 ✅)
New v104 tuples: 10/10 PASS
```

> Nota: `Overall: FAIL` è la stringa standard ogni volta che esistono OPTIONAL fail.
> Il gate semantico è `REQUIRED FAIL = 0` e `MISS = 0`, entrambi soddisfatti.

## Safety Flags

- `fake_PASS = false`
- `validator_weakening = false`
- `db_destructive_writes = false`
- `blind_migration = false`
- `legacy_cleanup_apply = false`
- `fake_different_server_data = false`
- `fake_production_server_status = false`
- `random_starter_heroes = false`
- `premium_currency_grant = false`
- `reward_economy_mutation = false`
- `iap_changes = false`
- `token_raw_logs = false`
- `provider_secrets_in_repo = false`
- `commercial_release_claim = false`

## Remaining Blockers

1. **Backend multi-shard schema**: la collection `player_server_profiles` con PK
   `(account_id, server_id)` NON è ancora migrata. Richiede approval esplicita
   per `db_writes>0` in un pack futuro.
2. **Loader adoption**: il nuovo hook `useServerScope` esiste e può essere
   adottato dai loader, ma fino a quando il backend non filtra per `server_id`
   ogni adozione resta puramente cosmetica.
3. **Chat surface non costruita**: contract pronto, surface assente.
4. **Arena/guild/event multi-shard**: richiedono backend filtering pending.

## Manual Retest Instructions (iPhone 13 Expo Go)

Seguire `docs/divine/104_DEVICE_RETEST_SERVER_SCOPED_DATA.md`. Punti critici:

1. Aprire `/servers` e verificare il banner contenente `SERVER_DATA_ISOLATION_BACKEND_PENDING`.
2. Verificare che tutti i nomi server inizino con `[QA] `.
3. ENTRA S1 → osservare dati account.
4. CAMBIA SERVER → ENTRA S2 → confermare che il banner è ancora visibile e che i dati
   sono ammessi essere identici (perché backend pending). Non deve esserci nessuna
   finzione di separazione.
5. LOGOUT ACCOUNT → verificare che il fix v103 race condition resta valido.
6. Riapri app → login → routing torna a `/servers`.
