# 172 — PROJECT ARTIFACT INVENTORY SCHEMA DRY RUN

## Verdetto locale
`PROJECT_ARTIFACT_INVENTORY_SCHEMA_DRY_RUN_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`

Diventerà `_COMPLETE_PUBLIC_REPO_VERIFIED` solo dopo Save to GitHub → branch `main` → PUSH e verifica della repo pubblica.

---

## Obiettivo (Stage 5 Artifact Migration)
Disegnare l'**intera architettura** dell'inventario futuro degli artefatti (5 collection, schema, indici, idempotency, ledger, rollback, contratti API, piano migrazione) **senza alcuna scrittura DB**, mantenendo il sistema esattamente nello stato safe del Stage 4.5.

## 🔒 Cosa NON è stato fatto in questo pack
- ❌ Nessuna `db.createCollection` reale
- ❌ Nessuna insert/update/delete in MongoDB
- ❌ Nessun endpoint live aggiunto (gli endpoint inventory restano **design-only**)
- ❌ Nessuna modifica a `backend/routes/artifacts.py` (i 7 POST restano lockati 423)
- ❌ Nessuna modifica a frontend (`artifacts-preview` resta statico)
- ❌ Nessuna modifica a `battle_engine.py` / `backend/.env` / `gacha.tsx`

## 📐 Schema progettato (5 collection design-only)

| Collection | Scopo | Live |
|---|---|:---:|
| `artifact_catalog_snapshot` | Snapshot immutabile della Bible (32 entry), con `snapshot_md5` per integrità | ❌ |
| `user_artifact_inventory` | Inventario per `(user_id, server_profile_id, artifact_id)`; quantity, status, locked, source_type, metadata_version | ❌ |
| `artifact_inventory_ledger` | Append-only event log con `idempotency_key` univoca, delta_quantity, event_type, actor_system | ❌ |
| `artifact_collection_state` | Aggregato per-user; `bonus_status` resta `inactive` finché Bible `gameplay_status=inactive` | ❌ |
| `artifact_idempotency_registry` | Fast-path lookup pre-write per chiavi idempotency | ❌ |

### Vincoli del design
- ✅ Compound unique key: `(user_id, server_profile_id, artifact_id)`
- ✅ Ledger **append-only**, `idempotency_key` unica, **mai hard-delete** post-live
- ✅ Pattern idempotency: `<source_type>:<source_id>:<user_id>:<artifact_id>`
- ✅ Constellations, Equipment, Runes, Divine Weapons **separati**
- ✅ Linka a `associated_hero_id` solo come riferimento; **zero** delta su stats eroe
- ❌ Forbidden field globali: `equip_slot_active`, `stat_bonus_active`, `combat_modifier`, `price`, `purchase_url`, `gacha_pity_counter`, `direct_hero_stat_delta`, `pvp_power_flag`

## 🧪 Sample documents (Track C)
8 documenti validati in-memory contro lo schema:
- 1 snapshot catalogo (`relic_aurora_eterna`)
- 2 inventory (`u_alpha_001`, `u_beta_002` con `locked=true`)
- 3 eventi ledger (grant + duplicate-key idempotent no-op verificato)
- 1 scenario duplicate-grant (stesso key → no-op, quantity 0)
- 1 scenario revoke su item `locked=true` → **bloccato** (`LOCKED_ITEM_REVOKE_BLOCKED` → 423)
- 1 collection_state con `bonus_status = inactive`

| Metrica | Valore |
|---|:---:|
| docs validated | 8 |
| docs passed | 8 |
| forbidden fields found | 0 |
| DB writes performed | **0** |
| DB collections created | **0** |

## 🛰️ Future API (Track D — design only)
4 endpoint disegnati, **nessuno implementato**:
- `GET /api/artifacts/inventory`
- `GET /api/artifacts/inventory/summary`
- `POST /api/artifacts/inventory/grant` (system/admin only, idempotency required)
- `POST /api/artifacts/inventory/revoke` (idempotency + reason required)

Tutti restano protetti da gate `ARTIFACT_INVENTORY_RUNTIME_ENABLED=true_explicit` (non attivo). Finché il gate è chiuso, la risposta canonica è `423 ARTIFACT_INVENTORY_NOT_LIVE`.

## 🗄️ Piano migrazione/rollback (Track E)
6 stage progettati (preflight → backup → create collections → populate snapshot → seed beta → go-live gate). **Tutto dry-run**:

- `applied_now: false`
- `db_writes_performed: 0`
- Strategia globale rollback: **never hard-delete** dopo go-live; compensating ledger entries
- 5 failure mode documentati (duplicate_grant, partial_seed, catalog_drift, profile collision, revoke-on-locked)

## 🕵️ Audit GET legacy (Track A)
| Endpoint | DB read | Player reachable | Decisione |
|---|:---:|:---:|---|
| `GET /api/artifacts` | sì (`user_artifacts`) | no (HIDDEN_BANNERS_V2) | NON usare come base; deprecate in pack futuro |
| `GET /api/constellations` | sì (`user_constellations`, `teams`) | no | out-of-scope, deprecate futuro |
| `GET /api/banners/special` | no | no | safe, lasciato in stato attuale |

Confermato che il futuro `user_artifact_inventory` **non riutilizza** `user_artifacts` legacy.

## 🔒 Invarianti rispettati
| File | MD5 atteso | OK |
|---|---|:---:|
| `backend/battle_engine.py` | `151ca35ad3bc35f0a6209cb3744ed440` | ✅ |
| `backend/.env` | `ff60bbb79efa329b71aa8ed351ea89b3` | ✅ |
| `frontend/app/artifacts-preview.tsx` | `0e75c94e00899af773dbc9faf7326a15` | ✅ |
| `frontend/app/artifacts.tsx` | `8849e21c44207fc1d0074cae2cdc6879` | ✅ |
| `frontend/app/(tabs)/gacha.tsx` | `f68b9239cec04ea54879f0be381e772a` | ✅ |
| `backend/routes/artifacts.py` | invariato (no modifiche logica) | ✅ |

7 POST mutativi legacy ancora `HTTP 423`. GET catalog `/api/artifacts/catalog` (32) e `/api/artifacts/catalog/preview` (10) preservati.

## 📁 File aggiunti
| Op | Path |
|:---:|---|
| A | `data/design/artifacts/inventory_schema_dry_run/artifact_inventory_source_legacy_get_audit_v1.json` |
| A | `data/design/artifacts/inventory_schema_dry_run/artifact_inventory_schema_design_v1.json` |
| A | `data/design/artifacts/inventory_schema_dry_run/artifact_inventory_sample_documents_v1.json` |
| A | `data/design/artifacts/inventory_schema_dry_run/artifact_inventory_future_api_contract_v1.json` |
| A | `data/design/artifacts/inventory_schema_dry_run/artifact_inventory_db_migration_rollback_plan_v1.json` |
| A | `data/design/artifacts/inventory_schema_dry_run/artifact_inventory_schema_dry_run_completion_v1.json` |
| A | `backend/scripts/validate_project_artifact_inventory_schema_dry_run_v1.py` |
| M | `backend/scripts/run_hero_skill_kit_validator_suite.py` (registrazione OPTIONAL) |
| A | `docs/divine/172_ARTIFACT_INVENTORY_SCHEMA_DRY_RUN.md` |

## Prossimo pack consigliato
`PROJECT_ARTIFACT_INVENTORY_GATED_IMPORT_PACK` (Stage 6) — richiede doppio signoff per impostare `ARTIFACT_INVENTORY_RUNTIME_ENABLED=true_explicit`.
