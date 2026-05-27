# 171 — PROJECT ARTIFACT LEGACY MUTATION ENDPOINT HARDENING

## Verdetto locale
`PROJECT_ARTIFACT_LEGACY_MUTATION_ENDPOINT_HARDENING_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

Diventerà `PROJECT_ARTIFACT_LEGACY_MUTATION_ENDPOINT_HARDENING_COMPLETE_PUBLIC_REPO_VERIFIED` solo dopo che l'utente avrà eseguito **Save to GitHub → branch `main` → PUSH** e che la repo pubblica conterrà i file di questo pack.

---

## Obiettivo
Isolare formalmente tutti i POST mutativi legacy di `artifact/constellation` in `backend/routes/artifacts.py` prima di procedere allo schema inventario (Stage 5). Gli endpoint POST rispondono ora con un envelope `423 Locked` coerente, **senza alcuna chiamata DB**, senza auth, senza random roll, senza spend gemme, senza grant.

## Endpoint hard-lockati (7)

| Endpoint | HTTP | Envelope code |
|---|:---:|---|
| `POST /api/artifacts/pull` | 423 | `ARTIFACT_MUTATION_ENDPOINT_LOCKED` |
| `POST /api/artifacts/pull10` | 423 | `ARTIFACT_MUTATION_ENDPOINT_LOCKED` |
| `POST /api/artifacts/fuse` | 423 | `ARTIFACT_MUTATION_ENDPOINT_LOCKED` |
| `POST /api/constellations/equip` | 423 | `CONSTELLATION_MUTATION_ENDPOINT_LOCKED` |
| `POST /api/constellations/fuse` | 423 | `CONSTELLATION_MUTATION_ENDPOINT_LOCKED` |
| `POST /api/constellations/pull` | 423 | `CONSTELLATION_MUTATION_ENDPOINT_LOCKED` |
| `POST /api/constellations/pull10` | 423 | `CONSTELLATION_MUTATION_ENDPOINT_LOCKED` |

> Nota: `POST /api/artifacts/equip` **non esiste** nel modulo (mai stato definito) e **non è stato creato** in questo pack.

## Envelope risposta

```json
// Artefatti
{
  "success": false,
  "locked": true,
  "system": "artifacts",
  "code": "ARTIFACT_MUTATION_ENDPOINT_LOCKED",
  "message": "Sistema Artefatti in preparazione. Azioni mutative non disponibili.",
  "allowed_now": [
    "GET /api/artifacts/catalog",
    "GET /api/artifacts/catalog/preview"
  ]
}

// Costellazioni
{
  "success": false,
  "locked": true,
  "system": "constellations",
  "code": "CONSTELLATION_MUTATION_ENDPOINT_LOCKED",
  "message": "Sistema Costellazioni in preparazione. Azioni mutative non disponibili.",
  "allowed_now": []
}
```

## Invarianti dei locked handler
- ❌ Nessuna dipendenza `Depends(get_current_user)`
- ❌ Nessun request body (rimossi `ArtifactFuseRequest` / `EquipConstellationRequest` dalle signature)
- ❌ Nessuna chiamata a `db.*` (insert/update/find/delete)
- ❌ Nessun `random.*` chiamato (modulo `random` ancora importato per le tabelle legacy in memoria ma mai eseguito)
- ❌ Nessuno spend gemme / grant / equip / fuse / craft
- ✅ Ritorno `JSONResponse(status_code=423, content=envelope)`

## Endpoint preservati read-only

| Endpoint | HTTP | Count |
|---|:---:|:---:|
| `GET /api/artifacts/catalog` | 200 | 32 |
| `GET /api/artifacts/catalog/preview` | 200 | 10 |
| `GET /api/artifacts/catalog?category=invalid` | 400 | — (no DB write) |

## Frontend / Gacha guards (immutati)
- `frontend/app/(tabs)/gacha.tsx` → `HIDDEN_BANNERS_V2 = {'artifact', 'constellation'}` continua a nascondere i banner e a impedire `setBanner('artifact'/'constellation')` (line 78). `doPull()` esce subito se `isActiveBannerLocked`.
- `frontend/app/artifacts.tsx` → redirect a `/artifacts-preview` immutato.
- `frontend/app/artifacts-preview.tsx` → MD5 stabile `0e75c94e00899af773dbc9faf7326a15` (nessuna modifica in questo pack).
- Nessun nuovo bottone di mutation aggiunto.

## Invarianti MD5
| File | MD5 atteso | MD5 attuale | OK |
|---|---|---|:---:|
| `backend/battle_engine.py` | `151ca35ad3bc35f0a6209cb3744ed440` | `151ca35ad3bc35f0a6209cb3744ed440` | ✅ |
| `backend/.env` | `ff60bbb79efa329b71aa8ed351ea89b3` | `ff60bbb79efa329b71aa8ed351ea89b3` | ✅ |
| `frontend/app/artifacts-preview.tsx` | `0e75c94e00899af773dbc9faf7326a15` | `0e75c94e00899af773dbc9faf7326a15` | ✅ |
| `frontend/app/artifacts.tsx` | `8849e21c44207fc1d0074cae2cdc6879` | `8849e21c44207fc1d0074cae2cdc6879` | ✅ |
| `frontend/app/(tabs)/gacha.tsx` | `f68b9239cec04ea54879f0be381e772a` | `f68b9239cec04ea54879f0be381e772a` | ✅ |

## File aggiunti / modificati
| Op | Path |
|:---:|---|
| M | `backend/routes/artifacts.py` |
| M | `backend/scripts/run_hero_skill_kit_validator_suite.py` |
| A | `backend/scripts/validate_project_artifact_legacy_mutation_endpoint_hardening_v1.py` |
| A | `data/design/artifacts/hardening/artifact_legacy_mutation_endpoint_audit_v1.json` |
| A | `data/design/artifacts/hardening/artifact_mutation_lock_response_contract_v1.json` |
| A | `data/design/artifacts/hardening/artifact_frontend_gacha_guard_recheck_v1.json` |
| A | `data/design/artifacts/hardening/artifact_backend_smoke_locked_mutation_tests_v1.json` |
| A | `data/design/artifacts/hardening/artifact_legacy_mutation_endpoint_hardening_completion_v1.json` |
| A | `docs/divine/171_ARTIFACT_LEGACY_MUTATION_ENDPOINT_HARDENING.md` |

## Mobile QA
Non richiesta: zero modifiche frontend. `/artifacts-preview` continua a funzionare e i banner artifact/constellation restano nascosti.

## Prossimo pack consigliato
`PROJECT_ARTIFACT_INVENTORY_SCHEMA_DRY_RUN_PACK` (Stage 5).
