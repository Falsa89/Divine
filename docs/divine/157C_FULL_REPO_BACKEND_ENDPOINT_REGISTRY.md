# 157C — Full Backend Endpoint & Mutation Registry (Track C)

Verdetto: `TRACK_C_FULL_BACKEND_ENDPOINT_AND_MUTATION_REGISTRY_READY`
File: `data/design/audit/full_repo/backend_endpoint_mutation_registry_v1.json`

## Coverage
- 219 endpoint backend FastAPI
- 100 mutating (POST/PUT/PATCH/DELETE)
- 7 inert/503 (server-profiles select, housing preview, etc.)

## Mutating per feature (highlights)
constellation:6, hero:5, gacha:4, forge:4, shop:4, guild:4, affinity:3, artifact:3, battlepass:3.

## Note
- Per ogni endpoint: file source, prefix router, body-scan per DB writes (insert/update/delete), auth Depends, classificazione 503/inert.
