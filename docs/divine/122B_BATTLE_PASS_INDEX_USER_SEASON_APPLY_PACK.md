# 122B — V8 BLOCK_B — BATTLE_PASS_INDEX_USER_SEASON_APPLY_PACK

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V8`  
**Block**: B  
**Mode**: `design_dry_run_no_db_write`  
**Verdict**: 🟢 `BLOCK_B_BATTLE_PASS_INDEX_USER_SEASON_READY`  
**Rollback**: N/A (dry-run/design-only, nessuna DB mutation)

---

## 1. Scopo

Definire l'**indice canonico** `idx_battle_pass_user_season` come **definition + dry-run script**, indirizzando il residuo **V4 BLOCK_A R4 (`INDEX_LIVE_DEFERRED`)** senza alcuna `create_index` call live in V8.

## 2. Index canonical definition

| Campo | Valore |
|---|---|
| Nome | `idx_battle_pass_user_season` |
| Collezione | `battle_pass` |
| Fields | `(user_id ASC, season ASC)` |
| Unique | ✅ True |
| Sparse | ❌ False |
| `create_index` call | **DEFERRED** → `BATTLE_PASS_INDEX_USER_SEASON_APPLY_OPS_PACK` |

### Razionale

Un battle_pass document per `(user, season)` e' canonical per il pattern **single-doc-per-season** coerente con il signoff V6 BLOCK_A:
- **BP_D1=ACCOUNT_WIDE**: doc keyed by `user_id` → compatible
- **BP_D3=ACCOUNT_WIDE_ONCE**: claim arrays inside doc account-wide → compatible
- **BP_D4=GLOBAL_SEASON**: index include `season` per unique constraint per season → compatible
- **V7 BLOCK_B `$setOnInsert` doc shape**: payload gia' contiene `"season": 1` default → compatible

## 3. Dry-run script

- **Path**: `/app/backend/scripts/prepare_battle_pass_user_season_index_dry_run_v1.py`
- **Auto-run**: ❌ No
- **Gating env**: `V8_BLOCK_B_APPLY=YES`
- **Default**: stampa la `create_index` call pianificata + pre-flight checks read-only (count documents senza `season`, aggregation duplicate `(user_id, season)`). Restituisce `DRY_RUN`.
- **Apply mode in V8**: **REFUSED** → `APPLY_REFUSED_NO_PACK_AUTHORIZATION`.

## 4. Pre-flight check (per futuro apply pack)

Prima di applicare l'unique index, il futuro ops pack DEVE verificare in modalita' **read-only**:

| Check | Espressione | Blocker se |
|---|---|---|
| Docs senza `season` | `db.battle_pass.count_documents({'season': {'$exists': False}})` | `> 0` → data backfill required |
| Duplicate `(user_id, season)` | aggregate `$group` + `$match count > 1` | `> 0` → dedupe required |

## 5. Acceptance criteria per apply pack futuro

1. Esplicita user authorization in chat message
2. Pre-flight read-only: 0 docs con season missing
3. Pre-flight read-only: 0 duplicate `(user_id, season)`
4. Index creation idempotente (`skip-if-exists` by name)
5. Rollback script con `drop_index('idx_battle_pass_user_season')`
6. Post-apply validator: index esiste con expected canonical properties

## 6. Residuo V4 BLOCK_A R4

| Stato | Valore |
|---|---|
| Pre-V8 | `INDEX_LIVE_DEFERRED` (V4 reasons_for_ready_not_applied R4) |
| Post-V8 | `DEFINITION_READY_APPLY_DEFERRED_TO_OPS_PACK` |
| R4 closure | parziale (definition ready; apply ancora deferred a ops pack autorizzato) |

## 7. Validator

- **Path**: `/app/backend/scripts/validate_battle_pass_user_season_index_definition_v1.py`
- **Suite task_id**: `V8-BLOCK-B-BATTLE-PASS-INDEX-USER-SEASON` (OPTIONAL)
- **Type**: read-only (no DB, no HTTP, no script execution)
- **Verifiche chiave**: plan integrity, index canonical fields, coerenza signoff V6, dry-run gated/non auto-run, upstream V4/V6 marker presenti

## 8. Forbidden scope verification

| Forbidden | Violato? |
|---|---|
| live DB index creation | ❌ No |
| DB migration/backfill | ❌ No |
| battle pass behavior change | ❌ No |
| reward/premium change | ❌ No |
| pricing/currency change | ❌ No |
| runtime route mutation | ❌ No |
