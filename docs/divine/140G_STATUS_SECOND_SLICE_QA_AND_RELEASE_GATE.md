# 140G — PROJECT_R Track G: Status Second-Slice QA & Release Gate

## Verdict
`TRACK_G_STATUS_SECOND_SLICE_QA_AND_RELEASE_GATE_READY`

## Marker JSON
`/app/data/design/project_management/project_r_status_second_slice_qa_release_gate_v1.json`

## Validator
`/app/backend/scripts/validate_project_r_status_second_slice_qa_release_gate_v1.py` → **[PASS]**

## QA requirements

### Fixture requirements
- Tutte e 8 le canonical fixtures (Track C) coperte.
- Ogni famiglia ha almeno una variante minor e una major.
- Test case: cancellazione coppie opposte.
- Test case: saturazione aggregate cap.
- Test case: PvP multiplier.
- Test case: boss guard multiplier.

### Deterministic regression
- Resolver: stesso input → output identico (no random).
- Flag-off byte-identical alla baseline (SHA256 sul payload envelope).
- `battle_engine.py` SHA256 invariato nelle fasi design + pure resolver.

### No-leak checks
- Con flag OFF: zero chiavi second-slice nell'API payload.
- Con flag OFF: zero chiavi second-slice nel battle log.
- Battle log byte-identical alla baseline con flag OFF.

### Mobile QA
- Frontend payload contract invariato nelle fasi design + pure resolver.
- UI/VFX schedulato solo dopo successo canary.
- Nessuna mobile build richiesta per questo pack.

## Release gate (signoff)
- rollback_owner: **required** (named individual or rotation)
- balance_signoff: **required**
- qa_signoff: **required**
- ops_signoff: **required**
- user_signoff: **required**

## Prod gate signatures (6)
`PROD_ROLLOUT_USER_APPROVAL`, `PROD_ROLLOUT_QA_APPROVAL`, `PROD_ROLLOUT_OPS_APPROVAL`, `PROD_ROLLOUT_ROLLBACK_OWNER_APPROVAL`, `PROD_ROLLOUT_BALANCE_APPROVAL`, `STATUS_RUNTIME_SECOND_SLICE_PROD_OK`.

## Side effects
Nessuno. `live_rollout_executed = false`, `db_writes = false`.
