# 143F — PROJECT_U Track F: Rollback / Kill-Switch Drill

## Verdict
`TRACK_F_SECOND_SLICE_ROLLBACK_KILL_SWITCH_DRILL_READY`

## Rollback eseguito (drill live)
1. `sed -i '/^STATUS_RUNTIME_SECOND_SLICE_ENABLED=/d' /app/backend/.env`
2. `sudo supervisorctl restart backend`
3. Verifica `.env` MD5 byte-identico al backup pre-flip
4. Verifica API smoke baseline
5. Verifica seam identity post-rollback (6 sample payloads)

## Risultati
| Check | Atteso | Osservato |
|---|---|---|
| Rollback time | ≤ 60s | **≈8s** ✅ |
| `.env` MD5 post-rollback | == backup `ff60bbb79e...` | `ff60bbb79e...` ✅ |
| `STATUS_RUNTIME_SECOND_SLICE_ENABLED` presente in `.env` | NO | NO ✅ |
| `battle_engine.py` md5 post-rollback | == `151ca35a...` (Pack T) | `151ca35a...` ✅ |
| Seam identity post-rollback | 6/6 | 6/6 ✅ |
| API smoke post-rollback | tutti come baseline | tutti OK ✅ |

## Validator
`/app/backend/scripts/validate_project_u_second_slice_rollback_kill_switch_v1.py` → **[PASS]**
