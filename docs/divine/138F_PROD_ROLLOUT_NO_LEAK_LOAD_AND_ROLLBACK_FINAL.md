# 138F — PROD ROLLOUT NO-LEAK + LOAD + ROLLBACK FINAL

**Pack**: `PROJECT_P` — Track F
**Verdict**: `TRACK_F_PROD_ROLLOUT_NO_LEAK_LOAD_AND_ROLLBACK_FINAL_READY_NOT_APPLIED_PENDING_APPROVAL`

Non applicato (nessuno stage entrato). Piano documentato:

- 5 endpoint × 2 marker forbidden audit
- Backend logs scan (`/var/log/supervisor/backend*.log`)
- Light load max 300 req/stage, non destructive, no spend, no gacha, no DB
- Rollback script da creare: `rollback_project_p_prod_status_first_slice_flag.py` (dry-run default + `--apply` esplicito + backup verification + smoke post-rollback)
- Stato finale post-rollout: `FLAG_OFF` (obbligatorio in assenza di marker `STATUS_RUNTIME_BUFF_SLICE_KEEP_ON_AFTER_PROD_ROLLOUT=true`)
