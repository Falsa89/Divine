# 133C — STATUS REQUIRED VALIDATORS PROMOTION

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_K` — Track C
**Verdict**: `TRACK_C_STATUS_REQUIRED_VALIDATORS_PROMOTED_TO_REQUIRED`
**Marker JSON**: `/app/data/design/status_effects/project_k_status_required_validators_promotion_v1.json`
**Validator**: `/app/backend/scripts/validate_project_k_status_required_validators_promotion_v1.py`

---

## Obiettivo

Valutare e — se sicuro — promuovere i 5 validator `REQUIRED-CANDIDATE` introdotti da Project J (OPTIONAL) alla sezione **REQUIRED** della suite, *senza* indebolire alcun REQUIRED preesistente.

## I 5 validator promossi

1. `validate_project_j_status_first_slice_resolver_pure_deterministic_v1.py`
2. `validate_project_j_status_first_slice_no_tick_loop_touch_v1.py`
3. `validate_project_j_status_first_slice_caps_respect_v1.py`
4. `validate_project_j_status_first_slice_pvp_fairness_audit_v1.py`
5. `validate_project_j_status_first_slice_rollback_runbook_v1.py`

## Rationale di sicurezza

I 5 validator asseriscono **invarianti strutturali** del modulo `status_first_slice_resolver_pure`:

- **purezza / determinismo** del resolver;
- **assenza di reference a tick loop** nel codice;
- **rispetto dei cap** numerici;
- **simmetria PvP** dei buff;
- **runbook di rollback** dichiarato e consistente.

Queste invarianti **non dipendono** dall'effettivo cablaggio del resolver in un battle runtime layer: restano stabili sia se Track B applica wiring sia se non lo applica (come nel caso attuale). La promozione **chiude** queste invarianti come barriere permanenti contro regressioni future.

## Diff suite REQUIRED

| Stato | Conteggio REQUIRED |
|-------|---------------------|
| Pre Pack K | **14** |
| Post Pack K | **19** (+5) |

`required_diff_guard_status`: `BREACH_APPROVED_BY_PACK_K_TRACK_C_PROMPT_AUTHORIZED` — promozione esplicitamente autorizzata dal prompt del Pack K, dunque la breccia del guard è *approvata e tracciata*.

## Conformità ai guardrail

- ✅ `required_weakening = false` (nessun REQUIRED rimosso o reso meno stringente).
- ✅ `fake_pass = false`.
- ✅ `hiding_failures = false`.
- ✅ I 5 validator passavano già stabilmente in OPTIONAL: la promozione non introduce flakiness.
- ✅ La suite parallela post-promozione resta `0 FAIL / 0 MISS`.
