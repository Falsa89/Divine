# 133F — STATUS RUNTIME CANARY ROLLBACK DRILL

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_K` — Track F
**Verdict**: `TRACK_F_STATUS_RUNTIME_CANARY_ROLLBACK_DRILL_EXECUTED_IN_PROCESS`
**Marker JSON**: `/app/data/design/status_effects/project_k_status_runtime_canary_rollback_drill_v1.json`
**Validator**: `/app/backend/scripts/validate_project_k_status_runtime_canary_rollback_drill_v1.py`

---

## Obiettivo

Eseguire un *drill di rollback* in-process per verificare che la commutazione del flag `STATUS_RUNTIME_BUFF_SLICE_ENABLED` produca lo stato atteso del resolver, senza alcun side-effect su processi esterni.

## Sequenza eseguita

| Step | Azione | `is_runtime_active()` atteso | Osservato |
|------|--------|------------------------------|-----------|
| D2 | `os.environ[FLAG] = 'true'` | `True` | ✅ |
| D3 | `os.environ[FLAG] = 'false'` | `False` | ✅ |
| D4 | `os.environ.pop(FLAG)` | `False` | ✅ |

Al termine del drill l'env è ripristinata al valore precedente (clean-up garantito da `try/finally`).

## Significato

Il drill prova che:

- la `kill-switch` (`flag=false`) e l'unset disattivano deterministicamente il resolver;
- la riattivazione (`flag=true`) è altrettanto deterministica;
- il drill è eseguibile in-process, senza richiedere modifiche env persistenti, restart o operazioni distruttive.

Poiché Track B non ha applicato wiring, non esiste rollback `destructive` da eseguire: il drill è puramente in-process sul resolver.

## Conformità ai guardrail

- ✅ Nessun rollback distruttivo eseguito.
- ✅ Nessun file riscritto in modo broad.
- ✅ Nessun env flag persistito.
- ✅ Nessuna mutazione live.
