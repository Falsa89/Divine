# 136F — CANARY ROLLBACK AND KILL-SWITCH DRILL

**Pack**: `PROJECT_N` — Track F
**Verdict**: `TRACK_F_CANARY_ROLLBACK_AND_KILL_SWITCH_DRILL_READY`

## Rollback script

`/app/backend/scripts/rollback_project_n_status_first_slice_canary_flag.py`

| Mode | Default | Effetto |
|------|---------|---------|
| dry-run | ✅ | Inspect-only, stampa md5 e stato |
| `--apply` | esplicito | Restore `.env` da backup + restart backend |

## Drill 6-step (eseguito a runtime)

| # | Azione | Esito |
|---|--------|-------|
| 1 | Capture pre-flip `.env` md5 | `ff60bbb79efa329b71aa8ed351ea89b3` |
| 2 | Flip flag ON (Track B) | flag appeso, restart, flag attivo |
| 3 | Verify smoke + battle con flag ON | smoke 200/404/200/200/503/503/503; battle byte-identical |
| 4 | Restore `.env` da backup | md5 ripristinato |
| 5 | Restart backend | rc=0, RUNNING |
| 6 | Verify post-rollback smoke | identico al pre-flip; flag assente |

**Kill-switch verificato**: l'operazione è reversibile in `~3 secondi` di restart backend.
