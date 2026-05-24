# 135F — BATTLE ENGINE STATUS SEAM ROLLBACK DRILL

**Pack**: `PROJECT_M` — Track F
**Verdict**: `TRACK_F_BATTLE_ENGINE_STATUS_SEAM_ROLLBACK_DRILL_READY`
**Marker JSON**: `/app/data/design/status_effects/project_m_battle_engine_status_seam_rollback_drill_v1.json`
**Validator**: `/app/backend/scripts/validate_project_m_battle_engine_status_seam_rollback_drill_v1.py`

## Rollback script

`/app/backend/scripts/rollback_project_m_battle_engine_status_seam.py`

| Mode | Default | Effetto |
|------|---------|---------|
| dry-run (default) | ✅ | Riconosce i 3 patch marker `PROJECT_M Track B`; stampa md5 corrente e md5 backup; nessuna modifica |
| `--apply` | esplicito | Ripristina `battle_engine.py` dal backup `battle_engine.py.project_m_pre_patch.bak` |

## Drill su temp copy

1. Pre-condizione: `battle_engine.py` modificato + backup intatto, md5 registrati.
2. Esecuzione: rollback in dry-run mode → marker `[DRY-RUN]`, rc=0, BE invariato.
3. Simulazione restore su temp copy: copia di `battle_engine.py` in directory temporanea, copia di backup sopra, verifica `md5(temp) == md5(backup)` → **byte-identical**.
4. Verifica post-drill: live `battle_engine.py` md5 invariato.

## Conformità ai guardrail

- ✅ Nessun rollback distruttivo eseguito sul live.
- ✅ Nessun broad rewrite.
- ✅ Live battle_engine.py preservato durante l'intero drill.
