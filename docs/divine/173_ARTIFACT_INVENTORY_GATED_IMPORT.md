# 173 — PROJECT ARTIFACT INVENTORY GATED IMPORT

## Verdetto locale
**`PROJECT_ARTIFACT_INVENTORY_GATED_IMPORT_READY_NOT_APPLIED_MISSING_LIVE_MARKERS`**

> Diventerà `_COMPLETE_PUBLIC_REPO_VERIFIED` solo dopo Save to GitHub → branch `main` → PUSH e verifica della repo pubblica.

---

## Esito

I **due live marker** richiesti per qualsiasi DB write **NON sono presenti** nell'env del container:

```
PROJECT_ARTIFACT_INVENTORY_LIVE_APPROVAL   → ASSENTE
ARTIFACT_INVENTORY_RUNTIME_ENABLED         → ASSENTE
```

Conseguenza (per design):
- ❌ Nessuna `db.createCollection` eseguita
- ❌ Nessun insert / update / delete in MongoDB
- ❌ Nessun grant emesso, nessun utente toccato
- ❌ Nessun endpoint live aggiunto
- ❌ Nessuna modifica frontend, gacha, battle_engine, IAP, shop, BP, VIP, Character Bible
- ✅ Pacchetto produce **solo readiness audit + apply plan + script gated**

## 📦 Deliverable

| Track | File | Stato |
|---|---|:---:|
| A | `data/design/artifacts/gated_import/artifact_gated_import_readiness_audit_v1.json` | READY |
| B | `data/design/artifacts/gated_import/artifact_import_source_target_mapping_v1.json` | READY |
| C | `data/design/artifacts/gated_import/artifact_migration_script_safe_default_v1.json` | READY |
| C | `backend/scripts/artifact_inventory_gated_import_apply.py` (runner safe-by-default) | READY |
| D | `data/design/artifacts/gated_import/artifact_gated_import_apply_or_ready_not_applied_v1.json` | READY_NOT_APPLIED |
| E | `data/design/artifacts/gated_import/artifact_gated_import_runtime_frontend_guard_v1.json` | READY |
| F | `backend/scripts/validate_project_artifact_inventory_gated_import_v1.py` | READY |
| H | `data/design/artifacts/gated_import/artifact_gated_import_completion_v1.json` | READY |
| Doc | `docs/divine/173_ARTIFACT_INVENTORY_GATED_IMPORT.md` | (questo file) |

## 🛡️ Runner gated — `artifact_inventory_gated_import_apply.py`

Caratteristiche:
- **Default**: dry-run, output JSON, **zero DB op**
- **Apply richiede**:
  1. env `PROJECT_ARTIFACT_INVENTORY_LIVE_APPROVAL=true`
  2. env `ARTIFACT_INVENTORY_RUNTIME_ENABLED=true_explicit`
  3. CLI flag `--apply`
  4. CLI flag `--i-understand-this-will-write`
- **NON** registrato in startup hooks, supervisord, cron, server runtime
- **Non importa** `motor` a top-level (no client DB instanziato all'import)
- Anche con tutti i marker, in questo Stage 6 il runner **rinvia esplicitamente** a Stage 7 (`PROJECT_ARTIFACT_INVENTORY_LIVE_ACTIVATION_SIGNOFF_PACK`), restituendo `PROJECT_ARTIFACT_INVENTORY_GATED_IMPORT_LIVE_APPROVAL_RECEIVED_DEFERRED_TO_NEXT_PACK` — **double safety**: anche se qualcuno settasse i marker per errore, nessun write reale avviene fino al pack dedicato

### Exit codes
| Codice | Significato |
|:---:|---|
| `0` | dry-run completato / live apply rinviato a Stage 7 |
| `2` | apply richiesto ma marker assenti → REFUSED, 0 DB op |
| `3` | apply richiesto senza `--i-understand-this-will-write` → REFUSED |
| `4` | drift MD5 su invarianti rilevato → REFUSED |

### Smoke verificati
```
$ python3 backend/scripts/artifact_inventory_gated_import_apply.py
  → exit 0, READY_NOT_APPLIED_MISSING_LIVE_MARKERS, db_writes=0

$ python3 backend/scripts/artifact_inventory_gated_import_apply.py --apply --i-understand-this-will-write
  → exit 2, REFUSED (marker assenti), db_writes=0

$ PROJECT_ARTIFACT_INVENTORY_LIVE_APPROVAL=true ARTIFACT_INVENTORY_RUNTIME_ENABLED=true_explicit \
  python3 backend/scripts/artifact_inventory_gated_import_apply.py --apply
  → exit 3, REFUSED (manca --i-understand-this-will-write), db_writes=0
```

## 🗺️ Source/Target mapping (Track B)

**Sorgenti canoniche (uniche ammesse)**:
- `data/design/artifacts/artifact_bible_launch_draft_v1.json` (32 entry)
- `data/design/artifacts/preview/artifact_preview_dataset_v1.json` (10 entry, cross-validation only)
- `data/design/artifacts/inventory_schema_dry_run/artifact_inventory_schema_design_v1.json` (shape target)

**Sorgenti vietate**:
- `GET /api/artifacts` (legacy placeholder)
- `GET /api/constellations` (out of scope)
- `GET /api/banners/special` (legacy rates)
- Collection `user_artifacts`, `user_constellations` (legacy schema incompatibile)

**Target** (5 collection, **created_only_with_live_markers: true**):
| Target | Index uniche | Live |
|---|---|:---:|
| `artifact_catalog_snapshot` | `(artifact_id)` | ❌ |
| `user_artifact_inventory` | `(user_id, server_profile_id, artifact_id)` | ❌ |
| `artifact_inventory_ledger` | `(idempotency_key)` append-only | ❌ |
| `artifact_collection_state` | `(user_id, server_profile_id)` | ❌ |
| `artifact_idempotency_registry` | `(idempotency_key)` | ❌ |

`canary_internal_only_scope.max_canary_grants_per_run = 0` (nessun grant pianificato anche con marker presenti).

## 🔒 Invarianti rispettati
| File | MD5 atteso | OK |
|---|---|:---:|
| `backend/battle_engine.py` | `151ca35ad3bc35f0a6209cb3744ed440` | ✅ |
| `backend/.env` | `ff60bbb79efa329b71aa8ed351ea89b3` | ✅ |
| `backend/routes/artifacts.py` | `893f244d85fd45cbe825996463995293` | ✅ |
| `frontend/app/artifacts-preview.tsx` | `0e75c94e00899af773dbc9faf7326a15` | ✅ |
| `frontend/app/artifacts.tsx` | `8849e21c44207fc1d0074cae2cdc6879` | ✅ |
| `frontend/app/(tabs)/gacha.tsx` | `f68b9239cec04ea54879f0be381e772a` | ✅ |

7 POST mutativi legacy ancora `423`; GET catalog 32/10. Nessuna nuova collection MongoDB.

## 🧪 Suite custom Python
Target: **704/704 PASS** (703 storici + nuovo `PROJECT-ARTIFACT-INVENTORY-GATED-IMPORT`).

## 🔜 Prossimo pack consigliato
`PROJECT_ARTIFACT_INVENTORY_LIVE_ACTIVATION_SIGNOFF_PACK` (Stage 7) — introduce esplicitamente i due live marker dietro doppio signoff dell'utente, oppure alternativa: shift di priorità su IAP/BP/Shop modernization se Artifact non è ora.
