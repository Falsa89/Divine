# 136B — STATUS FIRST SLICE CANARY FLAG FLIP

**Pack**: `PROJECT_N` — Track B
**Verdict**: `TRACK_B_STATUS_FIRST_SLICE_CANARY_FLAG_ENABLED_SAFE`
**Marker JSON**: `/app/data/design/status_effects/project_n_status_first_slice_canary_flag_flip_result_v1.json`
**Validator**: `/app/backend/scripts/validate_project_n_status_first_slice_canary_flag_v1.py`

## Operazione eseguita

1. Backup: `/app/backend/.env` → `/app/backend/.env.project_n_pre_flip.bak` (md5 `ff60bbb79efa329b71aa8ed351ea89b3`).
2. Append `STATUS_RUNTIME_BUFF_SLICE_ENABLED=true` a `/app/backend/.env`.
3. `sudo supervisorctl restart backend` → backend RUNNING entro ~3s.
4. Smoke post-flip: `200/404/200/200/503/503/503` (identico al pre-flip).
5. Deterministic 3v3 battle: SHA256 = `d951767a72b54b339eb660f6308d72c943a9a9e318539f639ce9fc7f416d3725` (**byte-identical** al baseline).
6. Rollback (Track F): `.env` ripristinato dal backup; md5 corrente == md5 backup; backend riavviato; flag rimosso.

## Perché il flag ON è byte-identical

Il seam Project_M ha un **doppio gate**: anche con `STATUS_RUNTIME_BUFF_SLICE_ENABLED=true`, il call site live in `simulate_battle` chiama il seam con `dry_run=False`; il seam ritorna `team_payload` invariato (`identity`) in quel ramo. Solo i test in-process che passano `dry_run=True` osservano il preview envelope. È quindi sicuro lasciare il flag attivo: nessun comportamento live cambia con Pack N.

## Stato finale

`FLAG_OFF` (rollback applicato dopo collezione metriche). `.env` md5 = `ff60bbb79efa329b71aa8ed351ea89b3` (identico al pre-flip baseline).

## Conformità ai guardrail

- ✅ No prod rollout.
- ✅ No dev-live broad rollout.
- ✅ No DB write.
- ✅ No battle code patch oltre seam Project_M.
- ✅ Rollback eseguito.
