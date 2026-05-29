# 177 — PROJECT ARTIFACT STAGE 8 DOC PATH CLEANUP

## Verdetto locale
**`PROJECT_ARTIFACT_STAGE8_DOC_PATH_CLEANUP_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`**

> Diventerà `PROJECT_ARTIFACT_STAGE8_DOC_PATH_CLEANUP_COMPLETE_PUBLIC_REPO_VERIFIED` SOLO dopo che l'utente ha eseguito **Save to GitHub → branch `main` → PUSH** e verificato manualmente la repo pubblica.

---

## Obiettivo
Cleanup esclusivamente documentale del mismatch sul doc 176 Stage 8. Nessuna modifica a runtime, DB, frontend, gacha, battle, IAP, shop, Battle Pass, VIP, Soul Forge, Character Bible o invarianti backend.

---

## Decisione canonica
Il path canonico per il documento Stage 8 è:

📄 `docs/divine/176_ARTIFACT_INVENTORY_LIVE_APPLY_AUTHORIZED_CANARY.md`

Il path generico `docs/divine/176_ARTIFACT_INVENTORY_LIVE_APPLY.md` è mantenuto come **alias/redirect note** breve verso il canonico (per non rompere link storici da chat e tracker).

**Motivo**: lo Stage 8 NON è stato un live apply generico — è stato un **apply canary autorizzato internal-only** ristretto ai soli due canary user (`sfqa@test.com`, `test@test.com`). Il path canonico riflette questa natura.

---

## Marker di approvazione
```
PROJECT_ARTIFACT_STAGE8_DOC_PATH_CLEANUP_APPROVAL = true
PROJECT_ACCELERATION_MODE                          = ARTIFACT_STAGE8_DOC_PATH_CLEANUP_ONLY
```

---

## Audit (Track A)

### File fisici esistenti pre-cleanup
| Path                                                                    | Presente | Ruolo pre-cleanup                            | MD5 pre-cleanup                       |
|-------------------------------------------------------------------------|----------|----------------------------------------------|---------------------------------------|
| `docs/divine/176_ARTIFACT_INVENTORY_LIVE_APPLY.md`                      | ✅ sì    | canonical_doc_at_non_canonical_path          | `df1465b0732e8f7b783a3c7b76b7f7db`    |
| `docs/divine/176_ARTIFACT_INVENTORY_LIVE_APPLY_AUTHORIZED_CANARY.md`    | ❌ no    | canonical_path_missing (broken-link target)  | n/a                                   |

### Riferimenti già al path canonico (broken link pre-cleanup)
- `data/design/artifacts/live_apply/artifact_live_apply_completion_v1.json` (`doc_176` key) → `docs/divine/176_ARTIFACT_INVENTORY_LIVE_APPLY_AUTHORIZED_CANARY.md`

### Riferimenti hardcoded a doc 176 in script
- `backend/scripts/validate_project_artifact_inventory_live_apply_v1.py` → **nessuno** (validator non hardcoda paths doc)
- `backend/scripts/run_hero_skill_kit_validator_suite.py` → **nessuno**

### Altri 6 JSON in `data/design/artifacts/live_apply/`
Usano `ARTIFACT_INVENTORY_LIVE_APPLY_AUTHORIZED_CANARY` come `task_id`/`track` (identifier uppercase), **non** come path file → nessuna modifica necessaria.

📄 Audit completo: `data/design/artifacts/live_apply_doc_cleanup/stage8_doc_path_audit_v1.json`

---

## Normalizzazione (Track B)

