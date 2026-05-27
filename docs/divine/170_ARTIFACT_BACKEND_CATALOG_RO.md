# 170 — PROJECT ARTIFACT BACKEND CATALOG RO

## Verdetto locale
`PROJECT_ARTIFACT_BACKEND_CATALOG_RO_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

(Diventerà `PROJECT_ARTIFACT_BACKEND_CATALOG_RO_COMPLETE_PUBLIC_REPO_VERIFIED` solo
dopo che l'utente avrà eseguito **Save to GitHub → branch `main` → PUSH** e
che ChatGPT avrà verificato la presenza dei file su GitHub `main`.)

---

## Obiettivo
Stage 4 della Artifact Migration: esporre via FastAPI un **catalogo
artefatti READ-ONLY** che legge esclusivamente dai JSON canonici versionati,
senza alcuna scrittura/lettura DB, senza ownership, inventory, equip, fuse,
craft, pull, prezzi o modificatori di combattimento.

## Endpoint aggiunti

### `GET /api/artifacts/catalog`
- Sorgente: `data/design/artifacts/artifact_bible_launch_draft_v1.json`
- Risposta: 32 entry filtrabili tramite query params whitelistati
- Campi whitelist per item:
  `artifact_id, display_name_it, display_name_en, category, faction_or_origin,
  associated_hero_id, associated_character_status, rarity_band,
  release_status, gameplay_status, short_lore_it, visual_identity,
  source_hint_future, ui_copy_short_it`
- Filtri ammessi:
  - `category` (whitelist 8 valori)
  - `release_status` (whitelist `launch_candidate | preview_only`)
  - `gameplay_status` (whitelist `cosmetic_prestige_only | inactive`)
  - `include_future_reserved` (default `false`; la Bible attuale non contiene voci future_reserved)
- Risposte di errore: 400 su valore filtro non valido, 503 (envelope sicuro) se JSON mancante/malformato. **Nessuna scrittura DB.**

### `GET /api/artifacts/catalog/preview`
- Sorgente: `data/design/artifacts/preview/artifact_preview_dataset_v1.json`
- Risposta: 10 entry preview-safe già firmate
- Campi whitelist per item:
  `artifact_id, display_name_it, category, rarity_band, release_status,
  gameplay_status, ui_copy_short_it, visual_hint`

## Smoke locali
| Endpoint | HTTP | Count | Forbidden fields | DB calls |
|----------|:----:|:-----:|:----------------:|:--------:|
| `/api/artifacts/catalog` | 200 | 32 | 0 | 0 |
| `/api/artifacts/catalog/preview` | 200 | 10 | 0 | 0 |
| `/api/artifacts/catalog?category=divine_relic` | 200 | 11 | 0 | 0 |
| `/api/artifacts/catalog?release_status=preview_only` | 200 | 6 | 0 | 0 |
| `/api/artifacts/catalog?category=invalid` | 400 | — | — | 0 |

## Invarianti rispettati
- `backend/battle_engine.py` MD5 **invariato** (`151ca35ad3bc35f0a6209cb3744ed440`)
- `backend/.env` MD5 **invariato** (`ff60bbb79efa329b71aa8ed351ea89b3`)
- `frontend/app/artifacts-preview.tsx` **NON modificato** (resta statico)
- `frontend/app/(tabs)/gacha.tsx` `HIDDEN_BANNERS_V2` continua a nascondere `artifact` e `constellation`
- `frontend/app/artifacts.tsx` continua a fare redirect a `/artifacts-preview`
- Nessun nuovo endpoint mutativo, nessun `equip/fuse/craft/pull` aggiunto
- Endpoint mutativi pre-esistenti su artefatti/costellazioni invariati (restano gated dai banner nascosti)

## File aggiunti / modificati
| Path | Tipo |
|------|------|
| `backend/routes/artifacts.py` | MOD — aggiunte SOLO 2 GET read-only catalogo |
| `backend/scripts/validate_project_artifact_backend_catalog_ro_v1.py` | NEW |
| `backend/scripts/run_hero_skill_kit_validator_suite.py` | MOD — registrato validator OPTIONAL |
| `data/design/artifacts/catalog_ro/artifact_catalog_source_manifest_contract_audit_v1.json` | NEW |
| `data/design/artifacts/catalog_ro/artifact_catalog_normalization_filters_v1.json` | NEW |
| `data/design/artifacts/catalog_ro/artifact_frontend_integration_policy_no_wiring_v1.json` | NEW |
| `data/design/artifacts/catalog_ro/artifact_catalog_backend_smoke_no_db_guard_v1.json` | NEW |
| `data/design/artifacts/catalog_ro/artifact_backend_catalog_ro_completion_v1.json` | NEW |
| `docs/divine/170_ARTIFACT_BACKEND_CATALOG_RO.md` | NEW (questo documento) |

## Frontend wiring policy
- In questo pack il frontend NON viene cablato sui nuovi endpoint.
- `/artifacts-preview` continua a renderizzare il dataset statico già firmato.
- Un eventuale pack futuro potrà migrare la preview verso `GET /api/artifacts/catalog/preview` con loading/error state e fallback statico.

## Prossimo pack consigliato
`PROJECT_ARTIFACT_INVENTORY_SCHEMA_DRY_RUN_PACK` (Stage 5: schema solo design, ancora niente scritture DB live).
