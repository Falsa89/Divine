# 117E — V3 BLOCK E — ROSTER VISIBILITY INVARIANT VALIDATOR

**Pack**: `MEGA_COMBO_SLC_ACCELERATION_V3`  
**Block**: E — `ROSTER_VISIBILITY_INVARIANT_VALIDATOR_PACK`  
**Verdict**: 🟢 `BLOCK_E_ROSTER_VISIBILITY_INVARIANT_VALIDATOR_READY`  
**Modalità**: SUITE EXTENSION ONLY

---

## 1. Invariants enforced (7)

| ID | Check | Contract |
|---|---|---|
| INV_HEROES_COUNT | `GET /api/heroes` count | `== 100` |
| INV_GAIA_404 | `GET /api/heroes/primordial_gaia` | HTTP `== 404` |
| INV_BOREA_200_INERT | `GET /api/heroes/borea` | HTTP `== 200` + `is_obtainable == False` |
| INV_GREEK_BOREA_200_INERT | `GET /api/heroes/greek_borea` | HTTP `== 200` + `is_obtainable == False` |
| INV_BOREA_NOT_OBTAINABLE | `borea/greek_borea` NOT in obtainable pool | no leak |
| INV_CHARACTER_BIBLE_UNCHANGED | `sanctuary.py` / `heroes.py` no unauthorized diff | only authorized patches |
| INV_DRIFT_DOCS_KNOWN | drift docs count <= soglia | `KNOWN_NONBLOCKING_V1` |

---

## 2. Validator strategy

| Campo | Valore |
|---|---|
| Script | `/app/backend/scripts/validate_roster_visibility_invariants_v1.py` |
| Behavior | read-only HTTP smoke + JSON parse |
| DB writes | **0** |
| Runtime mutations | **0** |
| Contract | PASS se tutti i 7 invariants holdano |

---

## 3. Suite registration

- Task ID: `V3-ROSTER-VISIBILITY-INVARIANTS`
- Sezione: **OPTIONAL**

---

## 4. Verdict

🟢 **`BLOCK_E_ROSTER_VISIBILITY_INVARIANT_VALIDATOR_READY`**