### Azioni applicate
| Azione                                  | Target                                                                     | Note                                                                                   |
|-----------------------------------------|----------------------------------------------------------------------------|----------------------------------------------------------------------------------------|
| **CREATE_CANONICAL_FILE**               | `docs/divine/176_ARTIFACT_INVENTORY_LIVE_APPLY_AUTHORIZED_CANARY.md`       | Copia del contenuto pre-cleanup + banner header che marca esplicitamente il canonico. |
| **REWRITE_AS_ALIAS_REDIRECT_NOTE**      | `docs/divine/176_ARTIFACT_INVENTORY_LIVE_APPLY.md`                         | Demoted ad alias breve di redirect al canonico (44 righe).                            |
| NO_CHANGE                               | `data/design/artifacts/live_apply/artifact_live_apply_completion_v1.json`  | Già referenzia path canonico → broken link auto-risolto dalla creazione del file.    |
| NO_CHANGE                               | `backend/scripts/validate_project_artifact_inventory_live_apply_v1.py`     | Nessun hardcoded doc path.                                                            |
| NO_CHANGE                               | `backend/scripts/run_hero_skill_kit_validator_suite.py`                    | Nessun hardcoded doc path; registrazione Stage 8 invariata.                           |
| NO_CHANGE                               | `data/design/artifacts/live_apply/*` (gli altri 6 JSON)                    | Solo task_id uppercase; nessun path file a doc 176.                                  |

### MD5 dei due file 176 post-cleanup
```
40dcef8ad0a3b646c081c93c30ea6f59  docs/divine/176_ARTIFACT_INVENTORY_LIVE_APPLY.md                       (alias redirect)
000b17aa5b88b068f5df687b221fe0a4  docs/divine/176_ARTIFACT_INVENTORY_LIVE_APPLY_AUTHORIZED_CANARY.md     (canonical)
```

📄 Normalizzazione completa: `data/design/artifacts/live_apply_doc_cleanup/stage8_doc_reference_normalization_v1.json`

---

## Validazione & Invarianti (Track C)

### Stage 8 master validator
```bash
python3 /app/backend/scripts/validate_project_artifact_inventory_live_apply_v1.py
```
**Risultato**: `[PASS] PROJECT_ARTIFACT_INVENTORY_LIVE_APPLY master validator` ✅

### Suite custom Python
```bash
python3 /app/backend/scripts/run_hero_skill_kit_validator_suite.py --parallel \
  --json-out /app/backend/reports/stage8_doc_cleanup_suite_run.json
```
**Risultato**:
```
Overall: PASS  (pass=707, fail=0, miss=0)
EXIT=0
```

> Note flakiness: la prima esecuzione parallela ha riportato 1 FAIL transient su `V21-PREFLIGHT` (OPTIONAL) per race condition sul JSON di risultato condiviso. Esecuzione singola del solo `V21-PREFLIGHT` → PASS. Seconda esecuzione completa della suite → 707/707 PASS. Flakiness preesistente, non causata dal doc cleanup.

### MD5 Invarianti (FINALI, confermati)
```
151ca35ad3bc35f0a6209cb3744ed440  backend/battle_engine.py            ✅ UNCHANGED
ff60bbb79efa329b71aa8ed351ea89b3  backend/.env                        ✅ UNCHANGED
893f244d85fd45cbe825996463995293  backend/routes/artifacts.py         ✅ UNCHANGED
```

### Frontend protetti — MD5 invariati
```
0e75c94e00899af773dbc9faf7326a15  frontend/app/artifacts-preview.tsx
8849e21c44207fc1d0074cae2cdc6879  frontend/app/artifacts.tsx
f68b9239cec04ea54879f0be381e772a  frontend/app/(tabs)/gacha.tsx
```

### Surface lock ancora attivi (verificate)
- ✅ Legacy POST artifact/constellation → `HTTP 423`
- ✅ Gacha banner artifact/constellation → **hidden**
- ✅ Nessuna UI player live per inventory
- ✅ Nessun DB write durante il cleanup (0 chiamate motor/mongo)

📄 Validation completa: `data/design/artifacts/live_apply_doc_cleanup/stage8_doc_cleanup_validation_v1.json`

---

## ❌ Conferma scope NON violato

