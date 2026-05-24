# 121E — V7 BLOCK_E — BOREA_INERT_BASELINE_INVARIANT_HARDENING

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V7`  
**Block**: E  
**Mode**: `suite_doc_only`  
**Verdict**: 🟢 `BLOCK_E_BOREA_INERT_BASELINE_INVARIANT_HARDENING_READY`  
**Timestamp**: 20260524T134500Z  
**Rollback**: N/A (suite-only, nessun runtime patch)

---

## 1. Scopo

Introdurre un **validator dedicato Borea-only** (`validate_borea_inert_baseline_v1.py`) indipendente dal `validate_roster_visibility_invariants_v2.py` per garantire una **separazione semantica chiara** e uno smoke piu' veloce focalizzato esclusivamente sulle invarianti `borea / greek_borea / primordial_gaia / heroes_count`.

## 2. Invarianti baseline canonical (9)

| ID | Invariante | HTTP / Field |
|---|---|---|
| **B_INV1** | `GET /api/heroes/borea` → 200 | 200 |
| **B_INV2** | borea `is_obtainable == False` (o assente = non-obtainable) | field |
| **B_INV3** | `GET /api/heroes/greek_borea` → 200 | 200 |
| **B_INV4** | greek_borea `is_obtainable == False` (o assente) | field |
| **B_INV5** | borea **NOT** in `/api/heroes` (obtainable subset hidden) | list |
| **B_INV6** | greek_borea **NOT** in `/api/heroes` (obtainable subset hidden) | list |
| **B_INV7** | `GET /api/heroes/primordial_gaia` → 404 (catalog-only) | 404 |
| **B_INV8** | `/api/heroes` count == 100 | length |
| **B_INV9** | borea/greek_borea slug invariati (legacy stability) | field |

## 3. Relazione con validator pregressi

| Validator | Source | Invariants | Scope |
|---|---|---|---|
| `validate_roster_visibility_invariants_v1.py` | V3 BLOCK_E | 7 | roster visibility ampio |
| `validate_roster_visibility_invariants_v2.py` | V5 BLOCK_C | 11 | superset v1 (+role visibility) |
| **`validate_borea_inert_baseline_v1.py`** | **V7 BLOCK_E** | **9** | **borea-only dedicato; smoke veloce** |

Il validator V7 BLOCK_E **non sostituisce** i precedenti — coesistono in OPTIONAL: i 3 garantiscono coverage progressivo con angolazioni diverse.

## 4. Inert semantics chiarita

Un eroe e' considerato **inert** quando:
- detail endpoint risponde **200** (catalog visibility)
- `is_obtainable` e' **esplicitamente False** OPPURE il campo e' **assente** dalla response (entrambi equivalgono a `not obtainable`)
- lo slug NON appare nel subset `/api/heroes` (lista degli obtainable)
- nessun cambiamento di slug rispetto al catalog canonico

Questa interpretazione e' coerente con la response attuale di `/api/heroes/borea` che NON espone `is_obtainable` per design (campo omesso = false implicito).

## 5. Forbidden scope verification

| Forbidden | Violato? |
|---|---|
| Borea activation | ❌ No |
| is_obtainable flip | ❌ No |
| Gacha/summon visibility change | ❌ No |
| Character Bible mutation | ❌ No |
| Runtime endpoint nuovo | ❌ No |

## 6. Registrazione suite

- **task_id**: `V7-BLOCK-E-BOREA-INERT-BASELINE`
- **section**: OPTIONAL
- **script**: `/app/backend/scripts/validate_borea_inert_baseline_v1.py`
- **Exit code**: 0 PASS / 1 FAIL
- **Stato post-V7**: ✅ PASS in `367 PASS / 0 FAIL / 0 MISS`

## 7. Smoke output

```
[PASS] V7 BLOCK_E Borea inert baseline invariants OK (9/9 + heroes=100 + primordial_gaia=404)
```
