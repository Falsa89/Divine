# 134C — STATUS PREFIGHT DRY-RUN CANARY PATH

**Pack**: `PROJECT_L_STATUS_FIRST_SLICE_FLAGGED_CANARY_ENV` — Track C
**Verdict**: `TRACK_C_STATUS_PREFIGHT_DRY_RUN_CANARY_READY`
**Marker JSON**: `/app/data/design/status_effects/project_l_status_prefight_dry_run_canary_v1.json`
**Validator**: `/app/backend/scripts/validate_project_l_status_prefight_dry_run_canary_v1.py`

---

## Obiettivo

Eseguire in-process un dry-run del path canary attraverso il seam, dimostrando che:

- in tutte le configurazioni *non* `(flag=true & dry_run=true)` il comportamento è *identity*;
- nella sola configurazione `(flag=true & dry_run=true)` il seam aggiunge un envelope preview senza mutare l'input.

## Matrice scenari

| ID | flag | `dry_run` | Atteso | Osservato |
|----|------|-----------|--------|-----------|
| DR1 | unset | `False` | identity | ✅ identity |
| DR2 | `false` | `False` | identity | ✅ identity |
| DR3 | `true` | `False` | identity (live activation **bloccata**) | ✅ identity |
| DR4 | `true` | `True`, statuses `[]` | zero envelope preview, payload immutato | ✅ envelope `{0,0,0,0}` |
| DR5 | `true` | `True`, statuses `[{buff_offensive, atk_pct, 0.10}]` | `atk_pct=0.10` (frazione; cap resolver `0.30`) | ✅ `atk_pct=0.10` |

## Note

- Il resolver puro lavora in *frazione* (cap master 0.30 = 30%). Track D5 valida quindi `0.10` (10%), non `10.0`.
- DR3 è il punto cruciale: con flag ON ma senza `dry_run=True`, il seam NON attiva il preview. Questo è il gating PROJECT_L: la commutazione `flag ON → effetto live` resta deferita a PROJECT_M.

## Conformità ai guardrail

- ✅ Nessuna mutazione battle live.
- ✅ Nessun DB write.
- ✅ Nessun frontend tocco.
