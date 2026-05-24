# 123E — PROJECT_A Track E — HOUSING_MVP_BACKEND_CONTRACT

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_A`  
**Track**: E  
**Mode**: `design_doc_only_inert_stub_candidate`  
**Verdict**: 🟢 `TRACK_E_HOUSING_MVP_BACKEND_CONTRACT_READY`  
**Rollback**: N/A (doc only, no code)

---

## 1. Scopo

Avanzare Housing da design-only verso MVP definendo:
- contratto backend (endpoint, caps, schema)
- acceptance criteria del **pure HousingBonusResolver stub** (NON creato in Track E)
- phase plan 1–6

**Zero** live route, **zero** resolver importato dal runtime, **zero** DB write, **zero** bonus application a battle/account.

## 2. Backend contract (endpoint pianificati)

| Method | Path | Descrizione | Status |
|---|---|---|---|
| GET | `/api/housing/rooms` | list rooms (cap, capienza, occupanti) | NOT_IMPLEMENTED |
| GET | `/api/housing/objects` | list arredamento catalog (read-only) | NOT_IMPLEMENTED |
| GET | `/api/housing/residents` | list residenti con room_id, status | NOT_IMPLEMENTED |
| POST | `/api/housing/claim-all` | claim all bonuses, idempotent | NOT_IMPLEMENTED |

### Caps canonical

| Cap | Valore |
|---|---|
| Rooms per user | 6 |
| Objects per room | 12 |
| Residents per room | 4 |
| Claim cooldown | 24h |
| Max claim per call | 1 |

### DB collections pianificate
- `housing_rooms`
- `housing_objects`
- `housing_residents`
- `housing_claims_log`

**Esistenti**: nessuna (verificato live: 41 collections post Track A, nessuna housing).

## 3. Pure HousingBonusResolver stub (NON creato in Track E)

**Contract**: funzione pura `(user_state) -> {bonus_set}`, deterministica, **zero side effect**, **NOT imported** da combat/account runtime.

### Acceptance criteria
1. Input: `{user_id, housing_rooms[], objects[], residents[]}`
2. Output: `{hp_bonus: 0, atk_bonus: 0, def_bonus: 0, healing_bonus: 0}`
3. Output **forzato a 0** nello stub (no application live)
4. Unit testabile via pytest con fixtures frozen
5. **No import** in `battle_engine`/`battle_core`/`combat`
6. **No DB write**

**Stub file candidate**: `/app/backend/services/housing_bonus_resolver_stub.py` (**NOT created** in Track E).  
**Creazione deferita a**: `HOUSING_MVP_RESOLVER_STUB_CREATION_PACK`.

## 4. Phase plan (6)

| # | Fase | Status |
|---|---|---|
| 1 | BACKEND_CONTRACT_DESIGN | ✅ **DONE in Track E** |
| 2 | PURE_RESOLVER_STUB_CREATION | PLANNED |
| 3 | DB_COLLECTIONS_SCHEMA_DEFINITION | PLANNED |
| 4 | INERT_GET_ENDPOINTS_IMPLEMENTATION | PLANNED |
| 5 | CLAIM_ENDPOINT_IDEMPOTENT_IMPLEMENTATION | PLANNED |
| 6 | BONUS_APPLICATION_TO_BATTLE_LIVE | 🚫 FORBIDDEN_OUT_OF_SCOPE_PROJECT_A |

## 5. Forbidden scope verification

| Forbidden | Violato? |
|---|---|
| `/api/housing` live | ❌ No |
| Live HousingBonusResolver | ❌ No |
| DB write | ❌ No |
| Battle/account stat application | ❌ No |
| Frontend/UI | ❌ No |
