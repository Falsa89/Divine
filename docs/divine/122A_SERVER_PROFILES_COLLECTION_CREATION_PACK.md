# 122A — V8 BLOCK_A — SERVER_PROFILES_COLLECTION_CREATION_PACK

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V8`  
**Block**: A  
**Mode**: `design_script_only_no_auto_run`  
**Verdict**: 🟢 `BLOCK_A_SERVER_PROFILES_COLLECTION_CREATION_READY`  
**Rollback**: N/A (dry-run/design-only, nessuna DB mutation)

---

## 1. Scopo

Preparare la **foundation inerte** per la creazione futura della collezione `server_profiles`:
- un **dry-run script** non auto-eseguibile, gated, che documenta le operazioni DB pianificate;
- un **plan JSON** con i requisiti di manual approval;
- un **validator** che verifica integrita' del plan e del gating del dry-run.

**Nessuna** collection creata. **Nessun** indice creato. **Zero** DB writes.

## 2. Upstream

- V6 BLOCK_C: `server_profiles_canonical_schema_proposal_v1.json` (10 fields canonical schema)
- V7 BLOCK_C: `server_profiles_schema_indexes_definition_v1.json` (3 indici canonical)

Questo pack chiude la **terza tappa** della progressione progettuale `proposal → indexes → collection-creation-plan` senza alcuna DB mutation.

## 3. Dry-run script

- **Path**: `/app/backend/scripts/prepare_server_profiles_collection_dry_run_v1.py`
- **Auto-run**: ❌ No (non in supervisord, non in suite, non chiamato da endpoint)
- **Gating env**: `V8_BLOCK_A_APPLY=YES`
- **Default mode** (no env): stampa le operazioni DB pianificate, restituisce `{"status": "DRY_RUN", "db_writes_executed": 0}`
- **Apply mode** in V8: **REFUSED** — lo script restituisce esplicitamente `APPLY_REFUSED_NO_PACK_AUTHORIZATION` perche' V8 BLOCK_A non autorizza l'apply. Il branch apply esiste solo per essere riutilizzato verbatim da un **futuro ops pack** con propria autorizzazione pack-level.

### Operazioni pianificate (stampate, non eseguite)

```
1) db.create_collection('server_profiles') if not exists
2) db.server_profiles.create_index([('user_id', 1), ('server_id', 1)], unique=True, name='idx_user_server')
3) db.server_profiles.create_index([('user_id', 1), ('is_archived', 1)], name='idx_user_active')
4) db.server_profiles.create_index([('server_id', 1), ('is_archived', 1)], name='idx_server_active')
```

## 4. Manual approval requirements (per futuro ops pack)

1. Esplicita autorizzazione utente in chat message per DB-write.
2. Verifica backend health (`/api/heroes=100`) immediatamente prima dell'apply.
3. Verifica mongo raggiungibile via `/api/heroes` 200.
4. Run dry-run in default mode (no env) PRIMA e capture output.
5. Capture pre-apply `db.list_collection_names()`.
6. Set `V8_BLOCK_A_APPLY=YES` e execute (solo via futuro pack, NON via V8).
7. Run post-apply validator immediatamente dopo.
8. Capture post-apply collection list + index list.

## 5. Validator

- **Path**: `/app/backend/scripts/validate_server_profiles_collection_creation_plan_v1.py`
- **Type**: read-only (no HTTP, no DB, no script execution)
- **Suite task_id**: `V8-BLOCK-A-SERVER-PROFILES-COLLECTION-PLAN` (OPTIONAL)
- **Verifiche**:
  1. Plan JSON integro + verdict corretto
  2. `runtime_patch_applied=False`, `db_collection_created=False`, `db_index_created=False`, `db_writes_executed=0`
  3. Dry-run script esiste e contiene gating `V8_BLOCK_A_APPLY`
  4. Dry-run script contiene clausola `APPLY_REFUSED_NO_PACK_AUTHORIZATION`
  5. Upstream V6 schema + V7 indexes esistenti
  6. 3 indici canonical consistenti
  7. Forbidden scope rispettato

## 6. Rollback strategy (per futuro apply)

- Collection vuota → `db.server_profiles.drop()` safe.
- Indici → `db.server_profiles.drop_indexes()` safe se nessuna app legge ancora.
- **In V8**: rollback N/A (no apply).

## 7. Forbidden scope verification

| Forbidden | Violato? |
|---|---|
| live collection creation | ❌ No |
| live index creation | ❌ No |
| DB migration/backfill | ❌ No |
| endpoint implementation | ❌ No |
| feature flag enable | ❌ No |
| second server opening | ❌ No |

## 8. Cosa sblocca

`SERVER_PROFILES_COLLECTION_APPLY_OPS_PACK` (futuro): autorizza esplicitamente l'esecuzione del dry-run con `V8_BLOCK_A_APPLY=YES`, creando la collection vuota + 3 indici canonical. Expected diff: +1 collection, +3 indexes, +0 data rows.
