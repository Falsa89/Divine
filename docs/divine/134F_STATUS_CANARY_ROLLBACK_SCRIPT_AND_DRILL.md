# 134F — STATUS CANARY ROLLBACK SCRIPT AND DRILL

**Pack**: `PROJECT_L_STATUS_FIRST_SLICE_FLAGGED_CANARY_ENV` — Track F
**Verdict**: `TRACK_F_STATUS_CANARY_ROLLBACK_SCRIPT_AND_DRILL_READY`
**Marker JSON**: `/app/data/design/status_effects/project_l_status_canary_rollback_script_and_drill_v1.json`
**Validator**: `/app/backend/scripts/validate_project_l_status_canary_rollback_script_and_drill_v1.py`

---

## Obiettivo

Fornire — dato che Track B ha creato codice — lo script di rollback e dimostrare che il drill in modalità dry-run sia eseguibile in sicurezza senza modificare alcun file.

## File rollback

`/app/backend/scripts/rollback_project_l_minimal_battle_runtime_seam.py`

## Modalità supportate

| Mode | Default | Effetto |
|------|---------|---------|
| dry-run (default, no flag) | ✅ | Stampa il path target, calcola le dimensioni, scansiona i file runtime forbidden per detector di importer; nessuna modifica |
| `--apply` | non default | Cancella fisicamente il seam *solo* se nessun forbidden runtime importer rileva il pattern `status_prefight_runtime_seam` |

## Drill eseguito

- Pre-condizione: seam presente, dimensione registrata.
- Esecuzione: `python3 rollback_project_l_minimal_battle_runtime_seam.py` (senza `--apply`).
- Esito: `rc=0`, marker `[DRY-RUN]` presente in stdout, seam **non modificato**, dimensione invariata.

## Safety guards

1. `--apply` rifiuta operazione se un live runtime importer è presente.
2. dry-run è il default; nessuna delete senza flag esplicito.
3. Nessun altro file può essere toccato dallo script.

## Conformità ai guardrail

- ✅ Nessun rollback distruttivo eseguito.
- ✅ Nessun broad rewrite.
