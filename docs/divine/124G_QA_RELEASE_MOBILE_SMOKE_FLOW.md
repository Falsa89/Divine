# 124G — PROJECT_B Track G — QA_RELEASE_MOBILE_SMOKE_FLOW

**Pack**: `MEGA_COMBO_PROJECT_ACCELERATION_B`  
**Track**: G  
**Mode**: `qa_doc_suite_only_no_runtime_mutation`  
**Verdict**: 🟢 `TRACK_G_QA_RELEASE_MOBILE_SMOKE_FLOW_READY`

---

## 1. Scopo

Definire e parzialmente automatizzare il **flow di QA mobile smoke** per la technical completion del progetto, **escluso** graphics/audio/art assets.

## 2. Flow matrix (13 step, 12 non-mutating)

| # | Nome | Endpoint | Atteso | Mutating? |
|---|---|---|---|---|
| 1 | LOGIN | `POST /api/login` | 200 | No |
| 2 | HEROES_CATALOG | `GET /api/heroes` | 200 + count=100 | No |
| 3 | BOREA_INERT | `GET /api/heroes/borea` | 200 | No |
| 4 | PRIMORDIAL_GAIA_INERT | `GET /api/heroes/primordial_gaia` | 404 | No |
| 5 | GACHA_SUMMON_PEEK | `GET /api/summon/rates` | 200 | No (no real spend) |
| 6 | BATTLE_ENTRY_DRY | `GET /api/battle/preview` | 200 | No (no actual battle) |
| 7 | POST_BATTLE_SUMMARY | `GET /api/user/me` | 200 | No |
| 8 | MENU_NAV_HOME | `GET /api/heroes` | 200 | No |
| 9 | SLC_GUARD_LEGACY_SERVER_SELECT | `POST /api/server/select` | 200/400 + deprecation log | **YES** (l'unico mutating) |
| 10 | SLC_GUARD_NEW_DUAL_ROUTE | `GET /api/server-profiles/select` | **503 + status=disabled** | No |
| 11 | AF2N_CANARY_STATUS_GUARD | `GET /api/affinity/gift-spend/canary-status` | 200/auth-bound | No |
| 12 | HOUSING_PLACEHOLDER | `GET /api/housing/rooms` | 404 (not implemented) | No |
| 13 | ARTIFACT_PLACEHOLDER | `GET /api/artifacts` | 200/404 | No |

## 3. Pre-release pass criteria

1. Tutti i 12 step non-mutating restituiscono il status atteso
2. Step 9 logga `divine.deprecation` WARNING almeno una volta
3. Nessun 500 error nell'intera matrix
4. Backend supervisor `RUNNING` durante l'intero flow
5. MongoDB supervisor `RUNNING` durante l'intero flow

## 4. Excludes (out of scope per technical completion)

- `graphics_finalization`
- `audio_finalization`
- `art_assets`

## 5. Validator

- **Path**: `/app/backend/scripts/validate_project_b_qa_release_mobile_smoke_flow_v1.py`
- **Suite task_id**: `PROJECT-B-TRACK-G-QA-RELEASE-MOBILE-SMOKE-FLOW` (OPTIONAL)
- **Type**: static (verifica struttura matrix, step IDs, mutating count <=1)
- **NON** esegue HTTP nella suite (separation of concerns)

## 6. Forbidden scope verification

| Forbidden | Violato? |
|---|---|
| Frontend implementation | ❌ No |
| Runtime behavior changes | ❌ No |
| Real gacha spend | ❌ No |
| Battle behavior mutation | ❌ No |
