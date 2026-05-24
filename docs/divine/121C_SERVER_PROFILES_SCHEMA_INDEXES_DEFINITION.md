# 121C — V7 BLOCK_C — SERVER_PROFILES_SCHEMA_INDEXES_DEFINITION

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V7`  
**Block**: C  
**Mode**: `design_suite_only`  
**Verdict**: 🟢 `BLOCK_C_SERVER_PROFILES_SCHEMA_INDEXES_DEFINITION_READY`  
**Timestamp**: 20260524T134500Z  
**Rollback**: N/A (design-only, nessun runtime patch, nessuna DB write)

---

## 1. Scopo

Formalizzare la **definizione canonica dei 3 indici** della collezione `server_profiles` proposta in V6 BLOCK_C (`120C_SERVER_PROFILES_CANONICAL_SCHEMA_PROPOSAL.md`), pronta per essere usata come contratto da un futuro `SERVER_PROFILES_SCHEMA_INDEXES_APPLY_PACK` (ops pack dedicato con esplicita DB-write authorization).

## 2. 3 Indici canonici

| Nome | Collezione | Campi | Unique | Sparse | Razionale |
|---|---|---|---|---|---|
| `idx_user_server` | server_profiles | `(user_id ASC, server_id ASC)` | ✅ | ❌ | Garantisce one profile per `(account, server)`. Lookup primario. |
| `idx_user_active` | server_profiles | `(user_id ASC, is_archived ASC)` | ❌ | ❌ | Lista profili attivi per account. |
| `idx_server_active` | server_profiles | `(server_id ASC, is_archived ASC)` | ❌ | ❌ | Lista profili attivi per server (capacity / load checks). |

## 3. `create_index` calls (DEFERRED)

```python
# DEFERRED to: SERVER_PROFILES_SCHEMA_INDEXES_APPLY_PACK (ops, requires explicit DB-write approval)
db.server_profiles.create_index([('user_id', 1), ('server_id', 1)], unique=True, name='idx_user_server')
db.server_profiles.create_index([('user_id', 1), ('is_archived', 1)],               name='idx_user_active')
db.server_profiles.create_index([('server_id', 1), ('is_archived', 1)],             name='idx_server_active')
```

## 4. Acceptance criteria per l'apply pack futuro

1. `create_index` calls eseguite solo via ops pack dedicato con esplicita DB-write approval.
2. Index creation idempotente (drop+recreate o skip-if-exists).
3. Rollback script fornito (drop_index per nome).
4. Post-apply validator che verifica l'esistenza degli indici sulla collezione.
5. Collezione `server_profiles` creata nello stesso ops pack OPPURE pre-esistente.

## 5. Validator (V7 BLOCK_C)

- **Path**: `/app/backend/scripts/validate_server_profiles_schema_indexes_definition_v1.py`
- **Type**: read-only (no HTTP, no DB, no `create_index`)
- **Suite task_id**: `V7-BLOCK-C-SERVER-PROFILES-INDEXES-DEFINITION` (OPTIONAL)
- **Verifiche**:
  1. Marker integrity + verdict
  2. `runtime_patch_applied=False`, `db_index_created=False`
  3. Esattamente 3 indici definiti
  4. Naming canonico (`idx_user_server`, `idx_user_active`, `idx_server_active`)
  5. Unique constraint solo su `(user_id, server_id)`
  6. Tutti `deferred_to_pack` definiti
  7. Cross-reference V6 BLOCK_C schema proposal esistente

## 6. Forbidden scope verification

| Forbidden | Violato? |
|---|---|
| DB index creation (`create_index`) | ❌ No |
| Generic DB write | ❌ No |
| Collection creation | ❌ No |
| Runtime endpoint implementation | ❌ No |

## 7. Cosa sblocca

Questo BLOCK_C fornisce il **contratto canonico** richiesto da:
- `SERVER_PROFILES_SCHEMA_INDEXES_APPLY_PACK` (ops pack futuro, DB-write)
- SLC-H implementation pack (dual-write phase) per coerenza schema-side
