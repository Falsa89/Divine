# v110 STAGING SMOKE — Environment Classification

**Pack**: `MEGA_RELEASE_ACCELERATION_72_v110_PSP_APPLY_STAGING_SMOKE_LIMITED`
**Track**: B
**Public sync tag**: `PUBLIC_SYNC_TAG_v110_PSP_APPLY_STAGING_SMOKE_LIMITED`

## Classificazione

**`LOCAL_CONTAINER_NON_PROD`**

- mongo_url: `mongodb://localhost:27017` (localhost, NOT mongodb+srv)
- db_name: `divine_waifus` (nessun hint `prod`, nessun hint `staging`)
- `staging_marker_doc_found`: false (no `environment_markers` collection con `v110_staging_clone_confirmed=true`)
- `production_marker_doc_found`: false
- `safe_to_apply`: **false**

## Decisione operativa

Per policy del pack 72, l'apply può procedere solo se classification = `STAGING_CLONE_CONFIRMED`. Per `LOCAL_CONTAINER_NON_PROD` il pack rifiuta apply/backup/rollback execution e ricade sul **fallback rollback dry-run only**.

Questo e l'ambiente del container di sviluppo, contiene dati reali dell'app in esecuzione (850 accounts, 2362 user_heroes osservati nel dry-run pack 70). Non e un clone staging dedicato. Procedere con apply qui sarebbe **disonesto** rispetto alle regole del pack che richiedono esplicitamente "staging/clone confermato".

## Per sbloccare il prossimo pack

Provisionare un MongoDB clone con uno dei seguenti markers:

```
// option A: dedicated staging DB name
export DB_NAME=divine_waifus_staging_clone
// option B: marker document
db.environment_markers.insertOne({marker: "v110_staging_clone_confirmed", value: true})
```

## Safety flags

production_db_smoke=false, fake_PASS=false, release_readiness_claimed=false.

Riferimento: `data/design/v110_psp_apply_staging_smoke/v110_environment_classification_v1.json`.
