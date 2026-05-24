# 136A — CANARY ENV PRECHECK AND SCOPE ASSERTION

**Pack**: `PROJECT_N` — Track A
**Verdict**: `TRACK_A_CANARY_ENV_PRECHECK_READY`
**Classifica**: `NON_PROD_LOCAL_ONLY`
**Marker JSON**: `/app/data/design/status_effects/project_n_canary_env_precheck_v1.json`
**Validator**: `/app/backend/scripts/validate_project_n_canary_env_precheck_v1.py`

## Evidenze raccolte

| Indicatore | Osservato | Esito |
|------------|-----------|-------|
| hostname | `agent-env-d6ffb22d-30ee-4092-ae62-3b8b80ed798c` | ✅ ephemeral container |
| MongoDB URL | `mongodb://localhost:27017` | ✅ local-only |
| JWT secret | dev default | ✅ |
| DB name | `divine_waifus` (dev catalog) | ✅ |
| EXPO_PACKAGER_PROXY_URL | `https://game-portal-327.preview.emergentagent.com` | ✅ preview env |
| Env `PROD/PRODUCTION/LIVE` | nessuna | ✅ |
| Supervisor | locale | ✅ |
| `/api/server-profiles/select` | 503 (disabled) | ✅ |
| `/api/housing/preview` | 503 (disabled) | ✅ |
| Backend health | RUNNING | ✅ |

**9 non-prod signals / 0 prod signals** → classifica `NON_PROD_LOCAL_ONLY` → flag flip autorizzato.
