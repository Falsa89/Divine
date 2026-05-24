# 134B — MINIMAL BATTLE RUNTIME SEAM INERT

**Pack**: `PROJECT_L_STATUS_FIRST_SLICE_FLAGGED_CANARY_ENV` — Track B
**Verdict**: `TRACK_B_MINIMAL_BATTLE_RUNTIME_SEAM_CREATED_INERT`
**Marker JSON**: `/app/data/design/status_effects/project_l_minimal_battle_runtime_seam_result_v1.json`
**Validator**: `/app/backend/scripts/validate_project_l_minimal_battle_runtime_seam_v1.py`

---

## Obiettivo

Creare il seam minimo isolato autorizzato da Track A, default no-op, mai importato dal runtime live.

## File creati

| File | Ruolo |
|------|-------|
| `/app/backend/game_logic/status_prefight_runtime_seam.py` | Seam inerte: espone `is_seam_active()` e `apply_prefight_status_slice_preview(team_payload, active_statuses=None, *, dry_run=False)` |
| `/app/backend/scripts/rollback_project_l_minimal_battle_runtime_seam.py` | Script di rollback con dry-run di default e modalità `--apply` esplicita |

## Contratto del seam

| Stato | Comportamento |
|-------|----------------|
| flag `STATUS_RUNTIME_BUFF_SLICE_ENABLED` OFF (unset / `false` / qualsiasi non-`true`) | **Identity**: ritorna `team_payload` immutato |
| flag ON, `dry_run=False` | **Identity** (live activation NON autorizzata da Pack L) |
| flag ON, `dry_run=True` | Ritorna una *shallow copy* con `status_envelope_preview` aggiunto; payload originale non mutato |

## Invarianti verificati

- ✅ Seam non importato da `battle_engine.py`, `battle_core.py`, `server.py`, né da `/app/backend/routes/*.py`.
- ✅ Default no-op rispettato.
- ✅ Nessun tick loop / DoT / formula change.
- ✅ Nessun DB write.
- ✅ Rollback dry-run testato (Track F).

## Forbidden scope rispettato

- ✅ unflagged status application: NO
- ✅ DoT/tick loop: NO
- ✅ broad battle refactor: NO
- ✅ combat.tsx / frontend: NO
- ✅ DB write: NO
