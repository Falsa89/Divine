# 139F — PROJECT_Q Track F: Artifact Import Approval Gate & Rollback Plan

## Verdict
`TRACK_F_ARTIFACT_IMPORT_APPROVAL_GATE_AND_ROLLBACK_READY_PENDING_APPROVAL`

## Marker JSON
`/app/data/design/artifacts/project_q_artifact_import_approval_gate_rollback_v1.json`

## Validator
`/app/backend/scripts/validate_project_q_artifact_import_approval_gate_rollback_v1.py` → **[PASS]**

## Firme richieste per live import (5)
| Firma | Stato attuale |
|---|---|
| `ARTIFACT_USER_APPROVAL` | ❌ assente |
| `ARTIFACT_ECONOMY_APPROVAL` | ❌ assente |
| `ARTIFACT_BALANCE_APPROVAL` | ❌ assente |
| `ARTIFACT_QA_APPROVAL` | ❌ assente |
| `ARTIFACT_IMPORT_LIVE_OK` | ❌ assente |

- **signatures_present_count = 0**
- **signatures_missing_count = 5**
- **live_import_authorized = false**
- **live_import_executed = false**
- **db_writes = false**

Il validator esegue scan indipendente su `/app/backend/.env` e `os.environ`: 0/5 firme rilevate, coerente col marker.

## Strategia di rollback (design)
Se un futuro Pack eseguirà live import con `--apply` (firme presenti), lo stesso script `import_project_q_artifact_bible_dry_run_v1.py` fornirà `--rollback` per rimuovere i documenti con `artifact_id` appartenente al batch (8). Nessuno stato parziale tollerato.

### Safety guards
- `--apply` richiede tutte e 5 le firme.
- `--rollback` non richiede firme aggiuntive (sempre sicuro).
- Il default rimane sempre `dry-run`.
- Nessuna operazione distruttiva su altre collection.

## Side effects
Nessuno: stato firme letto in modo read-only, nessuna modifica `.env`.
