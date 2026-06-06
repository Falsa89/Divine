# v108_AUTHORITATIVE_RUNTIME — Backend resolve-preview endpoint (Track C)

`POST /api/battle/instance/resolve-preview` — implementato in `backend/routes/v108_authoritative_runtime_resolve.py`.

Resolver deterministico in-memory (sha256 seed). NO DB, NO reward, NO progress, NO `/api/battle/simulate`, NO battle_engine import. authoritative_live=false sempre, authoritative_staging=true.

Smoke runtime: 4/4 case OK (happy=200, 3 blocchi=423).
