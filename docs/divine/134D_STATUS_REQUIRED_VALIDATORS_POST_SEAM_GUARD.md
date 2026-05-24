# 134D — STATUS REQUIRED VALIDATORS POST-SEAM GUARD

**Pack**: `PROJECT_L_STATUS_FIRST_SLICE_FLAGGED_CANARY_ENV` — Track D
**Verdict**: `TRACK_D_STATUS_REQUIRED_VALIDATORS_POST_SEAM_GUARD_READY`
**Marker JSON**: `/app/data/design/status_effects/project_l_status_required_validators_post_seam_guard_v1.json`
**Validator**: `/app/backend/scripts/validate_project_l_status_required_validators_post_seam_guard_v1.py`

---

## Obiettivo

Rafforzare la guardia sui 19 validator REQUIRED post-promozione Pack K, aggiungendo controlli che impediscono l'introduzione *non autorizzata* del seam o del resolver in un percorso runtime live.

## Conteggio REQUIRED

- Atteso: `19`
- Osservato (parsing in-script del file `run_hero_skill_kit_validator_suite.py`): ✅ `19`

## I 5 status REQUIRED validators (Pack K-promoted)

1. `validate_project_j_status_first_slice_resolver_pure_deterministic_v1.py`
2. `validate_project_j_status_first_slice_no_tick_loop_touch_v1.py`
3. `validate_project_j_status_first_slice_caps_respect_v1.py`
4. `validate_project_j_status_first_slice_pvp_fairness_audit_v1.py`
5. `validate_project_j_status_first_slice_rollback_runbook_v1.py`

Tutti **passing** nella suite parallel post-Pack L.

## Nuovi guard introdotti (in `validate_project_l_status_required_validators_post_seam_guard_v1.py`)

1. **seam non importato da battle_engine.py / battle_core.py / server.py / routes/\*.py** — scan testuale dei file con pattern `status_prefight_runtime_seam`.
2. **resolver puro non importato da forbidden runtime files** — scan testuale con pattern `status_first_slice_resolver_pure`.
3. **seam senza keyword tick/DoT/formula** — controllo che il file seam non contenga `tick_loop`, `apply_dot`, `damage_over_time`, `heal_over_time`.

## Modalità di registrazione

Il nuovo validator è registrato **OPTIONAL** (`PROJECT-L-TRACK-D-STATUS-REQUIRED-VALIDATORS-POST-SEAM-GUARD`). Promozione a REQUIRED non autorizzata da Pack L (default conservativo).

## Conformità ai guardrail

- ✅ `required_weakening = false`.
- ✅ Nessun REQUIRED rimosso o ammorbidito.
- ✅ Nessuna mutazione runtime.
