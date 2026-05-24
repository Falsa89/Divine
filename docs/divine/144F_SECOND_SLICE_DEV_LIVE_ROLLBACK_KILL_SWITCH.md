# 144F — STATUS SECOND SLICE — DEV-LIVE ROLLBACK / KILL-SWITCH

## Track F — `PROJECT_V_TRACK_F`

**Verdict:** `TRACK_F_SECOND_SLICE_DEV_LIVE_ROLLBACK_KILL_SWITCH_READY`

## 1. Obiettivo

Drill end-to-end di un rollback / kill-switch live dal flag ON al flag OFF, con verifica di identità funzionale, byte-identicality del `.env` e smoke API post-rollback.

## 2. Metodo

```
sed remove line `STATUS_RUNTIME_SECOND_SLICE_ENABLED` da /app/backend/.env
+ supervisorctl restart backend
+ identity check + smoke test
```

## 3. Esito

| Voce | Valore |
|---|---|
| Rollback eseguito | ✅ |
| Tempo di rollback (stimato) | ~8 s |
| Target tempo | 60 s |
| Dentro target | ✅ |
| `.env` MD5 pre-flip | `ff60bbb79efa329b71aa8ed351ea89b3` |
| `.env` MD5 post-rollback | `ff60bbb79efa329b71aa8ed351ea89b3` |
| Byte-identical | ✅ |

## 4. Smoke API post-rollback

| Endpoint | Status |
|---|---|
| `/api/heroes` | 200 |
| `/api/heroes/primordial_gaia` | 404 |
| `/api/heroes/borea` | 200 (inert) |
| `/api/heroes/greek_borea` | 200 (inert) |
| `/api/server-profiles/select` | 503 |
| `/api/housing/preview` | 503 |

## 5. Invarianti

- `battle_engine.py` integro: md5 `151ca35ad3bc35f0a6209cb3744ed440`.
- Identità funzionale verificata.
- Flag finale: **OFF / assente** nel `.env`.

## 6. Validator

`validate_project_v_second_slice_dev_live_rollback_kill_switch_v1.py` → **PASS**.
