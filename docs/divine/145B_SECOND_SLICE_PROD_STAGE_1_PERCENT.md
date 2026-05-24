# 145B — SECOND SLICE PROD STAGE 1%

## Track B — `PROJECT_W_TRACK_B`

**Verdict:** `TRACK_B_SECOND_SLICE_PROD_STAGE_1_READY_NOT_APPLIED_PENDING_APPROVAL`

## 1. Obiettivo

Abilitare il rollout prod al **1%** del traffico **solo** se Track A `READY_ALL_SIGNATURES_PRESENT` e ambiente `PROD_CONFIRMED`. In assenza, marcare lo stage come `READY_NOT_APPLIED` e produrre documentazione + rollback path.

## 2. Stato

| Voce | Valore |
|---|---|
| Target rollout | 1% |
| Applied | ❌ **false** |
| Stage marker `STATUS_SECOND_SLICE_PROD_STAGE_1_APPROVAL` | MANCANTE |
| Firme prod | 0/7 |
| Track A verdict | `BLOCKING_MISSING_SIGNATURES` |
| Env classification | `NON_PROD_LOCAL_ONLY` |
| Flag flipped | ❌ |
| Prod env touched | ❌ |
| DB writes | 0 |
| `battle_engine.py` mutated | ❌ |
| `.env` byte-identical | ✅ |

## 3. Smoke planned (se autorizzato)

- `/api/heroes`
- `/api/heroes/borea`
- `/api/heroes/greek_borea`

## 4. No-leak keys planned

- `status_second_slice_preview`
- `__second_slice_seam_version`
- `second_slice_active`
- `second_slice_deltas`

## 5. Rollback path

`/app/backend/scripts/rollback_project_w_second_slice_prod_stage_1.py` → documentato e disponibile (pure-doc, non eseguito perché nessun flip applicato).

## 6. Stop condition

- Error rate > baseline
- Leak rilevato
- p95 > target
- Rollback signal manuale

## 7. Validator

`validate_project_w_second_slice_prod_stage_1_v1.py` → **PASS**.
