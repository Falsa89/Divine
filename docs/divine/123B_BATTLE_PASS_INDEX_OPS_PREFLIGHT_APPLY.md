# 123B — PROJECT_A Track B — BATTLE_PASS_INDEX_OPS_PREFLIGHT_APPLY

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_A`  
**Track**: B  
**Mode**: `ops_apply_idempotent_no_behavior_change`  
**Verdict**: 🟢 `TRACK_B_BATTLE_PASS_INDEX_APPLIED_SAFE`  
**Rollback ID**: `project_a_track_b_battle_pass_user_season_index_20260524T150000Z`

---

## 1. Scopo

Chiudere il **residuo V4 BLOCK_A R4** (`INDEX_LIVE_DEFERRED`) applicando l'indice unique `idx_battle_pass_user_season` su `battle_pass(user_id, season)`. Nessun cambiamento comportamentale, zero data mutation.

## 2. Upstream chain

- V4 BLOCK_A: identificato R4 come deferred
- V6 BLOCK_A signoff: BP_D1/D3/D4 chiusi (sblocco prerequisito)
- V7 BLOCK_B: `$setOnInsert` con `season: 1` default (compatibile)
- V8 BLOCK_B: index definition canonical + dry-run gated
- **Project A Track B**: **APPLIED** (questo report)

## 3. Pre-flight checks (live)

| Check | Soglia | Valore | Esito |
|---|---|---|---|
| `battle_pass` total docs | n/a | **1** | info |
| docs senza `season` | == 0 | **0** | ✅ |
| duplicate `(user_id, season)` | == 0 | **0** | ✅ |
| `battle_pass` indexes pre | `['_id_']` | `['_id_']` | ✅ |

Pre-flight verdict: **PASS** → apply autorizzato.

## 4. Applied index

```python
db.battle_pass.create_index(
    [("user_id", 1), ("season", 1)],
    unique=True,
    name="idx_battle_pass_user_season",
)
```

| Campo | Valore |
|---|---|
| Nome | `idx_battle_pass_user_season` |
| Collezione | `battle_pass` |
| Fields | `(user_id ASC, season ASC)` |
| Unique | ✅ True |
| Sparse | ❌ False |
| Idempotenza | ✅ skip-if-exists by name |

## 5. Postflight state (live)

| Risorsa | Valore |
|---|---|
| `battle_pass` indexes | `['_id_', 'idx_battle_pass_user_season']` |
| `battle_pass` total docs | **1** (invariato) |
| Data mutation | **NONE** |

## 6. Behavior preservation

| Aspetto | Valore |
|---|---|
| `POST /api/battlepass/buy-premium` behavior | ✅ invariata |
| Reward logic | ✅ invariata |
| Premium/free lane logic | ✅ invariata |
| Cost (500 gemme) | ✅ invariato |
| Response schema | ✅ invariato |
| `$setOnInsert` pattern V7 BLOCK_B | ✅ preservato |

## 7. V4 R4 transition

| Stato | Valore |
|---|---|
| Pre-Project_A | `INDEX_LIVE_DEFERRED` (V4 reasons R4) |
| Post-Project_A | **`INDEX_LIVE_APPLIED`** ✅ |

## 8. Smoke post-apply

| Endpoint | Atteso | Risultato |
|---|---|---|
| `GET /api/heroes` | 100 | ✅ 100 |
| `GET /api/heroes/primordial_gaia` | 404 | ✅ 404 |
| `GET /api/heroes/borea` | 200 | ✅ 200 |
| `GET /api/heroes/greek_borea` | 200 | ✅ 200 |

## 9. Rollback

- **Path**: `/app/backend/scripts/rollback_project_a_battle_pass_user_season_index.py`
- **Gating env**: `PROJECT_A_TRACK_B_ROLLBACK=YES`
- **Idempotente**: ✅ (no-op se index gia' assente)
- **Comportamento**: `db.battle_pass.drop_index('idx_battle_pass_user_season')`. Documenti non toccati.

## 10. Validator

- **Path**: `/app/backend/scripts/validate_project_a_battle_pass_index_ops_v1.py`
- **Suite task_id**: `PROJECT-A-TRACK-B-BATTLE-PASS-INDEX-OPS` (OPTIONAL)
- **Type**: live read-only check via pymongo + source check su economy.py (V7 hardening invariato)
- **Esito V_A**: ✅ PASS

## 11. Forbidden scope verification

| Forbidden | Violato? |
|---|---|
| Battle pass reward/premium/price change | ❌ No |
| DB migration/backfill | ❌ No |
| Broad economy refactor | ❌ No |
| Frontend/UI | ❌ No |