| Categoria                                       | Status |
|-------------------------------------------------|--------|
| DB writes                                       | ❌ 0   |
| New artifact grants/revokes                     | ❌ 0   |
| Endpoint/runtime backend changes                | ❌ no  |
| Frontend changes                                | ❌ no  |
| Gacha changes                                   | ❌ no  |
| `battle_engine.py` / battle core changes        | ❌ no  |
| `backend/routes/artifacts.py` changes           | ❌ no  |
| `backend/.env` changes                          | ❌ no  |
| IAP / shop / BP / VIP / Soul Forge changes      | ❌ no  |
| Character Bible mutation                        | ❌ no  |
| REQUIRED validator weakening                    | ❌ no  |
| OPTIONAL validator weakening                    | ❌ no  |
| Suite registration changes                      | ❌ no  |
| New validator added                             | ❌ no  |
| fake PASS                                       | ❌ no  |

---

## File creati / modificati (Track D)

### Nuovi
- ✅ `docs/divine/176_ARTIFACT_INVENTORY_LIVE_APPLY_AUTHORIZED_CANARY.md` (canonical Stage 8 doc, 245 righe)
- ✅ `docs/divine/177_ARTIFACT_STAGE8_DOC_PATH_CLEANUP.md` (questo file)
- ✅ `data/design/artifacts/live_apply_doc_cleanup/stage8_doc_path_audit_v1.json`
- ✅ `data/design/artifacts/live_apply_doc_cleanup/stage8_doc_reference_normalization_v1.json`
- ✅ `data/design/artifacts/live_apply_doc_cleanup/stage8_doc_cleanup_validation_v1.json`

### Modificati
- 🔧 `docs/divine/176_ARTIFACT_INVENTORY_LIVE_APPLY.md` — riscritto come alias/redirect note (44 righe; MD5 `df1465b0…` → `40dcef8a…`)

### Non modificati (esplicitamente verificati)
- `backend/scripts/validate_project_artifact_inventory_live_apply_v1.py`
- `backend/scripts/run_hero_skill_kit_validator_suite.py`
- `backend/routes/artifacts.py`
- `backend/battle_engine.py`
- `backend/.env`
- Tutti i 7 JSON in `data/design/artifacts/live_apply/`
- Tutti i file frontend (incluso `artifacts-preview.tsx`, `artifacts.tsx`, `(tabs)/gacha.tsx`, `soul-forge.tsx`, `shop.tsx`, ecc.)

---

## Public Repo Sync Verification — PENDING (azione utente)

### Stato locale ✅
- Suite custom Python: **707/707 PASS** (seconda esecuzione, parallela)
- Stage 8 master validator: **PASS**
- MD5 invarianti: ✅ tutti rispettati
- DB live: ✅ 0 write durante cleanup
- Surface lock: ✅ tutti attivi

### Azione richiesta all'utente
1. **Aprire pannello Emergent → click "Save to GitHub"**
2. Selezionare branch **`main`**
3. **PUSH**

### Verifica manuale su GitHub.com
- ✅ `docs/divine/176_ARTIFACT_INVENTORY_LIVE_APPLY_AUTHORIZED_CANARY.md` esiste (canonical, ~245 righe, contiene "PATH CANONICO" nell'header)
- ✅ `docs/divine/176_ARTIFACT_INVENTORY_LIVE_APPLY.md` esiste come breve alias (~44 righe, contiene "ALIAS / REDIRECT NOTE")
- ✅ `docs/divine/177_ARTIFACT_STAGE8_DOC_PATH_CLEANUP.md` esiste
- ✅ `data/design/artifacts/live_apply_doc_cleanup/` contiene i 3 JSON
- ✅ `backend/scripts/run_hero_skill_kit_validator_suite.py` invariato (PUBLIC_SYNC_TAG_RESYNC_v5 ancora presente, registrazione Stage 8 ancora presente)
- ✅ `backend/routes/artifacts.py` MD5 `893f244d85fd45cbe825996463995293`

Solo dopo questa verifica manuale → **`PROJECT_ARTIFACT_STAGE8_DOC_PATH_CLEANUP_COMPLETE_PUBLIC_REPO_VERIFIED`**.

---

## Verdict finale locale

**`PROJECT_ARTIFACT_STAGE8_DOC_PATH_CLEANUP_READY_LOCAL_CONTAINER_PUBLIC_SYNC_PENDING`**
